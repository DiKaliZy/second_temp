import numpy as np

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
        if order[i] == "Xrotation" or order[i] == "XROTATION":
            Rx = getRotMatFrom([1,0,0],np.radians(data[i]))
            R = R @ Rx
        elif order[i] == "Yrotation" or order[i] == "YROTATION":
            Ry = getRotMatFrom([0,1,0], np.radians(data[i]))
            R = R @ Ry
        elif order[i] == "Zrotation" or order[i] == "ZROTATION":
            Rz = getRotMatFrom([0,0,1], np.radians(data[i]))
            R = R @ Rz
    return R

def extract_pos(order, data):
    P = []
    for i in range(len(order)):
        if order[i] == "Xposition" or order[i] == "XPOSITION":
            P.append(data[i])
        elif order[i] == "Yposition" or order[i] == "YPOSITION":
            P.append(data[i])
        elif order[i] == "Zposition" or order[i] == "ZPOSITION":
            P.append(data[i])
    return P
