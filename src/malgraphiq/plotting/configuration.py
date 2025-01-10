"""
Configuration settings for charts and visualizations.
"""

# Padding for radar chart labels
radarchart_padding = {
    "Filesystem":2,
    "Memory":0,
    "Operating\nSystem":15,
    "Cryptography":25,
    "Process":12,
    "Communication":30
}

# Abbreviation mapping for chart labels
abbreviation_map = {
    "Encryption Key":"EC",
    "Cryptographic Hash":"CH",
    "Encrypt Data":"ED",
    "Decrypt Data":"DD",
    "Get File Attributes":"GFA",
    "Read File":"RF",
    "Create or Open file":"COF",
    "Alter Filename Extension":"AFE",
    "Create Directory":"CD",
    "Copy File":"CF",
    "Delete File":"DF",
    "Move File":"MF",
    "Write File":"WF",
    "Create Thread":"CT",
    "Open Thread":"OT",
    "Enumerate Threads":"ET",
    "Process Enumeration":"PE",
    "Resume Thread":"RT",
    "Create Mutex":"CM",
    "Suspend Thread":"ST",
    "Create Process":"CP",
    "Open Process":"OP",
    "Check Mutex":"ChM",
}
