# Test reports
This folder contains some testing reports obtained from the [WinMET](https://doi.org/10.5281/zenodo.12647555) dataset. The reports have been processed with [MALVADA](https://github.com/reverseame/MALVADA/tree/main).

## Reports
Reports are compressed to save space. The .7z archives have no password. These are their characteristics:

- gcleaner_reports.7z
	- MD5: `b35b59edc1272002e875adc064fb9303`
	- Compressed size on disk: ~19 MiB
	- Uncompressed size on disk: ~910 MiB
- remcos_reports.7z
	- MD5:`f95bd2b454ceef3a86e1773af46863e2`
	- Compressed size on disk: ~44 MiB
	- Uncompressed size on disk: ~1476 MiB

## Visualizations
The final visualizations for each family (`GCleaner` and `Remcos`) are located within their corresponding folders: [gcleaner_visualizations](./gcleaner_visualizations) and [remcos_visualizations](./remcos_visualizations), respectively.

We deleted all the intermediate results (transition matrices, behavior and category graphs, and occurrence files).

### How to generate them
In order to generate the visual representations you see in this repository, we first launched the `all` execution mode of `malgraphiq.py` and then relaunched the `plots` phase to customize and re-scale the visualizations. The commands used were the following:

All commands assume current working directory as this folder. Modify paths according to your installation. **Executing the following commands will generate all the intermedaite results**.
- Extract the reports: `7z x gcleaner_reports.7z`
- Execute the entire pipeline for `GCleaner` family: `$ python3 ../src/malgraphiq/malgraphiq.py all gcleaner_100/ -c ../wbc/catalog.json -w ../winapi_categories/winapi_categories.json`.
	- Re-generate default visualizations with custom parameters: `$ python3 ../src/malgraphiq/malgraphiq.py plots . -rc_max 40 -bb --lower_figure_limit 30 --upper_figure_limit 90 --lower_figure_ratio 90 --fig_title GCleaner`
- Extract the reports: `7z x remcos_reports.7z`
- Execute the entire pipeline for `Remcos` family: `$ python3 ../src/malgraphiq/malgraphiq.py all remcos_100/ -c ../wbc/catalog.json -w ../winapi_categories/winapi_categories.json`.
	- Re-generate default visualizations with custom parameters: `$ python3 ../src/malgraphiq/malgraphiq.py plots . -rc_max 40 -bb --lower_figure_limit 30 --upper_figure_limit 90 --lower_figure_ratio 90 --fig_title Remcos`