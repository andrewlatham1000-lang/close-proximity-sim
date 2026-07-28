from PyQt5.QtOpenGL import *
from PyQt5.QtCore import Qt
from objects import *

class glWidget(QGLWidget):
    # Main widget for GUI display using PyOpenGL
    # to display wireframes of each body in the simulation
    # showing updated positions and rotations in a 3D space

    def __init__(self, parent):
        self.parent = parent
        QGLWidget.__init__(self, parent)
        self.setMinimumSize(900, 900)
        self.format().setVersion(4, 2)
        self.format().setProfile(QGLFormat.CoreProfile)
        
        # Setup for camera calculations
        self.rotation_pos0 = [0,0]
        self.rotation_pos1 = [0,0]
        self.translation_pos0 = [0,0]
        self.translation_pos1 = [0,0]
        self.camera_rotation = np.array([[1., 0., 0.],
                                         [0., 1., 0.],
                                         [0., 0., 1.]])
        self.rotate_camera([1,0,0], -90)
        self.rotate_camera([0, 1, 0], -15)
        self.rotate_camera([1,0,0], 15)
        self.zoom = 1
        self.camera_offset = np.array([0., 0., 0.])
        self.lim = 1

        # Flags to specify camera movement or rotation during mouse mouse event
        self.left_pressed = False
        self.right_pressed = False
        
        # Make point for environment origin and setup array to hold body information
        self.origin = Point()
    
    def rotate_camera(self, axis, angle):
        # Use quarternions to rotate camera around an axis
        # Currently converts into a rotation matrix, will change to use only quarternions
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

        self.camera_rotation = np.dot(R.T, self.camera_rotation)

    def mousePressEvent(self, event):
        # Press left mouse to rotate camera
        # Press right mouse to move camera
        if event.button() == Qt.LeftButton:
            self.left_pressed = True
            x, y = event.pos().x(), event.pos().y()
            self.rotation_pos0 = [x,y]

        if event.button() == Qt.RightButton:
            self.right_pressed = True
            x, y = event.pos().x(), event.pos().y()
            self.translation_pos0 = [x,y]

    def mouseMoveEvent(self, event):
        if self.left_pressed:
            # Record mouse movement and convert into camera rotations
            # The division by 5 is a scaling factor so that rotation matches mouse movement
            # If simulation is paused, need to call to redraw the screen

            x, y = event.pos().x(), event.pos().y()
            self.rotation_pos1 = [x,y]
            rotation_x = (self.rotation_pos1[1] - self.rotation_pos0[1]) / 5
            rotation_y = (self.rotation_pos1[0] - self.rotation_pos0[0]) / 5
            self.rotate_camera([1,0,0], rotation_x)
            self.rotate_camera([0,1,0], rotation_y)
            self.rotation_pos0 = self.rotation_pos1
            if self.parent.simulation_paused:
                self.update()

        if self.right_pressed:
            # Similar to rotation except camera translation
            # Scaling factor depends on 3d space limits and application width
            x, y = event.pos().x(), event.pos().y()
            self.translation_pos1 = [x,y]
            width = self.width()
            translation_y = (self.translation_pos0[1] - self.translation_pos1[1]) * 0.04 * self.lim / width
            translation_x = (self.translation_pos1[0] - self.translation_pos0[0]) * 0.04 * self.lim / width
            self.camera_offset += np.array([translation_x, translation_y, 0])
            self.translationn_pos0 = self.translation_pos1
            if self.parent.simulation_paused:
                self.update()

    def mouseReleaseEvent(self, event):
        # Resetting flags after mouse release
        if event.button() == Qt.LeftButton:
            self.left_pressed = False
            self.rotation_x = 0
            self.rotation_y = 0
        if event.button() == Qt.RightButton:
            self.right_pressed = False
            self.translation_x = 0
            self.translation_y = 0

    def wheelEvent(self, event):
        # Zoom when wheel scrolled
        if event.angleDelta().y() > 0:
            self.zoom *= 1.25
        else:
            self.zoom *= 0.8

        self.parent.time_controls.set_zoom(self.zoom)
        if self.parent.simulation_paused:
                self.update()

    def find_view_lims(self):
        # Currently broken, intended to auto set canvas limits during initialisation
        # based on location and dimension of bodies in sim
        max_x, max_y, max_z = 0, 0, 0
        for body in self.parent.bodies:
            x = abs(body.position[0])
            y = abs(body.position[1])
            z = abs(body.position[2])
            if x > max_x:
                max_x = x
            if y > max_y:
                max_y = y
            if z > max_z:
                max_z = z

        self.lim = max(max_x, max_y, max_z)

    
    def initializeGL(self):
        # Clear canvas and set initial view
        glClearColor(0.0, 0.0, 0.0, 0.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glViewport(0, 0, 600, 600)
        self.find_view_lims()
        lim = self.lim
        glOrtho(-lim, lim, -lim, lim, -1e5, 1e5)

    def resizeGL(self, w, h):
        # Keep viewport centered and square during resizing
        glViewport((w - h)//2, 0, h, h)
        
        
    def paintGL(self):
        # Reset canvas
        glClearColor(0.0, 0.0, 0.0, 0.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Plot origin point then all bodies in sim
        self.origin.plot(self.camera_rotation, self.zoom, self.camera_offset)
        for body in self.parent.bodies:
            body.plot(self.camera_rotation, self.zoom, self.camera_offset)