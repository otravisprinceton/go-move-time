import os

path = "/Users/owentravis/Documents/IW/Output"

curr = 201101

for h in range(11, 12):
    for i in range(9):
        os.mkdir(os.path.join(path, str(curr + i + (100 * h))))