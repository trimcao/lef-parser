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

# can make the stack to be an object if needed
stack = []

# store the statements info in a list
statements = []

# Now try using my data structure to parse
# open the file and start reading
path = "./libraries/FreePDK45/small.lef"
f = open(path, "r+")
# the program will run until the end of file f
for line in f:
    #print (stack)
    info = strToList(line)
    # check if the program is processing a statement
    if (len(stack) != 0):
        curState = stack[len(stack) - 1]
        nextState = curState.parseNext(info)
    else:
        curState = Statement()
        nextState = curState.parseNext(info)
    # check the status return from parseNext function
    if (nextState == 0):
        # continue as normal
        pass
    elif (nextState == 1):
        # remove the done statement from stack, and add it to the statements
        # list
        if (len(stack) != 0):
            statements.append(stack.pop())
    elif (nextState == -1):
        pass
    else:
        stack.append(nextState)
    #print (nextState)
f.close()

# print parsed statements
# be careful: this printing might include both parent and children objects,
# probably I need to separate them
print (statements)
for each in statements:
    print (each.toString())


