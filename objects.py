import numpy as np
from OpenGL.GL import *
from matplotlib import pyplot as plt
from relativeMotion import *

def quarternion_multiplication(q, p):
    # Performs quarternion multiplication q x p
    # ie. returns combined rotation of p followed by q

    return np.array([q[3]*p[0] + q[0]*p[3] + q[1]*p[2] - q[2]*p[1],
                     q[3]*p[1] - q[0]*p[2] + q[1]*p[3] + q[2]*p[0],
                     q[3]*p[2] + q[0]*p[1] - q[1]*p[0] + q[2]*p[3],
                     q[3]*p[3] - q[0]*p[0] - q[1]*p[1] - q[2]*p[2]])

def q2R(q):
    # Converts given quarternion into a rotation matrix
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

    return R

g0 = 9.80665
##########################################################################################################################
############################################ BODY & SHAPE CLASSES ########################################################
##########################################################################################################################


class Body:
    """
    Bodies are made of base shapes and are affected by physics
    Bodies will move and rotate around their calculated centre of mass
    Variables in body fixed frame:
        Centre of mass
        Inertia martrix
        Angular momentum
        Angular velocity
    Variables in global LVLH frame:
        Position
        Velocity
        Rotation matrix
        Quarternion & time derivative of

    """

    def __init__(self):
        self.name =str()
        self.position = np.array([0., 0., 0.])
        self.velocity = np.array([0., 0., 0.])
        self.COM = np.array([0.,0.,0.])
        self.basis = np.diag([1.,1.,1.])
        self.rotation_matrix = np.array([[1., 0., 0.],
                                         [0., 1., 0.],
                                         [0., 0., 1.]])
        self.quarternion = np.array([0., 0., 0., 1.])
        self.d_quarternion = np.array([0., 0., 0., 0.])
        self.inertia_matrix = np.array([[0., 0., 0.],
                                        [0., 0., 0.],
                                        [0., 0., 0.]])
        self.angular_momentum = np.array([0., 0., 0.])
        self.angular_velocity = np.array([0., 0., 0.])
        self.mass = 0
        
        
        self.shapes = np.array([], dtype=object)
        self.thrusters = np.array([], dtype=object)
        
    def calculate_COM(self):
        # Calculate COM of body
        if len(self.shapes) == 1:
            self.COM = self.shapes[0].position
        else:
            xs, ys, zs = np.array([s.position for s in self.shapes]).T

            ms = np.array([s.mass for s in self.shapes])
            M = np.sum(ms)
            self.mass = M
            self.COM = np.array([np.sum(xs * ms) / M,
                                 np.sum(ys * ms) / M,
                                 np.sum(zs * ms) / M])
        

    def calculate_inertia_matrix(self):
        # Calculate inertia matrix for body for rotational motion
        if len(self.shapes) == 1:
            self.inertia_matrix = self.shapes[0].inertia_matrix
        else:
            I = np.zeros((3,3))
            for s in self.shapes:
                I_cm = np.dot(s.rotation_matrix, np.dot(s.inertia_matrix, s.rotation_matrix.T))
                r1, r2, r3 = np.abs(s.position - self.COM)
                I_r = I_cm + s.mass * np.array([[r2**2 + r3**2,    r1 * r2   ,    r1 * r3   ],
                                                [   r1 * r2   , r1**2 + r3**2,    r2 * r3   ],
                                                [   r1 * r3   ,    r2 * r3   , r1**2 + r2**2]])
                I += I_r
            self.inertia_matrix = I

    def dH(self, H):
        # Impulsive change in angular momentum of body
        # H is a vector specifying change in angular momentum in body fixed x,y,z
        self.angular_momentum += H
        self.angular_velocity = np.dot(np.linalg.inv(self.inertia_matrix), self.angular_momentum)
    
        
    def add(self, obj):
        if obj.__class__.__name__ == "Thruster":
            self.thrusters = np.append(self.thrusters, obj)
            obj.parent = self
        else:
            self.shapes = np.append(self.shapes, obj)
            obj.parent = self
            if obj.__class__.__name__ == "FuelTank":
                obj.shape.parent = self
                obj.fuel.parent = self
            self.calculate_COM()
            self.calculate_inertia_matrix()
    
    def remove(self, obj):
        if obj.__class__.__name__ == "Thruster":
            i = np.where(self.thrusters == obj)
            self.thrusters = np.delete(self.thrusters, i)
            obj.parent = None
        else:
            i = np.where(self.shapes == obj)
            self.shapes = np.delete(self.shapes, i)
            obj.parent = None
            self.calculate_COM()
            self.calculate_inertia_matrix()
        
    def plot(self, camera_rotation, camera_zoom, camera_offset):
        # Convert COM to global coords and plot
        inertial_COM = camera_zoom * np.dot(camera_rotation, (self.position)) + camera_offset
        glPointSize(5)
        glColor3f(1,1,0)
        glBegin(GL_POINTS)
        glVertex3f(*inertial_COM)
        glEnd()
        
        # Find rotation matrix to convert shapes from body-fixed into global coords
        self.rotation_matrix = q2R(self.quarternion)
        for s in self.shapes:
            s.plot(camera_rotation, camera_zoom, camera_offset)
        for t in self.thrusters:
            t.plot(camera_rotation, camera_zoom, camera_offset)
    
    def move(self, offset):
        self.position += offset
    
    def rotate(self, axis, angle):
        angle = np.radians(angle)
        axis = axis / np.linalg.norm(axis)
        
        q = np.array([axis[0] * np.sin(angle/2),
                      axis[1] * np.sin(angle/2),
                      axis[2] * np.sin(angle/2),
                      np.cos(angle/2)])

        self.quarternion = quarternion_multiplication(q, self.quarternion)


    def update_timestep(self, dt, mu, target_h, target_position, target_velocity):
        # Time given in milliseconds
        # Update rotation, normalising quarternion to prevent shape deformation
        # then update quarternion derivative
        w1, w2, w3 = np.dot(q2R(self.quarternion), self.angular_velocity)
        w_matrix = np.array([[ 0 ,  w3, -w2, w1],
                             [-w3,  0 ,  w1, w2],
                             [ w2, -w1,  0 , w3],
                             [-w1, -w2, -w3, 0 ]])
        self.d_quarternion = np.dot(w_matrix, self.quarternion)
        dq = self.d_quarternion * dt / 1000
        self.quarternion += dq
        self.quarternion /= np.linalg.norm(self.quarternion)

        # Movement update
        # Uses functions from relativeMotion file to integrate relative
        # orbital motion equations using Euler predictor-corrector method
        state = np.concatenate((self.position, self.velocity))
        accel0 = relative_acceleration(
            state, 
            mu, 
            target_h, 
            target_position, 
            target_velocity
        )

        vel0 = self.velocity + accel0 * (dt/1000)
        pos0 = self.position + vel0 * (dt/1000) + 0.5 * accel0 * (dt/1000)**2
        half_state = np.concatenate((pos0, vel0))

        accel1 = relative_acceleration(
            half_state, 
            mu, 
            target_h, 
            target_position, 
            target_velocity
        )
        
        self.velocity = self.velocity + 0.5 * (accel0 + accel1) * (dt/1000)
        self.position = (
            self.position + 
            0.5  * (vel0 + self.velocity) * (dt/1000) +
            0.25 * (accel0 + accel1) * (dt/1000)**2
        )
        




class Shape:  
    # Parent class for all primitive shape objects
    def __init__(self, density):
        self.parent = None
        self.position = np.array([0., 0., 0.])
        self.basis = np.array([[1., 0., 0.],
                               [0., 1., 0.],
                               [0., 0., 1.]])
        self.rotation_matrix = np.array([[1., 0., 0.],
                                         [0., 1., 0.],
                                         [0., 0., 1.]])
        self.quarternion = np.array([0., 0., 0., 0.])

        self.density = density
        self.mass = density * self.volume()
        self.inertia_matrix = self.inertia()
        

    def scale(self, scale):
        if type(scale) == int or type(scale) == float:
            scale = scale * np.ones(3)
        scale_matrix = np.diag(scale)
        
        self.basis = np.dot(scale_matrix, self.basis)
        self.mass = self.density * self.volume()
        self.inertia_matrix = self.inertia()
        if self.parent:
            self.parent.calculate_COM()
            self.parent.calculate_inertia_matrix()
                
            
    def move(self, offset):
        self.position += offset
        if self.parent:
            self.parent.calculate_COM()
            self.parent.calculate_inertia_matrix()
            
            
    def rotate(self, axis, angle):
        angle = np.radians(angle)
        axis = axis / np.linalg.norm(axis)
        
        q = np.array([axis[0] * np.sin(angle/2),
                      axis[1] * np.sin(angle/2),
                      axis[2] * np.sin(angle/2),
                      np.cos(angle/2)])
        
        R = q2R(q)
        
        self.rotation_matrix = np.dot(R.T, self.rotation_matrix) 
        if self.parent:
            self.parent.calculate_COM()
            self.parent.calculate_inertia_matrix()

    def find_inertial(self, camera_rotation, camera_zoom, camera_offset):
        if self.parent:
            inertial_COM = (camera_zoom * 
                            np.dot(camera_rotation, 
                                (np.dot(self.parent.rotation_matrix, 
                                        self.position - self.parent.COM) + 
                                        self.parent.position)) + 
                            camera_offset)
            
            inertial_vertices = (camera_zoom * 
                                 np.dot(np.dot(camera_rotation, 
                                        np.dot(self.parent.rotation_matrix, 
                                                np.dot(self.rotation_matrix, self.basis))), 
                                        self.vertices.T).T + 
                                inertial_COM)
        else:
            inertial_COM = camera_zoom * np.dot(camera_rotation, self.position) + camera_offset
            inertial_vertices = camera_zoom * np.dot(np.dot(camera_rotation, np.dot(self.rotation_matrix, self.basis)), self.vertices.T).T + inertial_COM

        return inertial_COM, inertial_vertices
        
    def update_timestep(self):
        pass
            

class Thruster:
    def __init__(self, name, isp, tank):
        self.name = name
        self.parent = None
        self.position = np.zeros(3)
        self.isp = isp
        self.tank = tank

        self.vertices = np.array([
            [-0.05, -0.05, -0.05],
            [0.05, -0.05, -0.05],
            [0.05, 0.05, -0.05],
            [-0.05, 0.05, -0.05],
            
            [-0.05, -0.05, 0.05],
            [0.05, -0.05, 0.05],
            [0.05, 0.05, 0.05],
            [-0.05, 0.05, 0.05]
        ])
                
        self.lines  =   np.array([
            [0,1], [1,2], [2,3], [3,0],
            [4,5], [5,6], [6,7], [7,4],
            [0,4], [1,5], [2,6], [3,7],
            [0,2], [0,5], [0,7],
            [1,3], [1,4], [1,6],
            [2,5], [2,7],
            [3,4], [3,6],
            [4,6], [5,7],
        ])

    def burn(self, thrust_vector, dt):
        # Relate position to parent CoM
        # Find compoment passing through CoM -> convert to dv
        # Find component orthogonal to CoM -> convert to dH
        dt /= 1000

        pos2COM = self.parent.COM - self.position
        pos2COM_mag = np.linalg.norm(pos2COM)
        pos2COM_u = pos2COM / pos2COM_mag

        thrust_mag = np.linalg.norm(thrust_vector)
        thrust_u = thrust_vector / thrust_mag

        fuel_used = thrust_mag * dt / (self.isp * g0)
        if fuel_used >= self.tank.fuel.mass:
            fuel_used = self.tank.fuel.mass
            dt = fuel_used * self.isp * g0 / thrust_mag

        

        self.tank.burn_fuel(fuel_used)

        # Split thrust into pure & orthogonal components
        pure_thrust = np.dot(thrust_vector, pos2COM_u) * pos2COM_u
        orthog_thrust = np.cross(np.cross(pos2COM_u, thrust_vector), pos2COM_u)

        # Linear velocity change
        a = pure_thrust / self.parent.mass
        self.parent.velocity += a * dt

        # Rotation change
        self.parent.dH(orthog_thrust * dt)

    def plot(self, camera_rotation, camera_zoom, camera_offset):
        inertial_COM = (
            camera_zoom * 
            np.dot(camera_rotation, 
                (np.dot(self.parent.rotation_matrix, 
                        self.position - self.parent.COM) + 
                        self.parent.position)) + 
            camera_offset)

        inertial_vertices = (
            camera_zoom * 
            np.dot(np.dot(camera_rotation, self.parent.rotation_matrix), 
                self.vertices.T).T + 
            inertial_COM)

        glColor3f(0, 0.94, 0.94)
        glBegin(GL_LINES)

        for l in self.lines:
            glVertex3f(inertial_vertices[l[0], 0], inertial_vertices[l[0],1], inertial_vertices[l[0],2])
            glVertex3f(inertial_vertices[l[1], 0], inertial_vertices[l[1],1], inertial_vertices[l[1],2])

        glEnd()


class FuelTank:
    def __init__(self, name, shape, fuel):
        self.parent = None
        self.name = name
        self.shape = shape
        self.fuel = fuel
        self.mass = shape.mass + fuel.mass
        self.max_fuel = fuel.mass
        self.position = shape.position
        self.basis = shape.basis
        self.rotation_matrix = shape.rotation_matrix
        self.quarternion = shape.quarternion
        self.inertia_matrix = shape.inertia_matrix + fuel.inertia_matrix
        self.color = (min(1, 2 * (1 - self.fuel.mass / self.max_fuel)),
                      min(1, 2 * self.fuel.mass / self.max_fuel),
                      0)

    def burn_fuel(self, mf):
        self.fuel.mass -= mf
        self.fuel.inertia_matrix = self.fuel.inertia()

        self.mass = self.shape.mass + self.fuel.mass
        self.inertia_matrix = self.shape.inertia_matrix + self.fuel.inertia_matrix
        self.color = (min(1, 2 * (1 - self.fuel.mass / self.max_fuel)),
                      min(1, 2 * self.fuel.mass / self.max_fuel),
                      0)
        
        self.parent.calculate_COM()
        self.parent.calculate_inertia_matrix()

    def scale(self, scale):
        if type(scale) == int or type(scale) == float:
            scale = scale * np.ones(3)
        scale_matrix = np.diag(scale)
        
        self.basis = np.dot(scale_matrix, self.basis)
        self.inertia_matrix = self.inertia()

        if self.parent:
            self.parent.calculate_COM()
            self.parent.calculate_inertia_matrix()
                            
    def move(self, offset):
        self.position += offset
        if self.parent:
            self.parent.calculate_COM()
            self.parent.calculate_inertia_matrix()
                      
    def rotate(self, axis, angle):
        angle = np.radians(angle)
        axis = axis / np.linalg.norm(axis)
        
        q = np.array([axis[0] * np.sin(angle/2),
                        axis[1] * np.sin(angle/2),
                        axis[2] * np.sin(angle/2),
                        np.cos(angle/2)])
        
        R = q2R(q)
        
        self.rotation_matrix = np.dot(R.T, self.rotation_matrix) 
        if self.parent:
            self.parent.calculate_COM()
            self.parent.calculate_inertia_matrix()

    def plot(self, camera_rotation, camera_zoom, camera_offset):
        self.shape.plot(camera_rotation, camera_zoom, camera_offset, color=self.color)

    def update_timestep(self):
        pass
        


##########################################################################################################################
################################################### SHAPES ###############################################################
##########################################################################################################################


class Point(Shape):
    def __init__(self):
        super().__init__(0)
    
    def plot(self, camera_rotation, camera_zoom, camera_offset):

        inertial_COM = camera_zoom * np.dot(camera_rotation, self.position) + camera_offset
        global_axes = camera_zoom * np.dot(camera_rotation, np.dot(self.rotation_matrix, self.basis))

        glPointSize(8)
        glColor3f(1,1,1)
        glBegin(GL_POINTS)
        glVertex3f(*inertial_COM)
        glEnd()

        

        glBegin(GL_LINES)
        glColor3f(1,0,0)
        glVertex3f(inertial_COM[0], inertial_COM[1], inertial_COM[2])
        glVertex3f(inertial_COM[0] + 0.5*global_axes[0,0], 
                   inertial_COM[1] + 0.5*global_axes[1,0], 
                   inertial_COM[2] + 0.5*global_axes[2,0])
        
        glColor3f(0.5, 1, 0.35)
        glVertex3f(inertial_COM[0],inertial_COM[1],inertial_COM[2])
        glVertex3f(inertial_COM[0] + 0.5*global_axes[0,1], 
                   inertial_COM[1] + 0.5*global_axes[1,1], 
                   inertial_COM[2] + 0.5*global_axes[2,1])

        glColor3f(0.53,1,1)
        glVertex3f(inertial_COM[0],inertial_COM[1],inertial_COM[2])
        glVertex3f(inertial_COM[0] + 0.5*global_axes[0,2], 
                   inertial_COM[1] + 0.5*global_axes[1,2], 
                   inertial_COM[2] + 0.5*global_axes[2,2])
        glEnd()
    
    def volume(self):
        return 0
    
    def inertia(self):
        return np.zeros((3,3), dtype=np.float32)


class Cube(Shape):
    def __init__(self, density=2700):
        super().__init__(density)
        
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
        
    def plot(self, camera_rotation, camera_zoom, camera_offset):
        inertial_COM, inertial_vertices = self.find_inertial(camera_rotation, camera_zoom, camera_offset)


        glColor3f(0.9, 0.06, 0.9)
        glBegin(GL_LINES)

        for l in self.lines:
            glVertex3f(inertial_vertices[l[0], 0], inertial_vertices[l[0],1], inertial_vertices[l[0],2])
            glVertex3f(inertial_vertices[l[1], 0], inertial_vertices[l[1],1], inertial_vertices[l[1],2])

        glEnd()
            
    def volume(self):
        return np.prod(np.linalg.norm(self.basis, axis = 0))

    def inertia(self):
        lx, ly, lz = np.linalg.norm(self.basis, axis = 0)
        Ix = (1/12) * self.mass * (ly**2 + lz**2)
        Iy = (1/12) * self.mass * (lx**2 + lz**2)
        Iz = (1/12) * self.mass * (lx**2 + ly**2)
        return np.diag([Ix, Iy, Iz])
        

class ShellCube(Shape):
    def __init__(self, mass):
        super().__init__(mass)

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

    def plot(self, camera_rotation, camera_zoom, camera_offset, color=(0.9, 0.06, 0.9)):
        inertial_COM, inertial_vertices = self.find_inertial(camera_rotation, camera_zoom, camera_offset)


        glColor3f(*color)
        glBegin(GL_LINES)

        for l in self.lines:
            glVertex3f(inertial_vertices[l[0], 0], inertial_vertices[l[0],1], inertial_vertices[l[0],2])
            glVertex3f(inertial_vertices[l[1], 0], inertial_vertices[l[1],1], inertial_vertices[l[1],2])

        glEnd()
        
    def volume(self):
        return 1

    def inertia(self):
        lx, ly, lz = np.diag(self.basis)
        m = self.mass
        d = 3 * (lx*ly + lx*lz + ly*lz)

        #L-R contribution
        Ix_LR = ly**3 * lz + ly * lz**3
        Iy_LR = ly * lz**3 + 3 * lx**2 * ly * lz
        Iz_LR = ly**3 * lz + 3 * lx**2 * ly * lz

        #F-B contribution
        Ix_FB = lx * lz**3 + 3 * lx * ly**2 * lz
        Iy_FB = lx**3 * lz + lx * lz**3
        Iz_FB = lx**3 * lz + 3 * lx * ly**2 * lz

        #U-D contribution
        Ix_UD = lx * ly**3 + 3 * lx * ly * lz**2
        Iy_UD = lx**3 * ly + 3 * lx * ly * lz**2
        Iz_UD = lx**3 * ly + lx * lz**3

        Ix = (m/d) * (Ix_LR + Ix_FB + Ix_UD) 
        Iy = (m/d) * (Iy_LR + Iy_FB + Iy_UD) 
        Iz = (m/d) * (Iz_LR + Iz_FB + Iz_UD) 

        return np.diag([Ix, Iy, Iz])


class Sphere(Shape):
    def __init__(self, density=2700):
        super().__init__(density)
        
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
        
    def plot(self, camera_rotation, camera_zoom, camera_offset):
        inertial_COM, inertial_vertices = self.find_inertial(camera_rotation, camera_zoom, camera_offset)

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

    def scale(self, scale):
        if type(scale) == int or type(scale) == float:
            scale = scale * np.ones(3)
        else:
            scale = scale[0] * np.ones(3)
        
        self.basis = scale * self.basis
        self.mass = self.density * self.volume()
        self.inertia_matrix = self.inertia()
        if self.parent:
            self.parent.calculate_COM()
            self.parent.calculate_inertia_matrix()
            
    def volume(self):
        return (4/3) * np.pi * np.prod(np.linalg.norm(self.basis, axis = 0))

    def inertia(self):
        lx, ly, lz = np.linalg.norm(self.basis, axis = 0)
        Ix = (1/5) * self.mass * (ly**2 + lz**2)
        Iy = (1/5) * self.mass * (lx**2 + lz**2)
        Iz = (1/5) * self.mass * (lx**2 + ly**2)
        return np.diag([Ix, Iy, Iz])
        

class ShellSphere(Shape):
    def __init__(self, mass):
        super().__init__(mass)

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

    def plot(self, camera_rotation, camera_zoom, camera_offset, color=(0.9, 0.06, 0.9)):
        inertial_COM, inertial_vertices = self.find_inertial(camera_rotation, camera_zoom, camera_offset)

        X, Y, Z = inertial_vertices.T
        latX, latY, latZ = (np.array(np.split(X, self.n)).T, 
                            np.array(np.split(Y, self.n)).T, 
                            np.array(np.split(Z, self.n)).T)
        longX, longY, longZ = (np.array(np.split(X, self.n)), 
                                np.array(np.split(Y, self.n)), 
                                np.array(np.split(Z, self.n)))    
        
        glColor3f(*color)
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

    def scale(self, scale):
        if type(scale) == int or type(scale) == float:
            scale = scale * np.ones(3)
        else:
            scale = scale[0] * np.ones(3)
        
        self.basis = scale * self.basis
        self.mass = self.density * self.volume()
        self.inertia_matrix = self.inertia()
        if self.parent:
            self.parent.calculate_COM()
            self.parent.calculate_inertia_matrix()

    def volume(self):
        return 1

    def inertia(self):
        R = self.basis[0,0]
        I = (2/3) * self.mass * R**2
        return np.diag(I * np.ones(3))


class Cylinder(Shape):
    def __init__(self, density=2700):
        super().__init__(density)

        thetas = np.linspace(0, 2*np.pi, 8, endpoint=False)
        x = 0.5 * np.concatenate((np.cos(thetas), np.cos(thetas)))
        y = 0.5 * np.concatenate((np.sin(thetas), np.sin(thetas)))
        z = 0.5 * np.concatenate((np.ones(8), -np.ones(8)))
        
        self.vertices = np.array([x,y,z]).T
        self.lines = np.array([
            [0,1], [1,2], [2,3], [3,4], [4,5], [5,6], [6,7], [7,0],
            [8,9], [9,10], [10,11], [11,12], [12,13], [13,14], [14,15], [15,8],
            [0,8], [1,9], [2,10], [3,11], [4,12], [5,13], [6,14], [7,15]])

    def plot(self, camera_rotation, camera_zoom, camera_offset):
        inertial_COM, inertial_vertices = self.find_inertial(camera_rotation, camera_zoom, camera_offset)

        glColor3f(0.9, 0.06, 0.9)
        glBegin(GL_LINES)

        for l in self.lines:
            glVertex3f(inertial_vertices[l[0], 0], inertial_vertices[l[0],1], inertial_vertices[l[0],2])
            glVertex3f(inertial_vertices[l[1], 0], inertial_vertices[l[1],1], inertial_vertices[l[1],2])
        
        glEnd()

    def scale(self, scale):
        if type(scale) == int or type(scale) == float:
            scale = scale * np.ones(3)
        else:
            scale = np.array([scale[0], scale[0], scale[1]])

        scale_matrix = np.diag(scale)
        self.basis = np.dot(scale_matrix, self.basis)
        self.mass = self.density * self.volume()
        self.inertia_matrix = self.inertia()
        if self.parent:
            self.parent.calculate_COM()
            self.parent.calculate_inertia_matrix()
            
    def volume(self):
        return np.pi * np.prod(np.linalg.norm(self.basis, axis = 0))
    
    def inertia(self):
        lx, ly, lz = np.linalg.norm(self.basis, axis = 0)
        Ix = (1/12) * self.mass * (3*ly**2 + lz**2)
        Iy = (1/12) * self.mass * (3*lx**2 + lz**2)
        Iz = (1/4) * self.mass * (lx**2 + ly**2)
        return np.diag([Ix, Iy, Iz])


class ShellCylinder(Shape):
    def __init__(self, mass):
        super().__init__(mass)

        thetas = np.linspace(0, 2*np.pi, 8, endpoint=False)
        x = 0.5 * np.concatenate((np.cos(thetas), np.cos(thetas)))
        y = 0.5 * np.concatenate((np.sin(thetas), np.sin(thetas)))
        z = 0.5 * np.concatenate((np.ones(8), -np.ones(8)))
        
        self.vertices = np.array([x,y,z]).T
        self.lines = np.array([
            [0,1], [1,2], [2,3], [3,4], [4,5], [5,6], [6,7], [7,0],
            [8,9], [9,10], [10,11], [11,12], [12,13], [13,14], [14,15], [15,8],
            [0,8], [1,9], [2,10], [3,11], [4,12], [5,13], [6,14], [7,15]])

    def plot(self, camera_rotation, camera_zoom, camera_offset, color=(0.9, 0.06, 0.9)):
        inertial_COM, inertial_vertices = self.find_inertial(camera_rotation, camera_zoom, camera_offset)

        glColor3f(*color)
        glBegin(GL_LINES)

        for l in self.lines:
            glVertex3f(inertial_vertices[l[0], 0], inertial_vertices[l[0],1], inertial_vertices[l[0],2])
            glVertex3f(inertial_vertices[l[1], 0], inertial_vertices[l[1],1], inertial_vertices[l[1],2])
        
        glEnd()

    def scale(self, scale):
        if type(scale) == int or type(scale) == float:
            scale = scale * np.ones(3)
        else:
            scale = np.array([scale[0], scale[0], scale[1]])

        scale_matrix = np.diag(scale)
        self.basis = np.dot(scale_matrix, self.basis)
        self.mass = self.density * self.volume()
        self.inertia_matrix = self.inertia()
        if self.parent:
            self.parent.calculate_COM()
            self.parent.calculate_inertia_matrix()

    def volume(self):
        return 1
    
    def inertia(self):
        lx, ly, lz = np.linalg.norm(self.basis, axis = 0)
        r, h = lx, lz
        A = 2 * np.pi * r * h + 2 * np.pi * r**2
        m_cylinder = (2 * np.pi * r * h) / A
        m_circle = (np.pi * r**2) / A

        # From open cylinder
        Ix_cy = Iy_cy = (1/12) * m_cylinder * (6 * r**2 + h**2)
        Iz_cy = m_cylinder * r**2

        # From circles
        Ix_ci = Iy_ci = (1/2) * m_circle * (r**2 + h**2)
        Iz_ci = m_circle * r**2
        
        Ix = Ix_cy + Ix_ci
        Iy = Iy_cy + Iy_ci
        Iz = Iz_cy + Iz_ci

        return np.diag([Ix, Iy, Iz])