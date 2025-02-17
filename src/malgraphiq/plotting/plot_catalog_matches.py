# Razvan Raducu. https://github.com/RazviOverflow
import glob
import logging
from pathlib import Path
from os import path
import argparse
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

from plotting import color_maps
from plotting import configuration

# micro_objectives_alphabet = [
#     '[OC0001] Filesystem', 
#     '[OC0005] Cryptography',
#     '[OC0006] Communication', 
#     '[OC0002] Memory', 
#     '[OC0003] Process',
#     '[OC0008] Operating System'
# ]

def rename_indexes(df: pd.DataFrame) -> None:
    """
    Rename the indexes of the given pandas DataFrame _df_.
    
    All changes are made **inplace** so no DataFrame is returned, given that
    the one passed in as parameter will be modified.

    This functions assumes a DataFrame in a specific format.

    If the index name is "Number of graphs processed", replaces it with "Spawned Processes", otherwise, delete the ".Total matches" suffix from the indexes.

    Changes:
        - Replaces "Number of graphs processed" with "Spawned Processes".
        - Removes the ".Total matches" suffix from index names.

    Args:
        df (pd.DataFrame): DataFrame to modify.
    """
    #https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.rename.html
    for column_name in df:
        if column_name == "Number of graphs processed" or column_name == "n_processes":
            df.rename(columns={f"{column_name}":"Spawned Processes"}, inplace=True)
        else:
            df.rename(columns={f"{column_name}":column_name.removesuffix(".Total matches")}, inplace=True) # Python +3.9 https://stackoverflow.com/a/1038845
    return df

def drop_methods_indexes(df: pd.DataFrame) -> pd.DataFrame:
    """
    Delete all entrieis from _df_ corresponding to the method-level 
    of the behavioral catalog

    https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.drop.html
    https://stackoverflow.com/a/61166760

    Args:
        df (pd.DataFrame): Input DataFrame.

    Returns:
        pd.DataFrame: DataFrame with only micro-objective columns.
    """
    # In the context of DataFrames index is synonymous with row
    # An index corresponds to a method-level if it does not end with "Total matches"
    columns_to_drop = [column for column in df if not column.endswith("Total matches") and (column != "n_processes" or column != "Number of graphs processed")]
    new_df = df.drop(columns_to_drop, axis=1) # {0 or ‘index’, 1 or ‘columns’}, default 0
    return new_df

def get_micro_objectives_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Drops (deletes) all the columns whose name contains a dot '.' therefore 
    remaining only with those corresponding to micro-objectives. Example:

    Micro-objective column: [OC0001] Filesystem
    Micro-behavior column (dropped): [OC0001] Filesystem.[C0049] Get File Attributes

    Args:
        df (pd.DataFrame): Input DataFrame.

    Returns:
        pd.DataFrame: DataFrame with only micro-objective columns. A new copy of the modified DataFrame (inplace=False).
    """
    # In the context of DataFrames index is synonymous with row

    # If the row label contains more than zero dots, it means the label corresponds
    # to a micro_behavior level and therefore it must be dropped (i.e., [OC0001] Filesystem.[C0063] Move File)
    columns_to_drop = [column for column in df if column.count('.')]
    new_df = df.drop(columns_to_drop, axis=1)
    return new_df


def get_micro_behaviors_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Drops (deletes) all the columns whose name does not contain a dot '.' or
    corresponds to the "Spawned Processes" column, therefore remaining only with 
    those corresponding to micro-behaviors. Example:

    Micro-objective column (dropped): [OC0001] Filesystem
    Micro-behavior column: [OC0001] Filesystem.[C0049] Get File Attributes

    Args:
        df (pd.DataFrame): Input DataFrame.

    Returns:
        pd.DataFrame: DataFrame with only micro-behaviors columns. A new copy of the modified DataFrame (inplace=False).
    """
    # In the context of DataFrames index is synonymous with row

    # If the row label does not contain dots and it is not "Spawned Processes",
    # it means the label corresponds to a micro_objective level and therefore it must be dropped (i.e., [OC0001] Filesystem)
    columns_to_drops = [column for column in df if not column.count('.') and column != "Spawned Processes"]
    new_df = df.drop(columns_to_drops, axis=1)
    return new_df

def normalize(df: pd.DataFrame, min: int = 0, max: int = 1, transpose:bool = False) -> pd.DataFrame:
    """
    Normalize the values of the DataFrame _df_ in the given range [min, max].
    By default min is 0 and max is 1.

    Transpose is used to indicate whether to transpose de dataframe before normalizing it.
    Transposing it is useful when the normalization is done using the samples as base values
    instead of each micro-behavior. This is used when printing the figures of each category
    where we care about the min() and max() of each sample for the category, not the
    min() and max() of each micro-behavior (the latter sometimes results in divison by zero)

    Modify transpose according to your normalizations needs, as documented in Razvan Raducu's
    PhD dissertation or in the repository. 
        - False: per-category normalization.
        - True: per-sample normalization.

    Args:
        df (pd.DataFrame): DataFrame to normalize.
        min (int): Minimum value for normalization (default: 0).
        max (int): Maximum value for normalization (default: 1).
        transpose (bool): Whether to transpose the DataFrame before normalization (default: False).

    Returns:
        pd.DataFrame: Normalized DataFrame.
    """
    if transpose:
        df = df.T
    #normalized_df = (df-df.min()) / (df.max()-df.min()) * ((max - min) + min)
    
    normalized_df = (df) / (df.max()) * ((max - min) + min)
    #normalized_df = df / (df.max()-df.min()) * ((max - min) + min)
    #normalized_df['Spawned Processes'] = df['Spawned Processes'] #Restore value, no need to normalize
    normalized_df = normalized_df.replace(np.nan, 0) # Sometimes NaN may arise due divison by zero. https://saturncloud.io/blog/python-pandas-how-to-remove-nan-and-inf-values/
    if transpose:
        normalized_df = normalized_df.T
    return normalized_df

def generate_dataframe_specific_micro_objective(original_dataframe: pd.DataFrame, micro_objective: str) -> pd.DataFrame:
    """
    Generate a new DataFrame containing data for a specific micro-objective.

    Args:
        original_dataframe (pd.DataFrame): Original DataFrame containing multiple objectives.
        micro_objective (str): The specific micro-objective to extract.

    Returns:
        pd.DataFrame: DataFrame containing only the data for the specified micro-objective.
    """
    micro_objective_df = [col for col in original_dataframe if col.startswith(micro_objective)]
    micro_objective_df = original_dataframe[micro_objective_df]
    return micro_objective_df

def generate_barchart_per_micro_objective(
    df: pd.DataFrame, 
    micro_objectives, 
    title: str, 
    catalog_matches_plot_dir: str, 
    broken: bool,
    lower_figure_limit: int, 
    upper_figure_limit: int, 
    lower_figure_ratio: int
) -> None:
    """
    Generate and save barcharts for each micro-objective.

    Args:
        df (pd.DataFrame): DataFrame containing the data to plot.
        micro_objectives (list[str]): List of micro-objectives to generate barcharts for.
        title (str): Title for the charts.
        catalog_matches_plot_dir (str): Directory to save the generated charts.
        broken (bool): Whether to use broken barcharts.
        lower_figure_limit (int): Lower limit for broken barcharts.
        upper_figure_limit (int): Upper limit for broken barcharts.
        lower_figure_ratio (int): Ratio of lower figure height for broken barcharts.
    """

    for micro_objective in micro_objectives:
        micro_objective_df = generate_dataframe_specific_micro_objective(df, micro_objective)
        micro_objective_name_no_id = micro_objective[micro_objective.index(']')+1:].strip()
        #figure_title = title+"\n"+str(micro_objective_name_no_id)+" Micro-objective"
        figure_title = title
        file_name = title+"_"+str(micro_objective_name_no_id)+".pdf" if title else str(micro_objective_name_no_id)+".pdf"
        file_name = path.join(catalog_matches_plot_dir, file_name) if catalog_matches_plot_dir else file_name 
        if broken: 
            generate_pdf_broken_barchart(micro_objective_df, figure_title, file_name, lower_figure_limit, upper_figure_limit, lower_figure_ratio, micro_objective)
        else:
            generate_pdf_barchart(micro_objective_df, figure_title, file_name, micro_objective)

def clip_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clips data (only upper threshold) according to the value in the 0.9 or 90th quantile
    of the __df__ DataFrame. The midpoint technique is used for interpolation.

    This technique helps reduce the impact of extreme values on the dataset.

    Args:
        df (pd.DataFrame): Input DataFrame to clip.

    Returns:
        pd.DataFrame: Clipped DataFrame.
    """
    return df.clip(upper=df.quantile(0.9, interpolation='midpoint'), axis='columns', inplace=False)

def correct_execution(df: pd.DataFrame) -> bool:
    """
    Determines whether the _df_ DataFrame corresponds to a **correct execution**. 
    In this context, a **correct execution** is one that ended successfully, 
    regardless of the actual sample detonating or not.

    To consider an execution correct, we check how many times it matched with none of our behavioral
    patterns. In other words, if the sample has 0 matches with 90% or more of our micro-objectives 
    and micro-behaviors, we discard it. That is, we check whether the value 0 appears
    in 90% of the columns of the DataFrame or more.

    Args:
        df (pd.DataFrame): Input DataFrame to evaluate.

    Returns:
        bool: True if the execution is correct, False otherwise.
    """
    return df.T.value_counts().iloc[0] < len(df.columns)*0.90



def get_basic_colors(values_to_color: list[str]) -> list[str]:
    """
    Retrieve a list comprising the basic color values corresponding to each value from __values_to_color__.

    Args:
        values_to_color (list[str]): List of values for which to retrieve colors.

    Returns:
        list[str]: List of color codes corresponding to the input values.
    """
    color_list = []
    for value in values_to_color:
        if value not in color_maps.behavior_catalog_basic_colormap:
            color_list.append("#FFFFFF")
        else:
            color_list.append(color_maps.behavior_catalog_basic_colormap[value])
    return color_list

def generate_pdf_radarchart(
    df: pd.DataFrame, 
    fig_title: str, 
    fig_name: str,
    radarchart_max_scale: int, 
    micro_objective: str = None
) -> None:
    """
    Generate a radar chart from a DataFrame and save it as PDF.

    Args:
        df (pd.DataFrame): DataFrame with values to plot.
        fig_title (str): Title of the figure.
        fig_name (str): Name of the output file.
        radarchart_max_scale (int): Maximum scale value for the radar chart.
        micro_objective (Optional[str]): Specific micro-objective for labeling (optional).
    """
    normalized_df = normalize(df, 0, 100)
    #df = normalize(df.mean(), 0, 100) # Normalization of the means
    # We are printing only the mean of all the samples, not each one of them individually
    mean_df = normalized_df.mean() # IMPORTANT!!! Get the mean() AFTER normalization

    #Transform data into percentage
    mean_df = (100. * mean_df / mean_df.sum()).round(2)

    # In case the function is drawing micro-behaviors (micro_objective not none),
    # Delete the micro-objectvie from its name. That is: 
    # [OC0006] Communication.[C0001] Socket Communication -> [C0001] Socket Communication
    if micro_objective is not None:
        for index_name in mean_df.index:
            mean_df.rename(index={f"{index_name}":index_name.removeprefix(micro_objective+".")}, inplace=True) # Python +3.9 https://stackoverflow.com/a/1038845

    # Delete the ID
    labels = [index[index.index(']')+1:].strip().replace(" ", "\n") for index in mean_df.index] 
       
    categories=list(labels)
    number_of_categories = len(categories)
    angles = [n / float(number_of_categories) * 2 * np.pi for n in range(number_of_categories)]
    angles += angles[:1]
    # Initialise the spider plot
    ax = plt.subplot(111, polar=True)
    # If you want the first axis to be on top:
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    # Draw one axe per variable + add labels labels yet
    plt.xticks(angles[:-1], categories, size=10, weight='bold')
    # Draw ylabels
    ax.set_rlabel_position(0)
    #plt.yticks([0,25,50,75,100], ["0","25","50","75","100"], color="grey", size=7)
    plt.yticks([0,10,20,30,40,50,60,70,80,90,100], ["0%","10%","20%","30%","40%","50%","60%","70%","80%","90%","100%"], color="black", size=8)
    #plt.ylim(0,50)
    plt.ylim(0,radarchart_max_scale)
    # Format Y axis as percent https://stackoverflow.com/questions/31357611/format-y-axis-as-percent
    ax.yaxis.set_major_formatter(mtick.PercentFormatter())
    # ------- PART 2: Add plots

    # The snippet below was used back when each sample was drawn individually. 
    #for sample in df.index:
        #values=df.loc[sample].values.flatten().tolist()
        #values+=values[:1]
        #ax.plot(angles, values, linewidth=1, linestyle='solid', label=sample)
        #ax.fill(angles, values, alpha=0.25)
    # Now that we draw only the mean (like just one sample), the code is simpler
    values = list(mean_df)
    values+=values[:1]
    ax.plot(angles, values, linewidth=1, linestyle='solid', label="Mean values from all samples")
    ax.fill(angles, values, alpha=1)

    # Draw the points. Inspired by https://stackoverflow.com/a/59905577
    for index, angle in enumerate(angles):
        if values[index] != 0.0: # Don't draw the 0.0%
            ax.text(angle, values[index]+5, str(values[index])+"%", color='black', ha='center', va='center', size=9, weight='bold')
        #ax.scatter(angle, values[index], s=5, color="blue")

    plt.tick_params(axis='both', which='major', labelbottom=True, bottom=True, left=True, top=True)


    # Add custom padding (per label) on x Axis so labels do not overlap with figure
    #ax.tick_params(axis='x', which='major', pad=15)
    for tick in ax.xaxis.get_major_ticks():
        tick.set_pad(configuration.radarchart_padding[tick.label1.get_text()])

    # Title
    if micro_objective is None:
        plt.title(fig_title, fontsize=13)
    else:
        plt.title(micro_objective[micro_objective.index(']')+1:].strip(), fontsize=13)

    # Add legend
    #plt.legend( bbox_to_anchor=(0.1, 0.1), fontsize='small')
    
    # Save the figure
    plt.savefig(fig_name, format="pdf", bbox_inches="tight")

    plt.close() # So data does not get mixed up

# Broken-axis figure, genereted ad-hoc for Alina samples
def generate_pdf_broken_barchart(
    df: pd.DataFrame,
    fig_title: str,
    fig_name: str,
    user_supplied_lowerylim: int,
    user_supplied_upperylim: int,
    lower_figure_ratio: int,
    micro_objective: str = None
) -> None:
    """
    Generate a broken barchart and save it as a PDF.

    A broken barchart splits the Y-axis into two parts, enabling better visualization 
    of datasets with extreme values.

    Args:
        df (pd.DataFrame): DataFrame containing values to plot.
        fig_title (str): Title of the chart.
        fig_name (str): Name of the output file.
        user_supplied_lowerylim (int): Upper limit of the lower half of the chart.
        user_supplied_upperylim (int): Lower limit of the upper half of the chart.
        lower_figure_ratio (int): Percentage of the chart height allocated to the lower half.
        micro_objective (Optional[str]): Specific micro-objective for labeling (default: None).
    """

    # Normalize data
    normalized_df = normalize(df, 0, 100)

    # Get the mean
    mean_df = normalized_df.mean()
    #Transform data into percentage
    mean_df = (100. * mean_df / mean_df.sum()).round(2)
    mean_df = mean_df.replace(np.nan, 0)

    # Rename indexes by deleting their category
    for index_name in mean_df.index:
        mean_df.rename(index={f"{index_name}":index_name.removeprefix(micro_objective+".")}, inplace=True) # Python +3.9 https://stackoverflow.com/a/1038845
    colors = get_basic_colors(mean_df.index)
    legend_title = "Micro Behaviors"

    # Delete the ID and replace space with newline
    labels = [index[index.index(']')+1:].strip() for index in mean_df.index]

    # Generate xticks labels
    xtick_labels = []

    # Add abbreviations to labels in legend (if they got one)
    for i, label in enumerate(labels):
        # Delete redundant words on the fly
        if "Communication" in label:
            labels[i] = labels[i].replace("Communication", "")

        if label in configuration.abbreviation_map:
            labels[i] = label + f" ({configuration.abbreviation_map[label]})"
            # Fix typo on the fly
            if label == "Create or Open file":
                labels[i] = labels[i].replace("file", "File")
            xtick_labels.append(configuration.abbreviation_map[label])
        else:
            xtick_labels.append(labels[i])

    # Broken Axis figure: https://matplotlib.org/stable/gallery/subplots_axes_and_figures/broken_axis.html
    lower_figure_height_ratio = round(lower_figure_ratio / 100, 2)
    higher_figure_height_ratio = round(1 - lower_figure_height_ratio, 2)
    height_ratios=[higher_figure_height_ratio, lower_figure_height_ratio]
    #fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, height_ratios=[.1, .9])
    fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, height_ratios=height_ratios)
    fig.subplots_adjust(hspace=.1)  # adjust space between axes

    # ax1 is the upper part of the figure, ax2 is the lower one
    ax1bar = ax1.bar(xtick_labels, mean_df.values, label=xtick_labels, color=colors, zorder=1)
    ax2bar = ax2.bar(xtick_labels, mean_df.values, label=xtick_labels, color=colors, zorder=1)

    # Upper-part of the figure limit:
    ax1.set_ylim(user_supplied_upperylim, 100)

    # Lower-part of the figure limit:
    ####################################################################
    # Ad-hoc barcharts. Uncomment and customize this code as you seem
    # necessary in order to generate custom broken barcharts for your
    # specific needs.
    ####################################################################
    # if micro_objective in ["[OC0001] Filesystem","[OC0003] Process"]:
    #     ax2.set_ylim(0, 20)
    #     y_bbox_to_anchor = -.20
    # else:
    #     ax2.set_ylim(0, 55)
    #     y_bbox_to_anchor = -.10

    ax2.set_ylim(0, user_supplied_lowerylim)

    # hide the spines between ax and ax2
    ax1.spines.bottom.set_visible(False)
    ax2.spines.top.set_visible(False)
    #ax1.xaxis.tick_top()
    #ax1.tick_params(labeltop=False)  # don't put tick labels at the top
    #ax2.xaxis.tick_bottom()

    # Now, let's turn towards the cut-out slanted lines.
    # We create line objects in axes coordinates, in which (0,0), (0,1),
    # (1,0), and (1,1) are the four corners of the axes.
    # The slanted lines themselves are markers at those locations, such that the
    # lines keep their angle and position, independent of the axes size or scale
    # Finally, we need to disable clipping.

    d = .5  # proportion of vertical to horizontal extent of the slanted line
    kwargs = {"marker":[(-1, -d), (1, d)], 
                "markersize":12,
                "linestyle":"none",
                "color":"k",
                "mec":"k",
                "mew":1,
                "clip_on":False}
    ax1.plot([0, 1], [0, 0], transform=ax1.transAxes, **kwargs)
    ax2.plot([0, 1], [1, 1], transform=ax2.transAxes, **kwargs)
    
    
    #bar = plt.bar(labels, mean_df.values, label=labels, color=colors)
    #plt.yticks([0, 25, 50, 75, 100])
    
    ax1.bar_label(ax1bar, label_type='edge', fmt='%.2f%%', size=7, weight='bold', zorder=1) # Converts 0 into 0.00
    ax2.bar_label(ax2bar, label_type='edge', fmt='%.2f%%', size=7, weight='bold', zorder=1)
    ax1.set_facecolor('none')
    ax2.set_facecolor('none')

    # Add bar labels based on value range
    for i, (value, bar) in enumerate(zip(mean_df.values, ax1bar)):
        # if value <= user_supplied_lowerylim:  # Label in lower part
        #     ax2.text(bar.get_x() + bar.get_width() / 2, value - 5, f"{value:.2f}%", ha='center', va='bottom', fontsize=9)
        # elif value >= user_supplied_upperylim:  # Label in upper part
        #     ax1.text(bar.get_x() + bar.get_width() / 2, value - 5, f"{value:.2f}%", ha='center', va='bottom', fontsize=9)
        # else:  # Label at the split boundary
        #     ax1.text(bar.get_x() + bar.get_width() / 2, user_supplied_upperylim - 5, f"{value:.2f}%", ha='center', va='bottom', fontsize=9)
        if value >= user_supplied_lowerylim and value <= user_supplied_upperylim:
            ax1.text(bar.get_x() + bar.get_width() / 2, user_supplied_upperylim, f"{value:.2f}%", ha='center', va='bottom', fontsize=7, zorder=2, color='black', weight='bold')

    # Format Y axis as percent https://stackoverflow.com/questions/31357611/format-y-axis-as-percent
    ax1.yaxis.set_major_formatter(mtick.PercentFormatter())
    ax2.yaxis.set_major_formatter(mtick.PercentFormatter())
    
    #plt.bar_label(bar, label_type='edge')
    
    # Rotate labels https://stackoverflow.com/a/37708190
    #plt.xticks(rotation=90)
    
    # Hide labels https://stackoverflow.com/a/40860688
    #plt.xticks(xtick_labels)
    ax1.get_xaxis().set_visible(False) # hide ticks just for the upper figure
    #ax2.set_xticks(xtick_labels) # Set abbreviated ticks
    
    # Add legend and title
    #plt.title(micro_objective[micro_objective.index(']')+1:].strip(), fontsize=13)
    #plt.title(fig_title, fontsize=17)
    ax1.set_title(fig_title, fontsize=17, y=1.0, pad=12) # We use ax1.set_title to make sure title is on top of ax1 (upper figure)
    ncols = 2 if len(labels) >= 4 else 3
    plt.legend(labels, title=legend_title, loc="upper center", fontsize='small', ncols=ncols, bbox_to_anchor = (.5, -.17))#, prop={'size': 10})

    #ax.legend(handles=labels)

    # Show the graph
    plt.savefig(fig_name, format="pdf", bbox_inches="tight")
    plt.close() # So data does not get mixed up

def generate_pdf_barchart(
    df: pd.DataFrame, 
    fig_title: str,
    fig_name: str, 
    micro_objective: str = None
) -> None:
    """
    Generate a barchart and save it as a PDF.

    Args:
        df (pd.DataFrame): DataFrame containing values to plot.
        fig_title (str): Title of the barchart.
        fig_name (str): Output file name.
        micro_objective (Optional[str]): Specific micro-objective to label (default: None).
    """
    # Normalize data
    normalized_df = normalize(df, 0, 100)
    #breakpoint()
    # Get the mean
    mean_df = normalized_df.mean()
    # Delete the columns whose value is 0
    #mean_df = mean_df[mean_df.values != 0]
    #Transform data into percentage
    mean_df = (100. * mean_df / mean_df.sum()).round(2)
    mean_df = mean_df.replace(np.nan, 0)

    # Rename indexes by deleting their category
    for index_name in mean_df.index:
        mean_df.rename(index={f"{index_name}":index_name.removeprefix(micro_objective+".")}, inplace=True) # Python +3.9 https://stackoverflow.com/a/1038845
    #color = get_tonal_colors(mean_df.index)
    colors = get_basic_colors(mean_df.index)
    legend_title = "Micro Behaviors"

     # Delete the ID and replace space with newline
    labels = [index[index.index(']')+1:].strip() for index in mean_df.index]

    # Generate xticks labels
    xtick_labels = []

    # Add abbreviations to labels in legend (if they got one)
    for i, label in enumerate(labels):
        # Delete redundant words on the fly
        if "Communication" in label:
            labels[i] = labels[i].replace("Communication", "")

        if label in configuration.abbreviation_map:
            labels[i] = label + f" ({configuration.abbreviation_map[label]})"
            # Fix typo on the fly
            if label == "Create or Open file":
                labels[i] = labels[i].replace("file", "File")
            xtick_labels.append(configuration.abbreviation_map[label])
        else:
            xtick_labels.append(labels[i])

    #hatch = get_hatches(mean_df.index)

    # Delete the ID and replace space with newline
    #labels = [index[index.index(']')+1:].strip().replace(" ","\n") for index in mean_df.index] 
    #labels = [index[index.index(']')+1:].strip() for index in mean_df.index]
    #breakpoint()
    #colors = get_basic_colors(mean_df.index)
    
    #fig, ax = plt.subplots()
    #plt.bar(mean_df.index, mean_df.values, label=labels, color=colors)
    #ax = mean_df.plot(xticks=[], kind='bar', stacked=False, color=colors)
    #breakpoint()

    actual_bar = plt.bar(xtick_labels, mean_df.values, label=xtick_labels, color=colors)
    #plt.yticks([0, 25, 50, 75, 100])
    plt.ylim(0, 100) # Set 100 as limit, to cut figure right there
    plt.gca().yaxis.set_major_formatter(mtick.PercentFormatter(xmax=100)) # Format y-axis as percent
    plt.bar_label(actual_bar, label_type='edge', fmt='%.2f%%', size=9, weight='bold') # Converts 0 into 0.00

    
    #plt.bar_label(bar, label_type='edge')
    
    # Rotate labels https://stackoverflow.com/a/37708190
    #plt.xticks(rotation=90)
    
    # Hide labels https://stackoverflow.com/a/40860688
    #plt.xticks([])

    # Add legend and title
    #plt.title(micro_objective[micro_objective.index(']')+1:].strip(), fontsize=13)
    plt.title(fig_title, fontsize=17, y=1.0, pad=12)
    ncols = 2 if len(labels) >= 4 else 3
    plt.legend(labels, title=legend_title, loc="upper center", fontsize='small', ncols=ncols, bbox_to_anchor = (.5, -.05))
    #ax.legend(handles=labels)

    # Show the graph
    plt.savefig(fig_name, format="pdf", bbox_inches="tight")
    plt.close() # So data does not get mixed up

def main(json_catalog_matches: str | list, 
    figure_title: str, 
    radarchart_max_scale: int, 
    catalog_matches_plot_dir: str,
    broken_barcharts: bool,
    lower_figure_limit: int,
    upper_figure_limit: int,
    lower_figure_ratio: int,
    logger: logging.Logger
) -> None:
    """
    Generate charts and visualizations for catalog matches.

    Args:
        json_catalog_matches (str | dict): JSON file, directory containing JSON files or a list of dictionaries of catalog matches.
        figure_title (str): Title for the generated charts.
        radarchart_max_scale (int): Maximum scale for radar charts.
        catalog_matches_plot_dir (str): Directory to save generated plots.
        broken_barcharts (bool): Whether to generate broken barcharts.
        lower_figure_limit (int): Lower limit for broken barcharts.
        upper_figure_limit (int): Upper limit for broken barcharts.
        lower_figure_ratio (int): Ratio of lower figure height for broken barcharts.
        logger (logging.Logger): Logger for reporting.
    """

    dataframe_list = []
    json_files = []
    sample_nr = 1
    discarded = 0

    if isinstance(json_catalog_matches, list):
        for i, individual_pattern_matches in enumerate(json_catalog_matches):
            dataframe = pd.json_normalize(individual_pattern_matches)
            if not correct_execution(dataframe):
                logger.info(f"[!] Discarded dict number {i}, considered incorrect execution.")
                discarded += 1
                continue
            dataframe_list.append(dataframe)
            sample_nr += 1
    else:
        # Collect all JSON files
        if path.isfile(json_catalog_matches):
            json_files.append(json_catalog_matches)
        elif path.isdir(json_catalog_matches):
            json_files.extend(glob.glob(json_catalog_matches+"/*.json"))

        # Read all JSON files, in case the user passed a directory

        for json_file in json_files:
            with open(json_file, encoding='utf-8') as f:
                data = json.load(f)
                dataframe = pd.json_normalize(data)
                if not correct_execution(dataframe):
                    logger.info(f"[!] Discarded file {json_file}, considered incorrect execution.")
                    discarded += 1
                    continue
                # https://stackoverflow.com/a/58020454 Custom index
                #dataframe['Sample'] = 6932
                #dataframe = dataframe.set_index('index')
                #print(dataframe.index)
                dataframe_list.append(dataframe)
                logger.info(f"[+] Opened file {json_file} as sample {sample_nr}")
                sample_nr += 1
    logger.info(f"[+][+][+] Total samples: {len(json_files)} - Processed: {sample_nr-1} - Discarded: {discarded} ")

    Path(catalog_matches_plot_dir).mkdir(exist_ok=True, parents=True)

    # Concatenate the different DataFrames generated from the JSON files
    df = pd.concat(dataframe_list)
    # Call needed to make indexes incremental. Otherwise, they're all zeroes
    # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.reset_index.html
    df.reset_index(inplace=True, drop=True)
    df.index += 1 #To start at 1, not at 0 https://stackoverflow.com/a/20168416

    df_dropped = drop_methods_indexes(df)
    rename_indexes(df_dropped)

    title = figure_title if figure_title else ""

    micro_objectives_df = get_micro_objectives_dataframe(df_dropped)

    #from additional_code import generate_pdf_heatmap
    #generate_pdf_heatmap(micro_objectives_df, title, title + " spawned_processes.pdf", "spawned_processes")
    #df_dropped = df_dropped.drop("Spawned Processes", axis=1) # After creating the figure, the column Spawned Processes is no longer of use

    #micro_objectives_df = micro_objectives_df.drop("Number of graphs processed", axis=1)
    micro_objectives_df = clip_data(micro_objectives_df)
    #generate_pdf_heatmap(micro_objectives_df, title, "micro_objective.pdf", "micro-objective")
    
    micro_objective_names = micro_objectives_df.columns #Obtain the micro-objective level entries (categories)

    micro_behaviors_df = get_micro_behaviors_dataframe(df_dropped)
    micro_behaviors_df = clip_data(micro_behaviors_df)
    #separated_df = separate_micro_objectives_and_behaviors_by_mean(micro_behaviors_df)
    #generate_pdf_nestedpie(separated_df, title, "nested_pie.pdf")

    ############ BARCHART ############
    #generate_pdf_stackedbars(separated_df, title, "stackedbars.pdf")
    #generate_barchart_per_micro_objective(micro_behaviors_df, micro_objective_names, title)
    generate_barchart_per_micro_objective(micro_behaviors_df, micro_objective_names, title, catalog_matches_plot_dir, broken_barcharts, lower_figure_limit, upper_figure_limit, lower_figure_ratio)
    
    ############ PIECHART ############
    #generate_pdf_piechart(micro_objectives_df, title, title+"piechart.pdf")
    #generate_piechart_per_micro_objective(micro_behaviors_df, micro_objective_names, title)

    ############ HEATMAP ############
    #generate_pdf_heatmap(micro_behaviors_df, title, "micro_behavior.pdf", "micro-behavior", micro_objective_names)
    #generate_heatmap_per_micro_objective(micro_behaviors_df, micro_objective_names, title)
    
    ############ RADARCHART ############
    file_name = title+"_Micro-Objectives.pdf" if title else "Micro-Objectives.pdf"
    file_name = path.join(catalog_matches_plot_dir, file_name) if catalog_matches_plot_dir else file_name
    generate_pdf_radarchart(micro_objectives_df, title, file_name, radarchart_max_scale)
    #generate_pdf_radarchart(micro_behaviors_df, title, "micro_behavior_spider.pdf")
    #generate_radarchart_per_micro_objective(micro_behaviors_df, micro_objective_names, title)
