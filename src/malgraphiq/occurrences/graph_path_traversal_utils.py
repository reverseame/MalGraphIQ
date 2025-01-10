import networkx as nx

# Paths to be discarded (usually because they have no operational meaning but 
# result from our generation mechanism).
paths_to_filter = {
    "['GetCommandLine', 'GetCommandLine']":"",
    "['GetCommandLine', 'GetCommandLine', 'NtFreeVirtualMemory']":"",
    #"['WSAStartup', 'socket', 'setsockopt']":"",
    "['WSAStartup', 'closesocket']":"",
    "['WSAStartup', 'shutdown', 'closesocket']":"",
    "['NtCreateSection', 'NtMapViewOfSection']":"",
    "['NtQueryInformationThread', 'NtOpenSection']":"",
    "['NtWaitForSingleObject']":"",
    "['NtOpenKey']":"",
    "['NtQueryInformationThread', 'NtTerminateThread']":"",
    "['CryptAcquireContext', 'CryptDestroyKey']":"", 
    "['CryptAcquireContext'":"",
    "['CryptDestroyKey']":"",
}

def get_start_node(g: nx.DiGraph) -> str:
    """
    Retrieve the start node from a directed graph.

    Args:
        g (nx.DiGraph): Input graph.

    Returns:
        str: Start node label.
    """
    nodes_iterator = iter(g._node)
    first_node = next(nodes_iterator)
    # Start node should also be the first one and the only one with peripheries
    assert(g._node[first_node]["peripheries"] == "2") 
    return first_node

def already_in_paths(simple_paths: list[list[str]], path: list[str]) -> bool:
    """
    Check if any node from the the path _path_ is in at least one of the paths in _paths_.

    Args:
        simple_paths (list[list[str]]): List of existing paths.
        path (list[str]): Path to check for node presence.

    Returns:
        bool: True if any node from the path is present in the existing paths, False otherwise.
    """

    for aux_path in simple_paths:
        for node in path:
            if node in aux_path:
                return True
    return False

def node_already_in_paths(paths: list[str], node: str) -> bool:
    """
    Check if he node _node_ is present in any of the provided paths.

    Args:
        paths (list[str]): List of paths, where each path is a list of nodes.
        node (str): Node to check for presence.

    Returns:
        bool: True if the node is present in any path, False otherwise.
    """
    for path in paths:
        if node in path:
            return True
    return False

def filter_simple_paths(paths: list) -> list:
    """
    Filters the list paths by deleting all its elements (representing simple paths)
    present in the dict `paths_to_filter`, defined in this file. 

    Additionally, this function also deletes the sequence GetCommandLineA, GetCommandLineW
    from the beginning of the path.

    Args:
        paths (list): The list to filter, where each element is a simple path.

    Returns:
        list: The filtered path list.
    """

   
    for i, simple_path in enumerate(paths):
        #if len(simple_path) >= 2 and simple_path[0] == 'GetCommandLine' and simple_path[1] == 'GetCommandLine':
        #    paths[i] = simple_path[2:]
        if len(simple_path) >= 1 and simple_path[0] == 'GetCommandLine':
            paths[i] = simple_path[1:]


    new_paths = []

    for path in paths:
        if str(path) not in paths_to_filter:
            new_paths.append(path)

    return new_paths
    
def get_simple_paths(g: nx.DiGraph, start_node: str, min_length: int = 1) -> list:
    """
    Returns all the simple paths from start_node to 'others' node in graph g.

    If there are other nodes after the 'others' node (that is, 'others'
    node has successors), consider them as other individual paths
    from 'others' to 'others'. Then combine them to get every possible path.

    This function filters the irrelevant paths by invoking filter_simple_paths()

    Args:
        g (nx.DiGraph): The category graph to get the categorical walk from.
        start_node (str): The 'Start' node, according to its id/label (they're the same).
        min_length (int): Minimum numbers of nodes the simple paths must have (default: 1).

    Returns:
        list: List of simple paths.
    """
    simple_paths = []
    # get direct paths from 'Start' to 'others'
    for path in nx.all_simple_paths(g, source=start_node, target='others'):
        path = path[:-1] # Eliminate the 'others' node from the path
        #path = path[1:-1] # Eliminate the first (source) and last (target) nodes from the path
        #path = path[1:]
        #if len(path) > 1: # avoid single-node paths
        simple_paths.append(path)

    # Calculate all the successors of 'Start' that are also predecessors of 'others'.
    # This way, the paths whose start node is 'others' get preffixed with these
    # intermediate nodes, generating a new path for each one of them. 
    # start_successors = g.successors('Start')
    # others_predecessors = g.predecessors('others')
    # beginning_nodes = [node for node in start_successors if node in others_predecessors]

    # Calculate all the simple paths from 'others' to 'others'. Combine with 
    # previously calculated simple paths
    concatenated_paths = []
    if 'others' in g:
        for node in g.successors('others'):
            if not node_already_in_paths(simple_paths, node):
                for path in nx.all_simple_paths(g, source=node, target='others'):
                    path = path[:-1] # we only need to remove here the target, not the source
                    #if len(path) > 1: # avoid single-node paths
                    #if not already_in_paths(simple_paths, path):
                    for simple_path in simple_paths:
                        concatenated_paths.append(simple_path + path)
                    
    # Now merge the lists and delete those whose length is lesser than min_length
    all_paths = simple_paths+concatenated_paths
    all_paths = filter_simple_paths(all_paths) 
    all_paths[:] = [path for path in all_paths if len(path) > min_length]

    return all_paths

def get_unique_start_nodes(paths: list) -> list:
    """
    Get unique start nodes from a list of paths.

    Args:
        paths (list): List of paths.

    Returns:
        list: List of unique start nodes.
    """
    start_nodes = []
    for path in paths:
        start_nodes.append(path[0])
    return list(set(start_nodes))

def get_end_nodes(paths: list) -> list:
    """
    Get end nodes from a list of paths.

    Args:
        paths (list[list[str]]): List of paths.

    Returns:
        list[str]: List of end nodes.
    """
    end_nodes = []
    for path in paths:
        end_nodes.append(path[-1])
    
    # this could be a set instead of a list to avoid repeated end nodes (they are unneeded)
    return end_nodes

def is_path_feasible(g_behavior: nx.Graph, path: list[str]) -> bool:
    """
    Check if the path _path_ is feasible in graph _g_behavior_.

    A path is considered feasible if all its nodes are present in the graph.

    Args:
        g_behavior (nx.Graph): Behavior graph to check against.
        path (list[str]): Path to verify.

    Returns:
        bool: True if the path is feasible, False otherwise.
    """
    behavior_nodes = g_behavior.nodes()
    for node in path:
        if node not in behavior_nodes:
            #print(f"Node {node} not in behavior graph!")
            return False
    return True

def get_path_probability(g: nx.MultiDiGraph, path: list[str], initial_probability: float = 1.0) -> float:
    """
    Calculate the probability of the path (sequence of connected nodes) _path_ given
    the graph _g_.

    The probability is calculated by multiplying the edge weights (labeled as probabilities)
    along the path.

    Args:
        g (nx.MultiDiGraph): Graph containing the path.
        path (list[str]): List of nodes representing the path.
        initial_probability (float): Initial probability to start with (default: 1.0).

    Returns:
        float: Probability of the path.
    """
    probability = initial_probability
    graph_nodes_adjacency = g._adj
    for src_node, dst_node in zip(path, path[1:]):
        probability *= float(graph_nodes_adjacency[src_node][dst_node][0]['label'])

    return probability

def get_all_paths_from_node_to_node_and_probabilities(
    graph: nx.MultiDiGraph, 
    starting_node: str,
    destiny_node: str, 
    probability_threshold: float
) -> list[tuple[float, list[str]]]:
    """
    Get all paths and their probabilities between two nodes in a graph (from starting_node to destiny_node 
    in graph).

    Each path is represented as a tuple containing its probability and the sequence of nodes.

    Args:
        graph (nx.MultiDiGraph): Graph to search for paths.
        starting_node (str): Node to start the paths from.
        destiny_node (str): Node where the paths should end.
        probability_threshold (float): Minimum probability threshold for paths to be considered.

    Returns:
        list[tuple[float, list[str]]]: List of tuples, each containing the probability and path.
    """
    #paths = nx.single_source_dijkstra(graph, starting_node, destiny_node, weight=get_label_weight)
    #for i, simple_path in enumerate(nx.all_simple_paths(graph, starting_node, destiny_node, 8)):
    #    print(i, simple_path)

    ## CONFIGURATION PARAMETER: 'cutoff' -> This has a huge impact on the results.
    ## Based on our experiments, 5 is enough for the vast majority of the cases.
    paths = list(nx.all_simple_paths(graph, starting_node, destiny_node, 5)) # NEED TO LIMIT SOMEHOW THE LENGTH OF SIMPLE PATHS
    graph_nodes_adjacency = graph._adj
    all_paths = []
    for path in paths:
        skip = False
        probability = 1.0
        for src_node, dst_node in zip(path, path[1:]):
            weight = graph_nodes_adjacency[src_node][dst_node][0]
            if 'label' in weight:
                probability *= float(weight['label'])
            # If the probability of the path so far is under the threshold, we omit
            # this path and skip to the next one
            if probability < probability_threshold:
                skip = True
                break
        #print(f"Probability is: {probability} and threshold: {PROBABILITY_THRESHOLD}")
        if not skip:
            all_paths.append((probability, path))
    #pprint(sorted(all_paths))
    #sys.exit()
    #for path in paths:
    #    pprint(path)
    return all_paths

# def read_matrix_from_csv(file):
#     # It is very important to specify which column is the index.
#     transition_matrix = pd.read_csv(file, index_col=0) 
#     return transition_matrix
