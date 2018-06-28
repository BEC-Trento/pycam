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
from settings import default_savedir, bg_savedir, default_savenames, cameras_d, setup_d
from functions import default_picture, pictures_d
from modules.imageio.sis2_lib import write_sis
from modules.background_matching import BackgroundManager


class Main(QtGui.QMainWindow, Ui_MainWindow):
    def __init__(self, camera, name, *args, **kwargs):
        super(Main, self).__init__( *args, **kwargs)
        self.setupUi(self)
        self._roi_controls = [getattr(self, n) for n in ['roiHeightSpinBox', 'roiWidthSpinBox',
                              'roiTopSpinBox', 'roiLeftSpinBox']]
        self.imageView.getImageItem().axisOrder = 'row-major'

        self._name = name
        self._savedir = default_savedir
        self.saveNameComboBox.addItems(default_savenames + ['other'])
        self.set_savename(default_savenames[0])
        self._count = None
        self.count = 0
        self._frames_list = []
        self._finalize = None

        self.bgman = BackgroundManager(name=self._name, savedir=bg_savedir)
        self.on_toggle_bgmatch(False)


        self.saveToLineEdit.setText(os.path.join(self._savedir, self._savename))
        self.camera = camera

        setup_camera(self.camera, setup_d)
        # WARNING: tutte le funzioni e importazioni della ROI funzionano solo con un mode: FORMAT7
        # TODO: implementa switch: if isinstance(mode, Format7)
        self._mode = self.camera.mode
        print('Roi:', self._mode.roi)
#        print(self._mode.data_depth)
        self.limit_roi_spinboxes()
        self.rewrite_roi_spinboxes()
        self.connectInputWidgets()
        self.pictureSelectComboBox.addItems(list(pictures_d.keys()))
        self.pictureSelectComboBox.setCurrentIndex(self.pictureSelectComboBox.findText(default_picture))


    @property
    def count(self):
        return self._count
    @count.setter
    def count(self, value):
        self._count = value
        self.counterDisplay.display(value)

    @property
    def savepath(self):
        return self.saveToLineEdit.text()
        
    @property
    def rawsavepath(self):
        return self.savepath.replace('test', 'raw')
        
    @property
    def n_frames(self):
        return self.nFramesSpinBox.value()
    @property
    def save_flag(self):
        return self.saveRawCheckBox.isChecked()

    @property
    def match_bg(self):
        return self.bgMatchCheckBox.isChecked()

    def set_savename(self, name):
        if name == 'other':
            self.saveToLineEdit.setStyleSheet("")
            self.saveToLineEdit.setReadOnly(False)
        else:
            self._savename = name
            self.saveToLineEdit.setStyleSheet("QLineEdit {\n"
            "background-color: rgb(229, 229, 229)\n"
            "}")
            self.saveToLineEdit.setReadOnly(True)
            self.saveToLineEdit.setText(os.path.join(self._savedir, name))


    def set_savedir(self):
        self._savedir = QtGui.QFileDialog.getExistingDirectory()
        self.saveToLineEdit.setText(os.path.join(self._savedir, self._savename))
        print(self.savepath)

    def set_savedir_manual(self):
        self._savedir, self._savename = os.path.split(self.saveToLineEdit.text())


    def rewrite_roi_spinboxes(self):
        for box in self._roi_controls:
            box.blockSignals(True)
        (w,h), (l,t) = self._mode.roi[:2]
        self.roiHeightSpinBox.setValue(h)
        self.roiWidthSpinBox.setValue(w)
        ul, ut = self._mode.unit_position
        self.roiTopSpinBox.setValue(t)
        self.roiLeftSpinBox.setValue(l)
        ps = self._mode.packet_size
        fps, dt = self.calc_fps(w, h, ps)
        self.statusbar.showMessage('packet_size: %d | fps: %.2f | dt: %d ms'%(ps, fps, dt))
        for box in self._roi_controls:
            box.blockSignals(False)

    def limit_roi_spinboxes(self,):
        mw, mh = self._mode.max_image_size
#        print(mh,mw)
        uw, uh = self._mode.unit_size
        self.roiHeightSpinBox.setRange(uh, mh)
        self.roiHeightSpinBox.setSingleStep(uh)
        self.roiWidthSpinBox.setRange(uw, mw)
        self.roiWidthSpinBox.setSingleStep(uw)
        ul, ut = self._mode.unit_position
        self.roiTopSpinBox.setRange(0, mh)
        self.roiTopSpinBox.setSingleStep(ut)
        self.roiLeftSpinBox.setRange(0, mw)
        self.roiLeftSpinBox.setSingleStep(ul)

    def setup_roi(self,):
        self.stop_camera()
        mw, mh = self._mode.max_image_size
        w, h = self.roiWidthSpinBox.value(), self.roiHeightSpinBox.value()
        image_position=(self.roiLeftSpinBox.value(), self.roiTopSpinBox.value())
        image_size=(min(w, mw-image_position[0]), min(h, mh-image_position[1]))
        self._mode.image_position = image_position
        self._mode.image_size = image_size
        ps = self._mode.recommended_packet_size
        self._mode.packet_size = ps
        self.camera.trigger.mode = '1'
        print('ROI set to', self._mode.roi)
        print('Pack pars:', self._mode.packet_parameters)
        fps, dt = self.calc_fps(w, h, ps)
        self.statusbar.showMessage('packet_size: %d | fps: %.2f | dt: %d ms'%(ps, fps, dt))
#        print('Frame interval: %.3e'%self._mode.frame_interval)
        self.rewrite_roi_spinboxes()
        self.start_camera()

    def setup_roi_max(self,):
        self.stop_camera()
        self._mode.image_position = (0,0)
        self._mode.image_size = self._mode.max_image_size
        self._mode.packet_size = self._mode.recommended_packet_size
        self.camera.trigger.mode = '1'
        self.rewrite_roi_spinboxes()
        print('ROI set to max:', self._mode.roi)
        self.start_camera()


    def connectInputWidgets(self):
        self.saveToPushButton.clicked.connect(self.set_savedir)
        self.saveToLineEdit.textChanged.connect(self.set_savedir_manual)
        self.saveNameComboBox.currentIndexChanged[str].connect(self.set_savename)
        self.pictureSelectComboBox.currentIndexChanged[str].connect(self.load_picture)
        for spinbox in self._roi_controls:
            spinbox.valueChanged.connect(self.setup_roi)
        self.roiMaxPushButton.clicked.connect(self.setup_roi_max)
        self.bgMatchCheckBox.stateChanged.connect(self.on_toggle_bgmatch)
        self.bgAcquirePushButton.toggled.connect(self.on_toggle_bgacquire)
        self.bgLoadPushButton.clicked.connect(self.on_load_background)



    def load_picture(self, pic_name):
        d = pictures_d[pic_name]
        self._finalize = d['finalize_fun']
        n_frames = d['N_frames']
        if n_frames is not None:
            self.lock_n_frames(lock=True, value=n_frames)
        else:
            self.lock_n_frames(lock=False, value=-1)
        self.reset_pic_counter()
        print('Picture %s set up'%pic_name)


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


    def on_toggle_bgmatch(self, state):
        print('toggle use bgmatch')
        for widget in ['bgAcquirePushButton', 'bgLoadPushButton', 'bgNameGuiLabel', 'bgNameLabel']:
            getattr(self, widget).setVisible(state)
        pass

    def on_toggle_bgacquire(self, checked):
        if checked:
            self.last_pic = self.pictureSelectComboBox.currentText()
            self.pictureSelectComboBox.setVisible(False)
            self.load_picture('Movie')
            self._finalize = self.bgman.build_acquired_bg
        else:
            self.load_picture(self.last_pic)
            self.pictureSelectComboBox.setVisible(True)

    def on_load_background(self,):
        file, _ = QtGui.QFileDialog.getOpenFileName(dir=bg_savedir)
        print(file)
        self.bgman.load_dataset(file)
        disp = '-'.join(os.path.split(file)[1].split('-')[-2:])
        self.bgNameLabel.setText(disp)
        self.imageView.setImage(self.bgman.mask, autoRange=True, autoLevels=True,
            autoHistogramRange=True)

    def start_camera(self):
        self.camera.start_capture()
        self.camera.start_video()

    def process_images(self):
        '''
            QtCore.QTimer.singleShot(1, self.process_images)
            frame = None
            flag = True
            wcount = 1
            while flag:
                frame_ = self.camera.dequeue(poll=True)
                print(wcount)
                print(type(frame_))
                print(type(frame))
                wcount +=1
                if frame_ is not None:
                    if frame is not None:
                        frame.enqueue()
                    frame = frame_
                else:
                    if frame is not None:
                        flag = False
                    else:
                        return
        '''
        QtCore.QTimer.singleShot(10, self.process_images)
        frame = self.camera.dequeue(poll=True)
        if frame is not None:
            im = frame.copy().astype('Float64') #type uint16
            self.count += 1
            self._frames_list.append(im)
            print('acquired image %d'%self.count)
            print(im.dtype)
            
            if len(self._frames_list) == self.n_frames:
                self.finalize()


    def calc_fps(self, width, height, pack_size):
        fps = pack_size * 8000 /(width*height * 2)
        dt = int(np.ceil(1e3/fps))
        return fps, dt

    def finalize(self):
        if self._finalize is not None:
            print('apply finalize fun %s'%self._finalize.__name__)
        else:
            print('No finalize set')
            return
        bgfun = self.bgman.compute_bg if self.match_bg else None
        od, raw = self._finalize(self._frames_list,  bgfun)
        stack = np.empty((len(self._frames_list),)+self._frames_list[0].shape)
        for j, im in enumerate(self._frames_list):
            stack[j] = im
        print(stack.shape)
        self.imageView.setImage(stack, autoRange=True, autoLevels=True,
            autoHistogramRange=True)
        if od is not None:
            write_sis(self.savepath, od)
#            np.save(self.savepath[:-4]+'.npy', od)
        if self.save_flag and raw is not None:
            write_sis(self.rawsavepath, raw, sisposition='single', thalammer=False)
                
        self.reset_pic_counter()

    def reset_pic_counter(self):
        del self._frames_list
        self._frames_list = []
        self.count = 0


    def stop_camera(self):
        self.camera.stop_video()
        self.camera.stop_capture()

    def deinit_camera(self):
        pass

def setup_camera(cam, setups):
    cam.mode = cam.modes_dict[setups['camera_mode']]
    L = list(setups.keys())
    L.sort()
    for name in L:
        values = setups[name]
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
    main = Main(cam, name=name)
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
        raise(e)
