import os
import sys
import json

b= {'taskid': 12345, 'time': 1559194507, 'typeid': 58, 'type': 'pottedplant', 'box': {'x1': 43, 'y1': 189, 'x2': 114, 'y2': 238}}
a = json.dumps(b, indent=2)
print (a)
