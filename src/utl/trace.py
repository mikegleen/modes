"""
    Utility subroutine for trace
"""

from colorama import Style
from inspect import getframeinfo, stack
from os.path import basename


def trace_sub(level: int, verbose: int, template, color, args):
    if verbose >= level:
        if verbose > 1:
            caller = getframeinfo(stack()[1][0])
            print(f'{basename(caller.filename)} line {caller.lineno}: ', end='')
        if color:
            if len(args) == 0:
                print(f'{color}{template}{Style.RESET_ALL}')
            else:
                print(f'{color}{template.format(*args)}{Style.RESET_ALL}')
        else:
            if len(args) == 0:
                print(template)
            else:
                print(template.format(*args))
