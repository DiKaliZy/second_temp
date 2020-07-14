import wx
from wx import glcanvas
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import numpy as np
import mesh
from wx.glcanvas import *
import utility

def draw_shadow(self, model, light_pos):
    for joint in model.joint:
        start = np.array([joint.motion_pos[model.frame][0], joint.motion_pos[model.frame][1], joint.motion_pos[model.frame][2]])
        for child in joint.child:
            end = np.array([child.motion_pos[model.frame][0], child.motion_pos[model.frame][1], child.motion_pos[model.frame][2]])
            if self.skeleton_view == True:
                mesh.draw_mesh("LINE", start=start, end=end)
            else:
                projection_mat = np.identity(4)
                projection_mat[:3, :4] = utility.spot_light_projection_mat(light_pos,
                                                                                start)
                shadow_start = projection_mat @ np.append(start, np.array([1.]))
                start = shadow_start[:3]
                projection_mat = np.identity(4)
                projection_mat[:3, :4] = utility.spot_light_projection_mat(light_pos,
                                                                                end)
                shadow_end = projection_mat @ np.append(end, np.array([1.]))
                end = shadow_end[:3]

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