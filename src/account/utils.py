from django.db import transaction
from account.models import (
    Hash,
    Path,
    Escrow,
    Transact,
    Contract,
    Wallet
)
from networkx import (
    Graph,
    DiGraph,
    find_cycle,
    diameter,
    MultiGraph,
    condensation,
    NetworkXNoCycle,
    all_simple_paths,
    is_strongly_connected,
    kosaraju_strongly_connected_components
)


class TransactManager(object):
    """
        abstraction of the transaction: contract creation process
    """
    def __init__(self):
        self.hash_objs_dict = dict()
        self.contract_objs = list()

    def transact_contracts(self, followers_paths: dict, leaders: set, transformed_edges: list,
                           node_value: dict, hashes: dict, _diameter: int):
        """
            follower_path: all possible path from followers to each leaders
            leaders: all leaders in the transformed graph
            transformed_edges: all node interconnections
            node_value: the value (outward) of each transformed_edges
            node: all included Node in the current transaction
            diameter: diameter graph
        """

        # all or nothing
        contracts_transact = None
        try:
            with transaction.atomic():
                self.create_hashes_objs(hashes, leaders)
                print('hashes created')
                self.create_paths_objs(followers_paths, leaders)
                print('created paths')
                self.create_contract_objs(transformed_edges, node_value, _diameter)
                print('created contracts!!!!!')
                contracts_transact = Transact()
                contracts_transact.save()
                print('created transaction')
                contracts_transact.contracts.add(*self.contract_objs)
                print('added contracts to the transaction')
        except Exception as e:
            print(e)
            contracts_transact = None

        print('returning contracts_transact!!!')
        return contracts_transact

    def create_hashes_objs(self, hashes: dict, leaders: set):
        assert len(leaders)
        assert len(hashes)

        for owner, _hash in hashes.items():
            # store hashes of all leader
            if owner in leaders:
                _hash_obj = Hash(hash=_hash.decode(), owner=owner)
                _hash_obj.save()
                self.hash_objs_dict[owner] = _hash_obj

    def create_paths_objs(self, followers_paths: dict, leaders: set):
        assert len(followers_paths)
        assert len(leaders)

        for owner in leaders:
            # collect all the paths objs
            path_objs = list()
            for node, paths in followers_paths.items():
                for path in paths:
                    if owner == path[-1]:
                        path_obj = Path(src=node, route_len=len(path))
                        path_obj.save()
                        path_objs.append(path_obj)
                        break

            # find owner hash obj and add all paths of all followers
            self.hash_objs_dict[owner].paths.add(*path_objs)

    def create_contract_objs(self, transformed_edges: list, node_value: dict, _diameter:int):
        assert len(transformed_edges)
        assert len(node_value)
        assert _diameter > 1

        for edges in transformed_edges:
            key = edges[0] + '->' + edges[1]

            if node_value.get(key, None):
                value = node_value[key][0]
                value_type = node_value[key][1]

                escrow = Escrow(amount=value, type=value_type)
                escrow.save()

                contract = Contract(
                    senderP=Wallet.objects.get(username=edges[0]).id,
                    receiverP=Wallet.objects.get(username=edges[1]).id,
                    diameter=_diameter,
                    escrow=escrow
                )
                contract.save()
                contract.hashes.add(*self.hash_objs_dict.values())
                self.contract_objs.append(contract)


class XChainWeb(object):
    """
        -(1) It first finds the SCCs of the transaction graph.
        -(2) It then finds a feedback vertex set for each of the SCCs using a 2-approximation algorithm [8].
        -(3) It calculates the condensation graph, finds its sources and sinks and chooses representative sources and sinks.
        -(4) It determines the leader set as the union of the feedback vertex set of each SCC and representative sources.
        (5) It finds all the possible paths for each of the parties to each of the leaders.
         As we saw in IV, for the hashlock of each party for each leader, different timeouts are set for different paths.
        **(6) It generates hashed timelock contracts in the Solidity language.
    """

    def __init__(self, nodes: list, edges: list, node_values: dict, hashes: dict, tranform_graph: bool = True):
        # passable
        self.nodes = nodes
        self.edges = edges
        self.node_value = dict()  # {'A->B': (value, value_type) }
        self.hashes = hashes

        # native
        self.SCCs = list()
        self.leaders = set()
        self.rep_srcs = set()
        self.rep_sinks = set()
        self.contractor = None
        self.followers_paths = dict()
        self.condensation_graph = None
        self.feedback_vertex_set = set()
        self.transaction = None

        if tranform_graph:
            self.transform_graph(
                nodes,
                edges,
                node_values
            )

    def transform_graph(self, nodes, edges, node_value):
        print('FFKBV NFIOKLF B')
        self.nodes = ['A', 'B', 'C']
        self.edges = [('A', 'C'), ('B', 'C'), ('B', 'A'), ('C', 'B')]
        self.node_value = {
            'A->C': (2, 'bit'),
            'B->C': (1, 'bit'),
            'B->A': (1, 'zcoin'),
            'C->B': (2, 'ether')
        }

    def build_xchain_data(self):
        self.find_SCCS()
        self.find_all_fvs()
        self.condense_graph()
        self.find_representive_sink()
        self.find_representive_src()
        self.generate_leaders()
        self.find_all_path()

    def build_xchain_contracts(self):
        self.contractor = TransactManager()
        self.transaction = self.contractor.transact_contracts(
            self.followers_paths, self.leaders,
            self.edges, self.node_value,
            self.hashes, _diameter=diameter(self.create_graph('di'))
        )

    def create_graph(self, _type: str):

        if _type == 'di':
            graph = DiGraph()
        elif _type == 'mx':
            graph = MultiGraph()
        else:
            # _type == 'g'
            graph = Graph()

        graph.add_edges_from(self.edges)
        graph.add_nodes_from(self.nodes)
        return graph

    def find_SCCS(self):
        """
            (1) It first finds the SCCs of the transaction graph.
            verified
        """
        # scc requires a digraph
        graph = self.create_graph(_type='di')
        self.SCCs = list(kosaraju_strongly_connected_components(graph))
        self.SCCs.sort()

    def find_all_fvs(self):
        """
            (2) It then finds a feedback vertex set for each of the SCCs
            verified
        """
        graph_prime = self.create_graph(_type='di')


        try:
            # if cycle then cyclic nodes
            find_cycle(graph_prime)

            for scc in self.SCCs:
                if len(scc) > 1:
                    nodes_to_drop = list((set(graph_prime.nodes()) - scc))
                    graph = graph_prime.copy()
                    graph.remove_nodes_from(nodes_to_drop)

                    # graph is now only the current scc. is there any cycle
                    assert len(scc) == graph.__len__()

                    # idea: remove the nodes with the most out-edge
                    digraph = graph.copy()
                    out_degree_tup_list = list(digraph.out_degree(digraph.nodes()))
                    out_degree_tup_list.sort(key=lambda x: x[1], reverse=True)
                    print(out_degree_tup_list)

                    # nodes are in sorted order by out-degree DESC
                    for pair in out_degree_tup_list:
                        graph.remove_node(pair[0])
                        print(pair[0])
                        try:
                            # detect cycle
                            find_cycle(graph)
                        except NetworkXNoCycle:
                            # no more cycle exist for the graph
                            self.feedback_vertex_set.add(pair[0])
                            break
        except NetworkXNoCycle:
            # no cycle exist. no work needed
            pass

    def condense_graph(self):
        self.condensation_graph = condensation(self.create_graph(_type='di'), scc=self.SCCs)

    def find_representive_src(self):
        """
            (3.1) It calculates the condensation graph, finds its sources and
            sinks and chooses representative sources.

            representative source is chosen as an arbitrary node with a condense SCC
        """

        if not self.condensation_graph:
            self.condense_graph()

        G = self.condensation_graph
        G_prime = self.create_graph(_type='di')
        source_nodes = [node for node, indegree in G.in_degree(G.nodes()) if indegree == 0]

        for node_index in source_nodes:
            try:
                best_node = None
                best_node_degree = None

                for node in self.SCCs[node_index]:
                    current_degree = G_prime.out_degree(node)

                    if not best_node_degree and not best_node:
                        best_node = node
                        best_node_degree = current_degree

                    elif current_degree > best_node_degree:
                        best_node = node
                        best_node_degree = current_degree

                    # print(current_degree, node)
                    # print(best_node_degree, best_node)
                if best_node:
                    self.rep_srcs.add(best_node)
            except Exception as e:
                print(str(e))

    def find_representive_sink(self):
        """
         (3.2) It calculates the condensation graph, finds its sources and
            sinks and chooses sinks.

            representative sink is chosen as an arbitrary node with a condense SCC
        """
        if not self.condensation_graph:
            self.condense_graph()

        G = self.condensation_graph
        G_prime = self.create_graph(_type='di')

        sink_nodes = [node for node, outdegree in G.out_degree(G.nodes()) if outdegree == 0]

        for node_index in sink_nodes:
            try:
                best_node = None
                best_node_degree = None
                for node in self.SCCs[node_index]:
                    current_degree = G_prime.in_degree(node)
                    wild_card = G_prime.out_degree(node)

                    if node in self.rep_srcs:
                        pass

                    # this node has no out edge it definitely a sink
                    elif wild_card == 0:
                        self.rep_sinks.add(node)
                        best_node = None
                        best_node_degree = None

                    elif not best_node_degree and not best_node:
                        best_node = node
                        best_node_degree = current_degree

                    elif best_node_degree and current_degree > best_node_degree:
                        best_node = node
                        best_node_degree = current_degree

                if best_node:
                    self.rep_sinks.add(best_node)
            except Exception as e:
                print(str(e))

    def generate_leaders(self):
        if len(self.nodes) == 2:
            self.leaders = self.rep_srcs
        else:
            self.leaders = self.feedback_vertex_set.union(self.rep_srcs)

    def find_all_path(self):

        # here we used a undirected graph to find path for
        # strongly conn graph and non-strongly conn graph

        if is_strongly_connected(self.create_graph('di')):
            graph = self.create_graph('di')
        else:
            graph = self.create_graph('')

        followers = set(self.nodes) - self.leaders
        followers_paths = dict()

        for node in followers:
            generator = all_simple_paths(graph, source=node, target=self.leaders)
            paths = list()

            for path in generator:
                paths.append(path)

            followers_paths[node] = paths
        # dict with list of lists
        self.followers_paths = followers_paths


# from account.utils import *
# t = XChainWeb()
# t.find_SCCS()
# t.find_all_fvs()
# t.feedback_vertex_set
# t.condense_graph()
# t.find_representive_src()
# t.rep_srcs
# t.find_representive_sink()
# t.rep_sinks


# set 1
# nodes = ['A', 'B']
# edges = [('A', 'B'),('B', 'A')]
# node_value = {
#     'A->B': (1, 'bit'),
#     'B->A': (2, 'ether'),
# }

# set 2
# nodes = ['A', 'B', 'C']
# edges = [('A', 'C'), ('B', 'C'), ('B', 'A'), ('C', 'B')]
# node_value = {
#     'A->C': (2, 'bit'),
#     'B->C': (1, 'bit'),
#     'B->A': (1, 'zcoin'),
#     'C->B': (2, 'ether')
# }

# set 3
# nodes = ['A', 'B', 'C', 'D']
# edges = [('A', 'D'),('D', 'A'), ('D', 'B'), ('D', 'C')]
# node_value = {
#     'A->D': (1, 'ether'),
#     'D->A': (1, 'bit'),
#     'D->B': (1, 'bit'),
#     'D->C': (1, 'bit')
# }

# set 4
# nodes = ['A', 'B', 'C', 'D', 'E']
# edges = [('D', 'C'), ('A','E'), ('A', 'D'), ('E', 'C'),('A', 'B')]
# node_value = {
#     'A->B': (1, 'bit'),
#     'A->D': (1, 'bit'),
#     'A->E': (1, 'bit'),
#     'D->C': (3, 'ether'),
#     'E->C': (1, 'ether'),
# }

# set 5
# nodes = ['A', 'B', 'C', 'D', 'E','F']
# edges = [('D', 'E'), ('A','E'), ('A', 'F'), ('E', 'B'),('E', 'C'),('E','F')]
# node_value = {
#     'A->E': (5, 'ether'),
#     'A->F': (2, 'bit'),
#     'D->E': (6, 'ether'),
#     'E->B': (1, 'bit'),
#     'E->C': (2, 'bit'),
#     'E->F': (3, 'bit'),
# }

# set 6 not exactly correct but maybe still valid
# nodes = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
# edges = [
# ('A', 'B'),
# ('B', 'C'), ('B', 'D'),
# ('C', 'A'),
# ('D', 'E'), ('D', 'G'),
# ('E', 'G'), ('E', 'F'),
# ('F', 'E'),
# ]
# node_value = {
#     'A->B': (3, 'bit'),
#     'B->D': (5, 'ether'),
#     'B->C': (1, 'ether'),
#     'C->A': (3, 'zcoin'),
#     'D->E': (4, 'zcoin'),
#     'D->G': (8, 'zcoin'),
#     'E->G': (1, 'bit'),
#     'E->F': (3.5, 'bit'),
#     'F->E': (3, 'bit'),
# }

# from account.utils import *
# t = XChainWeb(nodes,edges,node_value,{'A': b'secret1', 'B': b'secret2','C': b'secret1', 'D': b'secret2','E': b'secret1','F': b'secret1'}, False)
# t.build_xchain_data()
