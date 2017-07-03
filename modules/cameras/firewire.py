#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Created on Tue Jul  4 00:32:41 2017
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

from pydc1394 import Camera
from ..imageio.tif_lib import write_tif

class FirewireCamera(Camera):
    def __init__(self, folder, file_ext, init_kwargs):
        super(FirewireCamera, self).__init__(**init_kwargs)
        self._counter = 0
        self._folder = folder
        self._ext = file_ext
        
        
    def _get_counter(self):
        return self._counter
    def _set_counter(self, value):
        self._counter = value
    counter = property(_get_counter, _set_counter)
        
    def _get_folder(self):
        return self._folder
    def _set_folder(self, path):
        self._folder = path
    raw_folder = property(_get_folder, _set_folder)
    
    @property
    def file_ext(self):
        return self._ext
        
    def start_camera(self):
        self.start_capture()
        self.start_video()

    def drop_frame(self):
        frame = None
        while True:
            frame_ = self.dequeue(poll=True)
            if frame_ is not None:
                if frame is not None:
                    frame.enqueue()
                frame = frame_
            else:
                break
        if frame is None:
            return
        # TODO: check byteorder issue
        im = frame.copy()#.astype('u2') #type uint16
        frame.enqueue()
        self.counter += 1
        return im


    def stop_camera(self):
        self.stop_video()
        self.stop_capture()
        
    