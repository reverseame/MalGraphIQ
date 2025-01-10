"""
Second phase. Matches the patterns defined in the Windows Behavior Catalog (WBC) [1] against the specified graphs.

[1]: https://github.com/reverseame/windows-behavior-catalog
"""
from .behavioral_pattern_occurrences import main as behavioral_pattern_occurrences
