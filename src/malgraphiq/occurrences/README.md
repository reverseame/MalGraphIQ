# MalGraphIQ occurrences phase

- **Input**: Set of graphviz `gv` files representing behavior or category call graphs.
- **Output**: Number of occurrences of each WBC pattern against the graphs.

```
$ python3 ../malgraphiq.py occurrences -h
usage: MalGraphIQ occurrences [-h] -c CATALOG [-m MAX_INTER_NODES] [-p PROB_THRESHOLD] [-l PATTERN_MIN_LENGTH] [-jf JSON_OUTPUT_FILE]
                              behavior_graph

positional arguments:
  behavior_graph        A behavior .gv file directory or list of directories containing .gv files in which patterns will be sought. The
                        program automatically parses all the .gv files contained in each directory.

options:
  -h, --help            show this help message and exit
  -c CATALOG, --catalog CATALOG
                        Path to the Windows Behavior Catalog (WBC) in JSON format. See https://github.com/reverseame/windows-behavior-catalog.
  -m MAX_INTER_NODES, --max_inter_nodes MAX_INTER_NODES
                        Max intermediate nodes from the behavior graph allowed between each pattern node (default: 0).
  -p PROB_THRESHOLD, --prob_threshold PROB_THRESHOLD
                        Probability threshold (default: 0.0). Paths below the threshold are discarded.
  -l PATTERN_MIN_LENGTH, --pattern_min_length PATTERN_MIN_LENGTH
                        Minimum pattern length, measured in number of nodes (default: 1).
  -jf JSON_OUTPUT_FILE, --json_output_file JSON_OUTPUT_FILE
                        Custom output JSON file for results (default: pattern_results_{asctime}.json).
```

*Commands executed assuming current working directory in this folder.*
## Occurrences of a directory with default parameters and default output file
```
$ python3 ../malgraphiq.py occurrences -c catalog.json ../graphs/REPORTS/6745/CATEGORY_GRAPH
```
Which generates an output file like: `pattern_results_{asctime}.json`.

## Occurrences of a single .gv file with default parameters and default output file
```
$ python3 ../malgraphiq.py occurrences -c catalog.json ../graphs/REPORTS/6745/CATEGORY_GRAPH/CreateSnapshot_Iterate.exe_4040_Files\ and\ I_O\ \(Local\ file\ system\)_API_per_Category_Transition_Matrix.gv
```

Which generates an output file like: `pattern_results_{asctime}.json`.

## Occurrences of a directory with custom matching and output parameters
```
$ python3 ../malgraphiq.py occurrences -c ~/Desktop/behaviors/catalog.json ../graphs/REPORTS/6745/CATEGORY_GRAPH -m 1 -p 0.2 -l 3 -jf catalog_matches
```

Which generates the file `catalog_matches.json`.