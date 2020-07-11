import numpy as np
from test_py.BVH_Motion import *
from test_py.utility import *

class BVH_Motion_root(BVH_Motion):
    def __init__(self, name):
        BVH_Motion.__init__(self, name)
        self.trans_origin = []
        self.trans_fps_set = []
        self.trans_final = []

    def setFrame(self, frame):
        self.frame = frame  # 프레임 수

    def setTPF(self, tpf):
        self.tpf = tpf # time per frame (프레임당 초) # 원본 파일 속도

    def loadData(self, datalist):
        temp = []
        if self.isEnd != True:
            temp = self.chopList(datalist, len(self.order))
            self.setTrans(temp)
            temp_rot = change2RotMat(self.order, temp)
            self.Rmat_origin.append(temp_rot)
            for i in range(len(self.child)):
                self.child[i].loadData(datalist)

    def setTrans(self, data):
        temp = [0, 0, 0]
        for i in range(len(self.order)):
            if self.order[i] == "Xposition" or self.order[i] == "XPOSITION":
                temp[0] = data[i]
            elif self.order[i] == "Yposition" or self.order[i] == "YPOSITION":
                temp[1] = data[i]
            elif self.order[i] == "Zposition" or self.order[i] == "ZPOSITION":
                temp[2] = data[i]
        self.trans_origin.append(temp)  # translate

    def SpeedDown(self, playSpeed):
        i = 1
        if self.isEnd != True:
            while i + 1 < (len(self.Rmat_final)):
                temp = lerp(self.trans_final[i], self.trans_final[i+1], 0.5)
                R = slerp(self.Rmat_final[i], self.Rmat_final[i+1], 0.5)
                self.Rmat_final.insert(i+1,R)
                self.trans_final.insert(i+1,temp)
                i += 2
            for i in range(len(self.child)):
                self.child[i].SpeedDown(playSpeed)

    def SpeedUp(self, playSpeed):
        i = 2
        if self.isEnd != True:
            while i < (len(self.Rmat_final)):
                del self.Rmat_final[i]
                del self.trans_final[i]
                i += 1
            for i in range(len(self.child)):
                self.child[i].SpeedUp(playSpeed)

    def fps_Sync(self, timer):
        temp_rot = []
        temp_trans = []
        ratio = timer / self.tpf
        index = 0
        print("a", len(self.Rmat_origin))
        while index * ratio < len(self.Rmat_origin) - 1:
            a = index * ratio       #어느 위치의 값인지 지정
            floor = int(np.floor(a))     #내림
            ceil = int(floor + 1)       #올림
            pro = a - floor         #interpolation 비율
            temp_rot.append(slerp(self.Rmat_origin[floor], self.Rmat_origin[ceil], pro))
            temp_trans.append(lerp(self.trans_origin[floor], self.trans_origin[ceil], pro))
            index += 1
        self.Rmat_fps_set = temp_rot
        self.trans_fps_set = temp_trans
        self.Rmat_final = list(self.Rmat_fps_set)
        self.trans_final = list(self.trans_fps_set)
        self.frame = len(self.Rmat_final)
        for i in range(len(self.child)):
            self.child[i].fps_Sync(ratio)

