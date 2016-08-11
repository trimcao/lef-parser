"""
Lef Parser
Author: Tri Cao
Email: tricao@utdallas.edu
Date: August 2016
"""

f = open('./libraries/FreePDK45/FreePDK45nm.lef', 'r+')

for line in f:
    print (line)

f.close()
