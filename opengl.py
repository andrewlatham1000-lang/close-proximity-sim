import sys
import ctypes
import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtOpenGL import *
from objects import *

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Relative motion")
        self.resize(900, 900)
        self.gl = glWidget(self)
        self.gl.format().setVersion(4, 2)
        self.gl.format().setProfile(QGLFormat.CoreProfile)
        self.setCentralWidget(self.gl)


class glWidget(QGLWidget):
    def __init__(self, parent):
        self.parent = parent
        QGLWidget.__init__(self, parent)
        self.setMinimumSize(900, 900)
        
        self.first_draw = True
        self.rotation_pos0 = [0,0]
        self.rotation_pos1 = [0,0]
        self.rotation_x = 0
        self.rotation_y = 0
        self.translation_pos0 = [0,0]
        self.translation_pos1 = [0,0]
        self.translation_x = 0
        self.translation_y = 0
        self.zoom = 1
        self.left_pressed = False
        self.right_pressed = False
        self.lim = 1
        COM = Point()


        cube = Cube()
        cube.rotate([0,1,0], 45)

        cylinder = Cylinder()
        cylinder.scale([1,1,2])
        cylinder.rotate([1,0,0], 90)
        cylinder.move([0,1.5,0])
        
        sphere = Sphere()
        sphere.scale(2)
        sphere.move([0,3, 0])

        satellite = Body()
        satellite.add(cube)
        satellite.add(cylinder)
        satellite.add(sphere)
        satellite.move(-satellite.COM)
        satellite.rotate([0,0,1], 90)

        cube2 = Cube()
        cube2.scale([0.5, 2, 2])
        satellite2 = Body()
        satellite2.add(cube2)
        satellite2.move([-2, 0, 0])
        

        self.bodies = np.array([COM, satellite, satellite2], dtype=object)

    def mousePressEvent(self, event):
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
            x, y = event.pos().x(), event.pos().y()
            self.rotation_pos1 = [x,y]
            self.rotation_x = (self.rotation_pos1[1] - self.rotation_pos0[1]) / 5
            self.rotation_y = (self.rotation_pos1[0] - self.rotation_pos0[0]) / 5
            self.rotation_pos0 = self.rotation_pos1
            self.update()
        if self.right_pressed:
            x, y = event.pos().x(), event.pos().y()
            self.translation_pos1 = [x,y]
            width = self.width()
            self.translation_y = (self.translation_pos0[1] - self.translation_pos1[1]) / (50*width / self.lim)
            self.translation_x = (self.translation_pos1[0] - self.translation_pos0[0]) / (50*width / self.lim)
            self.translationn_pos0 = self.translation_pos1
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.left_pressed = False
            self.rotation_x = 0
            self.rotation_y = 0
        if event.button() == Qt.RightButton:
            self.right_pressed = False
            self.translation_x = 0
            self.translation_y = 0

    def wheelEvent(self, event):
        if event.angleDelta().y() > 0:
            self.zoom = 1.25
        else:
            self.zoom = 0.8

        self.update()

    def find_view_lims(self):
        max_x, max_y, max_z = 0, 0, 0
        for body in self.bodies:
            x = abs(body.COM[0]) + abs(np.linalg.norm(body.basis[:, 0]))
            y = abs(body.COM[1]) + abs(np.linalg.norm(body.basis[:, 1]))
            z = abs(body.COM[2]) + abs(np.linalg.norm(body.basis[:, 2]))
            if x > max_x:
                max_x = x
            if y > max_y:
                max_y = y
            if z > max_z:
                max_z = z

        self.lim = max(max_x, max_y, max_z)

    
    def initializeGL(self):
        glClearColor(0.0, 0.0, 0.0, 0.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glViewport(0, 0, 900, 900)
        self.find_view_lims()
        lim = self.lim
        print(lim)
        glOrtho(-lim, lim, -lim, lim, -lim, lim)
        


    def resizeGL(self, w, h):
        glViewport((w-h)//2, 0, h, h)
        
    def paintGL(self):
        glClearColor(0.0, 0.0, 0.0, 0.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)


        if self.first_draw:
            for body in self.bodies:
                body.rotate([0,1,0], -45, global_rotate=True)
                body.rotate([1, 0, -1], 20, global_rotate=True)
            self.first_draw = False

        else:
            for body in self.bodies:
                body.rotate([1,0,0], self.rotation_x, global_rotate=True)
                body.rotate([0,1,0], self.rotation_y, global_rotate=True)
                body.scale(self.zoom, global_scale=True)
                body.move([self.translation_x, self.translation_y, 0])
            self.zoom = 1

        
        for body in self.bodies:
            body.plot()

        



def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())



if __name__ == "__main__":
    main()