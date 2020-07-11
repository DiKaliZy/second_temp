import numpy as np
import os

class Center_Mass():
    def __init__(self,Joint):
        self.cmass_scale = 0
        self.CM_axis = np.array([1])
        self.calc_center_of_mass(Joint)
        self.CM_axis = self.CM_axis / self.cmass_scale


    def calc_center_of_mass(self,Joint):
        #weighted sum of M_axis and mass
        if Joint.lv == 1:
            self.CM_axis = np.array(Joint.M_axis) * Joint.mass
        else:
            if Joint.M_axis  != []:
                self.CM_axis += np.array(Joint.M_axis) * Joint.mass
        self.cmass_scale += Joint.mass
        for child in Joint.child:
            self.calc_center_of_mass(child)
