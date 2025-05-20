import argparse
import logging
import sys

# Import each phase
import graphs
import occurrences
import plotting


def parse_arguments() -> argparse.Namespace:
    """
    Parse and combine arguments required by all phases.

    Returns:
        argparse.Namespace: Parsed arguments.
    """
    parser = argparse.ArgumentParser(
        prog="MalGraphIQ",
        description="Executes MalGraphIQ either in individual phases or the whole workflow: Transition Matrices and Graphs -> Behavioral Patterns -> Plotting."
    )

    group = parser.add_mutually_exclusive_group()
    group.add_argument("-q", "--quiet", action="store_true",
        help="Only error and critical messages are printed.")
    group.add_argument("-s", "--silent", action="store_true",
        help="Nothing is printed.")
    subparsers = parser.add_subparsers(dest='phase', required=True, 
        help="Specify the phase to run.")

    # Arguments for transition_matrix_and_graphs
    parser_transition = subparsers.add_parser("graphs", 
        help="Transition Matrices and Graphs phase. Renders CAPE reports and transforms them into transition matrices and different graphs (visualizations). By default generates both behavior and category transition matrices and graphs.")
    parser_transition.add_argument("json_dir", 
        help="A .json report o a directory containing one or more JSON reports. If the parameter is a directory, the program automatically parses all .JSON files within it.")
    parser_transition.add_argument("-o", "--output", default="./MATRICES_GRAPHS/", 
        help="Output folder (default: %(default)s).")
    parser_transition.add_argument("-w", "--winapi_categories", default="./winapi_categories.json", help="Path to winapi_categories.json file (as obtained from https://github.com/reverseame/winapi-categories). By default the program will look into the current working directory. If the file does not exist, the program will attempt to download it unless -nd/--no-download is specified. (default: %(default)s).")
    parser_transition.add_argument("-nd", "--no_download", action="store_true", 
        help=f"Prevents {parser.prog} from downloading winapi_categories.json. By default it attempts to download it in the -w/--winapi-categories specified path.")
    parser_transition.add_argument("-pp", "--print_transition_probabilities", action="store_true", help="Print transition probabilities on behavior and category graphs (default: %(default)s).")

    group = parser_transition.add_mutually_exclusive_group()
    group.add_argument(
        "-c", "--category",
        action="store_true",
        help="Generate only the category graph(s)."
    )
    group.add_argument(
        "-b", "--behavior",
        action="store_true",
        help="Generate only the behavior graph(s)."
    )

    # Arguments for behavioral_pattern_occurrences
    parser_behavior = subparsers.add_parser("occurrences", 
        help="Behavior Pattern Occurrences phase. Generates the occurrences of each pattern from the Windows Behavior Catalog (WBC) against the specified graph/s. WBC patterns are identified in the specified graph/s using a backtracking algorithm.")
    parser_behavior.add_argument("behavior_graph", 
        help="A behavior .gv file directory or list of directories containing .gv files in which patterns will be sought. In the second and third case, the program automatically parses all the .gv files contained in each directory.")
    parser_behavior.add_argument("-c", "--catalog", required=True, type=str, 
        help="Path to the Windows Behavior Catalog (WBC) in JSON format. See https://github.com/reverseame/windows-behavior-catalog.")
    parser_behavior.add_argument("-m", "--max_inter_nodes", type=int, default=0, 
        help="Max intermediate nodes from the behavior graph allowed between each pattern node (default: %(default)s).")
    parser_behavior.add_argument("-p", "--prob_threshold", type=float, default=0.0, 
        help="Probability threshold (default: %(default)s). Paths below the threshold are discarded.")
    parser_behavior.add_argument("-l", "--pattern_min_length", type=int, default=1, 
        help="Minimum pattern length, measured in number of nodes (default: %(default)s).")
    parser_behavior.add_argument("-jf", "--json_output_file", type=str,
        help="Custom output JSON file for results (default: pattern_results_{asctime}.json).")

    # Arguments for plot_catalog_matches
    parser_plot = subparsers.add_parser("plots", 
        help="Plot Catalog Matches phase. Plots the Micro-Objective and Micro-Behavior occurrences from the previous phase. You can find code for other type of visualizations in additional_code.py.")
    parser_plot.add_argument("json", 
        help="JSON file or directory of matches, or a list of match dictionaries, as produced by the previous phase.")
    parser_plot.add_argument("--fig_title", 
        help="Title for the generated plots (default: none).")
    parser_plot.add_argument("-rc_max", "--radarchart_max_scale", type=int, default=100, choices=range(0, 101), metavar="[0-100]", 
        help="Max scale for radarcharts (default: %(default)s).")
    parser_plot.add_argument("--match_plots_dir", type=str, default="./PLOTS/",
        help="If specified, WBC matches plots are written in that directory otherwise they are generated in the PLOTS folder, which is created if it does not exist (default: %(default)s).")
    parser_plot.add_argument("-bb", "--broken_barcharts", action="store_true", 
        help="Use broken barcharts. That is, break the Y-axis of the micro-behavior occurrences visualizations (default: %(default)s).")
    parser_plot.add_argument("--lower_figure_limit", type=int, default=50, choices=range(0, 101), metavar="[0-100]", 
        help="Specifies the upper limit of the lower half of the broken figure (default: %(default)s).")
    parser_plot.add_argument("--upper_figure_limit", type=int, default=50, choices=range(0, 101), metavar="[0-100]", 
        help="Specifies the lower limit of the upper half of the broken figure (default: %(default)s).")
    parser_plot.add_argument("--lower_figure_ratio", type=int, default=50, choices=range(10, 91), metavar="[10-90]", 
        help="Ratio (w.r.t total figure's height) of lower figure for broken barcharts. The upper figure ratio is 100 - the specified value. That is, the remaining space within the plot (default: %(default)s).")

    # Arguments for the "all" phase
    parser_all = subparsers.add_parser("all", 
        help="Run all phases sequentially.")

    # Transition matrices and graphs phase
    parser_all.add_argument("json_dir", 
        help="A .json report o a directory containing one or more JSON reports. If the parameter is a directory, the program automatically parses all .JSON files within it.")
    parser_all.add_argument("-o", "--output", default="./MATRICES_GRAPHS/", 
        help="Output folder (default: %(default)s).")
    parser_all.add_argument("-w", "--winapi_categories", default="./winapi_categories.json", 
        help="Path to winapi_categories.json file (as obtained from https://github.com/reverseame/winapi-categories). By default the program will look into the current working directory. If the file does not exist, the program will attempt to download it unless -nd/--no-download is specified. (default: %(default)s).")
    parser_all.add_argument("-nd", "--no_download", action="store_true", 
        help=f"Prevents {parser.prog} from downloading winapi_categories.json. By default it attempts to download it in the -w/--winapi-categories specified path.")
    parser_all.add_argument("-pp", "--print_transition_probabilities", action="store_true", 
        help="Print transition probabilities on behavior and category graphs (default: %(default)s).")

    group = parser_all.add_mutually_exclusive_group()
    group.add_argument(
        "--category",
        action="store_true",
        help="Generate only the category graph(s)."
    )
    group.add_argument(
        "--behavior",
        action="store_true",
        help="Generate only the behavior graph(s)."
    )

    # WBC occurrences phase
    parser_all.add_argument("-c", "--catalog", required=True, type=str, 
        help="Path to the Windows Behavior Catalog (WBC) in JSON format. See https://github.com/reverseame/windows-behavior-catalog.")
    parser_all.add_argument("-m", "--max_inter_nodes", type=int, default=0, 
        help="Max intermediate nodes from the behavior graph allowed between each pattern node (default: %(default)s).")
    parser_all.add_argument("-p", "--prob_threshold", type=float, default=0.0, 
        help="Probability threshold (default: %(default)s). Paths below the threshold are discarded.")
    parser_all.add_argument("-l", "--pattern_min_length", type=int, default=1, 
        help="Minimum pattern length, measured in number of nodes (default: %(default)s).")
    parser_all.add_argument("-jf", "--json_output_file", type=str,
        help="Custom output JSON file for results (default: pattern_results_{asctime}.json).")

    # Plotting phase
    parser_all.add_argument("--fig_title", 
        help="Title for the generated plots (default: none).")
    parser_all.add_argument("-rc_max", "--radarchart_max_scale", type=int, default=100, choices=range(0, 101), metavar="[0-100]", 
        help="Max scale for radarcharts (default: %(default)s).")
    parser_all.add_argument("--match_plots_dir", type=str, default="./PLOTS/",
        help="If specified, WBC matches plots are written in that directory otherwise they are generated in the PLOTS folder, which is created if it does not exist (default: %(default)s).")
    parser_all.add_argument("-bb", "--broken_barcharts", action="store_true", 
        help="Use broken barcharts. That is, break the Y-axis of the micro-behavior occurrences visualizations (default: %(default)s).")
    parser_all.add_argument("--lower_figure_limit", type=int, default=50, choices=range(0, 101), metavar="[0-100]", 
        help="Specifies the upper limit of the lower half of the broken figure (default: %(default)s).")
    parser_all.add_argument("--upper_figure_limit", type=int, default=50, choices=range(0, 101), metavar="[0-100]", 
        help="Specifies the lower limit of the upper half of the broken figure (default: %(default)s).")
    parser_all.add_argument("--lower_figure_ratio", type=int, default=50, choices=range(10, 91), metavar="[10-90]", 
        help="Ratio (w.r.t total figure's height) of lower figure for broken barcharts. The upper figure ratio is 100 - the specified value. That is, the remaining space within the plot (default: %(default)s).")

    return parser.parse_args()


def main() -> int:
    """
    Entry point for the MalGraphIQ program. Executes different phases based on user input.

    Returns:
        int: Exit code (0 for success).
    """
    args = parse_arguments()

    logging.basicConfig(level=logging.INFO, format="%(name)s (%(asctime)s) %(levelname)s - %(message)s")
    logger = logging.getLogger("MalGraphIQ")
    if args.quiet:
        logger.setLevel(logging.ERROR)
    elif args.silent:
        # Turn off the logger
        logger.setLevel(logging.CRITICAL + 1)

    if args.phase == "graphs":
        logger.info("[+] MalGraphIQ - Starting graphs phase [+]")

        graphs_to_generate = None
        if args.category:
            graphs_to_generate = 'category'
        elif args.behavior:
            graphs_to_generate = 'behavior'

        graphs.transition_matrix_and_graphs(
            args.json_dir,
            args.output,
            graphs_to_generate,
            args.winapi_categories,
            args.no_download,
            args.print_transition_probabilities,
            logger
        )
        logger.info("[+] MalGraphIQ - Finishing graphs phase [+]")
    elif args.phase == "occurrences":
        logger.info("[*] MalGraphIQ - Starting occurrences phase [*]")
        occurrences.behavioral_pattern_occurrences(
            args.behavior_graph,
            args.catalog,
            args.json_output_file,
            args.max_inter_nodes,
            args.prob_threshold,
            args.pattern_min_length,
            logger
        )
        logger.info("[*] MalGraphIQ - Finishing occurrences phase [*]")
    elif args.phase == "plots":
        plotting.plot_catalog_matches(
            args.json,
            args.fig_title,
            args.radarchart_max_scale,
            args.match_plots_dir,
            args.broken_barcharts,
            args.lower_figure_limit,
            args.upper_figure_limit,
            args.lower_figure_ratio,
            logger
        )
    elif args.phase == "all":

        graphs_to_generate = None
        if args.category:
            graphs_to_generate = 'category'
        elif args.behavior:
            graphs_to_generate = 'behavior'

        logger.info("[+] MalGraphIQ - Starting all phases sequentially [+]")

        # Step 1: Graphs Phase
        logger.info("[+] Starting graphs phase [+]")
        generated_category_graph_paths = graphs.transition_matrix_and_graphs(
            args.json_dir,
            args.output,
            graphs_to_generate,
            args.winapi_categories,
            args.no_download,
            args.print_transition_probabilities,
            logger
        )
        logger.info("[+] Graphs phase completed [+]")

        if not generated_category_graph_paths:
            logger.info("[+] No category graphs generated. Exiting. [+]")
            return 0

        # Step 2: Occurrences Phase
        logger.info("[+] Starting occurrences phase [+]")
        wbc_occurrences_list = occurrences.behavioral_pattern_occurrences(
                generated_category_graph_paths,
                args.catalog,
                args.json_output_file,
                args.max_inter_nodes,
                args.prob_threshold,
                args.pattern_min_length,
                logger
            )
        logger.info("[+] Occurrences phase completed [+]")

        # Step 3: Plots Phase
        logger.info("[+] Starting plots phase [+]")
        plotting.plot_catalog_matches(
            wbc_occurrences_list,
            args.fig_title,
            args.radarchart_max_scale,
            args.match_plots_dir,
            args.broken_barcharts,
            args.lower_figure_limit,
            args.upper_figure_limit,
            args.lower_figure_ratio,
            logger
        )
        logger.info("[+] All phases completed successfully [+]")
    else:
        logger.error("Invalid phase specified.")
        sys.exit(1)
    return 0


if __name__ == "__main__":
    main()
