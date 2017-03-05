###############################
# Helpers.py
###############################

import os


'''
Prettify given path by shorting it
'''
def shorten_path(path):
    components = path.split(os.sep)
    if len(components) > 3:
        return os.sep.join((components[0],components[1],"...",components[-2],components[-1]))
    return path

