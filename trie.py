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


class TrieNode:
    

    def __init__(self, char):
        self.char = char
        self.children = {}
        self.is_suffix = False
        self.has_rules = False


    def markSuffix(self, is_noun_suffix):
        self.is_noun_suffix = is_noun_suffix
        self.is_suffix = True
        if self.char in back_vowels:
            self.has_rules = True
            self.haplology_vowels = back_narrow_vowels
        elif self.char in front_vowels:
            self.has_rules = True
            self.haplology_vowels = front_narrow_vowels


    # dictionary lookup will be added
    def applyRules(self, word):
        stem = word[:-1]
        ## search in dictionary
        #possible_words = [stem]

        if stem[-1] in terminal_devoicing and self.is_noun_suffix: # ünsüz yumuşaması
            possible_words.append(stem[:-1] + terminal_devoicing[stem[-1]])
        else:
            if not self.is_noun_suffix:
                word_reverse = stem[::-1]
                for char in word_reverse:
                    if char in back_vowels:
                        possible_words.append(stem[:-1] + 'a')
                        break
                    elif char in front_vowels:
                        possible_words.append(stem[:-1] + 'e')
                        break
            else:
                vowel_counter = 0
                for letter in stem:
                    vowel_counter += letter in vowels
                    if vowel_counter > 1:
                        break
                if vowel_counter == 1 and stem[-1] not in vowels and stem[-2] not in vowels:
                    for vowel in self.haplology_vowels:
                        possible_words.append(stem[:-1] + vowel + stem[-1])

        return possible_words


class Trie:

    def __init__(self):
        self.root = TrieNode('')


    def insertSuffix(self, suffix, is_noun_suffix):
        current_node = self.root
        suffix = suffix[::-1]


        for char in suffix:
            if char in current_node.children:
                current_node = current_node.children[char]
            else:
                new_node = TrieNode(char)
                current_node.children[char] = new_node
                current_node = new_node

        current_node.markSuffix(is_noun_suffix)


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
