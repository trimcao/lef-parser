"""
Lef Parser
Author: Tri Cao
Email: tricao@utdallas.edu
Date: August 2016
"""
from util import *

"""
Note:
"""

def strToList(s):
    """
    Function to turn a string separated by space into list of words
    :param s: input string
    :return: a list of words
    """
    result = s.split()
    # check if the last word is ';' and remove it
    if result[len(result) - 1] == ";":
        result.pop()
    return result

#f = open("./libraries/FreePDK45/FreePDK45nm.lef", 'r+')
#for line in f:
#    print (line)
#f.close()

a = Macro('helloWorld')
#print (a.type)
#a.parseNext('s')

b = Macro('goodbye')

# can make the stack to be an object if needed
stack = []



