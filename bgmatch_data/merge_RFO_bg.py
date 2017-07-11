# -*- coding: utf-8 -*-

import numpy as np
import os

name = '2017-07-11-horiz-570-big.npy'

L = [file for file in os.listdir() if 'horiz' in file and file.endswith('.npy')]

if name in L:
    print('overwriting %s'%name)
    L.pop(L.index(name))
print(L)

images = [np.load(file) for file in L]
big = np.concatenate(images, axis=0)
np.save(name, big)