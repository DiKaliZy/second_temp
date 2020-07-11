import numpy as np
#import pyassimp
from OpenGL.GL import *

class BVHReader():
    def __init__(self):
        self.J_nowobj = None
        self.M_nowobj = None
        self.J_newobj = None
        self.M_newobj = None
        self.mode = None
        self.J_root = None
        self.M_root = None

    def LoadMesh(self, name):
        scene = pyassimp.load(name)
        self.load_model(scene)
        return scene

    def load_model(self, scene):
        #print(scene.rootnode.meshes[0].vertices)
        #print(len(scene.rootnode.meshes[0].vertices))
        #print(len(scene.rootnode.children[0].meshes))
        for index, mesh in enumerate(scene.meshes):
            self.prepare_gl_buffers(mesh)
        pyassimp.release(scene)

    def prepare_gl_buffers(self, mesh):
        mesh.gl = {}
        mesh.gl["vertices"] = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, mesh.gl["vertices"])
        glBufferData(GL_ARRAY_BUFFER,
                     mesh.vertices,
                     GL_STATIC_DRAW)
        print(mesh.vertices[48:60])
        # Fill the buffer for normals
        mesh.gl["normals"] = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, mesh.gl["normals"])
        glBufferData(GL_ARRAY_BUFFER,
                     mesh.normals,
                     GL_STATIC_DRAW)
        # Fill the buffer for vertex positions
        mesh.gl["triangles"] = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, mesh.gl["triangles"])
        glBufferData(GL_ELEMENT_ARRAY_BUFFER,
                     mesh.faces,
                     GL_STATIC_DRAW)
        print(mesh.faces)
        # Unbind buffers
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)

    def ReadFile(self, name, can_tpf, UseAssimp):
        scene = None
        filename = name.split('\\')
        filename = filename[len(filename) - 1]
        if UseAssimp == True:
            scene = self.LoadMesh(filename)

        file = open(name, 'r')
        temp = []
        lines = file.readlines()
        for line in lines:
            line = line.strip()
            line = line.replace(":","")
            line = line.split()

            if line[0] == "HIERARCHY":
                self.mode = 0
            elif line[0] == "MOTION":
                self.mode = 1

            if self.mode == 0:
                if line[0] == "JOINT":
                    self.J_newobj = BVH_Joint(line[1])
                    self.M_newobj = BVH_Motion(line[1])
                    self.J_newobj.motion = self.M_newobj
                elif line[0] == "ROOT":
                    self.J_newobj = BVH_Joint(line[1])
                    self.M_newobj = BVH_Motion_root(line[1])
                    self.J_newobj.motion = self.M_newobj
                    self.J_newobj.isRoot = True
                    self.M_newobj.isRoot = True
                elif line[0] == "OFFSET":
                    if self.J_nowobj.isRoot != True:
                        conv = list(map(float, line[1:4]))
                        self.J_nowobj.offset = conv
                    else:
                        self.J_nowobj.offset = [0,0,0]
                elif line[0] == "CHANNELS":
                    self.M_nowobj.channel = int(line[1])
                    endindex = len(line)
                    self.M_nowobj.order = line[2:endindex]
                elif line[0] == "End":
                    self.J_newobj = BVH_Joint(line[1])
                    self.J_newobj.isEnd = True
                    self.M_newobj = BVH_Motion(line[1])
                    self.M_newobj.isEnd = True
                    self.J_newobj.motion = self.M_newobj
                elif line[0] == "{":
                    if self.J_newobj.isRoot != True:
                        self.J_nowobj.addChild(self.J_newobj)
                        self.M_nowobj.addChild(self.M_newobj)
                        self.J_newobj.parent = self.J_nowobj
                        self.M_newobj.parent = self.M_nowobj
                        self.J_nowobj = self.J_newobj
                        self.M_nowobj = self.M_newobj
                    else:
                        self.J_nowobj = self.J_newobj
                        self.M_nowobj = self.M_newobj
                        self.J_root = self.J_nowobj
                        self.M_root = self.M_nowobj
                elif line[0] == "}":
                    self.J_nowobj = self.J_nowobj.parent
                    self.M_nowobj = self.M_nowobj.parent
            elif self.mode == 1:
                if line[0] == "Frames":
                    self.M_root.setFrame(int(line[1]))
                elif line[0] == "Frame":
                    self.M_root.setTPF(float(line[2]) * 1000)
                elif line[0] != "MOTION":
                    conv = list(map(float, line))
                    temp.append(conv)
        if UseAssimp != True:
            self.J_root.setMesh()
        else:
            self.J_root.setMesh(scene_node = scene.rootnode)
        for i in range(self.M_root.frame):
            self.M_root.loadData(temp[i])
        self.M_root.fps_Sync(can_tpf)
        file.close()
        return self.J_root

def MeshContent(start, end, m_type, mesh):
    diff = np.array(end) - np.array(start)
    length = np.sqrt(np.dot(diff, diff))
    thickness = length / 20
    if m_type == "BOX":
        '''
        a = np.array(end) + np.array([thickness, 0, -thickness])
        mesh.vertices.append(list(a))
        a = np.array(end) + np.array([-thickness, 0, -thickness])
        mesh.vertices.append(list(a))
        a = np.array(end) + np.array([-thickness, 0, thickness])
        mesh.vertices.append(list(a))
        a = np.array(end) + np.array([thickness, 0, thickness])
        mesh.vertices.append(list(a))
        a = np.array(start) + np.array([thickness, 0, thickness])
        mesh.vertices.append(list(a))
        a = np.array(start) + np.array([-thickness, 0, thickness])
        mesh.vertices.append(list(a))
        a = np.array(start) + np.array([-thickness, 0, -thickness])
        mesh.vertices.append(list(a))
        a = np.array(start) + np.array([thickness, 0, -thickness])
        mesh.vertices.append(list(a))
        '''

        mesh.vertices.append([-0., 0.07315201, 2.0688102])
        mesh.vertices.append([0., 20.6881, -0.73152])
        mesh.vertices.append([-2.0701032, 0., 0.])
        mesh.vertices.append([-2.0701032, 0., 0.])
        mesh.vertices.append([ 0., 20.6881, -0.73152])
        mesh.vertices.append([ 0., -0.07315201, -2.0688102])
        mesh.vertices.append([ 0., -0.07315201, -2.0688102])
        mesh.vertices.append([ 0., 20.6881, -0.73152])
        mesh.vertices.append([ 2.0701032, 0., 0.])
        mesh.vertices.append([ 2.0701032, 0., 0.])
        mesh.vertices.append([ 0., 20.6881, -0.73152])
        mesh.vertices.append([-0., 0.07315201, 2.0688102])

        mesh.faces.append([0,1,2])
        mesh.faces.append([3,4,5])
        mesh.faces.append([6,7,8])
        mesh.faces.append([9,10,11])

        '''
        mesh.faces.append([0, 1, 2])
        mesh.faces.append([0, 2, 3])
        mesh.faces.append([4, 5, 6])
        mesh.faces.append([4, 6, 7])
        mesh.faces.append([3, 2, 5])
        mesh.faces.append([3, 5, 4])
        mesh.faces.append([7, 6, 1])
        mesh.faces.append([7, 1, 0])
        mesh.faces.append([2, 1, 6])
        mesh.faces.append([2, 6, 5])
        mesh.faces.append([0, 3, 4])
        mesh.faces.append([0, 4, 7])
        '''

    elif m_type == "DIAMOND":
        ...
    elif m_type == "CORN":
        ...

def CreateMesh(start, end, m_type, mesh):
    mesh.gl = {}
    MeshContent(start, end, m_type, mesh)
    mesh.vertices = np.array(mesh.vertices)
    mesh.faces = np.array(mesh.faces)
    mesh.gl["vertices"] = glGenBuffers(1)

    glBindBuffer(GL_ARRAY_BUFFER, mesh.gl["vertices"])
    glBufferData(GL_ARRAY_BUFFER,
                 mesh.vertices,
                 GL_STATIC_DRAW)

    print(mesh.gl["vertices"])
    # Fill the buffer for normals
    mesh.gl["normals"] = glGenBuffers(1)
#    glBindBuffer(GL_ARRAY_BUFFER, mesh.gl["normals"])
#    glBufferData(GL_ARRAY_BUFFER,
#                 mesh.normals,
#                 GL_STATIC_DRAW)
    # Fill the buffer for vertex positions
    mesh.gl["triangles"] = glGenBuffers(1)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, mesh.gl["triangles"])
    glBufferData(GL_ELEMENT_ARRAY_BUFFER,
                 mesh.faces,
                 GL_STATIC_DRAW)
    print(mesh.faces)
    # Unbind buffers
    glBindBuffer(GL_ARRAY_BUFFER, 0)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)

    return mesh

class Mesh():
    def __init__(self):
        self.vertices = []
        self.normals = []
        self.faces = []
        self.gl = None

class BVH_Joint():
    def __init__(self, name):
        self.name = name
        self.offset = []
        self.parent = None
        self.motion = []
        self.meshes = []
        self.child = []
        self.check = 0
        self.isEnd = False
        self.isRoot = False

    def addChild(self, child):
        self.child.append(child)

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

    def setMotion(self, motion):
        if self.isEnd != True:
            self.motion = motion
            for i in range(len(self.child)):
                self.child[i].setMotion(motion.child[i])

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

    def SpeedDown(self, playSpeed):
        i = 1
        if self.isEnd != True:
            while i + 1 < (len(self.Rmat_final)):
                trans1 = np.array(self.Rmat_final[i])
                trans2 = np.array(self.Rmat_final[i+1])
                temp = (trans1 + trans2)/2
                R = slerp(self.Rmat_final[i], self.Rmat_final[i+1], 0.5)
                self.Rmat_final.insert(i+1,R)
                i += 2
            for i in range(len(self.child)):
                self.child[i].SpeedDown(playSpeed)

    def SpeedUp(self, playSpeed):
        i = 2
        if self.isEnd != True:
            while i < (len(self.Rmat_final)):
                del self.Rmat_final[i]
                i += 1
            for i in range(len(self.child)):
                self.child[i].SpeedUp(playSpeed)

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
            if self.order[i] == "XPOSITION":
                temp[0] = data[i]
            elif self.order[i] == "YPOSITION":
                temp[1] = data[i]
            elif self.order[i] == "ZPOSITION":
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

#==============================================================================

def lerp(T1, T2, t):
    T = (np.array(T1) * (1.0 - t)) + (np.array(T2) * t)
    return T

def slerp(R1,R2,t):
    R = (R1.T)@R2
    if np.arccos((R[0, 0] + R[1, 1] + R[2, 2] - 1)/2) == 0:
        ret = R1
    elif np.dot(t*log(R),t*log(R)) == 0:
        ret = R1
    else:
        ret = R1@exp(t*log((R1.T)@R2))
    return ret

def log(R):
    angl = np.arccos((R[0,0] + R[1,1] + R[2,2] -1)/2)

    v1 = (R[2,1]-R[1,2])/(2*np.sin(angl))
    v2 = (R[0,2]-R[2,0])/(2*np.sin(angl))
    v3 = (R[1,0]-R[0,1])/(2*np.sin(angl))
    r = np.array([v1,v2,v3]) * angl
    return r

def exp(rv):
    theta = l2norm(rv)
    axis = normalized(rv)
    R = getRotMatFrom(axis, theta)
    return R

def l2norm(v):
    return np.sqrt(np.dot(v, v))

def normalized(v):
    l = l2norm(v)
    return 1/l * np.array(v)

def getRotMatFrom(axis, theta):
    R = np.array([[np.cos(theta) + axis[0]*axis[0]*(1-np.cos(theta)),
                   axis[0]*axis[1]*(1-np.cos(theta))-axis[2]*np.sin(theta),
                   axis[0]*axis[2]*(1-np.cos(theta))+axis[1]*np.sin(theta)],
                  [axis[1]*axis[0]*(1-np.cos(theta))+axis[2]*np.sin(theta),
                   np.cos(theta)+axis[1]*axis[1]*(1-np.cos(theta)),
                   axis[1]*axis[2]*(1-np.cos(theta))-axis[0]*np.sin(theta)],
                  [axis[2]*axis[0]*(1-np.cos(theta))-axis[1]*np.sin(theta),
                   axis[2]*axis[1]*(1-np.cos(theta))+axis[0]*np.sin(theta),
                   np.cos(theta)+axis[2]*axis[2]*(1-np.cos(theta))]
                 ])
    return R

def change2RotMat(order,data):
    R = np.identity(3)
    for i in range(len(order)):
        if order[i] == "XROTATION":
            Rx = getRotMatFrom([1,0,0],np.radians(data[i]))
            R = R @ Rx
        elif order[i] == "YROTATION":
            Ry = getRotMatFrom([0,1,0], np.radians(data[i]))
            R = R @ Ry
        elif order[i] == "ZROTATION":
            Rz = getRotMatFrom([0,0,1], np.radians(data[i]))
            R = R @ Rz
    return R

def extract_pos(order, data):
    P = []
    for i in range(len(order)):
        if order[i] == "XPOSITION":
            P.append(data[i])
        elif order[i] == "YPOSITION":
            P.append(data[i])
        elif order[i] == "ZPOSITION":
            P.append(data[i])
    return P
