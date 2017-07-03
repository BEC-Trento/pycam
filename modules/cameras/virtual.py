#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Created on Sun Dec  4 21:46:06 2016
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
import os

from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

class VirtualCamera(PatternMatchingEventHandler):
    def __init__(self, folder, file_ext, init_kwargs):
        self._counter = 0
        self._folder = folder
        self._ext = file_ext
        init_kwargs.update({'patterns': ['*%s'%file_ext]})
        super(VirtualCamera, self).__init__(**init_kwargs)
        
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
        self.observer = Observer()
        self.observer.schedule(handler=self, path=self.folder)
        print('observer scheduled on ', self.folder)
        self.observer.start()

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
    
    def on_deleted(self, event):
        print(str(event.src_path) + ' ' + str(event.event_type))
        print("The raw file has been deleted: ")
        print("Ready!")

    def on_created(self, event):
        print(str(event.src_path) + ' ' + str(event.event_type))
        frame = self.read_fun(event.src_path, full_output=False)
        if self.flag_delete_raw:
            try:
                os.remove(event.src_path)
            except OSError:
                pass
            return frame

    def stop_camera(self):
        if self.observer is not None:
            self.observer.join()
            self.observer.stop()
        
    


