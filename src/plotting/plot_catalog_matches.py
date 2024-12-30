# Razvan Raducu. https://github.com/RazviOverflow
import argparse
import json
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.patheffects as PathEffects
import matplotlib.ticker as mtick
import glob
from os import path
from color_maps import *
from configuration import *

# micro_objectives_alphabet = [
#     '[OC0001] Filesystem', 
#     '[OC0005] Cryptography',
#     '[OC0006] Communication', 
#     '[OC0002] Memory', 
#     '[OC0003] Process',
#     '[OC0008] Operating System'
# ]

def parse_arguments():
    parser = argparse.ArgumentParser(
        prog="MalGraphIQ (Plotting)",
        description="Transform JSON behavioral catalog matches to specific figures. Radarcharts are employed for micro-objective occurrences while barcharts are used to represent micro-behavior occurrences. You can find code for other type of visualizations in additional_code.py.")
    parser.add_argument("json", nargs="*", help="The json file or directory/ies containing the matches, as produced by backtracking.py.")
    parser.add_argument("--fig_title", help="(Optional) Specify the title of the generated figure. By default it is empty.")
    #parser.add_argument("--level", help="Specifies the desired behavioral catalog level for which the figure will be generated.", choices=["micro-objective", "micro-behavior"], required=True)

    group = parser.add_mutually_exclusive_group()
    group.add_argument("-q", "--quiet", action="store_true",
                        help="Only error and critical messages are printed.")
    group.add_argument("-s", "--silent", action="store_true",
                        help="Nothing is printed.")
    arguments = parser.parse_args()
    return arguments


def rename_indexes(df: pd.DataFrame) -> None:
    """Renames the indexes of the given pandas DataFrame _df_.
    
    All changes are made **inplace** so no DataFrame is returned, given that
    the one passed in as parameter will be modified.

    This functions assumes a DataFrame in a specific format.

    If the index name is "n_processes", replaces it with "Spawned Processes".
    Otherwise, delete the ".Total matches" suffix from the indexes.    
    """
    #https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.rename.html
    for column_name in df:
        if column_name == "n_processes":
            df.rename(columns={f"{column_name}":"Spawned Processes"}, inplace=True)
        else:
            df.rename(columns={f"{column_name}":column_name.removesuffix(".Total matches")}, inplace=True) # Python +3.9 https://stackoverflow.com/a/1038845
    return df

def drop_methods_indexes(df: pd.DataFrame) -> pd.DataFrame:
    """Deletes all entrieis from _df_ corresponding to the method-level 
    of the behavioral catalog

    https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.drop.html
    https://stackoverflow.com/a/61166760
    """
    # In the context of DataFrames index is synonymous with row
    # An index corresponds to a method-level if it does not end with "Total matches"
    columns_to_drop = [column for column in df if not column.endswith("Total matches") and column != "n_processes"]
    new_df = df.drop(columns_to_drop, axis=1) # {0 or ‘index’, 1 or ‘columns’}, default 0
    return new_df

def get_micro_objectives_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Drops (deletes) all the columns whose name contains a dot '.' therefore 
    remaining only with those corresponding to micro-objectives. Example:

    Micro-objective column: [OC0001] Filesystem
    Micro-behavior column (dropped): [OC0001] Filesystem.[C0049] Get File Attributes

    Returns a new copy of the modified DataFrame (inplace=False).
    """
    # In the context of DataFrames index is synonymous with row

    # If the row label contains more than zero dots, it means the label corresponds
    # to a micro_behavior level and therefore it must be dropped (i.e., [OC0001] Filesystem.[C0063] Move File)
    columns_to_drop = [column for column in df if column.count('.')]
    new_df = df.drop(columns_to_drop, axis=1)
    return new_df


def get_micro_behaviors_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Drops (deletes) all the columns whose name does not contain a dot '.' or
    corresponds to the "Spawned Processes" column, therefore remaining only with 
    those corresponding to micro-behaviors. Example:

    Micro-objective column (dropped): [OC0001] Filesystem
    Micro-behavior column: [OC0001] Filesystem.[C0049] Get File Attributes

    Returns a new copy of the modified DataFrame (inplace=False).
    """
    # In the context of DataFrames index is synonymous with row

    # If the row label does not contain dots and it is not "Spaned Processes",
    # it means the label corresponds to a micro_objective level and therefore it must be dropped (i.e., [OC0001] Filesystem)
    columns_to_drops = [column for column in df if not column.count('.') and column != "Spawned Processes"]
    new_df = df.drop(columns_to_drops, axis=1)
    return new_df

def normalize(df: pd.DataFrame, min: int = 0, max: int = 1, transpose:bool = False) -> pd.DataFrame:
    """Normalizes the values of the DataFrame _df_ in the given range [min, max].
    By default min is 0 and max is 1.

    Transpose is used to indicate whether to transpose de dataframe before normalizing it.
    Transposing it is useful when the normalization is done using the samples as base values
    instead of each micro-behavior. This is used when printing the figures of each category
    where we care about the min() and max() of each sample for the category, not the
    min() and max() of each micro-behavior (the latter sometimes results in divison by zero)
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

def generate_heatmap_per_micro_objective(df: pd.DataFrame, micro_objectives, title:str) -> None:
    for micro_objective in micro_objectives:
        micro_objective_df = [col for col in df if col.startswith(micro_objective)]
        micro_objective_df = df[micro_objective_df]
        generate_pdf_heatmap(micro_objective_df, title+" "+str(micro_objective), title+" "+str(micro_objective)+" heatmap.pdf")

def generate_radarchart_per_micro_objective(df: pd.DataFrame, micro_objectives, title:str) -> None:
    for micro_objective in micro_objectives:
        micro_objective_df = [col for col in df if col.startswith(micro_objective)]
        micro_objective_df = df[micro_objective_df]
        micro_objective_name_no_id = micro_objective[micro_objective.index(']')+1:].strip()
        #generate_pdf_radarchart(micro_objective_df, title+" "+str(micro_objective), title+" "+str(micro_objective)+" radar.pdf")
        generate_pdf_radarchart(micro_objective_df, title+"\n"+str(micro_objective_name_no_id)+" Micro-objective", title+" "+str(micro_objective_name_no_id)+" radar.pdf", micro_objective)

def generate_piechart_per_micro_objective(df: pd.DataFrame, micro_objectives, title:str) -> None:
    for micro_objective in micro_objectives:
        micro_objective_df = [col for col in df if col.startswith(micro_objective)]
        micro_objective_df = df[micro_objective_df]
        micro_objective_name_no_id = micro_objective[micro_objective.index(']')+1:].strip()
        generate_pdf_piechart(micro_objective_df, title+"\n"+str(micro_objective_name_no_id)+" Micro-objective", title+" "+str(micro_objective_name_no_id)+" pie.pdf", micro_objective)

def generate_barchart_per_micro_objective(df: pd.DataFrame, micro_objectives, title:str) -> None:
     for micro_objective in micro_objectives:
        micro_objective_df = [col for col in df if col.startswith(micro_objective)]
        micro_objective_df = df[micro_objective_df]
        micro_objective_name_no_id = micro_objective[micro_objective.index(']')+1:].strip()
        #figure_title = title+"\n"+str(micro_objective_name_no_id)+" Micro-objective"
        figure_title = title
        generate_pdf_barchart(micro_objective_df, figure_title, title+" "+str(micro_objective_name_no_id)+".pdf", micro_objective)

def generate_broken_barchart_per_micro_objective(df: pd.DataFrame, micro_objectives, title:str) -> None:
    for micro_objective in micro_objectives:
        micro_objective_df = [col for col in df if col.startswith(micro_objective)]
        micro_objective_df = df[micro_objective_df]
        micro_objective_name_no_id = micro_objective[micro_objective.index(']')+1:].strip()
        #figure_title = title+"\n"+str(micro_objective_name_no_id)+" Micro-objective"
        figure_title = title
        generate_pdf_broken_barchart(micro_objective_df, figure_title, title+" "+str(micro_objective_name_no_id)+".pdf", micro_objective)

def clip_data(df: pd.DataFrame, quantile:int = 0.9) -> pd.DataFrame:
    """
    Clips data (only upper threshold) according to the value in the 0.9 quantile
    of the __df__ DataFrame. The midpoint technique is used for interpolation.
    """
    return df.clip(upper=df.quantile(0.9, interpolation='midpoint'), axis='columns', inplace=False)

def correct_execution(df: pd.DataFrame) -> bool:
    """
    Determines whether the _df_ DataFrame corresponds to a **correct execution**. 
    In this context, a **correct execution** is one that ended successfully, 
    regardless of the actual sample detonating or not.

    To consider an execution correct, we check how many times it matched with none of our behavioral
    patterns. In other words, if the sample has 0 matches with 90% or more of our micro-objectives 
    and micro-behaviors, we discard it. In yet another words, we check whether the value 0 appears
    in 90% of the columns of the DataFrame or more.
    """
    return dataframe.T.value_counts()[0] < len(dataframe.columns)*0.90

def get_tonal_colors(values_to_color: list) -> list:
    """
    Returns a list comprising the tonal color values corresponding to each value from __values_to_color__
    """
    color_list = []
    for value in values_to_color:
        if value not in behavior_catalog_tonal_colormap:
            color_list.append("#FFFFFF")
        else:
            color_list.append(behavior_catalog_tonal_colormap[value])
    return color_list

def get_basic_colors(values_to_color: list) -> list:
    """
    Returns a list comprising the basic color values corresponding to each value from __values_to_color__
    """
    color_list = []
    for value in values_to_color:
        if value not in behavior_catalog_basic_colormap:
            color_list.append("#FFFFFF")
        else:
            color_list.append(behavior_catalog_basic_colormap[value])
    return color_list

def get_hatches(values_to_hatch: list) -> list:
    """
    Returns a list comprising the hatch patterns corresponding to each value from __values_to_hatch__
    """
    hatch_list = []
    for value in values_to_hatch:
        if value not in behavior_catalog_hatchmap:
            hatch_list.append("")
        else:
            hatch_list.append(behavior_catalog_hatchmap[value])
    return hatch_list    

def generate_pdf_heatmap(df: pd.DataFrame, fig_title: str, fig_name: str, fig_type: str = "", categories = None) -> None:
    figure_width = 0.5 * len(df.index) # inches for each sample (width)
    figure_height = 0.5 * len(df.columns) # inches for each micro(objective/behavior) (height)
    plt.figure(figsize = (figure_width, figure_height))
    match fig_type:
        case "spawned_processes":
            df = df['Spawned Processes']
            df = np.asarray([df]) # Heatmap requires 2D dimensional array https://stackoverflow.com/questions/57888688/inconsistent-shape-between-the-condition-and-the-input-while-using-seaborn#comment102199104_57888688
            figure = sns.heatmap(df, square=True, annot=True, annot_kws={'size': 9}, cbar_kws={'shrink': .5}, fmt='d', cbar=False, cmap="rocket", vmin=0, vmax=25)
            plt.tick_params(axis='both', which='major', labelsize=6, labelbottom=False, labelleft=False, bottom=False, left=False, top=False)# https://stackoverflow.com/a/53304154
            #plt.tick_params(left=False, bottom=False, labelbottom=False, labelleft=False)
            plt.title(fig_title, fontsize=13)
            figure = figure.get_figure()
            figure.savefig(fig_name, bbox_inches="tight") #https://stackoverflow.com/a/49201252
            plt.close()
            return
        case "micro-behavior":
            horizontal_lines_indexes = list()
            actual_index = 0
            for category in categories:
                actual_index += sum(category in s for s in df.columns)
                horizontal_lines_indexes.append(actual_index)
            horizontal_lines_indexes = horizontal_lines_indexes[:-1]
            df = normalize(df, 0, 100)
        case "micro-objective":
            df = normalize(df, 0, 100)
        case _: #_ is the default case
            df = normalize(df, 0, 100)
    
    #### ATTENTION!!! df is transposed before drawing it!
    figure = sns.heatmap(df.T, square=True, annot=True, annot_kws={'size': 5}, cbar_kws={'shrink': .5}, fmt='.3f', cbar=True, cmap="magma")
    if fig_type == "micro-behavior":
        ax = figure.axes
        #breakpoint()
        ax.hlines(horizontal_lines_indexes, *ax.get_xlim(), color="Red")
    plt.tick_params(axis='both', which='major', labelsize=6, labelbottom=True, bottom=True, left=True, top=False)# https://stackoverflow.com/a/53304154
    plt.title(fig_title, fontsize=16)
    plt.xlabel("Sample", fontsize=8)
    plt.ylabel("Behavior", fontsize=8)
    figure = figure.get_figure()
    figure.savefig(fig_name, bbox_inches="tight") #https://stackoverflow.com/a/49201252
    plt.close()

def generate_pdf_radarchart(df: pd.DataFrame, fig_title: str, fig_name: str, micro_objective: str = None) -> None:
    normalized_df = normalize(df, 0 ,100)
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
    N = len(categories)
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
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
    plt.yticks([0,10,20,30,40,50], ["0%","10%","20%","30%","40%","50%"], color="black", size=8)
    #plt.ylim(0,50)
    plt.ylim(0,40) # ad-hoc example for Alina
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
        tick.set_pad(radarchart_padding[tick.label1.get_text()])

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

def generate_pdf_nestedpie(df: pd.DataFrame, fig_title: str, fig_name: str) -> None:
    """

    Inspired by: https://stackoverflow.com/a/67221817
    """

    # Delete the columns whose value is 0
    df = df[df.value != 0]

    outer_ring = df.groupby('Micro Objective').sum()
    inner_ring = df.groupby(['Micro Objective', 'Micro Behavior']).sum()

    # Create a nested pie chart
    fig, ax = plt.subplots(figsize=(15,15))
    size = 0.3

    # Outer ring
    outer_colors = get_basic_colors(outer_ring.index)
    # More info about returne valued by ax.pie: https://matplotlib.org/3.1.1/api/_as_gen/matplotlib.axes.Axes.pie.html
    outer_patches, outer_texts, outer_autotexts = ax.pie(outer_ring.values.flatten(), radius=1,
        #labels = outer_ring.index,
        autopct='%.3f',
        pctdistance=1.05,
        textprops=dict(weight='bold'),
        wedgeprops=dict(width=size, edgecolor='w'),
        colors=outer_colors)

    # Centering outer texts and outer numeric valuesfor patch, text in zip(inner_patches, inner_texts):
        #mang =(patch.theta1 + patch.theta2)/2.  # get mean_angle of the wedge
        ##print(mang, text.get_rotation())
        #text.set_rotation(mang)         # rotate the label by (mean_angle + 270)
        #text.set_va("center")
        #text.set_ha("center")
    #for number in outer_autotexts:
        #number.set_horizontalalignment('center')
        #number.set_verticalalignment('top')

    # Innter ring
    inner_labels = inner_ring.index.get_level_values(1)
    inner_colors = get_baisc_colors(inner_labels)
    inner_patches, inner_texts, inner_autotexts = ax.pie(inner_ring.values.flatten(), radius=1-size,
        labels = inner_labels,
        autopct='%.3f',
        pctdistance=0.75,
        labeldistance=1.05,
        rotatelabels=True,
        textprops=dict(fontsize=8),
        wedgeprops=dict(width=size, edgecolor='w'),
        colors=inner_colors)

    # Rotating labels: https://stackoverflow.com/a/50237578 
    #for patch, text in zip(inner_patches, inner_texts):
        #mang =(patch.theta1 + patch.theta2)/2.  # get mean_angle of the wedge
        ##print(mang, text.get_rotation())
        #text.set_rotation(mang)         # rotate the label by (mean_angle + 270)
        #text.set_va("center")
        #text.set_ha("center")

    # Centering inner texts and inner numeric values
    #for text in inner_texts:
        #text.set_horizontalalignment('center')
    #for number in inner_autotexts:
        #number.set_horizontalalignment('center')
        #number.set_verticalalignment('bottom')

    ax.set(aspect="equal")

    ax.legend(outer_ring.index, title="Micro Objectives")

    plt.title(fig_title, fontsize=13)
    
    # Add legend
    #plt.legend( bbox_to_anchor=(0.1, 0.1), fontsize='small')

    # Show the graph
    plt.savefig(fig_name, format="pdf", bbox_inches="tight")
    plt.close() # So data does not get mixed up

#def generate_pdf_piechart(values: list, colors: list, fig_title: str, fig_name: str, legend_title: str) -> None:
def generate_pdf_piechart(df: pd.DataFrame, fig_title: str, fig_name: str, micro_objective: str = None) -> None:
    # If the sum of every value in the DataFrame is 0, it means there is no
    # micro behavior from this micro objective present during the execution
    # In such case, exit the function because there is nothing to draw
    if df.sum().sum() == 0.0:
        return
   
    # Normalize data
    normalized_df = normalize(df, 0, 100)
    # Get the mean
    mean_df = normalized_df.mean()
    # Delete the columns whose value is 0
    mean_df = mean_df[mean_df.values != 0]
    #Transform data into percentage
    mean_df = (100. * mean_df / mean_df.sum()).round(2)

    # Obtain the biggest value in the list so it can be exploded in the pie chart
    # Given that mean_df.values is a np.array, instead of using max() and index() functions (for python lists)
    # np.argmax()can be used
    biggest_value_index = np.argmax(mean_df.values)
   
    hatch = None
    #breakpoint()
    if micro_objective is None:
        #color = get_tonal_colors(mean_df.index)
        color = get_basic_colors(mean_df.index)
        explode = None
        legend_title = "Micro Objectives"
        #hatch = get_hatches(mean_df.index)
    else:
        # Rename indexes by deleting their category
        for index_name in mean_df.index:
            mean_df.rename(index={f"{index_name}":index_name.removeprefix(micro_objective+".")}, inplace=True) # Python +3.9 https://stackoverflow.com/a/1038845
        #color = get_tonal_colors(mean_df.index)
        color = get_basic_colors(mean_df.index)
        #color = [behavior_catalog_colormap[micro_objective]] * len(df.index) # Repeat same color for each slice
        explode = [0.0] * len(mean_df.index)
        #breakpoint()
        explode[biggest_value_index] = 0.1
        #hatch = None
        legend_title = "Micro Behaviors"

    #hatch = get_hatches(mean_df.index)

    # Delete the ID
    labels = [index[index.index(']')+1:].strip() for index in mean_df.index] 
    
    patches, texts, autotexts = plt.pie(mean_df.values, radius=1,
        #labels = labels,
        autopct='%1.2f%%',
        explode=explode,
        labeldistance=1.05,
        #pctdistance=1.05,
        #textprops=dict(weight='bold'),
        textprops=dict(size=7),
        #wedgeprops=dict(width=size, edgecolor='w'),
        #height=1,
        #bottom=3,
        wedgeprops=dict(edgecolor='w'),
        colors=color,
        hatch=hatch,
        )

    # Apply a different edgecolor to the slice corresponding to the biggest value (the exploded one)
    # Only for micro-behaviors
    if micro_objective is not None:
        #patches[biggest_value_index].set_edgecolor('black')
        #patches[biggest_value_index].set_hatchcolor('white')
        patches[biggest_value_index].set_path_effects([PathEffects.Stroke(linewidth=1, foreground='black')])


    # Now that hatches are active, set the value color to white to improve readability
    # Only for micro-behaviors
    #if micro_objective is not None:
    #if micro_objective is None:
        #for autotext in autotexts:
            #autotext.set_color('white')
            #autotext.set_antialiased(True)
            #autotext.set_weight('bold')
            #autotext.zorder = 2
            ##autotext.set_fontsize(8)
            ##https://matplotlib.org/stable/api/patheffects_api.html#matplotlib.patheffects.Stroke
            #autotext.set_path_effects([PathEffects.withStroke(linewidth=2, foreground='black')])

    # Set 
    #breakpoint()

    # Add legend
    plt.legend(labels, title=legend_title, loc="center", fontsize='small', ncols=2, bbox_to_anchor = (.5, -.1))

    if micro_objective:
        plt.title(micro_objective[micro_objective.index(']')+1:].strip(), fontsize=13)
    else :
        plt.title(fig_title, fontsize=13)

    # Show the graph
    plt.savefig(fig_name, format="pdf", bbox_inches="tight")
    plt.close() # So data does not get mixed up

def generate_pdf_barchart(df: pd.DataFrame, fig_title: str, fig_name: str, micro_objective: str = None) -> None:

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

    #hatch = get_hatches(mean_df.index)

    # Delete the ID and replace space with newline
    #labels = [index[index.index(']')+1:].strip().replace(" ","\n") for index in mean_df.index] 
    labels = [index[index.index(']')+1:].strip() for index in mean_df.index]
    #breakpoint()
    #colors = get_basic_colors(mean_df.index)

    #fig, ax = plt.subplots()
    #plt.bar(mean_df.index, mean_df.values, label=labels, color=colors)
    #ax = mean_df.plot(xticks=[], kind='bar', stacked=False, color=colors)
    #breakpoint()
    bar = plt.bar(labels, mean_df.values, label=labels, color=colors)
    plt.yticks([0, 25, 50, 75, 100])
    plt.bar_label(bar, label_type='edge', fmt='%.2f%%', size=6) # Converts 0 into 0.00
    
    #plt.bar_label(bar, label_type='edge')
    
    # Rotate labels https://stackoverflow.com/a/37708190
    #plt.xticks(rotation=90)
    
    # Hide labels https://stackoverflow.com/a/40860688
    plt.xticks([])

    # Add legend and title
    #plt.title(micro_objective[micro_objective.index(']')+1:].strip(), fontsize=13)
    plt.title(fig_title, fontsize=13)
    #breakpoint()
    plt.legend(labels, title=legend_title, loc="center", fontsize='small', ncols=2, bbox_to_anchor = (.5, -.15))
    #ax.legend(handles=labels)

    # Show the graph
    plt.savefig(fig_name, format="pdf", bbox_inches="tight")
    plt.close() # So data does not get mixed up

# Broken-axis figure, genereted ad-hoc for Alina samples
def generate_pdf_broken_barchart(df: pd.DataFrame, fig_title: str, fig_name: str, micro_objective: str = None) -> None:

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

        if label in abbreviation_map:
            labels[i] = label + f" ({abbreviation_map[label]})"
            # Fix typo on the fly
            if label == "Create or Open file":
                labels[i] = labels[i].replace("file", "File")
            xtick_labels.append(abbreviation_map[label])
        else:
            xtick_labels.append(labels[i])

    # Broken Axis figure: https://matplotlib.org/stable/gallery/subplots_axes_and_figures/broken_axis.html
    fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, height_ratios=[.1, .9]) # Upper part 30% of the size of the figure
    fig.subplots_adjust(hspace=.1)  # adjust space between axes

    # ax1 is the upper part of the figure, ax2 is the lower one
    ax1bar = ax1.bar(xtick_labels, mean_df.values, label=xtick_labels, color=colors)
    ax2bar = ax2.bar(xtick_labels, mean_df.values, label=xtick_labels, color=colors)

    # Upper-part of the figure limit:
    ax1.set_ylim(90, 100)

    # Lower-part of the figure limit:
    if micro_objective in ["[OC0001] Filesystem","[OC0003] Process"]:
        ax2.set_ylim(0, 20)
        y_bbox_to_anchor = -.20
    else:
        ax2.set_ylim(0, 55)
        y_bbox_to_anchor = -.10

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
    kwargs = dict(marker=[(-1, -d), (1, d)], markersize=12,
                  linestyle="none", color='k', mec='k', mew=1, clip_on=False)
    ax1.plot([0, 1], [0, 0], transform=ax1.transAxes, **kwargs)
    ax2.plot([0, 1], [1, 1], transform=ax2.transAxes, **kwargs)
    
    
    #bar = plt.bar(labels, mean_df.values, label=labels, color=colors)
    #plt.yticks([0, 25, 50, 75, 100])
    
    ax1.bar_label(ax1bar, label_type='edge', fmt='%.2f%%', size=9, weight='bold') # Converts 0 into 0.00
    ax2.bar_label(ax2bar, label_type='edge', fmt='%.2f%%', size=9, weight='bold')

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
    plt.title(fig_title, fontsize=17)
    ncols = 2 if len(labels) >= 4 else 3
    plt.legend(labels, title=legend_title, loc="upper center", fontsize='small', ncols=ncols, bbox_to_anchor = (.5, -.07), prop={'size': 10})
    #ax.legend(handles=labels)

    # Show the graph
    plt.savefig(fig_name, format="pdf", bbox_inches="tight")
    plt.close() # So data does not get mixed up

def generate_pdf_stackedbars(df: pd.DataFrame, fig_title: str, fig_name: str) -> None:
    # Pivot the DataFrame
    df_pivot = df.pivot(index='Micro Objective', columns='Micro Behavior', values='value')
    #breakpoint()
    colors = get_basic_colors(df_pivot.columns)

    # Remove IDs both from index (micro-behaviors) and columns (micro-objective)
    for index_name in df_pivot.index:
        df_pivot.rename(index={f"{index_name}":index_name[index_name.index(']')+1:].strip()}, inplace=True) # Python +3.9 https://stackoverflow.com/a/1038845
    for column_name in df_pivot.columns:
        df_pivot.rename(columns={f"{column_name}":column_name[column_name.index(']')+1:].strip()}, inplace=True)

    # Plot the stacked bar chart
    ax = df_pivot.plot(kind='bar', stacked=True, color=colors, yticks=[0, 25, 50, 75, 100])

    # Customize the plot
    ax.set_ylabel('Matches')
    ax.set_xlabel('Micro Objective')
    ax.set_title('Stacked Bar Plot by Subcategory')

    plt.title(fig_title, fontsize=13)

    # Show the graph
    #plt.legend(bbox_to_anchor=(1.05, 1.0), loc='upper left', fontsize='small', title='Micro Behavior')
    plt.legend().remove()
    plt.savefig(fig_name, format="pdf", bbox_inches="tight")
    plt.close() # So data does not get mixed up

def main():

    json_files = list()

    # Collect all JSON files
    for file_path in arguments.json:
        if path.isfile(file_path):
            json_files.append(file_path)
        elif path.isdir(file_path):
            json_files.extend(glob.glob(file_path+"/*.json"))

    dataframe_list = list()

    # Read all JSON files, in case the user passed a directory
    sample_nr = 1
    discarded = 0
    for json_file in json_files:
        with open(json_file) as f:
            data = json.load(f)
            dataframe = pd.json_normalize(data)
            if not correct_execution(dataframe):
                logger.info(f"[+] Discarded file {json_file}")
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
    
    # Concatenate the different DataFrames generated from the JSON files
    df = pd.concat(dataframe_list)
    # Call needed to make indexes incremental. Otherwise, they're all zeroes
    # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.reset_index.html
    df.reset_index(inplace=True, drop=True)
    df.index += 1 #To start at 1, not at 0 https://stackoverflow.com/a/20168416

    # Transpose: df.T  # or df1.transpose()
    # Transpose the dataframe so columns correspond to each sample
    # At this point df contains all the information, at all 3 levels (micro-objective, micro-behavior and method)
    
    #df.to_csv("test_csv.csv")
    #df = normalize(df, 0, 100)

    df_dropped = drop_methods_indexes(df)
    rename_indexes(df_dropped)

    title = arguments.fig_title if arguments.fig_title else ""

    micro_objectives_df = get_micro_objectives_dataframe(df_dropped)
    generate_pdf_heatmap(micro_objectives_df, title, title + " spawned_processes.pdf", "spawned_processes")
    df_dropped = df_dropped.drop("Spawned Processes", axis=1) # After creating the figure, the column Spawned Processes is no longer of use

    micro_objectives_df = micro_objectives_df.drop("Spawned Processes", axis=1)
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
    generate_broken_barchart_per_micro_objective(micro_behaviors_df, micro_objective_names, title)
    
    ############ PIECHART ############
    #generate_pdf_piechart(micro_objectives_df, title, title+"piechart.pdf")
    #generate_piechart_per_micro_objective(micro_behaviors_df, micro_objective_names, title)

    ############ HEATMAP ############
    #generate_pdf_heatmap(micro_behaviors_df, title, "micro_behavior.pdf", "micro-behavior", micro_objective_names)
    #generate_heatmap_per_micro_objective(micro_behaviors_df, micro_objective_names, title)
    
    ############ RADARCHART ############
    generate_pdf_radarchart(micro_objectives_df, title, title+" Micro-Objectives.pdf")
    #generate_pdf_radarchart(micro_behaviors_df, title, "micro_behavior_spider.pdf")
    #generate_radarchart_per_micro_objective(micro_behaviors_df, micro_objective_names, title)

    """
    match arguments.level:
        case "micro-objective":
            micro_objective_df = get_micro_objective_dataframe(df_dropped)
            generate_pdf_heatmap(micro_objective_df, title, "micro_objective.pdf", "micro-objective")
        case "micro-behavior":
            micro_behavior_df = get_micro_behavior_dataframe(df_dropped)
            generate_pdf_heatmap(micro_behavior_df, title, "micro_behavior.pdf", "micro-behavior")
    """


if __name__ == "__main__":
    arguments = parse_arguments()
    logging.basicConfig(level=logging.INFO, format="%(name)s (%(asctime)s) %(levelname)s - %(message)s")
    logger = logging.getLogger("MalGraphIQ (Plotting)")
    if arguments.quiet:
        logger.setLevel(logging.ERROR)
    elif arguments.silent:
        # Turn off the logger
        logger.setLevel(logging.CRITICAL + 1)               