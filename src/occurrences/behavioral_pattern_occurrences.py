# Razvan Raducu. https://github.com/RazviOverflow
#import networkx as nx (Imported in path_common)
#import logging (Imported in path_common)
import sys
import pandas as pd
import argparse
import glob
import json
from pprint import pprint
from graph_path_traversal_utils import *
from os import path

MAX_INTERMEDIATE_NODES = 0 # maximum number of intermediate nodes allowed
PROBABILITY_THRESHOLD = 0.0
#NO_PROBABILITY = False

def parse_arguments():
    parser = argparse.ArgumentParser(
        prog="MalGraphIQ (Behavior Occurrences)",
        description="Identifies WBC patterns in the specified graph using a backtracking algorithm.")
    parser.add_argument("behavior_graph", 
        help="The behavior .gv file or directory in which patterns will be sought. In case a directory is specified, only .gv files will be considered.")
    parser.add_argument("-c", "--catalog", required=True, type=str,
        help="The path of the behavior catalog in JSON format. (See https://github.com/reverseame/windows-behavior-catalog)")
    parser.add_argument("-m", "--max_inter_nodes", type=int, default=0,
        help="(Default 0) The maximum number of intermediate nodes between each pattern node to consider in the behavior graph.")
    parser.add_argument("-p", "--prob_threshold", type=float, default=0.0,
        help="(Default 0.0) The probability threshold. Paths below the threshold are discarded.")
    parser.add_argument("--simple_paths_min_length", 
        help="(Default 1) Minimum numbers of nodes the simple paths must have, when calculating them from the .gv pattern files.")
    parser.add_argument("--json_file", required=False, 
        help="Specify the name of the JSON file to output the results. (.json extension will be automatically added)")

    group = parser.add_mutually_exclusive_group()
    group.add_argument("-q", "--quiet", action="store_true",
                        help="Only error and critical messages are printed.")
    group.add_argument("-s", "--silent", action="store_true",
                        help="Nothing is printed.")

    arguments = parser.parse_args()
    return arguments

def search(g_behavior,
    behavior_actual_node,
    pattern_node,
    pattern_path_to_find,
    result_path,
    end_node,
    step,
    solutions):
    '''

    Parameters:
        g_behavior: 
            Graph in which the pattern_path_to_find must be found, in case it exists.
        behavior_actual_node: 
            Pointer to the node of g_behavior being iterated over.
        pattern_node:
            The node of the pattern we're seeking in the behavior graph at the moment.
        pattern_path_to_find: 
            List of nodes (path) to find in g_behavior. This is the 'objective'.
        result_path: 
            The path from g_beh that starts and finishes with the same nodes
            as pattern_path_to_find and contains all the intermediate nodes in the same
            order with MAX_INTERMEDIATE_NODES intermediary nodes or less.
        end_node:
            Final node of pattern_to_find. If this node is found, it means the rest
            of the pattern has been already traversed and it is present in g_beh with
            max MAX_INTERMEDIATE_NODES intermediate nodes.
        step: 
            Number of steps so far. 
        solutions:
            The list of all the paths that represent a solution.

    This function is an implementation of the backtracking algorithm
    '''
    # Base condition: the pattern_node we're looking for at the moment 
    # is the end_node of the pattern. In that case, add it to the behavior_path
    # we've got so far and append the solution to solutions
    if behavior_actual_node == end_node:
        solution = result_path.copy()
        solutions.append(solution) 
        return result_path
    else:
        previous_length = len(result_path)
        # children = g_behavior.successors(behavior_actual_node)
        # The difference with successors() is that descendants() does not include itself
        # in case there is a loop (edge with same source and destiny) like (Node_X) ----> (Node_X))
        children = nx.descendants_at_distance(g_behavior,behavior_actual_node, 1)
        for child in children:
            if child == pattern_node:
                aux_path = result_path.copy()
                # If this child turns out to be the pattern_node we're seeking, add it to the result_path
                aux_path.append(child)
                # and now the next node we're seeking is the next node in pattern_path_to_find
                if pattern_path_to_find[-1] != pattern_node:
                    aux_pattern_node = pattern_path_to_find[pattern_path_to_find.index(pattern_node)+1] 
                else:
                    aux_pattern_node = pattern_node
                search(g_behavior, child, aux_pattern_node, pattern_path_to_find, aux_path, end_node, 0, solutions)
            elif step < MAX_INTERMEDIATE_NODES:
                aux_path = result_path.copy()
                aux_path.append(child)
                search(g_behavior, child, pattern_node, pattern_path_to_find, aux_path, end_node, step + 1, solutions)

            if result_path[-1] != end_node and len(result_path) != previous_length:
                # If finished iterating the branch of this child and the final node (end_node)
                # has not been reached (result_path[-1] != end_node) which means the pattern has not been found
                # yet and, at the same time, this child has been added to the result_path (len(result_path) != previous_length):
                # pop it because this child is not part of the solution (the seeked path)
                result_path.pop()

    return result_path

def get_label_weight(from_node, to_node, edge_attributes):
    if 'label' in edge_attributes[0]:
        return float(edge_attributes[0]['label'])
    else:
        return 0

def find_paths(g_behavior, pattern_simple_paths, simple_paths_min_length):
    '''
    Returns the simple paths present in g_behavior in MAX_INTERMEDIATE_NODES

    Parameters:
        g_behavior:
            Graph in which the simple_paths will be seek.
        pattern_simple_paths:
            Dict of pairs pattern-id:simple_path to seek in the graph.
        simple_paths_min_length:
            Minimum lenghth (measured in number of nodes) for the simple paths to be considered
    '''

    #print(f"{len(simple_paths)} individual paths to seek {simple_paths}")

    # Get only .values() because pattern_simple_paths is a dictionary whose key
    # is the ID of the pattern (.e.g: [C0036.004-P6]) and the value is the
    # pattern itself
    simple_paths = list(pattern_simple_paths.values())
    end_nodes = get_end_nodes(simple_paths)

    # We get the list of uniques first nodes of each simple path (pattern) to find:
    first_nodes = get_unique_start_nodes(simple_paths)
    # For each of these uniques first nodes, we get the probabilities from 'Start'
    # and insert them in a dictionary
    from_start_to_path = {}
    for node in first_nodes:
        if not g_behavior.has_node(node):
            continue
        start_node = get_start_node(g_behavior)
        # If start_node is the same node as target_node, nx.all_simple_paths(...) will return nothing when,
        # in this particular case, the path from start_node to target_node is the node itself
        if start_node == node:
            paths_for_node = [(1.0, start_node)]
        else:
            paths_for_node = get_all_paths_from_node_to_node_and_probabilities(g_behavior, start_node, node, PROBABILITY_THRESHOLD)
        from_start_to_path[node] = paths_for_node
        #print(f"Paths from Start to node {node}_ {paths_for_node}")   
        '''
        from_Start_to_path contains all the possible paths for any given node 
        from the 'Start' node to that node in the form of:
        {'Node':[
            (probability, [path_from_Start_to_node]),
            (probability, [path_from_Start_to_node]),
            (probability, [path_from_Start_to_node])
            ]
        }
        '''
    full_paths_found = 0
    for i, simple_path in enumerate(simple_paths):
        if not is_path_feasible(g_behavior, simple_path): 
            continue
        elif len(simple_path) < simple_paths_min_length:
            continue
        else:
            start_node = simple_path[0]
            path = []
            solutions = []
            path.append(start_node)

            if len(simple_path) == 1: # Single node simple_path
                solutions.append(simple_path) # Since this pattern is only 1 node long and the paths is feasible, just add it to solutions
            else:
                search(g_behavior, start_node, simple_path[1], simple_path[1:], path, end_nodes[i], 0, solutions) # Notice simple_path got deleted the first node because it is start_node and also the first one in path. We want to find the next nodes, excluding this first node.
            if not solutions:
                continue
            else:
                # If there is no probability threshold, the number of solutions found equals to the number 
                # of paths from the 'Start' node to solution[0]
                if PROBABILITY_THRESHOLD == 0.0:
                    for solution in solutions:
                        full_paths_found += len(from_start_to_path[solution[0]])
                else:
                    for solution in solutions:
                        if len(solution) == 1:
                            for prior_path in from_start_to_path[solution[0]]:
                                probability_of_full_solution = prior_path[0]
                                if probability_of_full_solution > PROBABILITY_THRESHOLD:
                                    full_paths_found += 1
                        else:
                            probability_of_solution = get_path_probability(g_behavior, solution)
                            if probability_of_solution > PROBABILITY_THRESHOLD:
                                for prior_path in from_start_to_path[solution[0]]:

                                    probability_of_full_solution = probability_of_solution*prior_path[0]
                                    if probability_of_full_solution > PROBABILITY_THRESHOLD:
                                        full_paths_found += 1
    return full_paths_found


def main(behavior_graph: str, catalog:str, json_file:str, max_internmediate_nodes: int, probability_threshold: int) -> None:
    MAX_INTERMEDIATE_NODES = max_internmediate_nodes
    PROBABILITY_THRESHOLD = probability_threshold

    try:
        with open(catalog) as catalog_file:
            behavior_catalog = json.load(catalog_file)
    except Exception as e:
        logger.error(f"[!] An unexpected error occurred: {e}. Cannot open {catalog}. ABORTING [!]")
        return -1

    behavior_graphs = list()
    if path.isfile(behavior_graph):
        behavior_graphs.append(behavior_graph)
    elif path.isdir(behavior_graph):
        behavior_graphs = glob.glob(behavior_graph+"/*.gv")
    else:
        logger.error("[!] ERROR. Unrecognized behavior parameters. Aborting.")

    combined_results = {}
    
    for behavior_graph in behavior_graphs:
        logger.info(f"[*] Analyzing graph {behavior_graph}")
        g_behavior = nx.nx_agraph.read_dot(behavior_graph)
        for micro_objective in behavior_catalog:
            micro_objective_id = micro_objective[:8]
            number_of_matches_per_micro_objective = 0
            for micro_behavior in behavior_catalog[micro_objective]:
                micro_behavior_id = micro_behavior[:7]
                number_of_matches_per_micro_behavior = 0
                for method in behavior_catalog[micro_objective][micro_behavior]:
                    method_id = method[:method.index(']')]                    
                    simple_paths = behavior_catalog[micro_objective][micro_behavior][method]
                    number_of_full_paths = find_paths(g_behavior, simple_paths, arguments.simple_paths_min_length)
                    if number_of_full_paths > 0:
                        number_of_matches_per_micro_behavior += number_of_full_paths                        
                    # Creating the dictionary skeleton and populating it
                    if f"{micro_objective}" not in combined_results:
                        combined_results[f"{micro_objective}"] = {}
                    if f"{micro_behavior}" not in combined_results[f"{micro_objective}"]:
                        combined_results[f"{micro_objective}"][f"{micro_behavior}"] = {}
                    if f"{method}" not in combined_results[f"{micro_objective}"][f"{micro_behavior}"]:
                        combined_results[f"{micro_objective}"][f"{micro_behavior}"][f"{method}"] = number_of_full_paths
                    else:
                        combined_results[f"{micro_objective}"][f"{micro_behavior}"][f"{method}"] += number_of_full_paths
                # After each micro_behavior is done, we add its matches to the total per micro_objectvie
                number_of_matches_per_micro_objective += number_of_matches_per_micro_behavior
                # After each micro_behavior is done, we add its total matches to the dictionary
                if "Total matches" not in combined_results[f"{micro_objective}"][f"{micro_behavior}"]:
                    combined_results[f"{micro_objective}"][f"{micro_behavior}"]["Total matches"] = number_of_matches_per_micro_behavior
                else:
                    combined_results[f"{micro_objective}"][f"{micro_behavior}"]["Total matches"] += number_of_matches_per_micro_behavior
            # After each micro_objective is done, we add its total matches to the dictionary
            if "Total matches" not in combined_results[f"{micro_objective}"]:
                combined_results[f"{micro_objective}"]["Total matches"] = number_of_matches_per_micro_objective
            else:
                combined_results[f"{micro_objective}"]["Total matches"] += number_of_matches_per_micro_objective

    if json_file:
        combined_results['n_processes'] = len(behavior_graphs)
        logger.info("[*] Dumping results to json file")
        with open(f"{json_file}.json", "w") as f:
            json.dump(combined_results, f)
    else:
        logger.info(f"[*] Results:")
        logger.info(f"[*] Number of processes: {len(behavior_graphs)}")
        print(json.dumps(combined_results, indent=4))

if __name__ == "__main__":
    arguments = parse_arguments()
    logging.basicConfig(level=logging.INFO, format="%(name)s (%(asctime)s) %(levelname)s - %(message)s")
    logger = logging.getLogger("MalGraphIQ (Behavior Occurrences)")
    if arguments.quiet:
        logger.setLevel(logging.ERROR)
    elif arguments.silent:
        # Turn off the logger
        logger.setLevel(logging.CRITICAL + 1)

    main(arguments.behavior_graph, arguments.catalog, arguments.json_file, arguments.max_inter_nodes, arguments.prob_threshold)