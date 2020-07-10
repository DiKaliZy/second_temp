#motion 관련 data
import utility
import numpy as np

class Models():
    def __init__(self):
        self.model_list = []

class Model():
    def __init__(self):
        self.model_name=''     #model file name   (bvh면 motion_name과 동일)
        self.file_type=''       #model 확장자
        self.motion_name = ''  # motion file name

        #focus는 기본적으로 재생 관련 기능 1순위 대상, pinned는 2순위
        self.focused=False      #현재 combo box 선택중인지(삭제, 모션 데이터 교체 대상 등 파일 관련)
        self.pinned=False       #pin 설정 되어 있는지(재생 관련만)
        self.played = False  # 재생 중인지 아닌지

        #model 관련
        self.joint_num = 0      #joint 개수
        self.joint = []         #joint list
        self.joint_root=None    #joint root
        self.model_origin = [0, 0, 0]   #model 자체 local origin 좌표
        self.model_scale = 1        #model 크기 보정

        #frame 관련
        self.fps=0              #fps
        self.max_frame = 0  # maximum frame
        self.frame = 0         #current frame
        self.start_frame = 0    #구간 반복 start frame
        self.end_frame = 0      #구간 반복 end frame

    def print_hierarchy(self, now_see):
        print("name : ", now_see.name)
        print("children # : ", len(now_see.child))
        if now_see.root != True:
            print("parent :", now_see.parent.name)
        print("----------------------------")
        if now_see.name[:3] != 'End':
            for child in now_see.child:
                self.print_hierarchy(child)
        else:
            pass

    def bvh_motion_injection(self, now_see, motion_list):
        motion_dat = []
        if now_see.name[:3] != 'End':
            channel = len(now_see.order)
            for i in range(channel):
                motion_dat.append(motion_list.pop(0))
            now_see.motion_dat.append(motion_dat)
            now_see.bvh_separate_motion_dat(motion_dat)
            for child in now_see.child:
                self.bvh_motion_injection(child, motion_list)
        else:
            pass

class Joint():
    def __init__(self, name, model):
        self.name = name      #joint name
        self.model = model    #집합 대상

        self.motion_dat = []    #motion data

        self.child = []  # hierarchical child
        self.parent = None  # hierarchical parent
        self.root = False    # root

        # bvh
        self.motion_rot = []
        self.motion_pos = []
        self.offset = []  # joint offset
        self.order = []  # position 및 rotation 순서 (x/y/z 순서)

    #rotation 및 euler rot angle을 변환하여 저장
    def bvh_separate_motion_dat(self, motion_dat):
        #print(self.order)
        #print(motion_dat)
        #print(self.name)
        R = np.identity(3)
        for i in range(len(self.order)):
            if self.order[i] == "Xrotation" or self.order[i] == "XROTATION":
                Rx = utility.getRotMatFrom([1, 0, 0], np.radians(motion_dat[i]))
                R = R @ Rx
            elif self.order[i] == "Yrotation" or self.order[i] == "YROTATION":
                Ry = utility.getRotMatFrom([0, 1, 0], np.radians(motion_dat[i]))
                R = R @ Ry
            elif self.order[i] == "Zrotation" or self.order[i] == "ZROTATION":
                Rz = utility.getRotMatFrom([0, 0, 1], np.radians(motion_dat[i]))
                R = R @ Rz

        self.motion_rot.append(R)
        if self.root == True:
            P = []
            for i in range(len(self.order)):
                if self.order[i] == "Xposition" or self.order[i] == "XPOSITION":
                    P.append(motion_dat[i])
                elif self.order[i] == "Yposition" or self.order[i] == "YPOSITION":
                    P.append(motion_dat[i])
                elif self.order[i] == "Zposition" or self.order[i] == "ZPOSITION":
                    P.append(motion_dat[i])
            self.motion_pos.append(P)