import numpy as np

frame = np.load("file.npy")

print(frame)

colsums = []
for i in range(640):
    sum = np.asarray([0,0,0])
    for j in range(480): 
        sum = np.add(sum,frame[j][i])
    colsums.append(np.median(sum))

print(colsums)
print(len(colsums))
