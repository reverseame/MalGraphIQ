# MalGraphIQ

When executing the `all` phase from MalGraphIQ, the specified reports are processed in the following order: Transition Matrices and Graphs -> Behavioral Patterns -> Plotting.


*Commands executed assuming current working directory in this folder.*

## Process `test_reports` directory with default values
*This command assumes the [WBC](https://github.com/reverseame/windows-behavior-catalog) repository at ~/Desktop.*
```
$ python3 malgraphiq.py all ../test_reports -c ~/Desktop/windows-behavior-catalog/catalog.json
```

This command will produce the following output:
- MATRICES_GRAPHS folder, containing the `csv`, `gv` and `pdf` files corresponding to transitoin matrices and behavior and category graphs. (Graphs phase).
- A .json file containing the behavior occurrences of the WBC against the specified category graphs. (Occurrences phase)
- PLOTS folder, containing the Micro-Objective and Micro-Behavior plots, depicting the behaviors identified. (Plotting phase)