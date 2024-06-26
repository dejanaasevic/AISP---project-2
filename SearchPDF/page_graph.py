class PageGraph:
    def __init__(self):
        self.graph = {}

    def get_reference(self, page):
        return self.graph.get(page, [])

    def add_reference(self, from_page, to_page):
        if from_page not in self.graph:
            self.graph[from_page] = []
        self.graph[from_page].append(to_page)
