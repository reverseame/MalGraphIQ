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

#### Micro-Objectives
![Screenshot 2025-01-13 114117](https://github.com/user-attachments/assets/52f85b78-6814-4c3c-a9c6-7fe494afef8f)

#### Process Micro-Behavior
![Screenshot 2025-01-13 114019](https://github.com/user-attachments/assets/5e017871-78ab-47e2-8b0d-dec7cd5ad584)

# Source code docs
Docs are present in [doc](./doc) folder.  

Documentation generated with [pdoc3](https://github.com/pdoc3/pdoc).
```
$ PYTHONPATH=src/malgraphiq pdoc3 src/malgraphiq -o doc --html
```

# Caveats, Warnings and Important Notes
1. <details> <summary><b>Behavior vs. Category Graphs</b></summary>
	
	While **behavior** and **category** graphs are both generated, behavior graphs are intended for visualization only, whereas category graphs are used for actual behavior identification (matching against WBC). While you can modify this behavior, please note that doing so can significantly impact performance. The backtracking algorithm may become unmanageable when parsing the entire behavior graph.
</details>

2. <details> <summary><b>Normalization of Occurrence Data</b></summary>
	
	When plotting occurrences, the data undergoes a **normalization process**. Currently, this is performed on a per-micro-objective or per-micro-behavior basis, which we will refer to as *default* or *per-category* normalization. This means:
	- All samples are compared, and their values are normalized for each micro-objective or micro-behavior.
	- The sample with the highest occurrence is assigned the max value, and the lowest occurrence is assigned the min value.
	This approach can lead to unusual results when processing a single report with MalGraphIQ. Since the min and max values are identical for a single micro-objective or micro-behavior, the results will appear evenly distributed. Keep this in mind when interpreting single-report outputs. 

	You can modify this behavior by adjusting the `normalize(df: pd.DataFrame, min: int = 0, max: int = 1, transpose:bool = False)` function from [plot_catalog_matches.py](./src/malgraphiq/plotting/plot_catalog_matches.py). By enabling the transpose parameter, you can change the normalization process to work on a per-sample basis rather than across all samples.

	With this modification, the normalization will consider all micro-behaviors within a specific micro-objective for a single sample. In this case:

	The micro-behavior with the highest occurrence within a sample becomes the max value.
	The micro-behavior with the lowest occurrence becomes the min value (all within the same sample).
	This allows for a more localized normalization process, tailored to individual sample data.

	To understand the difference in normalization methods, consider the following examples.

	# Normalization Techniques (3 samples)
	## Original Dataframe
	| Sample | [OC0001] Filesystem | [OC0005] Cryptography | [OC0006] Communication | [OC0002] Memory | [OC0003] Process | [OC0008] Operating System |
	|--------|---------------------|-----------------------|-------------------------|-----------------|-----------------|--------------------------|
	| **1**  | 64.0                | 0.0                   | 0                       | 27.0            | 14              | 18.0                     |
	| **2**  | 2.0                 | 0.0                   | 0                       | 4.0             | 2               | 4.0                      |
	| **3**  | 195.5               | 2.5                   | 0                       | 145.5           | 29              | 120.5                    |

	---

	## Normalized Dataframe
	**Default Normalization**:
	| Sample | [OC0001] Filesystem | [OC0005] Cryptography | [OC0006] Communication | [OC0002] Memory | [OC0003] Process | [OC0008] Operating System |
	|--------|---------------------|-----------------------|-------------------------|-----------------|-----------------|--------------------------|
	| **1**  | 32.737              | 0.0                   | 0.0                     | 18.557          | 48.276          | 14.938                   |
	| **2**  | 1.023               | 0.0                   | 0.0                     | 2.749           | 6.897           | 3.320                    |
	| **3**  | 100.000             | 100.0                 | 0.0                     | 100.000         | 100.000         | 100.000                  |

	Here normalization is done "per-category" (per columns). That is, given each micro-objective, take the values across all samples. Notice Filesystem, for example. Sample 3 has a value of 195.5, which is the highest one. This will be considered 100% and the rest are scaled relative to it. Same applies for the rest of micro-objectives.

	**Per-Sample Normalization**:
	| Sample | [OC0001] Filesystem | [OC0005] Cryptography | [OC0006] Communication | [OC0002] Memory | [OC0003] Process | [OC0008] Operating System |
	|--------|---------------------|-----------------------|-------------------------|-----------------|-----------------|--------------------------|
	| **1**  | 100.0               | 0.000                 | 0.0                     | 42.188          | 21.875          | 28.125                   |
	| **2**  | 50.0                | 0.000                 | 0.0                     | 100.000         | 50.000          | 100.000                  |
	| **3**  | 100.0               | 1.279                 | 0.0                     | 74.425          | 14.834          | 61.637                   |

	Conversely, here normalization is done "per-sample" (per rows). For each sample, its highest value is 100% and the rest are normalized with respect to it. Take for example sample 2. Both Memory and Operating System have a value of 4.0. It will be considered 100% and the remaining micro-objectives of the same sample are normalized with respect to it.

	---

	## Mean Dataframe

	Once the data is normalized, we calculate the average (mean) for each category across all samples.

	| Micro-objective           | **Default Mean** | **Per-Sample Mean** |
	|---------------------------|--------------|------------------|
	| [OC0001] Filesystem       | 44.587       | 83.333          |
	| [OC0005] Cryptography     | 33.333       | 0.426           |
	| [OC0006] Communication    | 0.000        | 0.000           |
	| [OC0002] Memory           | 40.435       | 72.204          |
	| [OC0003] Process          | 51.724       | 28.903          |
	| [OC0008] Operating System | 39.419       | 63.254          |

	This difference happens because the two methods emphasize different comparisons. Default Normalization highlights differences between samples for the same category, while Per-Sample Normalization shows how important each category is within a single sample

	---

	## To Percent

	Finally, the mean values are converted into percentages to make them easier to interpret.

	| Micro-objective           | **Default %** | **Per-Sample %** |
	|---------------------------|-----------|---------------|
	| [OC0001] Filesystem       | 21.28     | 33.59         |
	| [OC0005] Cryptography     | 15.91     | 0.17          |
	| [OC0006] Communication    | 0.00      | 0.00          |
	| [OC0002] Memory           | 19.30     | 29.10         |
	| [OC0003] Process          | 24.69     | 11.65         |
	| [OC0008] Operating System | 18.82     | 25.49         |

	This shift shows how the two methods can produce very different results. Default Normalization gives Cryptography more weight because it had high relative values in its category. In Per-Sample Normalization, Cryptography loses weight because it’s not a dominant feature in any single sample.

	---

	This comparison highlights a cardinality problem: certain categories, like Filesystem, have far more patterns than others, like Cryptography. Each normalization method focuses on different aspects:

	- Default Normalization compares how samples perform within the same category.
	- Per-Sample Normalization shows the relative importance of categories within each sample.

	Both methods are useful, depending on what you are trying to understand. Each normalization serves its unique purpose and highlights different aspects of the data.

	![different_normalization_techniques](https://github.com/user-attachments/assets/9ab00ef5-fa5c-4193-b467-1421ac14278c)

	# More examples
	<details>
		<summary><b>1 sample</b></summary>

	## Original Dataframe
	| Sample | [OC0001] Filesystem | [OC0005] Cryptography | [OC0006] Communication | [OC0002] Memory | [OC0003] Process | [OC0008] Operating System |
	|--------|---------------------|-----------------------|-------------------------|-----------------|-----------------|--------------------------|
	| **1**  | 327                 | 5                     | 0                       | 264             | 44              | 223                      |

	---
		
	## Normalized Dataframe

	| Sample | [OC0001] Filesystem | [OC0005] Cryptography | [OC0006] Communication | [OC0002] Memory | [OC0003] Process | [OC0008] Operating System |
	|--------|---------------------|-----------------------|-------------------------|-----------------|-----------------|--------------------------|
	| **Default Norm**            | 100.0                 | 100.0                   | 0.0             | 100.0           | 100.0           | 100.0                    |
	| **Per-Sample Norm**         | 100.0                 | 1.529                   | 0.0             | 80.734          | 13.456          | 68.196                   |

	---

	## Mean Datafram

	| Micro-objective           | **Default Mean** | **Per-Sample Mean** |
	|---------------------------|--------------|-----------------|
	| [OC0001] Filesystem       | 100.0        | 100.0           |
	| [OC0005] Cryptography     | 100.0        | 1.529           |
	| [OC0006] Communication    | 0.0          | 0.0             |
	| [OC0002] Memory           | 100.0        | 80.734          |
	| [OC0003] Process          | 100.0        | 13.456          |
	| [OC0008] Operating System | 100.0        | 68.196          |


	---

	## To percent

	| Micro-objective           | **Default %** | **Per-Sample %** |
	|---------------------------|---------------------|-------------------------|
	| [OC0001] Filesystem       | 20.0               | 37.89                  |
	| [OC0005] Cryptography     | 20.0               | 0.58                   |
	| [OC0006] Communication    | 0.0                | 0.00                   |
	| [OC0002] Memory           | 20.0               | 30.59                  |
	| [OC0003] Process          | 20.0               | 5.10                   |
	| [OC0008] Operating System | 20.0               | 25.84                  |

	![1_sample_micro_obj](https://github.com/user-attachments/assets/5ea7bad2-d651-4788-a3a7-68b1d6379764)
	![1_sample_micro_beh](https://github.com/user-attachments/assets/8b804f97-568c-4dee-b105-13063b910cd4)

	</details>
	<details>
		<summary><b>52 Guloader samples</b></summary>	
		
	![guloader_micro_obj](https://github.com/user-attachments/assets/26e9413e-3e2c-40c6-925d-6a68245000ed)
	</details>
	<details>
		<summary><b>83 Gcleaner samples</b></summary>	
		
	![gcleaner_micro_obj](https://github.com/user-attachments/assets/56957665-8994-479f-afcd-a5dd7cbe7e37)
	</details>
	<details>
		<summary><b>66 Alina samples</b></summary>

 	![alina_micro_obj](https://github.com/user-attachments/assets/90339a56-ea1d-436a-97f1-279161e6f7b1)
	</details>
	<details>
		<summary><b>48 Petya samples</b></summary>
		
	![petya_micro_obj](https://github.com/user-attachments/assets/07c1fc41-e9b2-4654-a5e5-b3e937074f7a)
	</details>


</details>

# Authors

[Razvan Raducu](https://www.youtube.com/@RazviOverflow)  
[Ricardo J. Rodríguez](https://webdiis.unizar.es/~ricardo/)  
[Pedro Álvarez](https://i3a.unizar.es/es/investigadores/pedro-javier-alvarez-perez-aradros)
