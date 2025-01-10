# MalGraphIQ graphs phase

- **By default both Behavior and Category graphs are generated.**
- **By default the script attempts to download the `winapi_categories.json` file if not present in the current working directory or the specified path.**

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