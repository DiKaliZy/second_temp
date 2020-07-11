import wx
from wx import glcanvas
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import numpy as np
import mesh

class GLCanvasBase(glcanvas.GLCanvas):
    def __init__(self, parent):
        glcanvas.GLCanvas.__init__(self, parent, -1)
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

        self.skeleton_view = True   #line으로 골격만 표현
        self.frame_view = True      #mesh, frame 설정

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
        elif keycode == wx.WXK_TAB:
            if self.skeleton_view == True:
                self.skeleton_view = False
            else:
                self.skeleton_view = True
        # Z키 입력 - polygon / frame 전환
        elif keycode == ord('Z'):
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

        gluPerspective(45, 1, 1., 1000)

        glDepthFunc(GL_LESS)
        glEnable(GL_DEPTH_TEST)
        glDepthMask(GL_TRUE)
        glClearDepth(1.)

    def OnDraw(self):
        gridlane = 10
        gridscale = 1
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

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
        #glEnable(GL_POLYGON_OFFSET_LINE)
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
        glLightfv(GL_LIGHT0, GL_POSITION, [-100., 130., 150., 1.])
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
        else:
            glColor3f(0.95, 0.95, 0.95)
            mesh.drawBox()

    def draw_bvh_motion(self, nowsee):
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

            #draw skeleton
            glPushMatrix()

            start = np.array([0,0,0])
            for child in nowsee.child:
                glColor3ub(200, 200, 200)
                end = np.array(child.offset)
                if self.skeleton_view == True:
                    if nowsee.model.focused == True:
                        glColor3f(0.9,0.3,0.3)
                    elif nowsee.model.pinned == True:
                        glColor3f(0.3, 0.9, 0.3)
                    else:
                        pass
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
                    mesh.draw_mesh("BOX", start=start, end=end, glDict=self.glDict, size=1)

                    #재생 조작 선택 대상 윤곽선 그리기
                    if nowsee.model.focused == True:
                        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
                        glColor3f(0.9, 0.3, 0.3)
                        mesh.draw_mesh("BOX", start=start, end=end, glDict=self.glDict, size=1)
                    elif nowsee.model.pinned == True:
                        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
                        glColor3f(0.3, 0.9, 0.3)
                        mesh.draw_mesh("BOX", start=start, end=end, glDict=self.glDict, size=1)
                    if self.frame_view == False:
                        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

                    glPopMatrix()
                    #total_offset_vec += parent2child
            glPopMatrix()

            for child in nowsee.child:
                self.draw_bvh_motion(child)

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