"""
First phase. Transforms a JSON report generated with CAPE [1] (for now) into transition matrices and behavior and category graphs.

[1]: https://github.com/kevoreilly/CAPEv2
"""

from .transition_matrix_and_graphs import main as transition_matrix_and_graphs
