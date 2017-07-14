# -*- coding: utf-8 -*-

import numpy as np
import os

name = '2017-07-13-horiz-big.npy'

L = [file for file in os.listdir() if '2017-07-13' in file and file.endswith('.npy')]
L.sort()

if name in L:
    print('overwriting %s'%name)
    L.pop(L.index(name))
print(L)


images = []
Nmax = 200
for file in L:
    i = np.load(file)
    I = np.arange(0,min(Nmax, i.shape[0]))
    np.random.shuffle(I)
    I = I[:Nmax]
    images.append(i[I])
big = np.concatenate(images, axis=0)
print('New db:', big.shape)

#for file in L:
#    os.remove(file)
    
np.save(name, big)