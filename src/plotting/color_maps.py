'''
File containing several maps used to color or give texture to charts.
'''

# https://colordesigner.io/color-scheme-builder
behavior_catalog_tonal_colormap = {
    "[OC0001] Filesystem" : "#3498db", #Blue
        "[C0049] Get File Attributes":"#4a9ede",
        "[C0051] Read File":"#6dace3",
        "[C0016X] Create or Open file":"#82b6e6",
        "[C0015] Alter Filename Extension":"#96c0ea",
        "[C0046] Create Directory":"#a9caed",
        "[C0045] Copy File":"#bbd4f1",
        "[C0047] Delete File":"#0f88ca",
        "[C0063] Move File":"#d3d9ff",
        "[C0052] Write File":"#006aa9",
    "[OC0005] Cryptography" : "#2ecc71", #Green
        "[C0028] Encryption Key":"#50d27e",
        "[C0027] Encrypt Data":"#6ad78c",
        "[C0029] Cryptographic Hash":"#00b75d",
        "[C0031] Decrypt Data":"#00a34b",
    "[OC0006] Communication" : "#e67e22", #Orange
        "[C0001] Socket Communication":"#ed8b3c",
        "[C0005] WinINet Communication":"#f29752",
        "[C0002] HTTP Communication":"#f6a467",
    "[OC0002] Memory" : "#9b59b6", #Purple
        "[C0007] Allocate Memory":"#a669bd",
        "[C0008] Change Memory Protection":"#b079c5",
    "[OC0003] Process" : "#e74c3c", #Red
        "[C0038] Create Thread":"#ed624e",
        "[C0064] Enumerate Threads":"#f37560",
        "[C0054] Resume Thread":"#f78773",
        "[C0055] Suspend Thread":"#fb9886",
        "[C0065] Open Process":"#ffaa99",
        "[C0066] Open Thread":"#d63d2f",
        "[C0070X] Process Enumeration":"#c42c23",
        "[C0042] Create Mutex":"#b31717",
        "[C0017] Create Process":"#a2000a",
        "[C0043] Check Mutex":"#910000",
    "[OC0008] Operating System" : "#f1c40f", #Yellow
        "[C0036] Registry":"#f5ca39",
        "[C0034] Environment Variable":"#f8cf53",
    }

# Inspired by https://sashamaps.net/docs/resources/20-colors/ (Convenient, 99%)
behavior_catalog_basic_colormap = {
    "[OC0001] Filesystem" : "#3498db", #Blue
        "[C0049] Get File Attributes":"#3498db",
        "[C0051] Read File":"#2ecc71",
        "[C0016X] Create or Open file":"#e67e22",
        "[C0015] Alter Filename Extension":"#9b59b6",
        "[C0046] Create Directory":"#e74c3c",
        "[C0045] Copy File":"#f1c40f",
        "[C0047] Delete File":"#42d4f4",
        "[C0063] Move File":"#aaffc3",
        "[C0052] Write File":"#ffd8b1",
    "[OC0005] Cryptography" : "#2ecc71", #Green
        "[C0028] Encryption Key":"#3498db",
        "[C0027] Encrypt Data":"#2ecc71",
        "[C0029] Cryptographic Hash":"#e67e22",
        "[C0031] Decrypt Data":"#9b59b6",
    "[OC0006] Communication" : "#e67e22", #Orange
        "[C0001] Socket Communication":"#3498db",
        "[C0005] WinINet Communication":"#2ecc71",
        "[C0002] HTTP Communication":"#e67e22",
    "[OC0002] Memory" : "#9b59b6", #Purple
        "[C0007] Allocate Memory":"#3498db",
        "[C0008] Change Memory Protection":"#2ecc71",
    "[OC0003] Process" : "#e74c3c", #Red
        "[C0038] Create Thread":"#3498db",
        "[C0064] Enumerate Threads":"#2ecc71",
        "[C0054] Resume Thread":"#e67e22",
        "[C0055] Suspend Thread":"#9b59b6",
        "[C0065] Open Process":"#e74c3c",
        "[C0066] Open Thread":"#f1c40f",
        "[C0070X] Process Enumeration":"#42d4f4",
        "[C0042] Create Mutex":"#aaffc3",
        "[C0017] Create Process":"#ffd8b1",
        "[C0043] Check Mutex":"#a9a9a9",
    "[OC0008] Operating System" : "#f1c40f", #Yellow
        "[C0036] Registry":"#3498db",
        "[C0034] Environment Variable":"#2ecc71",
    }

# https://matplotlib.org/stable/gallery/shapes_and_collections/hatch_style_reference.html
behavior_catalog_hatchmap = {
    "[OC0001] Filesystem" : "*", #Blue
        "[C0049] Get File Attributes":"/",
        "[C0051] Read File":"\\",
        "[C0016X] Create or Open file":"|",
        "[C0015] Alter Filename Extension":"-",
        "[C0046] Create Directory":"+",
        "[C0045] Copy File":"x",
        "[C0047] Delete File":"o",
        "[C0063] Move File":"O",
        "[C0052] Write File":".",
    "[OC0005] Cryptography" : "O", #Green
        "[C0028] Encryption Key":"/",
        "[C0027] Encrypt Data":"\\",
        "[C0029] Cryptographic Hash":"|",
        "[C0031] Decrypt Data":"-",
    "[OC0006] Communication" : "o", #Orange
        "[C0001] Socket Communication":"/",
        "[C0005] WinINet Communication":"\\",
        "[C0002] HTTP Communication":"|",
    "[OC0002] Memory" : "+", #Purple
        "[C0007] Allocate Memory":"/",
        "[C0008] Change Memory Protection":"\\",
    "[OC0003] Process" : "-", #Red
        "[C0038] Create Thread":"/",
        "[C0064] Enumerate Threads":"\\",
        "[C0054] Resume Thread":"|",
        "[C0055] Suspend Thread":"-",
        "[C0065] Open Process":"+",
        "[C0066] Open Thread":"x",
        "[C0070X] Process Enumeration":"o",
        "[C0042] Create Mutex":"O",
        "[C0017] Create Process":".",
        "[C0043] Check Mutex":"*",
    "[OC0008] Operating System" : ".", #Yellow
        "[C0036] Registry":"/",
        "[C0034] Environment Variable":"\\",
    }