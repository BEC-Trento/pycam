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

def finalize_picture_OD_4_frames(frames_list, match_bg_fun=None):
    frames_list = [f.astype(np.float64) for f in frames_list]
    bg = frames_list[3]
    atoms, probe0 = frames_list[0:2]
    atoms = atoms - bg
    probe = probe0 if match_bg_fun is None else match_bg_fun(atoms)
    probe = probe - bg
    #TODO: check this step here
    OD = np.log((probe+1)/(atoms+1))
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
    for atoms in frames:
        probe = probe0 if match_bg_fun is None else match_bg_fun(atoms)
        OD = np.log((probe+1)/(atoms+1))
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
        OD = np.log((probe+1)/(f+1))
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

def picture_dark_ground(frames_list,):
    frames_list = [f.astype(np.float64) for f in frames_list]
    bg = frames_list[3]
    alpha = 45

    omega = 1.6e-3
    atoms, probe = frames_list[0:2]
    atoms = atoms 
    
    atoms=atoms+1
    probe=probe+1
    
    T = atoms/(alpha*probe)
    
  #  OD = 2*(np.sqrt(T+omega**2) - omega)
    OD = 2*(np.sqrt(T))
    return OD  

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
'Dark ground': 
    {'finalize_fun': picture_dark_ground,
     'N_frames': 4,
     },
}

default_picture = 'Picture 4 frames'
