vowels = {'a', 'e', 'ı', 'i', 'o', 'ö', 'u', 'ü'}
terminal_devoicing = {
    'ğ': 'k',
    'g': 'k',
    'c': 'ç',
    'b': 'p',
    'd': 't'
}

haplology = {
    ''
}
narrow_vowels = {'ı', 'i', 'u', 'ü'}
strong_consonants = {'k', 'ç', 'p', 't'}


class TrieNode:
    

    def __init__(self, char):
        self.char = char
        self.children = {}
        self.is_suffix = False
        self.has_rules = False


    def markSuffix(self):
        self.is_suffix = True
        self.has_rules = self.char in vowels


    # dictionary lookup will be added
    def applyRules(self, word):
        possible_words = [word]
        if word[-1] in terminal_devoicing:
            possible_words.append(word[:-1] + terminal_devoicing[word[-1]])
        else:

            vowel_counter = 0
            for letter in word:
                vowel_counter += letter in vowels
                if vowel_counter > 1:
                    break
            if vowel_counter == 1 and word[-1] not in vowels and word[-2] not in vowels:
                for vowel in narrow_vowels:
                    possible_words.append(word[:-1] + vowel + word[-1])

        return possible_words


class Trie:

    def __init__(self):
        self.root = TrieNode('')


    def insertSuffix(self, suffix):
        current_node = self.root
        suffix = suffix[::-1]


        for char in suffix:
            if char in current_node.children:
                current_node = current_node.children[char]
            else:
                new_node = TrieNode(char)
                current_node.children[char] = new_node
                current_node = new_node

        current_node.markSuffix()


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
