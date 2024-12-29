import json
import requests
import pandas as pd
import numpy as np
from graphviz import Digraph
import matplotlib.pyplot as plt
from pathlib import Path
import argparse
import logging
import os
import glob

from categories_colors_map import categories_and_colors as colors

JSON_DATA = {}
PRINT_EDGE_LABELS = False

def parse_arguments():
    """
    Arguments parsing.
    """
    parser = argparse.ArgumentParser(
        prog="MalGraphIQ (Transition Matrices and Graphs)",
        description="Renders CAPE reports and transforms them into transition matrixes and different graphs (visualizations).")
    parser.add_argument("json_dir", help="A .json report o a directory containing one or more JSON reports. If the parameter is a directory, the program automatically parses all .JSON files within it.")
    parser.add_argument("-o", "--output", default="REPORTS",
                        help="Output folder.")
    parser.add_argument("-w", "--winapi-categories", default="./winapi_categories.json",
                        help="Path to winapi_categories.json file (as obtained from https://github.com/reverseame/winapi-categories). By default the program will look into the current working directory. If the file does not exist, the program will attempt to download it unless -nd/--no-download is specified.")

    group2 = parser.add_mutually_exclusive_group()
    group2.add_argument(
        "-c", "--category", 
        action="store_true", 
        help="Generate only the category graph(s)."
    )
    group2.add_argument(
        "-b", "--behavior", 
        action="store_true", 
        help="Generate only the behavior graph(s)."
    )

    parser.add_argument("-nd", "--no-download", action="store_true",
                        help=f"Prevents {parser.prog} from downloading winapi_categories.json. By default it attempts to download it in the -w/--winapi-categories specified path.")
    parser.add_argument("-pp", "--print_transition_probabilities", action="store_true",
                        help=f"If specified, transition probabilities are printed in the visualizations (behavior and category graphs). By default they aren't printed.")

    group = parser.add_mutually_exclusive_group()
    group.add_argument("-q", "--quiet", action="store_true",
                        help="Only error and critical messages are printed.")
    group.add_argument("-s", "--silent", action="store_true",
                        help="Nothing is printed.")

    # Parse the arguments
    args = parser.parse_args()
    
    return parser.parse_args()


def prob_error(row, total_probabilities, matrix):
    return f"The probabilities of row: {row} do not sum 1\n{total_probabilities}\n{matrix}"

# https://stackoverflow.com/a/58666031
def unique(sequence):
    seen = set()
    return [x for x in sequence if not (x in seen or seen.add(x))]

def transition_matrix(data, alphabet):
    '''
    Generation of the transition matrix by creating a 
    len(alphabet)xlen(alphabet) matrix and fulfilling with 0.0 by now
    '''
    # Buscar info acerca de las matrices dispersas
    matrix = pd.DataFrame(0.0, index=alphabet, columns=alphabet)
    '''
    In order to count how many times each states transitions to
    one another, we use two pointers: previous_state and actual_state.
        previous_state: points to the first state in the alphabet and moves on
        actual_state: points to the second state in the alphabet and moves on
    Counting means adding (sum) 1 to the cell of the transition matrix
    corrseponding to the row actual_state and the column previous_state. That is:
    matrix[previous_state][actual_state]
    
    In other words, we reached the actual state (matrix[actual_state]) from
    the previous state matrix[previous_state][actual_state], and that's a transition
    '''
    previous_state = data[0]
    for actual_state in data[1:]:
        #matrix[actual_state][previous_state] += 1.0
        #matrix[previous_state][actual_state] += 1.0
        matrix.loc[actual_state, previous_state] += 1.0
        previous_state = actual_state
    
    '''
    To get the probabilities, we must first know how many times a given state
    transitions. That is, the sum of all its transitions, regardless of the
    destiny state, To achieve that, the sum() method can be used
    https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.sum.html
    the default axis is 0, which stand for index and it sums ALL the indexes
    of a given column (counterintuitive thinking)
    '''
    total = matrix.sum()
    for element in alphabet:
        matrix[element] = matrix.div(total[element])[element]
    
    '''
    Very important to transpose the DataFrame given that Panda's DF access is made
    by columns, not by rows as a normal matrix. So after generating the data and 
    getting the probabilities, it must be transposed to represent an actual matrix.
    '''
    matrix = matrix.transpose()
    total_probabilities = matrix.sum(axis=1)
    for i, row in enumerate(total_probabilities):
        if row == 0:
            print(f"[!] Skipping ASSERT. Probability is zero. Probably last API call?\n{total_probabilities.index[i]}: {total_probabilities[i]}")
            continue
        row = np.around(row, 2) # Rounding to 2 decimals so 0.9999999000001 becomes 1
        assert row == 1, prob_error(row, total_probabilities, matrix)
    return matrix

def render_matrix(matrix, alphabet, graphname, labels=True):
    graph = Digraph(graphname, format='pdf', engine='dot')

    start_of_graph = True
    drawn_nodes = {} # Avoid re-adding nodes
    for i, row in enumerate(matrix.index):
        for column in matrix.columns:
            if matrix.loc[row][column] > 0: # Use .loc() to access DataFrame by row label
                #breakpoint()
                shape = 'ellipse'
                peripheries = "0"
                if start_of_graph:
                    #shape = 'box'
                    peripheries = "2"
                    start_of_graph = False
                if row not in drawn_nodes:
                    graph.node(row, label=row, peripheries = peripheries, style='filled', fillcolor=colors[alphabet[row]] if row != 'others' else colors['others']) # 'others' node
                    drawn_nodes[row] = ""
                # Unrolling the 'others' node
                #if row in alphabet:
                    #graph.node(row, label=row, style='filled', fillcolor=colors[alphabet[row]])
                #else:
                    ##graph.node(row, label=row, style='filled', fillcolor=colors[row]) # Colored
                    #graph.node(row, label=row, style='filled', fillcolor='#FFFFFF') # Uncolored
                if column not in drawn_nodes:
                    graph.node(column, label=column, style='filled', fillcolor=colors[alphabet[column]] if column != 'others' else colors['others']) # 'others' node
                    drawn_nodes[column] = ""
                # Unrolling the 'others' node
                #if column in alphabet:
                    #graph.node(column, label=column, style='filled', fillcolor=colors[alphabet[column]])
                #else:
                    ##graph.node(column, label=column, style='filled', fillcolor=colors[column]) # Colored
                    #graph.node(column, label=column, style='filled', fillcolor='#FFFFFF') # Uncolored
                edge_color = "black"
                label = str(np.around(matrix.loc[row][column], 4)) 
                if labels:
                    graph.edge(row, column, label=label, fontcolor=edge_color)
                else:
                    graph.edge(row, column) # No label
                #graph.edge(row, column, label=str(np.around(matrix.loc[row][column],4)))
                #if start_of_graph:
                    #start_of_graph = False
                    ##graph.node('Start', label='Start', style='filled', fillcolor='black', fontcolor='white')
                    #graph.node('Start', label='', style='filled', fillcolor='black', fontcolor='white', shape='circle')
                    #graph.edge('Start', row)
    graph.render()

def obtain_winapi_file(winapi_categories_path: str) -> str | int:
    try:
        logger.info("[*] Downloading winapi_categories.json from official repo (https://github.com/reverseame/winapi-categories)")
        r = requests.get("https://raw.githubusercontent.com/reverseame/winapi-categories/refs/heads/main/winapi_categories.json")
        with open(winapi_categories_path, "w") as winapi_categories:
            winapi_categories.write(r.text)
        logger.info(f"[*] Successfully downloaded at {winapi_categories_path}")
        return winapi_categories_path
    except Exception as e:
        logger.error(f"[!] An unexpected error occurred: {e}. Cannot download winapi_categories.json [!]")
        return -1

def load_categories(winapi_categories_path: str, dont_download_winapi: bool) -> int:
    if not os.path.exists(winapi_categories_path):
        if dont_download_winapi:
            logger.warning("[!] winapi_categories.json file not found. Category refactoring can't be done. You can download it from https://github.com/reverseame/winapi-categories [!]")
            logger.warning("[!] You could, for example, run the following command: \n\t $ wget https://raw.githubusercontent.com/reverseame/winapi-categories/refs/heads/main/winapi_categories.json")
            return -1
        else:
            logger.info("[*] winapi_categories.json file not detected, attempting to download it.")
            if (winapi_categories_path := obtain_winapi_file(winapi_categories_path)) == -1:
                logger.error("[!] Cannot obtain winapi_categories.json. Continuing without it [!]")
                return winapi_categories_path
    else:
        logger.info(f"[*] {winapi_categories_path} found. No need to download.")

    try:
        global JSON_DATA
        with open(winapi_categories_path) as file:
            JSON_DATA = json.load(file)
        return 0
    except Exception as e:
        logger.error(f"[!] An unexpected error occurred: {e}. Cannot open winapi_categories.json [!]")
        return -1

def generate_api_call_transitions(api_call_transitions, alphabet, process_name, process_id, behavior_graph_path, print_edge_labels):
    """
    Generate API call transitions matrix and save it to a file.

    Args:
        api_call_transitions (list): API call transitions data.
        alphabet (list): Alphabet for transitions.
        process_name (str): Process name.
        process_id (int): Process ID.
        behavior_graph_path (str): Path to save the API call transitions matrix.
        print_edge_labels (bool): Whether to print edge labels.
    """
    api_call_transitions_matrix = transition_matrix(api_call_transitions, list(alphabet))
    filename = f"{behavior_graph_path}/{process_name}_{process_id}_API_Calls_Transition_Matrix"
    api_call_transitions_matrix.to_csv(f"{filename}.csv")
    render_matrix(api_call_transitions_matrix, alphabet, filename, print_edge_labels)

def generate_api_per_category_transitions(api_per_category_transitions, alphabet, process_name, process_id, category_graph_path, print_edge_labels):
    """
    Generate API per category transitions matrix and save it to a file.

    Args:
        api_per_category_transitions (dict): API per category transitions data.
        process_name (str): Process name.
        process_id (int): Process ID.
        category_graph_path (str): Path to save the API per category transitions matrix.
        print_edge_labels (bool): Whether to print edge labels.
    """
    for category in api_per_category_transitions:
        api_per_category_alphabet = list(unique(api_per_category_transitions[category]))
        api_per_category_transitions_matrix = transition_matrix(api_per_category_transitions[category], api_per_category_alphabet)
        category = category.replace('/', '_') # Needed to dele slashes from category names like '.. I/O ...'
        filename = f"{category_graph_path}/{process_name}_{process_id}_{category}_API_per_Category_Transition_Matrix"
        api_per_category_transitions_matrix.to_csv(f"{filename}.csv")
        render_matrix(api_per_category_transitions_matrix, alphabet, filename, print_edge_labels)


#     api_per_category_alphabet = list(unique(api_per_category_transitions[category]))              
#     api_per_category_transitions_matrix = transition_matrix(api_per_category_transitions[category], api_per_category_alphabet)
#     category = category.replace('/', '_') # Needed to dele slashes from category names like '.. I/O ...'
#     filename = f"{API_PER_CATEGORY_PATH}/{process_name}_{process_id}_{category}_API_per_Category_Transition_Matrix"
#     api_per_category_transitions_matrix.to_csv(f"{filename}.csv")
#     render_matrix(api_per_category_transitions_matrix, alphabet, filename, PRINT_EDGE_LABELS)


def generate_transition_matrices_and_graphs(json_report: str, output_dir: str, graphs_to_generate: str) -> str | int:
    """

    Returns: 
        The directory where files were created
    """
    logger.info(f"[+] Processing {os.path.basename(json_report)} [+]")
    try:
        with open(json_report) as f:
            data = json.load(f)
    except Exception as e:
        logger.error(f"[!] ERROR. Cannot parse {json_report}: {e}. Skipping")
        return -1

    REPORTS_PATH = f"./{output_dir}/{os.path.basename(json_report)[:os.path.basename(json_report).index('.')]}" # strip extension
    BEHAVIOR_GRAPH_PATH = REPORTS_PATH+"/BEHAVIOR_GRAPH"
    CATEGORY_GRAPH_PATH = REPORTS_PATH+"/CATEGORY_GRAPH"       

    Path(BEHAVIOR_GRAPH_PATH).mkdir(exist_ok=True, parents=True)
    Path(CATEGORY_GRAPH_PATH).mkdir(exist_ok=True)      
    
    # All categories: https://github.com/kevoreilly/CAPEv2/blob/8df267f658ac0ea6c8879e720815a6a432456ee6/web/templates/analysis/behavior/_search_results.html#L10
    # CAPEv2 web colors: https://github.com/kevoreilly/CAPEv2/blob/5d5ba06d8788ac561b267b20eec49e437decdf88/web/static/css/style.css#L166

    #************ CATEGORY REFACTORING (IF winapi_categories.json IS AVAILABLE) *****************
    if JSON_DATA: ## If dict evaluates to True it has been populated, otherwise False
        for process  in data['behavior']['processes']:
            process['refactored_calls'] = [] # <- New list of refactored calls. We replicate the 
            # original ['calls'] list but adding the ['new_category'] entry because modifying
            # the original ['calls'] entries seems impossible given that each entry is an instance
            # of ParseProcessLog, not just dict or list entries. In other words, the call variable
            # from the following loop can be modified with call['new_category']... but the changes
            # do not persist out of the loop.
            for call in process['calls']:
                api_call = call['api']
                if api_call == "sysenter": # Ad-hoc sysenter skip
                    continue 
                # If the API call is not in its generic form (i.e., it ends with either 'A' or 'W')
                # we transform it. From a behavioral perspective, it is irrelevant whether the
                # arguments are passed in ANSI or Unicode (wide) form
                if api_call.endswith('A') or api_call.endswith('W'):
                    api_call = api_call[:-1]
                    call['api'] = api_call
                # Some Windows API calls end with a 'A' or 'W' and their winapi_categories.json 
                # representation does not contain that last character. We explicitly check for it
                # by removing the last char of every api_call. Others end with 'Ex'
                new_category = ""
                if api_call in JSON_DATA: 
                    # We create a new field just to maintain the old call['category']
                    # field so web interface is able to parse the information
                    # If the new category (from JSON_DATA) already equals to the category,
                    # then just maintain the old category, otherwise assign the new one.
                    new_category = JSON_DATA[api_call]['category']
                elif api_call.lower() in JSON_DATA:
                    # Case added to conver inconsistencies in WINAPI naming. Some functions'
                    # generic form is lowercase (for some unknown reason). For example:
                    # GetAddrInfoW becomes GetAddrInfo when supressed the W. However, its
                    # generic form is getaddrinfo (lowercase). More info:
                    # https://learn.microsoft.com/en-us/windows/win32/api/ws2tcpip/nf-ws2tcpip-getaddrinfo#remarks
                    new_category = JSON_DATA[api_call.lower()]['category']
                elif api_call[:-1] in JSON_DATA:
                    new_category = JSON_DATA[api_call[:-1]]['category']
                # Considering all API calls with the Ex suffix (like NtAllocateVirtualMemoryEx or NtAddAtomEx, but not CreateMutex)
                elif api_call.endswith('Ex') and api_call[:-2] in JSON_DATA:
                    new_category = JSON_DATA[api_call[:-2]]['category']
                else:
                    new_category = "unknown"
                    logger.warning(f"[!!!] WARNING: New category (refactored) of API {call['api']} found in process {process['process_name']} is unknown.\n Old CAPE category is: {call['category']}\nPlease consider updating or modifying winapi_categories.json [!!!]")
                call['new_category'] = new_category
                process['refactored_calls'].append(call)
        
    #************ FOR PROCESS IN DATA['BEHAVIOR']['PROCESS'] *******************
    for process in data['behavior']['processes']:
        pid = process['process_id']
        # Skip this particular process if its 'calls' key is empty. That is, the process
        # is tracked by cape but its behavior (API calls) is missing for some unknown reason
        if not len(process['calls']):
            logger.warning(f"[!] ERROR. Skipping process {pid} from analysis because no behavior activity was tracked [!]")
            continue

        # api_call_transitions contains every single API call
        api_call_transitions = [] 

        # api_per_category_transitions contains every API call (in order) for every category
        api_per_category_transitions = {}

        # Alphabet contains the possible states or API calls (unique values) 
        # with their corresponding category
        alphabet = {}

        for call in process['refactored_calls']:
            cypher_query = ""
            api_call = call['api']
            api_category = call['new_category'] # After refactoring.
            api_cape_category= call['category']

            # Rendering of the graph is done outside the loop
            # **************************************************************

            # Tracking every single transition
            api_call_transitions.append(api_call)

            # Tracking every API call per category. 
            # Given that we want to track also the interaction with "other"
            # categories, we track the API in its category, and "others" for
            # the rest of categories
            if api_category not in api_per_category_transitions:
                api_per_category_transitions[api_category] = [api_call]
            else:
                for category in api_per_category_transitions:
                    if category == api_category:
                        api_per_category_transitions[api_category].append(api_call)
                    else:
                        api_per_category_transitions[category].append("others") # With 'others' node

            # Creating the alphabet
            if api_call not in alphabet:
                alphabet[api_call] = api_category 

        # Render the resource graph for the particular PID
        process_name = process['process_name']
        process_id = process['process_id']


        actions = {
            'category': lambda: generate_api_call_transitions(api_call_transitions, alphabet, process_name, process_id, BEHAVIOR_GRAPH_PATH, PRINT_EDGE_LABELS),
            'behavior': lambda: generate_api_per_category_transitions(api_per_category_transitions, alphabet, process_name, process_id, CATEGORY_GRAPH_PATH, PRINT_EDGE_LABELS),
        }

        actions.get(graphs_to_generate, lambda: (
            generate_api_call_transitions(api_call_transitions, alphabet, process_name, process_id, BEHAVIOR_GRAPH_PATH, PRINT_EDGE_LABELS), 
            generate_api_per_category_transitions(api_per_category_transitions, alphabet, process_name, process_id, CATEGORY_GRAPH_PATH, PRINT_EDGE_LABELS)
            ))()

    #*********** END FOR PROCESS IN DATA['BEHAVIOR']['PROCESS'] ****************        
    return json_report    

def main(json_dir: str, output_dir: str, graphs_to_generate: str, winapi_categories: str, no_download: bool, print_transition_probabilities: bool) -> None:

    load_categories(winapi_categories, no_download)

    global PRINT_EDGE_LABELS
    PRINT_EDGE_LABELS = True if print_transition_probabilities else False


    processed_paths = []
    if os.path.isdir(json_dir):
        logger.info("[*] Report directory - attempting to parse all .json files.")
        reports = glob.glob(arguments.json_dir + "/*.json")
        for report in reports:
            logger.info(f"[*] Parsing {report}.")
            if generate_transition_matrices_and_graphs(report, output_dir, graphs_to_generate) != -1:
                processed_paths.append(report)
    else:
        logger.info(f"[*] Parsing {json_dir}.")
        if generate_transition_matrices_and_graphs(json_dir, output_dir, graphs_to_generate) != -1:
            processed_paths.append(json_dir)
    return processed_paths

if __name__ == '__main__':
    arguments = parse_arguments()
    logging.basicConfig(level=logging.INFO, format="%(name)s (%(asctime)s) %(levelname)s - %(message)s")
    logger = logging.getLogger("MalGraphIQ (Transition Matrices and Graphs)")
    if arguments.quiet:
        logger.setLevel(logging.ERROR)
    elif arguments.silent:
        # Turn off the logger
        logger.setLevel(logging.CRITICAL + 1)

    graphs_to_generate = None
    if arguments.category:
        graphs_to_generate = 'category'
    elif arguments.behavior:
        graphs_to_generate = 'behavior'

    main(arguments.json_dir, arguments.output, graphs_to_generate, arguments.winapi_categories, arguments.no_download, arguments.print_transition_probabilities)