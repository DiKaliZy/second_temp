import wx
from wx import glcanvas
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import numpy as np
import mesh
import utility
from wx.glcanvas import *

import temp

class GLCanvasBase(glcanvas.GLCanvas):
    def __init__(self, parent):

        #linux ubuntu 환경에서 DEPTH_TEST 제대로 작동시키기 위해 필요한 부분.
        #왜 이렇게 해야 작동하는지는 모르겠음.
        #참조 주소 :
        #https://discuss.wxpython.org/t/opengl-depth-buffer-deosnt-seem-to-work-in-wx-glcanvas/27513/10
        attribs = [WX_GL_RGBA, WX_GL_DOUBLEBUFFER, WX_GL_DEPTH_SIZE, 24]
        glcanvas.GLCanvas.__init__(self, parent, -1, attribList=attribs)

        self.frame = parent.GetParent()
        self.init = False
        self.shift = False
        self.clicked = False
        self.at = np.array([0, 0, 0])
        self.up = np.array([0, 1, 0])
        self.leng = 10
        self.azimuth = np.radians(30)
        self.elevation = np.radians(30)
        self.cam = np.array([self.leng * np.sin(self.azimuth), self.leng * np.sin(self.elevation), self.leng * np.cos(self.azimuth)])

        self.model_list = []
        self.timeset =  (1/30) * 1000   #ms단위
        self.isrepeat = True
        self.pause = False
        self.timer = wx.Timer(self)

        self.skeleton_view = False   #line으로 골격만 표현
        self.frame_view = False      #mesh, frame 설정

        self.modelID = []

        self.playSpeed = 2      #0 = 0.25배, 1 = 0.5배, 2= 1배

        self.slider = []

        self.model = None

        self.context = glcanvas.GLContext(self)

        self.timer.Start(self.timeset)

        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_RIGHT_DOWN, self.OnMouseDown)  #camera rotate
        self.Bind(wx.EVT_RIGHT_UP, self.OnMouseUp)
        self.Bind(wx.EVT_MOTION, self.OnMouseMotion)
        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)  #shift + mouse drag -> camera move
        self.Bind(wx.EVT_KEY_UP, self.OnKeyUp)
        self.Bind(wx.EVT_MOUSEWHEEL, self.Wheel)    #zoom in, zoom out
        self.Bind(wx.EVT_TIMER, self.OnTime)

    def OnSize(self, event):
        wx.CallAfter(self.DoSetViewport)
        event.Skip()

    def DoSetViewport(self):
        size = self.size = self.GetClientSize()
        self.SetCurrent(self.context)
        glViewport(0, 0, size.width, size.height)

    def OnTime(self, event):
        self.Refresh()

    #마우스 클릭 조작
    def OnMouseDown(self, event):
        self.CaptureMouse()
        self.mx, self.my = self.lastmx, self.lastmy = event.GetPosition()
        if self.clicked == False:
            self.clicked = True
        else:
            event.Skip()

    def OnMouseUp(self, event):
        self.ReleaseMouse()
        self.clicked = False

    #마우스 움직임 조작
    def OnMouseMotion(self, event):
        if self.clicked == True:
            self.lastmx, self.lastmy = self.mx, self.my
            self.mx, self.my = event.GetPosition()
            normy = (self.my - self.lastmy) * np.sqrt(np.dot(self.cam - self.at, self.cam - self.at)) / 120
            normx = -(self.mx - self.lastmx) * np.sqrt(np.dot(self.cam - self.at, self.cam - self.at)) / 120
            normry = (self.my - self.lastmy) / 100
            normrx = -(self.mx - self.lastmx) / 100
            #Camera Panning
            if self.shift == True:
                self.getWUV()
                paramU = self.u * normx
                paramV = self.v * normy
                param = paramU + paramV
                self.cam = self.cam + param
                self.at = self.at + param

                self.Refresh(False)

            #Camera Rotate(Orbit)
            elif self.shift == False:
                None
                self.leng = np.sqrt(np.dot(self.cam - self.at, self.cam - self.at))

                # Elevation
                if self.elevation + normry <= np.radians(90) and self.elevation + normry >= np.radians(-90):
                    self.elevation += normry
                elif self.elevation + normry >= np.radians(90):
                    self.elevation = np.radians(89.9)
                elif self.elevation + normry <= np.radians(-90):
                    self.elevation = np.radians(-89.9)
                #Azirmuth
                self.azimuth += normrx
                self.cam = np.array([self.leng * np.cos(self.elevation) * np.sin(self.azimuth),
                                     self.leng * np.sin(self.elevation),
                                     self.leng * np.cos(self.elevation) * np.cos(self.azimuth)])
                self.cam += self.at
                self.Refresh(False)
        else:
            event.Skip()

    #키 입력
    def OnKeyDown(self, event):
        move = 2    # 키보드 입력으로 이동시킬 frame 수
        keycode = event.GetKeyCode()
        if keycode == wx.WXK_SHIFT:
            if self.shift == False:
                self.shift = True
            else:
                event.Skip()
        elif keycode == wx.WXK_SPACE:
            for model in self.model_list:
                if model.focused == True or model.pinned == True:
                    if model.played == False:
                        model.played = True
                    else:
                        model.played = False
        elif keycode == wx.WXK_LEFT:
            for model in self.model_list:
                if model.focused == True or model.pinned == True:
                    model.played = False
                    #start frame이 end frame보다 작은 경우
                    if model.start_frame <= model.end_frame:
                        if model.frame - move >= model.start_frame:
                            model.frame += -move
                        else:
                            model.frame = model.start_frame
                    #start frame이 end frame보다 큰 경우
                    else:
                        if not(model.frame - move < model.start_frame and model.frame - move >= model.end_frame):
                            if model.frame - move < 0:
                                model.frame = model.max_frame - (move - model.frame)
                            else:
                                model.frame += -move
                        else:
                            model.frame = model.start_frame
                if model.focused == True:
                    self.frame.play_slider.SetValue(model.frame)
            self.Refresh()
        elif keycode == wx.WXK_RIGHT:
            for model in self.model_list:
                if model.focused == True or model.pinned == True:
                    model.played = False
                    # start frame이 end frame보다 작은 경우
                    if model.start_frame <= model.end_frame:
                        if model.frame + move <= model.end_frame:
                            model.frame += move
                        else:
                            model.frame = model.end_frame
                    # start frame이 end frame보다 큰 경우
                    else:
                        if not (model.frame + move < model.start_frame and model.frame + move >= model.end_frame):
                            if model.frame + move > model.max_frame:
                                model.frame = 0 + (model.frame + move - model.max_frame)
                            else:
                                model.frame += move
                        else:
                            model.frame = model.end_frame
                if model.focused == True:
                    self.frame.play_slider.SetValue(model.frame)
            self.Refresh()
        elif keycode == wx.WXK_UP:
            ...
        elif keycode == wx.WXK_DOWN:
            ...
        #mesh/skeleton 전환
        elif keycode == ord('Z'):
            if self.skeleton_view == True:
                self.skeleton_view = False
            else:
                self.skeleton_view = True
        # Z키 입력 - polygon / frame 전환
        elif keycode == ord('X'):
            if self.frame_view == True:
                self.frame_view = False
            else:
                self.frame_view = True
        else:
            event.Skip()

    def OnKeyUp(self, event):
        if event.GetKeyCode() == wx.WXK_SHIFT:
            self.shift = False
        else:
            event.Skip()

    #마우스 휠 -> 줌인, 줌아웃
    def Wheel(self, event):
        self.getWUV()
        paramW = self.w * 5
        #wheel up -> zoom in
        if event.GetWheelRotation() > 0:
            if np.sqrt(np.dot(self.cam - paramW - self.at, self.cam - paramW - self.at)) >= np.sqrt(np.dot(paramW, paramW)):
                self.cam = self.cam - paramW
                self.Refresh(False)
            elif np.sqrt(np.dot(self.cam - self.w - self.at, self.cam - self.w - self.at)) >= 2*np.sqrt(np.dot(self.w, self.w)):
                self.cam = self.cam - self.w
                self.Refresh(False)
            else:
                event.Skip()
        #wheel down -> zoom out
        elif event.GetWheelRotation() < 0:
            self.cam = self.cam + paramW
            self.Refresh(False)
        else:
            event.Skip()

    def OnEraseBackground(self, event):
        pass # Do nothing, to avoid flashing on MSW.

    def OnPaint(self, event):
        dc = wx.PaintDC(self)
        self.SetCurrent(self.context)
        if not self.init:
            self.InitGL()
            self.init = True
        self.OnDraw()

    #카메라 좌표 계산
    def getWUV(self):
        self.w = (self.cam - self.at)/np.sqrt(np.dot((self.cam - self.at),(self.cam - self.at)))
        if np.dot(np.cross(self.up, self.w),np.cross(self.up, self.w)) != 0:
            self.u = np.cross(self.up, self.w)/np.sqrt(np.dot(np.cross(self.up, self.w),np.cross(self.up, self.w)))
        else:
            self.u = np.array([np.sin(self.azimuth),0,np.cos(self.azimuth)])
        self.v = np.cross(self.w, self.u)/np.sqrt(np.dot(np.cross(self.w, self.u),np.cross(self.w, self.u)))

class Canvas(GLCanvasBase):

    def InitGL(self):

        self.light_pos = [0., 50., 20., 1.]
        self.glDict = {}
        self.model_list = self.frame.models.model_list

        mesh.GLCreateList(self.glDict, 'SPHERE', mesh.drawSphere)
        mesh.GLCreateList(self.glDict, 'BOX', mesh.drawBox)
        mesh.GLCreateList(self.glDict, 'PLATE', mesh.drawPlate)

        glShadeModel(GL_SMOOTH)
        glClearColor(0.96,0.96,0.9,1.)

        glEnable(GL_CULL_FACE)
        #glCullFace(GL_BACK)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        gluPerspective(45, 1., 1., 1000)

        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)
        #glDepthRange(0, 1)
        glDepthMask(GL_TRUE)
        glClearDepth(1.)

    def OnDraw(self):
        gridlane = 10
        gridscale = 1
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        # gluLookAt(self.light_pos[0], self.light_pos[1], self.light_pos[2], self.at[0], self.at[1], self.at[2], 0, 1, 0)
        gluLookAt(self.cam[0], self.cam[1], self.cam[2], self.at[0], self.at[1], self.at[2], 0, 1, 0)

        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        #draw checker_box
        for i in range(-2 * gridlane, 2 * gridlane + 1):
            for j in range(-2 * gridlane, 2 * gridlane + 1):
                glPushMatrix()
                glScale(gridscale, gridscale, gridscale)
                if (j + i) % 2 == 0:
                    glColor3f(1., 1., 1.)
                    glTranslatef(i, 0., j)
                    mesh.draw_mesh("PLATE", glDict = self.glDict)
                else:
                    glColor3f(.7, .7, .7)
                    glTranslatef(i, 0., j)
                    mesh.draw_mesh("PLATE", glDict = self.glDict)
                glPopMatrix()

        # draw grid
        glColor3f(0.3, 0.3, 0.3)
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

        glBegin(GL_LINES)
        for i in range(-2 * gridlane, gridlane * 2 + 2):
            glVertex3fv(np.array([i * gridscale, 0.001, gridlane * gridscale * 2 + 1]))
            glVertex3fv(np.array([i * gridscale, 0.001, gridlane * -gridscale * 2]))
            glVertex3fv(np.array([gridlane * gridscale * 2 + 1, 0.001, gridscale * i]))
            glVertex3fv(np.array([gridlane * -gridscale * 2, 0.001, gridscale * i]))
        glEnd()

        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_RESCALE_NORMAL)
        glEnable(GL_NORMALIZE)

        glLightfv(GL_LIGHT0, GL_AMBIENT, [0.3, 0.3, 0.3, 1.])
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.3, 0.3, 0.3, 1.])
        glLightfv(GL_LIGHT0, GL_POSITION, self.light_pos)
        glLightfv(GL_LIGHT0, GL_SPECULAR, [1.,1.,1.,1.])

        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT,GL_AMBIENT_AND_DIFFUSE)
        glMaterialfv(GL_FRONT, GL_SPECULAR, [1., 1., 1., 1.])
        glMaterialfv(GL_FRONT, GL_SHININESS, 10)

        if self.frame_view == False:
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

        self.draw_model()
        glDisable(GL_LIGHTING)

        self.SwapBuffers()

    #model별 그림자
    def draw_shadow(self, model, light_pos):
        for joint in model.joint:
            start = np.array(
                [joint.motion_pos[model.frame][0], joint.motion_pos[model.frame][1], joint.motion_pos[model.frame][2]])
            for child in joint.child:
                end = np.array([child.motion_pos[model.frame][0], child.motion_pos[model.frame][1],
                                child.motion_pos[model.frame][2]])

                #각 관절 별 projection 좌표 구하기
                projection_mat = np.identity(4)
                projection_mat[:3, :4] = utility.spot_light_projection_mat(light_pos, start)
                shadow_start = projection_mat @ np.append(start, np.array([1.]))
                start = shadow_start[:3]
                projection_mat = np.identity(4)
                projection_mat[:3, :4] = utility.spot_light_projection_mat(light_pos, end)
                shadow_end = projection_mat @ np.append(end, np.array([1.]))
                end = shadow_end[:3]

                if self.skeleton_view == True:
                    mesh.draw_mesh("LINE", start=start, end=end)
                else:
                    parent2child = end - start
                    newy = (parent2child) / np.sqrt((parent2child) @ np.transpose(parent2child))
                    if newy[0] == 0. and newy[1] == 1. and newy[2] == 0.:
                        rotmat = np.identity(3)
                    else:
                        rotaxis = np.cross(newy, np.array([0, 1, 0]))
                        rotaxis = rotaxis / np.sqrt(rotaxis @ np.transpose(rotaxis))
                        newz = np.cross(rotaxis, newy)
                        newz = newz / np.sqrt(newz @ np.transpose(newz))
                        rotmat = np.column_stack((rotaxis, newy, newz))

                    glPushMatrix()

                    glTranslatef(start[0] + parent2child[0] / 2, 0.0001, start[2] + parent2child[2] / 2)

                    mat = np.identity(4)
                    mat[:3, :3] = rotmat
                    glMultMatrixf(mat.T)

                    a = end[0] - start[0]
                    b = end[2] - start[2]

                    mesh.draw_mesh("BOX",
                                   start=np.array([0, 0, 0]),
                                   end=np.array([a, 0, b]),
                                   glDict=self.glDict, size=joint.scale)
                    glPopMatrix()

    #모델 그리기
    def draw_model(self):
        if len(self.model_list) > 0 :
            for model in self.model_list:
                root = model.joint_root
                glPushMatrix()
                #model 그리는 local origin coordinate 변경
                glTranslatef(model.model_origin[0], model.model_origin[1], model.model_origin[2])
                #model scal 보정
                glScalef(model.model_scale, model.model_scale, model.model_scale)

                #frame당 모션 그리기
                self.draw_bvh_motion(root)
                glPopMatrix()

                glPushMatrix()
                #그림자 그리기 위해 lighting 제거
                glDisable(GL_LIGHTING)
                glColor3f(0.2, 0.2, 0.2)
                #====================================================================================
                #현재 구현은 단순히 그림자를 xz평면에 각 관절 좌표값을 투영하여 기존 model을 그리듯이 xz 평면 상에 그린 것
                #최소 목표 : 광원에 따른 projection matrix를 구해서 draw_shadow 호출 할 필요 없이
                #           glMultMatrix 후 draw model 하면 바로 그림자 그려지도록 하기
                #가능하면 shadow map 같은 거 써서 구현할 수 있도록 해 보기? 

                # 1. spot light 환경에서 각 관절 별 projection 좌표 구해서 hierarchical하게 하나하나 그리는 방식
                #(spot light : 광원에서 나온 빛이 방사형으로 쏘아져 각 부분별로 다르게 projection)
                #self.draw_shadow(model, self.light_pos)
                #=====================================================================================
                # 2. direction light 환경에서 light source 좌표와 root 좌표가 이루는 vector를 light direction으로 정해서 projection
                # (direction light : 이론상 광원이 무한대 떨어진 거리에 위치하여 모든 vertex가 동일한 direction의 빛을 받는다 가정)
                projection = np.identity(4)
                projection[:3, :4] = utility.direction_light_projection_mat(self.light_pos,
                                                                            root.motion_pos[model.frame])
                glMultMatrixf(projection.T)
                self.draw_bvh_motion(root, shadow= True)
                #=====================================================================================
                glPopMatrix()
                glEnable(GL_LIGHTING)
        else:
            glColor3f(0.95, 0.95, 0.95)
            mesh.drawBox()

    def draw_bvh_motion(self, nowsee, shadow = False):
        M = np.identity(4)
        if len(nowsee.child) != 0:
            rot_matrix = nowsee.motion_rot[nowsee.model.frame]
            glPushMatrix()
            glTranslatef(nowsee.offset[0], nowsee.offset[1], nowsee.offset[2])
            if nowsee.root == True:
                trans_mat = nowsee.motion_pos[nowsee.model.frame]
                glTranslatef(trans_mat[0], trans_mat[1], trans_mat[2])
            M[:3, :3] = rot_matrix
            glMultMatrixf(M.T)

            glPushMatrix()

            start = np.array([0,0,0])
            for child in nowsee.child:
                end = np.array(child.offset)

                # draw skeleton
                if self.skeleton_view == True and shadow == False:
                    if nowsee.model.focused == True:
                        glColor3f(0.9, 0.3, 0.3)
                    elif nowsee.model.pinned == True:
                        glColor3f(0.3, 0.9, 0.3)
                    else:
                        glColor3f(0.5, 0.5, 0.5)
                    mesh.draw_mesh("LINE", start=start, end=end)

                else:
                    parent2child = end - start
                    newy = (parent2child) / np.sqrt((parent2child) @ np.transpose(parent2child))
                    if newy[0] == 0. and newy[1] == 1. and newy[2] == 0.:
                        rotmat = np.identity(3)
                    else:
                        rotaxis = np.cross(newy, np.array([0, 1, 0]))
                        rotaxis = rotaxis / np.sqrt(rotaxis @ np.transpose(rotaxis))
                        newz = np.cross(rotaxis, newy)
                        newz = newz / np.sqrt(newz @ np.transpose(newz))
                        rotmat = np.column_stack((rotaxis, newy, newz))

                    glPushMatrix()
                    glTranslatef(parent2child[0] / 2, parent2child[1] / 2, parent2child[2] / 2)
                    mat = np.identity(4)
                    mat[:3, :3] = rotmat
                    glMultMatrixf(mat.T)

                    #재생 조작 선택 대상 윤곽선 그리기
                    if nowsee.model.focused == True and shadow == False:
                        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
                        glColor3f(0.9, 0.3, 0.3)
                    elif nowsee.model.pinned == True and shadow == False:
                        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
                        glColor3f(0.3, 0.9, 0.3)
                    mesh.draw_mesh("BOX", start=start, end=end, glDict=self.glDict, size=nowsee.scale)
                    if self.frame_view == False and shadow == False:
                        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
                        glColor3f(0.5, 0.5, 0.5)
                        mesh.draw_mesh("BOX", start=start, end=end, glDict=self.glDict, size=nowsee.scale)

                    glPopMatrix()
                    #total_offset_vec += parent2child
            glPopMatrix()

            for child in nowsee.child:
                self.draw_bvh_motion(child, shadow)

            glPopMatrix()

    def OnTime(self, event):
        if len(self.frame.models.model_list)>0:
            for index in range(len(self.frame.models.model_list)):
                if self.frame.models.model_list[index].played == True:
                    end_frame = self.frame.models.model_list[index].end_frame
                    if self.frame.models.model_list[index].frame + 1 <= self.frame.models.model_list[index].max_frame:
                        if self.frame.models.model_list[index].frame != end_frame:
                            self.frame.models.model_list[index].frame += 1
                            #slider 갱신
                            if self.frame.models.model_list[index].focused == True:
                                self.frame.play_slider.SetValue(self.frame.models.model_list[index].frame)
                        else:
                            self.frame.models.model_list[index].frame = self.frame.models.model_list[index].start_frame
                    else:
                        #if self.frame.models.modelisrepeat == True:
                        self.frame.models.model_list[index].frame = 0
        self.Refresh()