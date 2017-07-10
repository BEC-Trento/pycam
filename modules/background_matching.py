#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Created on Mon July 10
# Copyright (C) 2017  Carmelo Mordini
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

import numpy as np
import os
from datetime import datetime
import json
from .imageio import read_sis, write_sis

class BackgroundManager():
    def __init__(self, name, savedir):
        self._name = name
        self.savedir = savedir
        self.B_dataset = None
        self.dataset_name = None
        self.imshape = None
        self.mask = None
        self.beta = None
        self.BB_inv = None
        

    def get_timestamped_name(self,):
        fmt='%Y-%m-%d-%H-%M-%S-{fname}'
        return datetime.now().strftime(fmt).format(fname=self._name)
    
    def load_dataset(self, path_list):
        self.sis_path_list = path_list
        # _l = []
        # for p in path_list:
        #     b = self.readsis_simple(p)[1]
        #     _l.append(b)
        _l = [self.readsis_simple(p)[1] for p in path_list]
        B_dataset = np.concatenate([b[np.newaxis, :,:] for b in _l], axis=0)
        self.imshape = B_dataset[0].shape
        self.B_dataset = B_dataset
        # return B_dataset
        
    def build_acquired_bg(self, frames_list):
        dataset = np.concatenate([f[np.newaxis, ...] for f in frames_list], axis=0)
        self.name = self.get_timestamped_name()
        path = os.path.join(self.savedir, self.name + '.npy')
        np.save(path, dataset)
        print('saved bg dataset %s'%path)
        return None
    
    def load_mask(self, mask):
        self.mask = mask
        
    def compute_bg_matrix(self,):
        if self.B_dataset is None:
            print('You must load a dataset first')
            return
        if self.mask is None:    
            print('You must set a mask first')
            return
        beta = np.concatenate([b[self.mask][np.newaxis, :] for b in self.B_dataset], axis=0)
        self.BB = np.dot(beta, beta.T)        
        self.beta = beta
        # return beta, BB_inv

    def compute_bg(self, image, output_coeff=False):
        alpha = np.dot(self.beta, image[self.mask])
        try:        
            c = np.linalg.solve(self.BB, alpha)
        except np.linalg.LinAlgError as err:
            print(err)
            print('BB matrix is singular: will pseudo-solve')
            c = np.linalg.lstsq(self.BB, alpha)
        B_opt = np.sum(self.B_dataset*c[:, np.newaxis, np.newaxis], axis=0)
        if output_coeff:
            return c, B_opt
        else:
            return B_opt
        

