# MalGraphIQ
Transform your malware sandbox reports and execution traces into behavior and category graphs.

# Contents
The MalGraphIQ repository contains the following elements:
- [src](./src): Source code.
- [doc](./doc): Source code documentation.
- [test_reports](./test_reports): Test reports and data to try MalGraphIQ. 
- [requirements.txt](./requirements.txt): Requirements for the tool to run. Install with `pip3 install -r requirements.txt`.

# Requirements
Besides installing the modules listed in [requirements.txt](./requirements.txt), MalGraphIQ also relies on the following resources:
- [Windows Behavior Catalog (WBC)](https://github.com/reverseame/windows-behavior-catalog). Specifically, the catalog.json files that defines the patterns MalGraphIQ will seek to match. You can either clone the whole repo or just download the .json file. In either case, you must specify the .json file's path when running MalGraphIQ with the `-c/--catalog` option.
- [winapi_categories](https://github.com/reverseame/winapi-categories). A .json file containing our categorization of Windows API and syscalls. MalGraphIQ will attempt to download it if not present in the specified path, unless `-nd, --no_download` is specified. It can be downloaded manually downloaded with a command like:  
```
$ wget https://raw.githubusercontent.com/reverseame/winapi-categories/refs/heads/main/winapi_categories.json
```

# How To Use
## Documentation and help
MalGraphIQ and all its phases are documented and can be read about via the `-h/--help` flag. For example:
```
$ python3 src/malgraphiq/malgraphiq.py -h
usage: MalGraphIQ [-h] [-q | -s] {graphs,occurrences,plots,all} ...

Executes MalGraphIQ either in individual phases or the whole workflow: Transition Matrices and Graphs -> Behavioral Patterns -> Plotting.

positional arguments:
  {graphs,occurrences,plots,all}
                        Specify the phase to run.
    graphs              Transition Matrices and Graphs phase. Renders CAPE reports and transforms them into transition matrices and different
                        graphs (visualizations). By default generates both behavior and category transition matrices and graphs.
    occurrences         Behavior Pattern Occurrences phase. Generates the occurrences of each pattern from the Windows Behavior Catalog (WBC)
                        against the specified graph/s. WBC patterns are identified in the specified graph/s using a backtracking algorithm.
    plots               Plot Catalog Matches phase. Plots the Micro-Objective and Micro-Behavior occurrences from the previous phase. You can
                        find code for other type of visualizations in additional_code.py.
    all                 Run all phases sequentially.

options:
  -h, --help            show this help message and exit
  -q, --quiet           Only error and critical messages are printed.
  -s, --silent          Nothing is printed.

```

## Usage example
MalGraphIQ comprises three main phases: (1) [graphs](./src/malgraphiq/graphs), (2) [occurrences](./src/malgraphiq/occurrences), and (3) [plots](./src/malgraphiq/plotting). 

1. Graphs phase generates transition matrices and category and behavior graphs.
2. Occurrences phase matches the patterns defined in the WBC against specified category graphs, counting their occurrences.
3. Plots phase plots the occurrences into radarcharts and barcharts visualizations, depicting the identified behavior(s).

Using the main script file `malgraphiq.py` you can invoke the whole workflow (each phase pipelined in sequence) or each phase individually. Each phase has a corresponding README.md file in their respective directory where you can see execution examples.

You can use MalGraphIQ with almost all parameters with their default value. A basic execution is similar to runnig the following command: *(notice `all` phase is invoked, running the entire workflow)*
```
$ python3 src/malgraphiq/malgraphiq.py all test_reports -c ~/Desktop/windows-behavior-catalog/catalog.json
```

Or you can run the `all` phase with custom parameters:
```
$ python3 src/malgraphiq/malgraphiq.py all -o custom_options/MATRICES_AND_GRAPHS -w ~/Desktop/winapi_categories.json -c ~/Desktop/windows-behavior-catalog/catalog.json -jf custom_options/occurences_results --fig_title "Custom Figures" -rc_max 30 --catalog_matches_plot_dir custom_options/MATCHES_PLOTS -bb --lower_figure_limit 15 --upper_figure_limit 55 test_reports
```

Given that each phase generates intermediary results/artifacts, any particular phase can be repeated. In the following example, the plots file is re-executed with different parameters, taking as input the file named `custom_options/occurences_results.json`, generated in the previous phase.
```
$ python3 src/malgraphiq/malgraphiq.py plots --fig_title "Custom Figures" -rc_max 30 --catalog_matches_plot_dir custom_options/MATCHES_PLOTS -bb --lower_figure_limit 15 --upper_figure_limit 35 custom_options/occurences_results.json --lower_figure_ratio 35
```

## Best use-case
MalGraphIQ has many potential applications, but we believe its most valuable use is when analyzing samples from the same malware family. This approach allows MalGraphIQ to clearly illustrate their behavior.For example,  imagine you’re analyzing 100 samples of WannaCry from the [WinMET](https://doi.org/10.5281/zenodo.12647555) dataset. With MalGraphIQ, you would generate graphs like the ones shown below:

# Source code docs
Docs are present in [doc](./doc) folder.  

Documentation generated with [pdoc3](https://github.com/pdoc3/pdoc).
```
$ PYTHONPATH=src/malgraphiq pdoc3 src/malgraphiq -o doc --html
```

# Caveats, Warnings and Important Notes
1. <details> <summary>**Behavior vs. Category Graphs**</summary>
	While **behavior** and **category** graphs are both generated, behavior graphs are intended for visualization only, whereas category graphs are used for actual behavior identification (matching against WBC). While you can modify this behavior, please note that doing so can significantly impact performance. The backtracking algorithm may become unmanageable when parsing the entire behavior graph.
</details>
2. <details> <summary> **Normalization of Occurrence Data**</summary>  
When plotting occurrences, the data undergoes a **normalization process**. Currently, this is performed on a per-micro-objective or per-micro-behavior basis. This means:
	- All samples are compared, and their values are normalized for each micro-objective or micro-behavior.
	- The sample with the highest occurrence is assigned the max value, and the lowest occurrence is assigned the min value.
	This approach can lead to unusual results when processing a single report with MalGraphIQ. Since the min and max values are identical for a single micro-objective or micro-behavior, the results will appear evenly distributed. Keep this in mind when interpreting single-report outputs. 

	You can modify this behavior by adjusting the `normalize(df: pd.DataFrame, min: int = 0, max: int = 1, transpose:bool = False)` function from [plot_catalog_matches.py](./src/malgraphiq/plotting/plot_catalog_matches.py). By enabling the transpose parameter, you can change the normalization process to work on a per-sample basis rather than across all samples.

	With this modification, the normalization will consider all micro-behaviors within a specific micro-objective for a single sample. In this case:

	The micro-behavior with the highest occurrence within a sample becomes the max value.
	The micro-behavior with the lowest occurrence becomes the min value (all within the same sample).
	This allows for a more localized normalization process, tailored to individual sample data.
</details>

# Authors

[Razvan Raducu](https://www.youtube.com/@RazviOverflow)  
[Ricardo J. Rodríguez](https://webdiis.unizar.es/~ricardo/)  
[Pedro Álvarez](https://i3a.unizar.es/es/investigadores/pedro-javier-alvarez-perez-aradros)