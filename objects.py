import numpy as np
from OpenGL.GL import *
from matplotlib import pyplot as plt

class Body:
    def __init__(self):
        self.COM = np.array([0,0,0])
        self.basis = np.array([[1., 0., 0.],
                               [0., 1., 0.],
                               [0., 0., 1.]])
        
        self.shapes = np.array([], dtype=object)
        
    def calculate_COM(self):
        if len(self.shapes) == 1:
            self.COM = self.shapes[0].COM
        else:
            xs, ys, zs = np.array([s.COM for s in self.shapes]).T
            self.COM = np.array([np.mean(xs),
                                 np.mean(ys),
                                 np.mean(zs)])
        
    def add(self, shape):
        self.shapes = np.append(self.shapes, shape)
        shape.parent = self
        self.calculate_COM()
    
    def remove(self, shape):
        i = np.where(self.shapes == shape)
        self.shapes = np.delete(self.shapes, i)
        shape.parent = None
        
    def plot(self):
        glPointSize(5)
        glColor3f(1,1,0)
        glBegin(GL_POINTS)
        glVertex3f(*self.COM)
        glEnd()


        # ax.plot(self.COM[0], self.COM[1], self.COM[2], "ro")
        
        # basis_colors = np.array(["red", "green", "blue"])
        # for c, b in enumerate(self.basis.T):
        #     ax.plot(
        #         [self.COM[0], self.COM[0]+b[0]],
        #         [self.COM[1], self.COM[1]+b[1]],
        #         [self.COM[2], self.COM[2]+b[2]],
        #         color=basis_colors[c]
        #         )
            
        for s in self.shapes:
            s.plot()
            
    def scale(self, scale, global_scale=False):
        if type(scale) == int or type(scale) == float:
            scale = scale * np.ones(3)
        scale_matrix = np.diag(scale)
        
        if global_scale:
            self.COM = np.dot(scale_matrix, self.COM)
            for s in self.shapes:
                s.COM = np.dot(scale_matrix, s.COM)
                s.basis = np.dot(scale_matrix, s.basis)
        else:
            for s in self.shapes:
                s.COM = np.dot(scale_matrix, s.COM - self.COM) + self.COM
                s.basis = np.dot(scale_matrix, s.basis)
        
            
            
    
    def move(self, offset):
        self.COM += offset
        for s in self.shapes:
            s.COM += offset
    
    def rotate(self, axis, angle, global_rotate=False):
        angle = np.radians(angle)
        axis = axis / np.linalg.norm(axis)
        
        q = np.array([axis[0] * np.sin(angle/2),
                      axis[1] * np.sin(angle/2),
                      axis[2] * np.sin(angle/2),
                      np.cos(angle/2)])
        q1, q2, q3, q4 = q
        
        R1 = np.array([q1**2 - q2**2 - q3**2 + q4**2,
                       2 * (q1*q2 + q3*q4),
                       2 * (q1*q3 - q2*q4)])
        
        R2 = np.array([2 * (q1*q2 - q3*q4),
                       -q1**2 + q2**2 - q3**2 + q4**2,
                       2 * (q1*q4 + q2*q3)])
        
        R3 = np.array([2 * (q1*q3 + q2*q4),
                       2 * (-q1*q4 + q2*q3),
                       -q1**2 - q2**2 + q3**2 + q4**2])
        
        R = np.array([R1, 
                      R2, 
                      R3])
 
        self.basis = np.dot(R.T, self.basis)
        
        if global_rotate:
            self.COM = np.dot(R.T, self.COM)
            for s in self.shapes:
                s.COM = np.dot(R.T, s.COM)
                s.basis = np.dot(R.T, s.basis)
        else:
            for s in self.shapes:
                s.COM = np.dot(R.T, s.COM - self.COM) + self.COM
                s.basis = np.dot(R.T, s.basis)
        


class Shape:  
    def scale(self, scale, global_scale=False):
        if type(scale) == int or type(scale) == float:
            scale = scale * np.ones(3)
        scale_matrix = np.diag(scale)
        
        self.basis = np.dot(scale_matrix, self.basis)
        if global_scale:
            self.COM = np.dot(scale_matrix, self.COM)
                
            
    def move(self, offset, global_offset=False):
        self.COM += offset
            
            
    def rotate(self, axis, angle, global_rotate=False):
        angle = np.radians(angle)
        axis = axis / np.linalg.norm(axis)
        
        q = np.array([axis[0] * np.sin(angle/2),
                      axis[1] * np.sin(angle/2),
                      axis[2] * np.sin(angle/2),
                      np.cos(angle/2)])
        q1, q2, q3, q4 = q
        
        R1 = np.array([q1**2 - q2**2 - q3**2 + q4**2,
                       2 * (q1*q2 + q3*q4),
                       2 * (q1*q3 - q2*q4)])
        
        R2 = np.array([2 * (q1*q2 - q3*q4),
                       -q1**2 + q2**2 - q3**2 + q4**2,
                       2 * (q1*q4 + q2*q3)])
        
        R3 = np.array([2 * (q1*q3 + q2*q4),
                       2 * (-q1*q4 + q2*q3),
                       -q1**2 - q2**2 + q3**2 + q4**2])
        
        R = np.array([R1, 
                      R2, 
                      R3])

        self.basis = np.dot(R.T, self.basis) 
        if global_rotate:
            self.COM = np.dot(R.T, self.COM)

        
            
class Point(Shape):
    def __init__(self):
        self.parent = None
        self.COM = np.array([0., 0., 0.])
        
        self.basis = np.array([[1., 0., 0.],
                               [0., 1., 0.],
                               [0., 0., 1.]])
    
    def plot(self):
        glPointSize(8)
        glColor3f(1,1,1)
        glBegin(GL_POINTS)
        glVertex3f(*self.COM)
        glEnd()

        glBegin(GL_LINES)
        glColor3f(1,0,0)
        glVertex3f(self.COM[0],self.COM[1],self.COM[2])
        glVertex3f(self.COM[0] + 0.5*self.basis[0,0], 
                   self.COM[1] + 0.5*self.basis[1,0], 
                   self.COM[2] + 0.5*self.basis[2,0])
        
        glColor3f(0.5, 1, 0.35)
        glVertex3f(self.COM[0],self.COM[1],self.COM[2])
        glVertex3f(self.COM[0] + 0.5*self.basis[0,1], 
                   self.COM[1] + 0.5*self.basis[1,1], 
                   self.COM[2] + 0.5*self.basis[2,1])

        glColor3f(0.53,1,1)
        glVertex3f(self.COM[0],self.COM[1],self.COM[2])
        glVertex3f(self.COM[0] + 0.5*self.basis[0,2], 
                   self.COM[1] + 0.5*self.basis[1,2], 
                   self.COM[2] + 0.5*self.basis[2,2])
        glEnd()


class Cube(Shape):
    def __init__(self):
        self.parent = None
        self.COM = np.array([0., 0., 0.])
        self.basis = np.array([[1., 0., 0.],
                               [0., 1., 0.],
                               [0., 0., 1.]])
        
        self.vertices = np.array([[-0.5, -0.5, -0.5],
                                  [0.5, -0.5, -0.5],
                                  [0.5, 0.5, -0.5],
                                  [-0.5, 0.5, -0.5],
                                  
                                  [-0.5, -0.5, 0.5],
                                  [0.5, -0.5, 0.5],
                                  [0.5, 0.5, 0.5],
                                  [-0.5, 0.5, 0.5]])
        
        self.lines  =   np.array([[0,1], [1,2], [2,3], [3,0],
                               [4,5], [5,6], [6,7], [7,4],
                               [0,4], [1,5], [2,6], [3,7]])
        
    def plot(self):
        
        glColor3f(0.9, 0.06, 0.9)
        glBegin(GL_LINES)

        inertial_vertices = np.dot(self.basis, self.vertices.T).T + self.COM

        for l in self.lines:
            glVertex3f(inertial_vertices[l[0], 0], inertial_vertices[l[0],1], inertial_vertices[l[0],2])
            glVertex3f(inertial_vertices[l[1], 0], inertial_vertices[l[1],1], inertial_vertices[l[1],2])


        glEnd()
            
        
class Sphere(Shape):
    def __init__(self):
        self.parent = None
        self.COM = np.array([0., 0., 0.])
        self.basis = np.array([[1., 0., 0.],
                               [0., 1., 0.],
                               [0., 0., 1.]])
        
        self.n, self.m = 9, 5
        theta = np.linspace(0, 2*np.pi, self.n)
        phi = np.linspace(0, np.pi, self.m)

        positions = np.zeros((1,3))

        for t in theta:
            for p in phi:
                x = 0.5 * np.sin(p) * np.cos(t)
                y = 0.5 * np.sin(p) * np.sin(t)
                z = 0.5 * np.cos(p)
                positions = np.append(positions, np.array([[x,y,z]]), axis=0)
        
        self.vertices = positions[1:]
        
    def plot(self):
        inertial_vertices = np.dot(self.basis, self.vertices.T).T + self.COM
        X, Y, Z = inertial_vertices.T
        latX, latY, latZ = (np.array(np.split(X, self.n)).T, 
                            np.array(np.split(Y, self.n)).T, 
                            np.array(np.split(Z, self.n)).T)
        longX, longY, longZ = (np.array(np.split(X, self.n)), 
                               np.array(np.split(Y, self.n)), 
                               np.array(np.split(Z, self.n)))    
        
        glColor3f(0.9, 0.06, 0.9)
        glBegin(GL_LINES)

        for i in range(1, len(latX)-1):
            for j in range(len(latX[i])-1):
                glVertex3f(latX[i, j], latY[i, j], latZ[i, j])
                glVertex3f(latX[i, j+1], latY[i, j+1], latZ[i, j+1])
                

        for i in range(1, len(longX)):
            for j in range(len(longX[i])-1):
                glVertex3f(longX[i, j], longY[i, j], longZ[i, j])
                glVertex3f(longX[i, j+1], longY[i, j+1], longZ[i, j+1])

        glEnd()
        

class Cylinder(Shape):
    def __init__(self):
        self.parent = None
        self.COM = np.array([0., 0., 0.])
        self.basis = np.array([[1., 0., 0.],
                               [0., 1., 0.],
                               [0., 0., 1.]])

        thetas = np.linspace(0, 2*np.pi, 8, endpoint=False)
        x = 0.5 * np.concatenate((np.cos(thetas), np.cos(thetas)))
        y = 0.5 * np.concatenate((np.sin(thetas), np.sin(thetas)))
        z = 0.5 * np.concatenate((np.ones(8), -np.ones(8)))
        
        self.vertices = np.array([x,y,z]).T
        self.lines = np.array([
            [0,1], [1,2], [2,3], [3,4], [4,5], [5,6], [6,7], [7,0],
            [8,9], [9,10], [10,11], [11,12], [12,13], [13,14], [14,15], [15,8],
            [0,8], [1,9], [2,10], [3,11], [4,12], [5,13], [6,14], [7,15]])

    def plot(self):
        inertial_vertices = np.dot(self.basis, self.vertices.T).T + self.COM

        glColor3f(0.9, 0.06, 0.9)
        glBegin(GL_LINES)

        for l in self.lines:
            glVertex3f(inertial_vertices[l[0], 0], inertial_vertices[l[0],1], inertial_vertices[l[0],2])
            glVertex3f(inertial_vertices[l[1], 0], inertial_vertices[l[1],1], inertial_vertices[l[1],2])
        
        glEnd()


