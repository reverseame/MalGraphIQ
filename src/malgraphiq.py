import json
import pandas as pd
import numpy as np
from graphviz import Digraph
import matplotlib.pyplot as plt
from pathlib import Path

from malgraphiq_utils.common import categories_and_colors as colors

import re
import sys
import os

#from lib.cuckoo.common.abstracts import Processing
#from lib.cuckoo.common.config import Config

JSON_DATA = {}
CAPE_PATH = "/opt/CAPEv2/"
#WINAPI_CATEGORIES_JSON_PATH = f"{CAPE_PATH}/modules/processing/winapi_categories.json"
WINAPI_CATEGORIES_JSON_PATH = "./winapi_categories.json"
PRINT_EDGE_LABELS = True

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

#def render_matrix_with_categories(matrix, alphabet, graphname):
    #graph = Digraph(graphname, format='pdf', engine='dot')
#
    #start_of_graph = True
    #for i, row in enumerate(matrix.index):
        #for column in matrix.columns:
            #if matrix.loc[row][column] > 0: # Use .loc() to access DataFrame by row label
                ##breakpoint()
                # TODO ---> CHANGE THE NODE DRAWING TO MIMIC THE BEHAVIOR OF render_matrix()  
                #shape = 'ellipse' 
                #if start_of_graph:
                    #shape = 'octagon'
                    #start_of_graph = False
                #graph.node(row, label=f"{row}\n<<{alphabet[row]}>>", style='filled', fillcolor=colors[alphabet[row]] if row != 'others' else colors['others'], shape=shape)
                #graph.node(column, label=f"{column}\n<<{alphabet[column]}>>", style='filled', fillcolor=colors[alphabet[column]] if column != 'others' else colors['others'])
                #graph.edge(row, column, label=str(np.around(matrix.loc[row][column],4)))
                ##if start_of_graph:
                    ##start_of_graph = False
                    ###graph.node('Start', label='Start', style='filled', fillcolor='black', fontcolor='white')
                    ##graph.node('Start', label='', style='filled', fillcolor='black', fontcolor='white', shape='circle')
                    ##graph.edge('Start', row)
    #graph.render()

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

def load_categories():
    if not os.path.exists(WINAPI_CATEGORIES_JSON_PATH):
        print("[!] winapi_categories.json file not found. Category refactoring can't be done. You can download it from https://github.com/reverseame/winapi-categories [!]\n", end="")
        print("[!] You could, for example, run the following command: [!]\n\t $ wget https://raw.githubusercontent.com/reverseame/winapi-categories/refs/heads/main/winapi_categories.json")
        return -1
    else:
        global JSON_DATA
        with open(WINAPI_CATEGORIES_JSON_PATH) as file:
            JSON_DATA = json.load(file)

#class Markov(Processing)
class Markov():
    def run(self):
        #PATH_FOLDER = Config("processing").markov.path ## Obtained from CAPEv2 (Cuckoo) variable environment (.conf file)
        #ANALYSIS_ID = str(self.results['info']['id']) ## Obtained from CAPEv2's self.results['info']['id']

        # Paths to write results
        # API_PATH = PATH_FOLDER + ANALYSIS_ID + "/API"
        # API_CATEGORY_PATH = PATH_FOLDER + ANALYSIS_ID + "/API_CATEGORY"
        # API_PER_CATEGORY_PATH = PATH_FOLDER + ANALYSIS_ID + "/API_PER_CATEGORY"
        # API_PATH_IAT = PATH_FOLDER + ANALYSIS_ID + "/API_IAT"
        # API_PER_CATEGORY_PATH_IAT = PATH_FOLDER + ANALYSIS_ID + "/API_PER_CATEGORY_IAT"        

        print(f"[+++++++++++++++++++++++] Processing {os.path.basename(sys.argv[1])}")
        try:
            with open(sys.argv[1]) as f:
                data = json.load(f)
        except Exception as e:
            print(f"[!] ERROR. Cannot parse {sys.argv[1]}: {e}. Skipping", file=sys.stderr)

        REPORTS_PATH = f"./REPORTS/{os.path.basename(sys.argv[1])}"
        API_PATH = REPORTS_PATH+"/API"
        API_PATH_IAT = REPORTS_PATH+"/API_IAT"
        API_CATEGORY_PATH = REPORTS_PATH+"/API_CATEGORY"
        API_PER_CATEGORY_PATH = REPORTS_PATH+"/API_PER_CATEGORY"
        API_PER_CATEGORY_PATH_IAT = REPORTS_PATH+"/API_PER_CATEGORY_IAT"        

        Path(API_PATH).mkdir(exist_ok=True, parents=True)
        Path(API_PATH_IAT).mkdir(exist_ok=True, parents=True)
        Path(API_CATEGORY_PATH).mkdir(exist_ok=True)
        Path(API_PER_CATEGORY_PATH).mkdir(exist_ok=True)
        Path(API_PER_CATEGORY_PATH_IAT).mkdir(exist_ok=True)        
        
        # All categories: https://github.com/kevoreilly/CAPEv2/blob/8df267f658ac0ea6c8879e720815a6a432456ee6/web/templates/analysis/behavior/_search_results.html#L10
        # CAPEv2 web colors: https://github.com/kevoreilly/CAPEv2/blob/5d5ba06d8788ac561b267b20eec49e437decdf88/web/static/css/style.css#L166

        #data = self.results

        #with open("../data_example/from_CAPEv2/28_report.json") as f:
        #with open(sys.argv[1]) as f:
        #    data = json.load(f)

        # Variable containing all the IAT declared function. Dictionary in the form:
        # {'function_name' : 'library'}
        # This is used only as a container for ALL the declared functions in the
        # IAT. Its purpose is solely filtering the API calls/transitions.
        iat_alphabet = {}

        # Reading the IAT for each process individually
        if not 'pe' in data['target']['file']:
            print(f"[!] ERROR. File is not in PE format [!]. (No IAT will be retrieved. Continuing analysis")
        elif not 'imports' in data['target']['file']['pe']:
            print(f"[!] ERROR. No imports in report {sys.argv[1]}??? [!]")
        else:
            for process in data['behavior']['processes']:
                pid = process['process_id']
                iat_alphabet[pid] = {}

                imports = data['target']['file']['pe']['imports']
                for library_name in imports:
                    full_library_name = imports[library_name]['dll']
                    for import_ in imports[library_name]['imports']:
                        iat_alphabet[pid][import_['name']] = full_library_name

        #************ CATEGORY REFACTORING (IF winapi_categories.json IS AVAILABLE) *****************
        if load_categories() != -1:
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
                        #print(f"[+++] Found {api_call}. Converting to generic version {api_call[:-1]}")
                        api_call = api_call[:-1]
                        call['api'] = api_call
                    #print(f"API_CALL {api_call}")
                    #if call['category'] == "crypto":
                    #    print(f"[+][+][+][+][+][+][+] CRYPTO API DETECTED: {api_call}")
                    #print(f"SELF_RESULTS {self.results['behavior']['processes'][process_num]['calls'].lastcall['api']}")
                    # Some Windows API calls end with a 'A' or 'W' and their winapi_categories.json 
                    # representation does not contain that last character. We explicitly check for it
                    # by removing the last char of every api_call. Others end with 'Ex'
                    #api_call = api_call.replace('_','') # DNS related calls
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
                        #new_category = call['category']
                        new_category = "unknown"
                        print(f"[!!!] WARNING: New category (refactored) of API {call['api']} found in process {process['process_name']} is unknown.\n Old CAPE category is: {call['category']}\nPlease consider updating or modifying winapi_categories.json [!!!]")
                    call['new_category'] = new_category
                    process['refactored_calls'].append(call)
                    #https://github.com/kevoreilly/CAPEv2/blob/7c392ffb963e519b9c9ee2b5045a829ec17fb28c/modules/processing/behavior.py#L60
                    #self.results['behavior']['processes'][process_num]['calls'].lastcall.update(call)

        #api_filter = API_Filter()
        # Open DB connection
        # NEO4J = False
        # URI = "bolt://localhost:7687"
        # USERNAME = "cape"
        # PASSWORD = "cape"
        # DATABASE_NAME = "cape"
        # analysis_id = data['info']['id'] 
        # db_conn = Neo4jDriver(URI, USERNAME, PASSWORD, DATABASE_NAME)
        # if NEO4J:
        #     # Delete the DB before storing new data
        #     db_conn.wipe_db() # ATTENTION!
        #     cypher_query=f'''
        #     CREATE (a:ANALYSIS_{analysis_id} {{identifier:'Analysis {analysis_id}'}})
        #     '''
        #     # Query creating the new analysis node
        #     db_conn.send_query(cypher_query)
            

        #************ FOR PROCESS IN DATA['BEHAVIOR']['PROCESS'] *******************
        for process in data['behavior']['processes']:
        #for process in self.results['behavior']['processes']:
            pid = process['process_id']
            # Skip this particular process if its 'calls' key is empty. That is, the process
            # is tracked by cape but its behavior (API calls) is missing for some unknown reason
            if not len(process['calls']):
                print(f"[!] ERROR. Skipping process {pid} from analysis because no behavior activity was tracked [!]")
                continue

            # api_call_transitions contains every single API call
            api_call_transitions = [] 

            # api_call_in_iat_transitions contains every API call made to functions
            # declared in the IAT
            api_call_in_iat_transitions = []

            # api_category_transitions contains the category sucession/transitions
            api_category_transitions = []

            # api_per_category_transitions contains every API call (in order) for every category
            api_per_category_transitions = {}

            # api_in_iat_per_category_transitions ontains every API call (in order)
            # made to functions declared in the IAT, for every category
            api_in_iat_per_category_transitions = {}

            # Alphabet contains the possible states or API calls (unique values) 
            # with their corresponding category
            alphabet = {}
            old_cape_alphabet = {}

            # Alphabet that contains only used API calls from the IAT. This is used
            # to create the transition matrix since we only care about the functions
            # from the IAT that are actually used/called at least once
            used_iat_alphabet = {}

            category_alphabet = {}

            used_iat_category_alphabet = {}

            # Resources access tracking, for each PID
            # syncrhonization includes mutexes
            resources_categories = ['filesystem', 'registry', 'network', 'synchronization', 'threading', 'process'] # Classic CAPE categories
            #resources_categories.append(['Directory Management', 'Files and I/O (Local file system)', 'Disk Management', 'Volume Management', 'Windows Shell', 'Registry', 'Windows Internet (WinINet)', 'CNG Cryptographic Primitive', 'Network Management', 'Domain Name System (DNS)', 'Windows Sockets (Winsock)', 'Windows Networking (WNet)', 'Synchronization', 'Structured Exception Handling', 'Process']) # New refactoring categories 

            # Variable indicating a new process is being iterated
            start_of_resource_tracking = True

            # Variable used to track thread_id(s)
            spotted_thread_ids = {}

            for call in process['refactored_calls']:
                cypher_query = ""
                api_call = call['api']
                api_category = call['new_category'] # After refactoring.
                api_cape_category= call['category']

                # ********************* RESOURCES ACCESSES *********************
                # if NEO4J:
                #     if api_cape_category in resources_categories:
                #         if start_of_resource_tracking:
                #             # PID node
                #             # Cypher: merge is used because it will create the node only if it doesn't exist already
                #             process_name = process['process_name']
                #             process_path = process['module_path']
                #             cypher_query+=f'''
                #             MATCH (a:ANALYSIS_{analysis_id})
                #             MERGE (a)-[:HAS_PROCESS]->(p:Process_{pid}{{
                #                                             identifier:'Process {pid}',
                #                                             process_name:'{process_name}',
                #                                             process_path: '{process_path}'
                #                                             }})                        
                #             '''
                #             db_conn.send_query(cypher_query)
                #             cypher_query=""
                #             start_of_resource_tracking=False

                #         # Thread node + edge
                #         thread_id = call['thread_id']
                #         if thread_id not in spotted_thread_ids:                        
                #             cypher_query+=f'''
                #             MATCH (p:Process_{pid}{{identifier:'Process {pid}'}})
                #             MERGE (p)-[:HAS_THREAD]->(t:Thread_{thread_id}{{identifier:'Thread {thread_id}'}})                        
                #             '''

                #         # API call node + edge
                #         cypher_query+=f'''
                #         MERGE (t)-[:PERFORMS]->(CAT:{api_cape_category}{{identifier:'{api_cape_category}'}})
                #         MERGE (CAT)-[:CALLS]->(c:{api_call}{{identifier:'{api_call}'}})
                #         '''
                #         cypher_query += api_filter.neo4j_filtering(api_call, call['arguments'], api_cape_category) 
                #         # For each call belonging to resource-related categories, we run the resulting query
                #         if cypher_query != "":
                #             db_conn.send_query(cypher_query)
                # **************************************************************        

                #***************** TRACKING APIs PRESENT IN IAT ****************
                # Detecting the API calls present in the IAT. Bear in mind some
                # Windows API calls end with a 'A' or 'W' and their IAT declaration
                # does not contain that last character. We explicitly check for it
                # by removing the last char of every api_call.
                if pid in iat_alphabet:
                    if api_call in iat_alphabet[pid] or api_call[:-1] in iat_alphabet[pid]:
                        api_call_in_iat_transitions.append(api_call)

                        # Tracking every API call from IAT per category
                        # Given that we want to track also the interaction with "other"
                        # categories, we track the API in its category, and "others" for
                        # the rest of categories
                        if api_category not in api_in_iat_per_category_transitions:
                            api_in_iat_per_category_transitions[api_category] = [api_call]
                        else:
                            for category in api_in_iat_per_category_transitions:
                                if category == api_category:
                                    api_in_iat_per_category_transitions[api_category].append(api_call)
                                else:
                                    api_in_iat_per_category_transitions[category].append("others")


                        if api_call not in used_iat_alphabet:
                            used_iat_alphabet[api_call] = api_category

                        if api_category not in used_iat_category_alphabet:
                            used_iat_category_alphabet[api_category] = api_category

                # Rendering of the graph is done outside the loop
                # **************************************************************

                # Tracking every single transition
                api_call_transitions.append(api_call)

                # Tracking every category transition
                api_category_transitions.append(api_category)

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
                            #api_per_category_transitions[category].append(api_category) # Unrolling 'others' node

                # Creating the alphabet
                if api_call not in alphabet:
                    alphabet[api_call] = api_category 

                if api_call not in old_cape_alphabet:
                    old_cape_alphabet[api_call] = api_cape_category 

                if api_category not in category_alphabet:
                    category_alphabet[api_category] = api_category

            # Render the resource graph for the particular PID
            #sys.exit()
            
            process_name = process['process_name']
            process_id = process['process_id']

            ############################
            ### API CALL TRANSITIONS ###
            ############################
            #api_call_transitions_matrix = transition_matrix(api_call_transitions, list(alphabet))
            #filename = f"{API_PATH}/{process_name}_{process_id}_API_Calls_Transition_Matrix"
            #api_call_transitions_matrix.to_csv(f"{filename}.csv")
            #render_matrix(api_call_transitions_matrix, alphabet, filename, PRINT_EDGE_LABELS)
            #render_matrix_with_categories(api_call_transitions_matrix, alphabet, filename)
            #filename = f"{API_PATH}/{process_name}_{process_id}_old_cape_API_Calls_Transition_Matrix"
            #render_matrix_with_categories(api_call_transitions_matrix, old_cape_alphabet, filename)
            ########################################################################

            
            ################################################
            ### RENDER API CALLS ONLY PRESENT IN THE IAT ###
            ################################################
            ##pprint(used_iat_alphabet, sort_dicts=False)
            #if not api_call_in_iat_transitions:
                #print(f"[!] API CALLS IN IAT EMPTY. Probably no imports for process {process_name} with PID {process_id}?. SKIPPING [!]")
            #else:
                #api_call_in_iat_transitions_matrix = transition_matrix(api_call_in_iat_transitions, list(used_iat_alphabet))
                #filename = f"{API_PATH_IAT}/{process_name}_{process_id}_API_Calls_in_IAT_Transition_Matrix"
                #api_call_in_iat_transitions_matrix.to_csv(f"{filename}.csv")
                #render_matrix(api_call_in_iat_transitions_matrix, alphabet, filename)
            ########################################################################
            """@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
            ################################
            ### API CATEGORY TRANSITIONS ###
            ################################
            api_category_transitions_matrix = transition_matrix(api_category_transitions, list(category_alphabet))
            filename = f"{API_CATEGORY_PATH}/{process_name}_{process_id}_API_Category_Transition_Matrix"
            api_category_transitions_matrix.to_csv(f"{filename}.csv")
            render_matrix(api_category_transitions_matrix, category_alphabet, filename)
            ########################################################################
            """
            ####################################
            ### API PER CATEGORY TRANSITIONS ###
            ####################################
            for category in api_per_category_transitions:
                #if len(api_per_category_transitions[category]) == 1:
                    #pprint(f"[!] SKIPPING CATEGORY {category}. IT CONTAINS A SINGLE OBJECT: {api_per_category_transitions[category]}")
                    #continue         
                # set() is used to uniqify the list -> The problem with set is that 
                # it reorders elements, we need to know the exact order of the calls
                # Solution: https://stackoverflow.com/a/58666031
                api_per_category_alphabet = list(unique(api_per_category_transitions[category]))              
                api_per_category_transitions_matrix = transition_matrix(api_per_category_transitions[category], api_per_category_alphabet)
                category = category.replace('/', '_') # Needed to dele slashes from category names like '.. I/O ...'
                filename = f"{API_PER_CATEGORY_PATH}/{process_name}_{process_id}_{category}_API_per_Category_Transition_Matrix"
                api_per_category_transitions_matrix.to_csv(f"{filename}.csv")
                render_matrix(api_per_category_transitions_matrix, alphabet, filename, PRINT_EDGE_LABELS)
            ########################################################################

            
            #############################################################
            ### RENDER API CALLS ONLY PRESENT IN THE IAT PER CATEGORY ###
            ############################################################# 
            # for category in api_in_iat_per_category_transitions:
            #     #if len(api_in_iat_per_category_transitions[category]) == 1:
            #         #pprint(f"[!] SKIPPING CATEGORY {category}. IT CONTAINS A SINGLE OBJECT: {api_in_iat_per_category_transitions[category]}")
            #         #continue
            #     api_in_iat_per_category_alphabet = list(unique(api_in_iat_per_category_transitions[category]))

            #     api_in_iat_per_category_transitions_matrix = transition_matrix(api_in_iat_per_category_transitions[category], api_in_iat_per_category_alphabet)
            #     category = category.replace('/', '_') # Needed to dele slashes from category names like '.. I/O ...'
            #     filename = f"{API_PER_CATEGORY_PATH_IAT}/{process_name}_{process_id}_{category}_API_in_IAT_per_Category_Transition_Matrix"
            #     api_in_iat_per_category_transitions_matrix.to_csv(f"{filename}.csv")
            #     render_matrix(api_in_iat_per_category_transitions_matrix, alphabet, filename)
            ########################################################################
            #matrix.to_excel('markov.xlsx', sheet_name='X_Process_Transition_Matrix')
        #*********** END FOR PROCESS IN DATA['BEHAVIOR']['PROCESS'] ****************        
        #self.key = "key"
        #return "Markov processing done"
        """@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@"""
        

if __name__ == '__main__':
    markov = Markov()
    markov.run()