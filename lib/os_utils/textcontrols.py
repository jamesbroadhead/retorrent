"""
os_utils.textcontrols

Utils to control text on the terminal
"""


def bold(string):
    boldtext = "\033[1m"
    resetbold = "\033[0;0m"
    return boldtext + string + resetbold
