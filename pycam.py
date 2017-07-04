#!/usr/bin/python3
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
import numpy as np
from PySide import QtGui, QtCore
from modules.ui.main_ui import Ui_MainWindow

from pydc1394 import Camera
from settings import default_savedir, default_savename, cameras_d, setup_d, pictures_d
from modules.imageio.sis2_lib import write_sis


class Main(QtGui.QMainWindow, Ui_MainWindow):
    def __init__(self, camera, *args, **kwargs):
        super(Main, self).__init__( *args, **kwargs)
        self.setupUi(self)
        self.imageView.getImageItem().axisOrder = 'row-major'
        
        self._savedir = default_savedir
        self._savename = default_savename
        self._count = None
        self.count = 0
        self._frames_list = []
        self._finalize = None

        self.connectInputWidgets()
        self.pictureSelectComboBox.addItems(list(pictures_d.keys()))
        self.saveToLineEdit.setText(os.path.join(self._savedir, self._savename))
        self.camera = camera
        setup_camera(self.camera, setup_d)
        
    @property
    def count(self):
        return self._count
    @count.setter
    def count(self, value):
        self._count = value
        self.counterSpinBox.setValue(value)
        
    @property
    def savepath(self):
        return self.saveToLineEdit.text()
    @property
    def n_frames(self):
        return self.nFramesSpinBox.value()
    @property
    def save_flag(self):
        return self.saveRawCheckBox.isChecked()
        
    def connectInputWidgets(self):
        self.saveToPushButton.clicked.connect(self.change_savedir)
        self.pictureSelectComboBox.currentIndexChanged[str].connect(self.load_picture)
        self.saveToLineEdit.textChanged.connect(self.change_savedir_manual)
        
        
    def load_picture(self, pic_name):
        d = pictures_d[pic_name]
        self._finalize = d['finalize_fun']
        n_frames = d['N_frames']
        if n_frames is not None:
            self.lock_n_frames(lock=True, value=n_frames)
        else:
            self.lock_n_frames(lock=False, value=-1)
        
        
    def lock_n_frames(self, lock=True, value=1):
        self.nFramesSpinBox.setValue(value)
        if lock:
            self.nFramesSpinBox.setStyleSheet("QSpinBox {\n"
            "border: 1px solid rgb(0,0,0);\n"
            "border-radius: 4px;\n"
            "background-color: rgb(229, 229, 229)\n"
            "}")
            self.nFramesSpinBox.setReadOnly(True)
            self.nFramesSpinBox.setButtonSymbols(QtGui.QAbstractSpinBox.NoButtons)
        else:
            self.nFramesSpinBox.setStyleSheet("")
            self.nFramesSpinBox.setReadOnly(False)
            self.nFramesSpinBox.setButtonSymbols(QtGui.QAbstractSpinBox.UpDownArrows)
        
    def change_savedir(self):
        self._savedir = QtGui.QFileDialog.getExistingDirectory()
        path = os.path.join(self._savedir, self._savename)
        self.saveToLineEdit.setText(path)
        print(self.savepath)
        
    def change_savedir_manual(self):
        self._savedir, self._savename = os.path.split(self.saveToLineEdit.text())
        
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
        im = frame.copy().astype('Float64') #type uint16
        self.count += 1
        print('acquired image %d'%self.count)
        print(im.dtype)
        frame.enqueue()
        if self.save_flag:
            self.save_frame(im)
        self._frames_list.append(im)
#        self.imageView.setImage(im, autoRange=True, autoLevels=True,
#            autoHistogramRange=True)
        if len(self._frames_list) == self.n_frames:
            self.finalize()
            
            
    def save_frame(self, frame):
        print('Save NotImplemented')
#        fname = 'im-%d.tif'%self.count
#        write_tif(os.path.join(self.savedir, fname), frame)
        
    def finalize(self):
        if self._finalize is not None:
            print('apply finalize fun %s'%self._finalize.__name__)
        od = self._finalize(self._frames_list)
        stack = np.empty((len(self._frames_list),)+od.shape)
        for j, im in enumerate(self._frames_list):
            stack[j] = im
        print(stack.shape)
        self.imageView.setImage(stack, autoRange=True, autoLevels=True,
            autoHistogramRange=True)
        write_sis(self.savepath, od)
        np.save(self.savepath[:-4]+'.npy', od)
        self._frames_list = []
        self.count = 0


    def stop_camera(self):
        self.camera.stop_video()
        self.camera.stop_capture()
        
    def deinit_camera(self):
        pass
    
def setup_camera(cam, setups):
    cam.mode = cam.modes_dict[setups['camera_mode']]
    for name, values in setups.items():
        try:
            print("setting up %s"%name)
            feat = getattr(cam, name)
            for k, v in values.items():
                setattr(feat, k, v)
        except AttributeError:
            pass
#            print(e)
#            print("Feature %s not set up"%name)
    
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
    
    parser = argparse.ArgumentParser(description='Camera names.')
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
    
    
