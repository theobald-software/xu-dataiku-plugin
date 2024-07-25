import sys

"""
Modification of the module search path is intended for debugging purposes only.
This __init__.py file should not be included when building the plugin for official release, to prevent code injection.
Instead, the common library code must be copied into the python-lib directory.
"""
sys.path.append("c:\\source\\python-plugins")
print(sys.path)
