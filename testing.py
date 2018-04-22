import numpy as np
import PIL.Image

frame = np.load("file.npy")

img = PIL.Image.new('RGB',(640,480))
pixels = img.load()

for i in range(img.size[0]):
    for j in range(img.size[1]):
        pixels[i,j] = (frame[j][i][0],frame[j][i][1],frame[j][i][2])

img.show()

print(frame)
print(frame*-1)

print(np.add(frame,frame*-1))