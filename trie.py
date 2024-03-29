from pickle import load as pickle_load
import pandas as pd
from os.path import join as os_join

back_vowels = {'a', 'ı', 'o', 'u'}
front_vowels = {'e', 'i', 'ö', 'ü'}
vowels = back_vowels.union(front_vowels)
terminal_devoicing = {
    'ğ': 'k',
    'g': 'k',
    'c': 'ç',
    'b': 'p',
    'd': 't'
}

back_narrow_vowels = {'ı', 'u'}
front_narrow_vowels = {'i', 'ü'}
strong_consonants = {'k', 'ç', 'p', 't'}


with open(os_join('dictionary', 'nouns.pkl'), 'rb') as f:
    noun_dictionary = set(pickle_load(f))

with open(os_join('dictionary', 'verbs.pkl'), 'rb') as f:
    verb_dictionary = set(pickle_load(f))



class TrieNodeDerivational:

    def __init__(self, char):
        self.char = char
        self.children = {}
        self.is_suffix = False

    def markSuffix(self, input_form, output_form):
        self.is_suffix = True

        self.input_form, self.output_form = input_form, output_form
    
        if self.char in back_vowels or self.char in front_vowels:
            self.has_rules = True

    
    def applyRules(self, stem, possible_words=[], current_suffix=''):

        ## search in dictionary
        found = False
        if (self.input_form == 'N' and stem in noun_dictionary) or (self.input_form == 'V' and stem in verb_dictionary):
            # possible_words.append((stem, current_suffix))
            found = True
        else:
            # ünsüz yumuşaması
            if stem[-1] in terminal_devoicing:
                possible_word = stem[:-1] + terminal_devoicing[stem[-1]]
                if (possible_word in verb_dictionary and self.input_form == 'V') or (possible_word in noun_dictionary and self.input_form == 'N'):
                    # possible_words.append((possible_word, current_suffix))

                    stem = possible_word
                    found = True


        return stem, found




class TrieNodeInflectional:

    def __init__(self, char):
        self.char = char
        self.children = {}
        self.is_suffix = False
        self.has_rules = False

        self.is_noun_suffix, self.is_verb_suffix = False, False
        self.compare_priority, self.transit_priority = 0, 0


    def markSuffix(self, is_noun_suffix, is_verb_suffix, compare_priority, transit_priority):
        
        self.is_noun_suffix, self.is_verb_suffix = is_noun_suffix, is_verb_suffix
        self.compare_priority, self.transit_priority = compare_priority, transit_priority

        self.is_suffix = True
        self.haplology_vowels = {}

        if self.char in back_vowels:
            self.has_rules = True
            self.haplology_vowels = back_narrow_vowels
        elif self.char in front_vowels:
            self.has_rules = True
            self.haplology_vowels = front_narrow_vowels


    # dictionary lookup will be added
    def applyRules(self, stem, possible_words=[], current_suffix=''):

        suffix = '-' + current_suffix
        possible_words.append((stem, suffix))

        # ünsüz yumuşaması
        if stem[-1] in terminal_devoicing:
            possible_word = stem[:-1] + terminal_devoicing[stem[-1]]
            possible_words.append((possible_word, suffix))


        # ünlü daralması
        possible_word = None
        if self.is_verb_suffix and stem[-1] in vowels:
            if stem[-1] in back_narrow_vowels:
                possible_word = stem[:-1] + 'a'
            elif stem[-1] in front_narrow_vowels:
                possible_word = stem[:-1] + 'e'

        if possible_word is not None and self.compare_priority <= 1:
            possible_words.append((possible_word, suffix))


        # ünlü düşmesi
        if self.is_noun_suffix:
            vowel_counter = 0
            for letter in stem:
                vowel_counter += letter in vowels
                if vowel_counter > 1:
                    break
            if vowel_counter == 1 and stem[-1] not in vowels and stem[-2] not in vowels:
                for vowel in self.haplology_vowels:
                    possible_word = stem[:-1] + vowel + stem[-1]
                    possible_words.append((possible_word, suffix))



class TrieDerivational:

    def __init__(self):
        self.root = TrieNodeDerivational('')
        self.loadSuffixes()


    def insertSuffix(self, suffix, input_form, output_form):
        suffix = suffix[::-1]
        current_node = self.root            

        for char in suffix:
            if char in current_node.children:
                current_node = current_node.children[char]
            else:
                new_node = TrieNodeDerivational(char)
                current_node.children[char] = new_node
                current_node = new_node

        current_node.markSuffix(input_form, output_form)



    def loadSuffixes(self):
        df = pd.read_csv(os_join('Suffixes', 'Derivational', 'turkish_derivational_suffixes.csv'))

        for _, row in df.iterrows():
            self.insertSuffix(row['suffix'], row['input_form'], row['output_form'])



    def search(self, stem, suffix_accumulation):
        possible_words = []
        possible_roots = []
        if stem in verb_dictionary or stem in noun_dictionary:
            possible_words.append((stem, suffix_accumulation))
            possible_roots.append(stem)
        self.traverseTrie(stem, self.root, possible_words, possible_roots, suffix_accumulation, '')

        return possible_words, possible_roots


    def traverseTrie(self, remaining_word, current_node, possible_words, possible_roots, suffix, current_form):
        current_suffix = current_node.char + suffix
        if len(remaining_word) < 2:
            return False

        dictionary_match = False
        if current_node.is_suffix and (current_node.output_form == current_form or current_form == ''):
            remaining_word, dictionary_match = current_node.applyRules(remaining_word, possible_words, current_suffix)

        char = remaining_word[-1]

        if char in current_node.children:
            next_node = current_node.children[char]
            longer_found = self.traverseTrie(remaining_word[:-1], next_node, possible_words, possible_roots, current_suffix, current_form)

            if (not longer_found) and current_node.is_suffix and (current_node.output_form == current_form or current_form == ''):
                if dictionary_match:
                    possible_words.append((remaining_word, '-' + current_suffix))
                    possible_roots.append(remaining_word)
                return self.traverseTrie(remaining_word, self.root, possible_words, possible_roots, '-' + current_suffix, current_node.input_form) or dictionary_match
            
            return longer_found
        else:
            if current_node.is_suffix and (current_node.output_form == current_form or current_form == ''):
                if dictionary_match:
                    possible_words.append((remaining_word, '-' + current_suffix))
                    possible_roots.append(remaining_word)
                return self.traverseTrie(remaining_word, self.root, possible_words, possible_roots, '-' + current_suffix, current_node.input_form) or dictionary_match



class TrieInflectional:

    def __init__(self):
        self.rootNoun = TrieNodeInflectional('')
        self.rootVerb = TrieNodeInflectional('')
        self.rootCommon = TrieNodeInflectional('')
        self.loadSuffixes()


    def insertSuffix(self, suffix, is_noun_suffix, is_verb_suffix, compare_noun_priority, transit_noun_priority, compare_verb_priority, transit_verb_priority):
        suffix = suffix[::-1]
        if is_noun_suffix and ((transit_noun_priority == 6 and compare_noun_priority < 6) or transit_noun_priority < 6):
            compare_priority = compare_noun_priority
            if transit_noun_priority == 6:
                transit_priority = compare_noun_priority
            else:
                transit_priority = transit_noun_priority

            current_node = self.rootNoun            

            for char in suffix:
                if char in current_node.children:
                    current_node = current_node.children[char]
                else:
                    new_node = TrieNodeInflectional(char)
                    current_node.children[char] = new_node
                    current_node = new_node

            current_node.markSuffix(is_noun_suffix, False, compare_priority, transit_priority)

        if is_verb_suffix and transit_verb_priority <= 2:
            compare_priority, transit_priority = compare_verb_priority, transit_verb_priority
            current_node = self.rootVerb

            for char in suffix:
                if char in current_node.children:
                    current_node = current_node.children[char]
                else:
                    new_node = TrieNodeInflectional(char)
                    current_node.children[char] = new_node
                    current_node = new_node

            current_node.markSuffix(False, is_verb_suffix, compare_priority, transit_priority)
        
        if (transit_noun_priority >= 6 and compare_noun_priority == 6) or transit_verb_priority >= 3:
            if transit_noun_priority == 7:
                transit_priority, compare_priority = 7, 7
            else:
                transit_priority, compare_priority = 6, 6

            current_node = self.rootCommon

            for char in suffix:
                if char in current_node.children:
                    current_node = current_node.children[char]
                else:
                    new_node = TrieNodeInflectional(char)
                    current_node.children[char] = new_node
                    current_node = new_node

            current_node.markSuffix(True, True, compare_priority, transit_priority)

    def loadSuffixes(self):
        df = pd.read_csv(os_join('Suffixes', 'Inflectional', 'turkish_inflectional_suffixes.csv'))

        for _, row in df.iterrows():
            self.insertSuffix(row['suffix'], row['is_noun_suffix'], row['is_verb_suffix'], row['compare_noun_priority'], row['transit_noun_priority'], row['compare_verb_priority'], row['transit_verb_priority'])


    def countSuffixes(self, starting_node=None):
        if starting_node is None:
            starting_node = self.root

        children = starting_node.children
        if len(children) == 0:
            return 0 + starting_node.is_suffix
        sum = starting_node.is_suffix
        for letter in children:
            sum += self.countSuffixes(children[letter])

        return sum


    def findSuffix(self, substring, node, suffixes):
        current_suffix = node.char + substring
        if node.is_suffix:
            suffixes.append(current_suffix)
        if len(node.children) == 0:
            return
        else:
            for char in node.children:
                self.findSuffix(current_suffix, node.children[char], suffixes)


    def printSuffixes(self):
        suffixes = []
        for char in self.root.children:
            self.findSuffix(self.root.char, self.root.children[char], suffixes)
        
        print(suffixes)

        
    def search(self, stem):
        preprocessed = [(stem, '')]
        self.traverseTrie(stem, self.rootCommon, self.rootCommon, preprocessed, "", 8)
        possible_words = [(stem, '')]
        for prep in preprocessed:
            self.traverseTrie(prep[0], self.rootNoun, self.rootNoun, possible_words, prep[1], 8)
            self.traverseTrie(prep[0], self.rootVerb, self.rootVerb, possible_words, prep[1], 5)

        return possible_words


    def traverseTrie(self, remaining_word, current_node, root_node, possible_words, suffix, current_priority):
        current_suffix = current_node.char + suffix
        if len(remaining_word) < 2:
            return

        if current_node.is_suffix and current_node.compare_priority < current_priority:
            current_node.applyRules(remaining_word, possible_words, current_suffix)

        char = remaining_word[-1]

        if char in current_node.children:
            current_node = current_node.children[char]
            self.traverseTrie(remaining_word[:-1], current_node, root_node, possible_words, current_suffix, current_priority)
            if current_node.is_suffix and current_node.compare_priority < current_priority:
                if current_node.transit_priority >= current_priority and current_node.compare_priority > 0:
                    self.traverseTrie(remaining_word[:-1], root_node, root_node, possible_words, '-' + current_node.char + current_suffix, current_node.compare_priority)
                else:
                    self.traverseTrie(remaining_word[:-1], root_node, root_node, possible_words, '-' + current_node.char + current_suffix, current_node.transit_priority)
                return
        else:
            return




trie_inflectional = TrieInflectional()
trie_derivational = TrieDerivational()
def searchStems(input: str):
    dictionary_results = []

    possible_words, possible_roots = trie_inflectional.search(input), []
    for possible_word in possible_words:
        dictionary_matches, dictionary_roots = trie_derivational.search(possible_word[0], possible_word[1])

        dictionary_results = dictionary_results + dictionary_matches
        possible_roots += dictionary_roots

    return set(dictionary_results), set(possible_roots)