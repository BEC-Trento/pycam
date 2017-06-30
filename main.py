#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Created on Fri Feb 10 12:44:42 2017
# Copyright (C) 2016  Carmelo Mordini
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import sys, os, time
from PySide import QtGui, QtCore
from modules.ui.main_ui import Ui_MainWindow

from pydc1394 import Camera
from settings import default_savedir, setup_camera, cameras_d
from modules.lib_tif import write_tif


class Main(QtGui.QMainWindow, Ui_MainWindow):
    def __init__(self, camera, *args, **kwargs):
        super(Main, self).__init__( *args, **kwargs)
        self.setupUi(self)
        self.connectInputWidgets()
        
        self.imageView.getImageItem().axisOrder = 'row-major'
        self.saveToLineEdit.setText(default_savedir)
        
        self._count = None
        self.count = 0
        self.camera = camera
        setup_camera(self.camera)
        
    @property
    def count(self):
        return self._count
    @count.setter
    def count(self, value):
        self._count = value
        self.counterSpinBox.setValue(value)
        
    @property
    def savedir(self):
        return self.saveToLineEdit.text()
        
    def connectInputWidgets(self):
        self.saveToPushButton.clicked.connect(self.change_savedir)
        
    def change_savedir(self):
        path = QtGui.QFileDialog.getExistingDirectory()
        self.saveToLineEdit.setText(path)
        print(self.savepath)
        
    def start_camera(self):
        self.camera.start_capture()
        self.camera.start_video()

    def process_images(self):
        QtCore.QTimer.singleShot(50, self.process_images)
        frame = None
        while True:
            frame_ = self.camera.dequeue(poll=True)
            if frame_ is not None:
                if frame is not None:
                    frame.enqueue()
                frame = frame_
            else:
                break
        if frame is None:
            return
        im = frame.copy().astype('u2') #type uint16
        self.count += 1
        print('acquired image %d'%self.count)
        print(im.dtype)
        fname = 'im-%d.tif'%self.count
        write_tif(os.path.join(self.savedir, fname), im)
        frame.enqueue()
        self.imageView.setImage(im, autoRange=True, autoLevels=True,
            autoHistogramRange=True)
            


    def stop_camera(self):
        self.camera.stop_video()
        self.camera.stop_capture()
        
    def deinit_camera(self):
        pass
    
def _main(guid, name):
    app = QtGui.QApplication(sys.argv)
    cam = Camera(guid=guid, iso_speed=800)
    main = Main(cam)
    main.setWindowTitle('pyCAM -- %s'%name)
    
    main.show()
    try:
        main.start_camera()
        time.sleep(.5)
        main.process_images()
#        cam.img.autoRange()
#        cam.img.autoLevels()
#        QtGui.app.instance().exec_()
        status = app.exec_()
    finally:
        main.stop_camera()
        main.deinit_camera()
        sys.exit(status)
        
if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Test.')
    parser.add_argument('name', action='store', type=str, help='Camera name (see settings.py)')
    args = parser.parse_args()
    
    try:
        guid = cameras_d[args.name]
        _main(guid, args.name)
    except KeyError as e:
        print(e)
        s = '%s not registered in the camera database.\nSee settings.py for valid camera names:\n'%(args.name)
        s += 'registered cameras:\n' + '\n'.join(['%s:\t%d'%(name, cameras_d[name]) for name in cameras_d])
        print(s)
    
    