import random
import itertools
from networkx import (
    MultiGraph,
    DiGraph,
    find_cycle,
    NetworkXNoCycle,
    kosaraju_strongly_connected_components,
    is_strongly_connected,
    condensation
)


class TransactionManager(object):
    """
        -(1) It first finds the SCCs of the transaction graph.
        -(2) It then finds a feedback vertex set for each of the SCCs using a 2-approximation algorithm [8].
        -(3) It calculates the condensation graph, finds its sources and sinks and chooses representative sources and sinks.
        (4) It determines the leader set as the union of the feedback vertex set of each SCC and representative sources.
        (5) It finds all the possible paths for each of the parties to each of the leaders.
         As we saw in IV, for the hashlock of each party for each leader, different timeouts are set for different paths.
        **(6) It generates hashed timelock contracts in the Solidity language.
    """

    def __init__(self, graph: MultiGraph):
        self.graph = graph
        self.SCCs = None
        self.feedback_vertex_set = set()
        self.rep_srcs = set()
        self.rep_sinks = set()
        self.leaders = set()
        self.followers = set()

        self.condensation_graph = None

    def find_SCCS(self):
        """
            (1) It first finds the SCCs of the transaction graph.
        """
        # scc requires a digraph
        graph = DiGraph(self.graph)

        if is_strongly_connected(graph):
            # a list of sets ie [{0, 1, 2, 3}, {10, 11, 12}]
            self.SCCs = [c for c in sorted(kosaraju_strongly_connected_components(graph), key=len, reverse=True)]
        else:
            self.SCCs = list()

    def find_all_fvs(self):
        """
            (2) It then finds a feedback vertex set for each of the SCCs
        """
        if not self.SCCs:
            return

        # a list of tuple(1...N)
        nodes_combos = list(itertools.product(*self.SCCs))
        acyclic = False
        temp_fvs = set()

        for nodes_combo in nodes_combos:
            graph = self.graph.copy()
            for node in nodes_combo:
                temp_fvs.add(node)
                graph.remove_node(node)
                try:
                    # detect cycle
                    find_cycle(graph)
                except NetworkXNoCycle:
                    # no more cycle exist for the graph
                    acyclic = True
                    break
            if acyclic:
                break
            else:
                # clear temp set. the combo tried is not valid
                temp_fvs = set()

        # fvs found
        self.feedback_vertex_set = temp_fvs

    def condense_graph(self):
        self.condensation_graph = condensation(DiGraph(self.graph.copy()))

    def find_representive_src(self):
        """
            (3.1) It calculates the condensation graph, finds its sources and
            sinks and chooses representative sources.

            representative source is chosen as an arbitrary node with a condense SCC
        """

        if not self.condensation_graph:
            self.condense_graph()

        G = self.condensation_graph

        source_nodes = [node for node, indegree in G.in_degree(G.nodes()) if indegree == 0]

        for node_index in source_nodes:
            try:
                rep_src = random.choice(
                    list(
                        self.SCCs[node_index]
                    )
                )
                self.rep_srcs.add(rep_src)
            except:
                pass

    def find_representive_sink(self):
        """
         (3.2) It calculates the condensation graph, finds its sources and
            sinks and chooses sinks.

            representative sink is chosen as an arbitrary node with a condense SCC
        """
        if not self.condensation_graph:
            self.condense_graph()

        G = self.condensation_graph

        sink_nodes = [node for node, outdegree in G.out_degree(G.nodes()) if outdegree == 0]

        for node_index in sink_nodes:
            try:
                rep_sink = random.choice(
                    list(
                        self.SCCs[node_index]
                    )
                )
                self.rep_sinks.add(rep_sink)
            except:
                pass

    def generate_leaders(self):
        self.leaders = self.feedback_vertex_set.union(self.rep_srcs)
