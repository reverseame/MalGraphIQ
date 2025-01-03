## Standalone execution examples

### Barcharts (unbroken)
```
$ python3 plot_catalog_matches.py ../occurrences/test.json -rc_max 30 --catalog_matches_plot_dir visualizations
```

### Broken barcharts with default division values 0% - 50% | 50% - 100%
```
$ python3 plot_catalog_matches.py ../occurrences/test.json -rc_max 30 --catalog_matches_plot_dir visualizations --broken_barcharts
```

### Broken barcharts with division values 0% - 20% | 80% - 100%
```
$ python3 plot_catalog_matches.py ../occurrences/test.json -rc_max 30 --catalog_matches_plot_dir visualizations --broken_barcharts --lower_figure_limit 20 --upper_figure_limit 80
```

### Broken barcharts with division values 0% - 20% | 80% - 100%, but breaking is at 30% height, not in the center of the plot.
```
$ python3 plot_catalog_matches.py ../occurrences/test.json -rc_max 30 --catalog_matches_plot_dir visualizations --broken_barcharts --lower_figure_limit 20 --upper_figure_limit 80 --lower_figure_ratio 30
```