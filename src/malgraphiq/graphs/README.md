# MalGraphIQ graphs phase

- **Input**: Set of execution traces or reports generated with [CAPE](https://github.com/kevoreilly/CAPEv2) or [MALVADA](https://github.com/reverseame/MALVADA) (e.g., the [WinMET](https://doi.org/10.5281/zenodo.12647555) dataset).
- **Output**: Behavior and category call graphs, along with transition matrices and graphviz files.
- **By default both Behavior and Category graphs are generated (when neither `-c` nor `-b` are specified).**
- **By default the script attempts to download the `winapi_categories.json` file if not present in the current working directory or the specified path (`-w`).**

```
$ python3 malgraphiq.py graphs -h
usage: MalGraphIQ graphs [-h] [-o OUTPUT] [-w WINAPI_CATEGORIES] [-nd] [-pp] [-c | -b] json_dir

positional arguments:
  json_dir              A .json report o a directory containing one or more JSON reports. If the parameter is a directory, the program
                        automatically parses all .JSON files within it.

options:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        Output folder of transition matrices and call graphs (default: ./MATRICES_GRAPHS/).
  -w WINAPI_CATEGORIES, --winapi_categories WINAPI_CATEGORIES
                        Path to winapi_categories.json file (as obtained from https://github.com/reverseame/winapi-categories). By default the
                        program will look into the current working directory. If the file does not exist, the program will attempt to download
                        it unless -nd/--no-download is specified. (default: ./winapi_categories.json).
  -nd, --no_download    Prevents MalGraphIQ from downloading winapi_categories.json. By default it attempts to download it in the -w/--winapi-
                        categories specified path.
  -pp, --print_transition_probabilities
                        Print transition probabilities on behavior and category graphs (default: False).
  -c, --category        Generate only the category graph(s).
  -b, --behavior        Generate only the behavior graph(s).
```

*Commands executed assuming current working directory in this folder.*
## Generate graphs for a directory containing several reports with default values and output directory
```
$ python3 ../malgraphiq.py graphs ../../test_reports
```
Which generates the `MATRICES_GRAPHS` folder that contains a folder for every report present in `test_reports`. Namely, `26409`, `57405` and `6745`. Each of these subfolders in turn contains two folders: `BEHAVIOR_GRAPH` and `CATEGORY_GRAPHS`, corresponding to the behavior and category graphs, respectively. These two folders contain three types of files: (1) `csv` files for transition matrices; (2) `gv` files for graphviz files representing the graphs; and (3) `pdf` files for PDF visualizations of the gv files.

*This structure is repeated for all the subsequent examples.*

## Generate only category graphs for a directory containing several reports with specific output and categories path
```
$ python3 ../malgraphiq.py graphs ../../test_reports -o VISUALIZATIONS -w ~/Desktop/winapi_categories.json -c
```