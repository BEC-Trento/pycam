# -*- coding: utf-8 -*-
"""
Created on Thu Jun 29 17:53:40 2017

@author: bec1
"""

cameras_d = {'vertical': 2892819673563407,
             }

default_savedir = '/home/bec1/camera/raw'

setup_d = {
 'camera_mode': 'FORMAT7_0',
 'brightness': {'value': 0},
 'exposure': {'value': 50},
 'gain': {'value': 0, },#'active': 1},
 'gamma': {'active': 0},
 'shutter': {'value': 1},
# 'temperature': <pydc1394.camera2.Temperature at 0x7f5eca140400>,
 'trigger': {'active': True, 'source': '0', 'mode': '1', 'polarity': 'ACTIVE_HIGH'},
 'trigger_delay': {'value': 0},
}


def setup_camera(cam, setups={}):
    cam.mode = cam.modes_dict[setup_d['camera_mode']]
    for name, values in setup_d.items():
        try:
            print("setting up %s"%name)
            feat = getattr(cam, name)
            for k, v in values.items():
                setattr(feat, k, v)
        except AttributeError as e:
            pass
#            print(e)
#            print("Feature %s not set up"%name)