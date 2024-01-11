from pickle import load as pickle_load
import pandas as pd

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


with open('nouns.pkl', 'rb') as f:
    noun_dictionary = set(pickle_load(f))

with open('verbs.pkl', 'rb') as f:
    verb_dictionary = set(pickle_load(f))


class TrieNode:
    
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

        if self.char in back_vowels:
            self.has_rules = True
            self.haplology_vowels = back_narrow_vowels
        elif self.char in front_vowels:
            self.has_rules = True
            self.haplology_vowels = front_narrow_vowels


    # dictionary lookup will be added
    def applyRules(self, stem, possible_words=[], current_suffix=''):

        ## search in dictionary
        if self.is_noun_suffix and stem in noun_dictionary:
            possible_words.append((stem, current_suffix))

        if self.is_verb_suffix and stem in verb_dictionary:
            possible_words.append((stem, current_suffix))


        # ünsüz yumuşaması
        if stem[-1] in terminal_devoicing:
            possible_word = stem[:-1] + terminal_devoicing[stem[-1]]
            if possible_word in verb_dictionary or possible_word in noun_dictionary:
                possible_words.append((stem, current_suffix))


        # ünlü daralması
        possible_word = None
        if self.is_verb_suffix:
            word_reverse = stem[::-1]
            for char in word_reverse:
                if char in vowels:
                    if char in back_narrow_vowels:
                        possible_word = stem[:-1] + 'a'
                    elif char in front_narrow_vowels:
                        possible_word = stem[:-1] + 'e'

                    break

        if possible_word is not None and possible_word in verb_dictionary:
            possible_words.append((stem, current_suffix))


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
                    if possible_word in noun_dictionary:
                        possible_words.append((stem, current_suffix))


        return possible_words


class Trie:

    def __init__(self):
        self.rootNoun = TrieNode('')
        self.rootVerb = TrieNode('')
        self.loadSuffixes()


    def insertSuffix(self, suffix, is_noun_suffix, is_verb_suffix, compare_noun_priority, transit_noun_priority, compare_verb_priority, transit_verb_priority):
        if is_noun_suffix:
            current_node = self.rootNoun
            suffix = suffix[::-1]

            for char in suffix:
                if char in current_node.children:
                    current_node = current_node.children[char]
                else:
                    new_node = TrieNode(char)
                    current_node.children[char] = new_node
                    current_node = new_node

            current_node.markSuffix(is_noun_suffix, is_verb_suffix, compare_noun_priority, transit_noun_priority)

        if is_verb_suffix:
            current_node = self.rootVerb
            suffix = suffix[::-1]

            for char in suffix:
                if char in current_node.children:
                    current_node = current_node.children[char]
                else:
                    new_node = TrieNode(char)
                    current_node.children[char] = new_node
                    current_node = new_node

            current_node.markSuffix(is_noun_suffix, is_verb_suffix, compare_verb_priority, transit_verb_priority)
            

    def loadSuffixes(self):
        df = pd.read_csv('turkish_inflectional_suffixes.csv')

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
        possible_words = []
        self.traverseTrie(stem, self.rootNoun, self.rootNoun, possible_words, "", 8)
        self.traverseTrie(stem, self.rootVerb, self.rootVerb, possible_words, "", 5)


    def traverseTrie(self, remaining_word, current_node, root_node, possible_words, suffix, current_priority):
        current_suffix = current_node.char + suffix
        if len(remaining_word) < 3:
            return
            
        if current_node.is_suffix and current_node.compare_priority < current_priority:
            current_node.applyRules(remaining_word, possible_words, current_suffix)

        char = remaining_word[-1]

        if char in current_node.children:
            current_node = current_node.children[char]
            self.search(remaining_word[:-1], current_node, possible_words, current_suffix, current_priority)
            if current_node.is_suffix and current_node.compare_priority < current_priority:
                self.search(remaining_word[:-1], root_node, possible_words, '-' + current_node.char + current_suffix, current_node.transit_priority)
                return
        else:
            return 
        
        
    

    def stem(self, word):
        possible_words = []
        if word in noun_dictionary or verb_dictionary:
            possible_words = [(word, '')]

        self.search(word, self.root, possible_words, '')
        return possible_words