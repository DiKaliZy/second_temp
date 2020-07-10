from OpenGL.GL import *
import numpy as np

# mesh 미리 그려서 glDict에 저장
def GLCreateList(glDict, newName, drawFunction):
    newID = glGenLists(1)
    glNewList(newID, GL_COMPILE)
    drawFunction()
    glEndList()
    glDict[newName] = newID

def drawPlate():
    glBegin(GL_QUADS)
    glNormal3fv(np.array([0., 1., 0.]))
    glVertex3fv(np.array([0. , 0., 0.]))
    glVertex3fv(np.array([0. , 0., 1.]))
    glVertex3fv(np.array([1. , 0., 1.]))
    glVertex3fv(np.array([1. , 0., 0.]))

    glNormal3f(0.0, -1.0, 0.0)
    glVertex3f(1, -0.001, 0)
    glVertex3f(1, -0.001, 1)
    glVertex3f(0, -0.001, 1)
    glVertex3f(0, -0.001, 0)

    glNormal3f(0.0, 0.0, 1.0)
    glVertex3f(1, -0.001, 1)
    glVertex3f(0, -0.001, 1)
    glVertex3f(0, 0, 1)
    glVertex3f(1, 0, 1)

    glNormal3f(1.0, 0.0, 0.0)
    glVertex3f(1, 0, 1)
    glVertex3f(1, -0.001, 1)
    glVertex3f(1, -0.001, 0)
    glVertex3f(1, 0, 0)

    glNormal3f(0.0, 0.0, -1.0)
    glVertex3f(1, 0, 0)
    glVertex3f(1, -0.001, 0)
    glVertex3f(0, -0.001, 0)
    glVertex3f(0, 0, 0)

    glNormal3f(-1.0, 0.0, 0.0)
    glVertex3f(0, 0, 0)
    glVertex3f(0, -0.001, 0)
    glVertex3f(0, -0.001, 1)
    glVertex3f(0, 0, 1)

    glEnd()

def draw_mesh(type, start= (), end=None, glDict = None, size= None,
              x_size = None, y_size = None, z_size = None):
    if type == "LINE":
        glBegin(GL_LINES)
        glVertex3fv(start)
        glVertex3fv(end)
        glEnd()
    elif type == "PLATE":
        glCallList(glDict[type])
    else:
        glPushMatrix()
        if len(start)>0:
            glTranslatef(start[0],start[1],start[2])
        if size != None:
            if type == "SPHERE":
                glScale(size/10,size/10,size/10)
            elif type == "BOX":
                length = np.sqrt((np.array(end)-np.array(start)) @ np.transpose(np.array(end)-np.array(start)))
                area = size/(length*100)
                glScale(area, length, area)
        else:
            if x_size != None:
                glScalef(x_size, 1, 1)
            if y_size != None:
                glScalef(1, y_size, 1)
            if z_size != None:
                glScalef(1, 1, z_size)
        glCallList(glDict[type])
        glPopMatrix()

def drawBox():
    glBegin(GL_QUADS)
    glNormal3f(0.0, 0.0, 1.0)
    glVertex3f(0.5, 0.5, 0.5)
    glVertex3f(-0.5, 0.5, 0.5)
    glVertex3f(-0.5, -0.5, 0.5)
    glVertex3f(0.5, -0.5, 0.5)

    glNormal3f(1.0, 0.0, 0.0)
    glVertex3f(0.5, 0.5, 0.5)
    glVertex3f(0.5, -0.5, 0.5)
    glVertex3f(0.5, -0.5, -0.5)
    glVertex3f(0.5, 0.5, -0.5)

    glNormal3f(0.0, 0.0, -1.0)
    glVertex3f(0.5, 0.5, -0.5)
    glVertex3f(0.5, -0.5, -0.5)
    glVertex3f(-0.5, -0.5, -0.5)
    glVertex3f(-0.5, 0.5, -0.5)

    glNormal3f(-1.0, 0.0, 0.0)
    glVertex3f(-0.5, 0.5, -0.5)
    glVertex3f(-0.5, -0.5, -0.5)
    glVertex3f(-0.5, -0.5, 0.5)
    glVertex3f(-0.5, 0.5, 0.5)

    glNormal3f(0.0, -1.0, 0.0)
    glVertex3f(0.5, -0.5, -0.5)
    glVertex3f(0.5, -0.5, 0.5)
    glVertex3f(-0.5, -0.5, 0.5)
    glVertex3f(-0.5, -0.5, -0.5)

    glNormal3f(0.0, 1.0, 0.0)
    glVertex3f(-0.5, 0.5, -0.5)
    glVertex3f(-0.5, 0.5, 0.5)
    glVertex3f(0.5, 0.5, 0.5)
    glVertex3f(0.5, 0.5, -0.5)

    glEnd()

def drawSphere(numLats=10, numLongs=5):
    for i in range(0, numLats + 1):
        lat0 = np.pi * (-0.5 + float(float(i-1)/float(numLats)))
        z0 = np.sin(lat0)
        zr0 = np.cos(lat0)

        lat1 = np.pi * (-0.5 + float(float(i) / float(numLats)))
        z1 = np.sin(lat1)
        zr1 = np.cos(lat1)

        glBegin(GL_QUAD_STRIP)

        for j in range(0, numLongs + 1):
            lng = 2*np.pi * float(float(j-1)/float(numLongs))
            x = np.cos(lng)
            y = np.sin(lng)
            glVertex3f(x*zr0,y*zr0,z0)
            glVertex3f(x*zr1,y*zr1,z1)

        glEnd()