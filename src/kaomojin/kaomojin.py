from collections import defaultdict
from importlib import resources


def _init_kaomoji_dict():
    kaomoji_dict = defaultdict(set)
    with resources.path("kaomojin.data", "kaomoji") as dirpath:
        for path in dirpath.glob("*.tsv"):
            with open(path) as f:
                for line in f:
                    kao = line.strip()
                    n = len(kao)
                    kaomoji_dict[n].add(kao)
    return kaomoji_dict


kaomoji_dict = _init_kaomoji_dict()


class Node:
    def __init__(self, pos, text):
        self.pos = pos
        self.text = text
        self.left_nodes = []
        self.right_nodes = []
        self.best_left_node = None
        self.score = 0.0

    def __repr__(self):
        return self.__class__.__name__ + '({}, "{}")'.format(self.pos, self.text)

    def __eq__(self, node):
        return (
            self.__class__ is node.__class__
            and self.pos == node.pos
            and self.text == node.text
        )

    def __ne__(self, node):
        return not self.__eq__(node)


class BOT(Node):  # Beginning of text
    def __init__(self):
        super().__init__(-1, self.__class__.__name__)


class EOT(Node):  # End of text
    def __init__(self, pos):
        super().__init__(pos, self.__class__.__name__)


class Kaomoji(Node):
    pass


class NonKaomoji(Node):
    pass


class DG:
    """The directed graph representing possible tokenizations."""

    def __init__(self, text):
        self.make_graph(text)

    def __len__(self):
        return len(self._graph)

    def __getitem__(self, key):
        return self._graph[key]

    @property
    def max_token_length(self):
        return max(kaomoji_dict.keys())

    def make_graph(self, text):
        self.text = text
        length = len(text)

        # Initialize empty graph.
        graph = [[BOT()]]
        for _ in range(length + 1):
            graph.append([])
        self._graph = graph

        # Start parsing...
        for i in range(length):
            for j in range(i + 1, min(length + 1, i + 1 + self.max_token_length)):
                subtext = text[i:j]
                if subtext in kaomoji_dict.get(len(subtext), {}):
                    node = Kaomoji(i, subtext)
                    self._add_node(j, node)

        # Finalize graph.
        self._add_node(length + 1, EOT(length))

    def _add_node(self, idx, node):
        if node in self._graph[idx]:
            return

        pos = node.pos

        # If no node on the left side exists to which the new node connects, create one.
        if len(self._graph[pos]) == 0:
            i = pos - 1
            while 1:
                if len(self._graph[i]):
                    break
                i -= 1
            nonkaomoji_node = NonKaomoji(i, self.text[i:pos])
            self._add_node(pos, nonkaomoji_node)

        # Connect the new node to existing node(s) its left side.
        left_nodes = self._graph[pos]
        node.left_nodes = left_nodes
        for left_node in left_nodes:
            if node not in left_node.right_nodes:
                left_node.right_nodes.append(node)

        self._graph[idx].append(node)

    def optimize(self):
        return Viterbi.optimize(self)


class Viterbi:
    @classmethod
    def score_node(cls, node):
        if isinstance(node, Kaomoji):
            return +2.0 * len(node.text)
        return 0.0

    @classmethod
    def score_edge(cls, left_node, node):
        if isinstance(left_node, Kaomoji) and isinstance(node, Kaomoji):
            return -1.0
        return 0.0

    @classmethod
    def optimize(cls, graph):
        length = len(graph)
        for idx in range(1, length):
            for node in graph[idx]:
                score = -9999
                best_left_node = None

                node_score = cls.score_node(node)

                left_nodes = node.left_nodes
                for left_node in left_nodes:
                    edge_score = cls.score_edge(left_node, node)
                    partial_score = left_node.score + edge_score + node_score
                    if partial_score > score:
                        score = partial_score
                        best_left_node = left_node

                node.best_left_node = best_left_node
                node.score = score

        result = []
        node = graph[-1][0].best_left_node
        while 1:
            if isinstance(node, BOT):
                break
            result.append(node)
            node = node.best_left_node

        return reversed(result)


def analyze(text):
    dg = DG(text)
    return dg.optimize()


def extract(text):
    kaomojis = []
    for node in analyze(text):
        if isinstance(node, Kaomoji):
            kaomojis.append(node)
    return kaomojis


def extract_and_replace(text, new):
    texts = []
    kaomojis = []
    num = 0
    for node in analyze(text):
        if isinstance(node, Kaomoji):
            texts.append(new.format(num=num, pos=node.pos, text=node.text))
            kaomojis.append(node)
            num += 1
        else:
            texts.append(node.text)
    return kaomojis, "".join(texts)


def replace(text, new):
    texts = []
    num = 0
    for node in analyze(text):
        if isinstance(node, Kaomoji):
            texts.append(new.format(num=num, pos=node.pos, text=node.text))
            num += 1
        else:
            texts.append(node.text)
    return "".join(texts)
