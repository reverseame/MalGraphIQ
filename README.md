# MalGraphIQ
Transform your malware sandbox reports and execution traces into behavior and category graphs.

# Contents
The MalGraphIQ repository contains the following elements:
- [src](./src): Source code.
- [requirements.txt](./requirements.txt): Requirements for the tool to run. Install with `pip3 install -r requirements.txt`.

# Requirements
Besides installing the modules listed in [requirements.txt](./requirements.txt), MalGraphIQ also relies on the following resources:
- [winapi_categories](https://github.com/reverseame/winapi-categories). A .json file containing our categorization of Windows API and syscalls. It can be downloaded with a command like:  
	`$ wget https://raw.githubusercontent.com/reverseame/winapi-categories/refs/heads/main/winapi_categories.json`

# How To Use
TODO

Documentation generated with [pdoc3](https://github.com/pdoc3/pdoc).
```
$ PYTHONPATH=src/malgraphiq pdoc3 src/malgraphiq -o doc --html
```

# Example Data
TODO

# Authors

[Razvan Raducu](https://www.youtube.com/@RazviOverflow)  
[Ricardo J. Rodríguez](https://webdiis.unizar.es/~ricardo/)  
[Pedro Álvarez](https://i3a.unizar.es/es/investigadores/pedro-javier-alvarez-perez-aradros)