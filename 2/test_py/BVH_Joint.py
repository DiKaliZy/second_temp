import numpy as np
import math
from test_py.Mesh import *

class BVH_Joint():
    def __init__(self, name):
        self.name = name
        self.offset = []
        self.parent = None
        self.meshes = []
        self.mass = 0
        self.J_axis = []  #list of Joint [x, y, z] per frames
        self.M_axis = []
        self.M_offset = None    #offset of COM for joint axis [0,0,0]
        self.M_mass = 0  # COM mass scale
        self.child = []
        self.check = 0
        self.isEnd = False
        self.isRoot = False
        self.motion = None
        self.lv = 10

    def addChild(self, child):
        self.child.append(child)

    def setaxis(self, x, y, z):
        self.axis = [x, y, z]

    def setMass(self, mass_effect):
        self.mass = mass_effect

    def setMesh(self, scene_node = None, mesh_form = "BOX"):
        if self.isEnd != True:
            if scene_node != None:
                self.meshes = scene_node.meshes
                print(self.meshes)
                if scene_node.meshes:
                    print(scene_node.meshes[0])
                #for i in range(len(self.child)):
                    #self.child[i].setMesh(scene_node.children[i])
            else:
                #for i in range(len(self.child)):
                print(self.name)
                mesh = Mesh()
                self.meshes.append(CreateMesh([0, 0, 0], self.child[0].offset, mesh_form, mesh))
                    #self.child[i].setMesh(mesh_form = mesh_form)

    def compute_Axis(self):
        temp_axis = []
        for i in range(len(self.motion.Rmat_final)):
            pointer = self
            axis = np.array([0., 0., 0., 1.])
            while pointer!=None:
                temp_t = np.identity(4)
                temp_r = np.identity(4)
                temp_t[:3, 3] = pointer.offset

                temp_r[:3,:3] = pointer.motion.Rmat_final[i]
                axis = np.dot(temp_r, axis)
                axis = np.dot(temp_t, axis)

                if pointer.isRoot == True:

                    ori = [0., 0., 0., 0.]
                    ori[:3] = pointer.motion.trans_final[i]
                    axis = axis + ori

                pointer = pointer.parent
            res = np.array(axis[:3])
            temp_axis.append(res)
        return temp_axis

    def set_Axis(self):
        self.J_axis = self.compute_Axis()
        '''
        method 1 . 각 part에 mass  (c/lv, c = # of child , lv = joint level) -> center of mass
        -> J_axis - frame당 각 joint의 절대 좌표
        -> M_axis - frame당 part의 중심 좌표
        -> 
        '''
        #method 1
        if len(self.child) > 0:
            for child in self.child:
                child.set_Axis()

            for idx , J_axis in enumerate(self.J_axis):
                t = J_axis
                for child in self.child:
                    t = t + child.J_axis[idx]
                t = t / (len(self.child) + 1)
                self.M_axis.append(t)
            #mass by lv
            '''self.mass =  20 + int(math.pow(len(self.child) + 1,2) - math.pow(self.lv,2))
            if self.mass <= 0:
                if self.lv == 8:
                    self.mass = 70
                elif self.lv <= 10:
                    self.mass = 10 - self.lv
                else :
                    self.mass = 0'''
            # mass by name
            self.mass = setmass(self.name)
            #self.mass = 10 * len(self.child) / (self.lv * np.log(self.lv + 1))

            #set M_offset
            if len(self.child) > 0:
                weighted_offset = np.array([0, 0, 0]) * self.mass
                mass = self.mass
                for child in self.child:
                    weighted_offset = weighted_offset + np.array(child.offset) * child.mass
                    mass = mass + child.mass
                weighted_offset = weighted_offset / mass
                self.M_offset = weighted_offset
                self.M_mass = mass
                print("mass ", self.mass, "offset", self.offset)
                print(self.name, " M_offset : ", self.M_offset)

        else :
            ...

    def setMotion(self, motion):
        if self.isEnd != True:
            self.motion = motion
            for i in range(len(self.child)):
                self.child[i].setMotion(motion.child[i])

    def setMoffset(self):
        if len(self.child) > 0:
            weighted_offset = np.array([0, 0, 0]) * self.mass
            mass = self.mass
            for child in self.child:
                weighted_offset = weighted_offset + np.array(child.offset) * child.mass
                mass = mass + child.mass
            weighted_offset = weighted_offset / mass
            self.M_offset = weighted_offset
            print("mass ", self.mass, "offset", self.offset)
            print(self.name, " M_offset : ", self.M_offset)

# mass by name
def setmass(JointName):
    dict = {'hip' : 12, 'abdomen' : 10, 'chest': 12, 'neck' : 0.3,
            'head' : 5, 'rCollar' : 0.5, 'lCollar' : 0.5, 'rShldr' : 2, 'lShldr': 2,
            'rForeArm' : 1.5, 'lForeArm' : 1.5, 'rButtock' : 0.1, 'lButtock' : 0.1,
            'rThigh' : 6, 'lThigh' : 6, 'rShin' : 4, 'lShin' : 4, 'rFoot' : 1, 'lFoot' : 1}
    return dict.get(JointName,0)
