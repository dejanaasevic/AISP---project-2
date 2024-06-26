class TrieNode:
    def __init__(self):
        self.children = {}
        self.word_end = False


class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.word_end = True

    def starts_with(self, prefix):
        node = self.root
        for char in prefix:
            if char not in node.children:
                return False
            node = node.children[char]
        return True

    def search_words(self, words):
        results = []
        for word in words:
            node = self.root
            found = True
            for char in word:
                if char not in node.children:
                    found = False
                    break
                node = node.children[char]
            if found:
                results.append(word)
        return results
