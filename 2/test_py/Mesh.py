import numpy as np
from OpenGL.GL import *

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
