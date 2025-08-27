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
- Agenttesla_reports.7z
	- MD5: `3d2e37e5866eaeb10de5d7d0184bdce4`
	- Compressed size on disk: ~42 MiB
	- Uncompressed size on disk: ~1798 MiB
- Amadey_reports.7z
	- MD5: `1b9be17244e700690868ed5ccf7583e6`
	- Compressed size on disk: ~29 MiB
	- Uncompressed size on disk: ~1503 MiB
- Berbew_reports.7z
	- MD5: `2f09e1c4d392ee45d6930a7025e8c9b4`
	- Compressed size on disk: ~14 MiB
	- Uncompressed size on disk: ~773 MiB
- Gamarue_reports.7z
	- MD5: `a2f7ed92fac69bc3adc2447745d8ced3`
	- Compressed size on disk: ~30 MiB
	- Uncompressed size on disk: ~1343 MiB
- Guloader_reports.7z
	- MD5: `b64b48db5aa6c1f3b6148652dcd5d4e6`
	- Compressed size on disk: ~66 MiB
	- Uncompressed size on disk: ~4066 MiB
- Noon_reports.7z
	- MD5: `cdd32592c637617f377da136929b50bb`
	- Compressed size on disk: ~42 MiB
	- Uncompressed size on disk: ~1753 MiB
- Strab_reports.7z
	- MD5: `90bfadd450d7b3f6b611f6efad28f579`
	- Compressed size on disk: ~15 MiB
	- Uncompressed size on disk: ~593 MiB
- Taskun_reports.7z
	- MD5: `b5e020506d1400f16614818f7854723e`
	- Compressed size on disk: ~47 MiB
	- Uncompressed size on disk: ~1991 MiB
- Vbclone_reports.7z
	- MD5: `83e4b45f71232b5d07d97071241a3e42`
	- Compressed size on disk: ~57 MiB
	- Uncompressed size on disk: ~5316 MiB
- Virlock_reports.7z
	- MD5: `5780b925b8fee93ee480166b59d5ec17`
	- Compressed size on disk: ~139 MiB
	- Uncompressed size on disk: ~4489 MiB

## Visualizations
The final visualizations for each family are located within their corresponding folders.

We deleted all the intermediate results (transition matrices, behavior and category graphs, and occurrence files).

### How to generate them
_This is an example for `gcleaner` and `remcos` families._

In order to generate the visual representations you see in this repository, we first launched the `all` execution mode of `malgraphiq.py` and then relaunched the `plots` phase to customize and re-scale the visualizations. The commands used were the following:

All commands assume current working directory as this folder. Modify paths according to your installation. **Executing the following commands will generate all the intermedaite results**.
- Extract the reports: `7z x gcleaner_reports.7z`
- Execute the entire pipeline for `GCleaner` family: `$ python3 ../src/malgraphiq/malgraphiq.py all gcleaner_100/ -c ../wbc/catalog.json -w ../winapi_categories/winapi_categories.json`.
	- Re-generate default visualizations with custom parameters: `$ python3 ../src/malgraphiq/malgraphiq.py plots . -rc_max 40 -bb --lower_figure_limit 30 --upper_figure_limit 90 --lower_figure_ratio 90 --fig_title GCleaner`
- Extract the reports: `7z x remcos_reports.7z`
- Execute the entire pipeline for `Remcos` family: `$ python3 ../src/malgraphiq/malgraphiq.py all remcos_100/ -c ../wbc/catalog.json -w ../winapi_categories/winapi_categories.json`.
	- Re-generate default visualizations with custom parameters: `$ python3 ../src/malgraphiq/malgraphiq.py plots . -rc_max 40 -bb --lower_figure_limit 30 --upper_figure_limit 90 --lower_figure_ratio 90 --fig_title Remcos`