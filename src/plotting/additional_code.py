import pandas as pd
import matplotlib.pyplot as plt

def separate_micro_objectives_and_behaviors_by_mean(df: pd.DataFrame) -> pd.DataFrame:
    """Computes the mean of the __df__ dataframe and separates it into a DataFrame of the form:
    | Micro-Objective   | Micro-Behavior| Value |
    |                   |               |       |
    ...
    
    Returns the new DataFrame
    """
    # Initialize an empty list to store the new data
    new_data = []

    # Compute the mean of the incoming df and normalize the values
    local_df = normalize(df, 0, 100).mean() # Computing the mean of the normalizations
    #local_df = normalize(df.mean(), 0, 100) # Normalizing the means

    #Transform data into percentage
    local_df = (100. * local_df / local_df.sum()).round(2)

    # Iterate over rows in the original DataFrame
    for col, value in local_df.items():
        # Split the column name into category and subcategory
        micro_objective, micro_behavior = col.split('.')
        # Append a new row to the list with category, subcategory, and value
        new_data.append({'Micro Objective': micro_objective, 'Micro Behavior': micro_behavior, 'value': value})

    # Create a new DataFrame from the list
    new_df = pd.DataFrame(new_data)
    return new_df

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

def generate_heatmap_per_micro_objective(df: pd.DataFrame, micro_objectives, title:str) -> None:
    for micro_objective in micro_objectives:
        micro_objective_df = [col for col in df if col.startswith(micro_objective)]
        micro_objective_df = df[micro_objective_df]
        generate_pdf_heatmap(micro_objective_df, title+" "+str(micro_objective), title+" "+str(micro_objective)+" heatmap.pdf")

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

def generate_piechart_per_micro_objective(df: pd.DataFrame, micro_objectives, title:str) -> None:
    for micro_objective in micro_objectives:
        micro_objective_df = [col for col in df if col.startswith(micro_objective)]
        micro_objective_df = df[micro_objective_df]
        micro_objective_name_no_id = micro_objective[micro_objective.index(']')+1:].strip()
        generate_pdf_piechart(micro_objective_df, title+"\n"+str(micro_objective_name_no_id)+" Micro-objective", title+" "+str(micro_objective_name_no_id)+" pie.pdf", micro_objective)

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