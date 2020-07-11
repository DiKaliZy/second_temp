import numpy as np
from utility import *

class BVH_Motion():
    def __init__(self, name):
        self.name = name
        self.parent = None
        self.child = []
        self.order = []  # type순서
        self.channel = 0
        self.Rmat_origin = []   #original rotation matrix
        self.Rmat_fps_set = []  #fps 설정 적용
        self.Rmat_final = []  # 최종(배수 적용)
        self.isRoot = False
        self.isEnd = False

    def fps_Sync(self, ratio):
        temp = []
        index = 0
        while index * ratio < len(self.Rmat_origin) - 1:
            a = index * ratio  # 어느 위치의 값인지 지정
            floor = int(np.floor(a))  # 내림
            ceil = int(floor + 1)  # 올림
            pro = a - floor  # interpolation 비율
            temp.append(slerp(self.Rmat_origin[floor], self.Rmat_origin[ceil], pro))
            index += 1
        self.Rmat_fps_set = temp
        self.Rmat_final = list(self.Rmat_fps_set)
        for i in range(len(self.child)):
            self.child[i].fps_Sync(ratio)

    def addChild(self, child):
        self.child.append(child)

    def chopList(self, datalist, channel):
        temp = []
        for i in range(channel):
            temp.append(datalist.pop(0))
        #print(self.name)
        #print(temp)
        return temp

    def loadData(self, datalist):
        temp = []
        if self.isEnd != True:
            temp = self.chopList(datalist, len(self.order))
            temp_rot = change2RotMat(self.order, temp)
            self.Rmat_origin.append(temp_rot)
            for i in range(len(self.child)):
                self.child[i].loadData(datalist)
        else:
            arr = np.identity(3)
            self.Rmat_origin.append(arr)

    def SpeedDown(self, playSpeed):
        i = 1
        while i + 1 < (len(self.Rmat_final)):
            trans1 = np.array(self.Rmat_final[i])
            trans2 = np.array(self.Rmat_final[i + 1])
            temp = (trans1 + trans2) / 2
            R = slerp(self.Rmat_final[i], self.Rmat_final[i + 1], 0.5)
            self.Rmat_final.insert(i + 1, R)
            i += 2
        if self.isEnd != True:
            for i in range(len(self.child)):
                self.child[i].SpeedDown(playSpeed)

    def SpeedUp(self, playSpeed):
        i = 2
        while i < (len(self.Rmat_final)):
            del self.Rmat_final[i]
            i += 1
        if self.isEnd != True:
            for i in range(len(self.child)):
                self.child[i].SpeedUp(playSpeed)

