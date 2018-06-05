#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Created on Wed Feb 15 17:01:03 2017
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
import numpy as np

cameras_d = {'vert': 2892819673539838,#2892819673563407,
             'horiz': 2892819673536359,
             'axial': 2892819673563407,
             }

default_savedir = '/home/stronzio/c-siscam-img' #os.path.abspath('.')
bg_savedir = '/home/bec/pycam/bgmatch_data'
default_savenames = ['test_0.sis', 'test_1.sis']

setup_d = {
 'camera_mode': 'FORMAT7_0',
 'mode': {'color_coding': 'Y16'},
 'brightness': {'value': 0},
 'exposure': {'value': 50},
 'gain': {'value': 0, },#'active': 1},
 'gamma': {'active': 0},
 'shutter': {'value': 20},
# 'temperature': <pydc1394.camera2.Temperature at 0x7f5eca140400>,
 'trigger': {'active': True, 'source': '0', 'mode': '1', 'polarity': 'ACTIVE_HIGH'},
 'trigger_delay': {'value': 5000},
}



            
def finalize_picture_OD_4_frames(frames_list, match_bg_fun=None):
    frames_list = [f.astype(np.float64) for f in frames_list]
    bg = frames_list[3]
    atoms, probe0 = frames_list[0:2]
    atoms = atoms - bg
    probe = probe0 if match_bg_fun is None else match_bg_fun(atoms)
    probe = probe - bg 
    #TODO: check this step here
    OD = np.log((probe+1)/(atoms+1))
#    OD[OD<0] = 0
    h, w = OD.shape
    OD = np.pad(OD, pad_width=((0,1234-h), (0,1624-w)), mode='constant', constant_values=0)
    return OD        

def finalize_picture_1_frame(frames_list,):
    f = frames_list[0]
    frame = f.astype(np.float64)
    return frame
    
def finalize_picture_movie_n_frames(frames_list, match_bg_fun=None):
    probe0 = frames_list[-1]
    frames = frames_list[:-1]
    Nframes = len(frames)
    print('Ho trovato %d immagini'%Nframes)
    odlist = []
    for f in frames:
        probe = probe0 if match_bg_fun is None else match_bg_fun(f)
        OD = -np.log((f+1e-5)/(probe+1e-5))
        OD[OD<0] = 0
        odlist.append(OD)
    h, w = OD.shape
    W = 1624
    H = 1234
    Lw = W // w
    Lh = H // h
    Nframes_written = Lw * Lh
    image = np.zeros((H, W))
    dims = (Lh, Lw)
    print('Writing the first %d out of %d frames in a %d x %d matrix\ntotal picture size: %d x %d'%(Nframes_written, Nframes, Lh, Lw, H, W))
    for j, od in enumerate(odlist[:Nframes_written]):
        p, q = np.unravel_index(j, dims)
        image[p*h:(p+1)*h, q*w:(q+1)*w] = od
    return image
    
def finalize_picture_movie_n_frames_vary_height(frames_list,):
    probe = frames_list[0]
    frames = frames_list[1:]
    Nframes = len(frames)
    print('Ho trovato %d immagini'%Nframes)
    odlist = []
    for f in frames:
        OD = -np.log((f+1e-5)/(probe+1e-5))
        OD[OD<0] = 0
        odlist.append(OD)
    h, w = OD.shape
    W = 1624
    Lw = W // w
    Lh = Nframes // Lw + 1
    H = h*Lh
    image = np.zeros((H, W))
    dims = (Lh, Lw)
    print('Writing %d frames in a %d x %d matrix\ntotal picture size: %d x %d'%(Nframes, Lh, Lw, H, W))
    for j, od in enumerate(odlist):
        p, q = np.unravel_index(j, dims)
        image[p*h:(p+1)*h, q*w:(q+1)*w] = od
    return image

pictures_d = {
'Picture 4 frames': 
    {'finalize_fun': finalize_picture_OD_4_frames,
     'N_frames': 4,
     },
'Picture single frame': 
    {'finalize_fun': finalize_picture_1_frame,
     'N_frames': 1,
     },
'Movie': 
    {'finalize_fun': finalize_picture_movie_n_frames,
     'N_frames': None,
     },
}

default_picture = 'Picture 4 frames'
