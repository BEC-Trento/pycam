#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Created on Tue Jul  4 00:12:36 2017
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
from abc import ABCMeta, abstractmethod

class BaseCamera(metaclass=ABCMeta):
    def __init__(self, ):
        pass
    
    @abstractmethod
    def setup(self, **kwargs):
        pass