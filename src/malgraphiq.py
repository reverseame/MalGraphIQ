import argparse
import logging
import sys
from pathlib import Path

# Import each phase
import graphs
import occurrences
import plotting


def parse_arguments():
    """
    Parse and combine arguments required by all three phases.
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
    
    subparsers = parser.add_subparsers(dest='phase', required=True, help="Specify the phase to run.")

    # Arguments for transition_matrix_and_graphs
    parser_transition = subparsers.add_parser("graphs", help="Transition Matrix and Graphs phase. By default generates both behavior and category graphs.")
    parser_transition.add_argument("json_dir", help="Directory containing JSON reports.")
    parser_transition.add_argument("-o", "--output", default="REPORTS", help="Output folder.")
    parser_transition.add_argument("-w", "--winapi_categories", default="./winapi_categories.json", help="Path to winapi_categories.json.")
    parser_transition.add_argument("-nd", "--no_download", action="store_true", help="Disable downloading of winapi_categories.json.")
    parser_transition.add_argument("-pp", "--print_transition_probabilities", action="store_true", help="Print transition probabilities on graphs.")

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
    parser_behavior = subparsers.add_parser("occurrences", help="Behavior Pattern Occurrences phase.")
    parser_behavior.add_argument("behavior_graph", help="Behavior graph file or directory.")
    parser_behavior.add_argument("-c", "--catalog", required=True, help="Path to the behavior catalog JSON.")
    parser_behavior.add_argument("-m", "--max_inter_nodes", type=int, default=0, help="Max intermediate nodes allowed.")
    parser_behavior.add_argument("-p", "--prob_threshold", type=float, default=0.0, help="Probability threshold.")
    parser_behavior.add_argument("-l", "--pattern_min_length", type=int, default=1, help="Minimum pattern length.")
    parser_behavior.add_argument("-jf", "--json_output_file", help="Custom output JSON file for results.")

    # Arguments for plot_catalog_matches
    parser_plot = subparsers.add_parser("plots", help="Plot Catalog Matches phase.")
    parser_plot.add_argument("json", help="JSON file or directory of matches.")
    parser_plot.add_argument("--fig_title", help="Title of the generated figure.")
    parser_plot.add_argument("-rc_max", "--radarchart_max_scale", type=int, default=100, choices=range(0, 101), metavar="[0-100]", help="Max scale for radarcharts.")
    parser_plot.add_argument("--catalog_matches_plot_dir", help="Directory for plot outputs.")
    parser_plot.add_argument("-bb", "--broken_barcharts", action="store_true", help="Use broken barcharts.")
    parser_plot.add_argument("--lower_figure_limit", type=int, default=50, choices=range(0, 101), metavar="[0-100]", help="Lower limit for broken barcharts.")
    parser_plot.add_argument("--upper_figure_limit", type=int, default=50, choices=range(0, 101), metavar="[0-100]", help="Upper limit for broken barcharts.")
    parser_plot.add_argument("--lower_figure_ratio", type=int, default=50, choices=range(10, 91), metavar="[10-90]", help="Ratio of lower figure for broken barcharts.")

    return parser.parse_args()


def main():
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
            args.fig_title or "",
            args.radarchart_max_scale,
            args.catalog_matches_plot_dir,
            args.broken_barcharts,
            args.lower_figure_limit,
            args.upper_figure_limit,
            args.lower_figure_ratio,
            logger
        )
    else:
        logger.error("Invalid phase specified.")
        sys.exit(1)


if __name__ == "__main__":
    main()
