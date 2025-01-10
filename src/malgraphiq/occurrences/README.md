# MalGraphIQ occurrences phase
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