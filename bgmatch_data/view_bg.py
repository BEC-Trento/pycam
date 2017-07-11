# -*- coding: utf-8 -*-
import pyqtgraph as pg
import numpy as np
import sys

#A = np.random.rand(100,100)
name = '2017-07-11-RFO-big.npy'
A = np.load(name)

app = pg.Qt.QtGui.QApplication(sys.argv)
im = pg.ImageView()
im.getImageItem().axisOrder = 'row-major'
im.setImage(A)
im.show()

app.exec_()