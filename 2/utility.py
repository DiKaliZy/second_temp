import numpy as np

def lerp(T1, T2, t):
    T = (np.array(T1) * (1.0 - t)) + (np.array(T2) * t)
    return T

def slerp(R1,R2,t):
    R = (R1.T)@R2
    if R[0, 0] > 1.0:
        R[0, 0] = 1.0
    if R[1, 1] > 1.0:
        R[1, 1] = 1.0
    if R[2, 2] > 1.0:
        R[2, 2] = 1.0
    '''if R[0, 0] == 1.0 or R[1, 1] == 1.0 or R[2, 2] == 1.0 :
        print("R", R)
        print("resul : ", R[0, 0] , R[1, 1] , R[2, 2])'''
    if np.arccos((R[0, 0] + R[1, 1] + R[2, 2] - 1)/2) == 0:
        ret = R1
    elif np.dot(t*log(R),t*log(R)) == 0:
        ret = R1
    else:
        ret = R1@exp(t*log((R1.T)@R2))
    return ret

def log(R):
    angl = np.arccos((R[0, 0] + R[1, 1] + R[2, 2] - 1)/2)
    if angl != 0:
        v1 = (R[2, 1]-R[1, 2])/(2*np.sin(angl))
        v2 = (R[0, 2]-R[2, 0])/(2*np.sin(angl))
        v3 = (R[1, 0]-R[0, 1])/(2*np.sin(angl))
        r = np.array([v1, v2, v3]) * angl
    else:
        v1 = (R[2, 1] - R[1, 2])
        v2 = (R[0, 2] - R[2, 0])
        v3 = (R[1, 0] - R[0, 1])
        r = np.array([v1, v2, v3])
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

#euler rotation angle 받아서 rotation matrix 생성
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


def gen_rotmat(origin, target):
    ori = (origin) / np.sqrt((origin) @ np.transpose(origin))
    targ = (target) / np.sqrt((target) @ np.transpose(target))
    rotaxis = np.cross(ori, targ)
    rotaxis = rotaxis / np.sqrt(rotaxis @ np.transpose(rotaxis))
    newz = np.cross(rotaxis, targ)
    newz = newz / np.sqrt(newz @ np.transpose(newz))
    aftrot = np.column_stack((targ, rotaxis, newz))
    befz = np.cross(rotaxis, origin)
    befz = befz / np.sqrt(befz @ np.transpose(befz))
    befrot = np.column_stack((origin, rotaxis, befz))
    if np.linalg.det(befrot) == 0:
        rotmat = np.identity(3)
    else:
        rotmat = aftrot * np.linalg.inv(befrot)
    mat = np.identity(4)
    mat[:3, :3] = rotmat

    return mat, rotmat

def spot_light_projection_mat(light_source, root_loc):
    start = np.array(light_source[:3])
    end = np.array(root_loc)
    direction_vec = normalized(start - end)
    t = (-end[1]) / direction_vec[1]
    proj_vec_x = np.array([1, 0, 0, t * direction_vec[0]])
    proj_vec_y = np.array([0, 0, 0, 0.001])
    proj_vec_z = np.array([0, 0, 1, t * direction_vec[2]])
    projection_mat = np.row_stack((proj_vec_x, proj_vec_y, proj_vec_z))
    return projection_mat
