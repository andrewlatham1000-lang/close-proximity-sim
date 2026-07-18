import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *
from PyQt5.QtCore import Qt, QTimer, QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QDesktopWidget
from PyQt5.QtOpenGL import *

from objects import *
from glwidget import glWidget
from time_control import *
from dock_panels import *
import missionParser as mp
import relativeMotion as relmo

class MissionWindow(QMainWindow):
    # Main window containing OpenGL rendered visualiser,
    # time controls, mission timeline, and right dock (TBD)
     
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Relative motion")
        self.setStyleSheet("background-color:black")
        self.setWindowIcon(QIcon("icons\\main_window_icon.png"))
        # Icon from Icon8 (https://icons8.com/icon/5374/satellite)
        self.setIconSize(QSize(20, 20))
        self.resize(1700, 980)

        # Information about the target point, currently set as a Keplerian orbit
        # defined in the mission file
        self.mission_path = str()
        self.mu = float()
        self.target_data = np.array([0., 0., 0., 0., 0., 0.])
        self.target_position = np.array([0., 0., 0.])
        self.target_velocity = np.array([0., 0., 0.])
        self.target_h = 0
        self.tp0 = float()

        # Keep track of time passing in simulation 
        # and mission events occuring
        self.simulation_time = 0
        self.simulation_dt = 10
        self.simulation_paused = True # Flag to allow for camera movement when simulation is paused
        self.event_times = list()
        self.mission_cmds = list()
        self.event_index = 0
        
        self.time_warp = np.array([1,2,5,10])
        self.current_warp = 0
        
        # Main timer for refreshing GUI
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.timestep)

    def initUI(self):
        # Called after loading a mission to this object
        # Creates all child widgets and adds to window layout
        self.gl = glWidget(self)
        self.time_controls = TimeControl(self)
        self.left_dock = LeftDock(self)
        self.left_dock.initialise_timeline()
        self.right_dock = RightDock(self)

        main_windows_layout = QHBoxLayout()
        main_windows_layout.addWidget(self.left_dock)
        main_windows_layout.addWidget(self.gl)
        main_windows_layout.addWidget(self.right_dock)
        main_windows_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
       
        central_layout = QVBoxLayout()
        central_layout.addWidget(self.time_controls)
        central_layout.addLayout(main_windows_layout)

        central_widget = QWidget()
        central_widget.setLayout(central_layout)
        self.setCentralWidget(central_widget)

        # Makes window appear centered in screen when first created
        frame = self.frameGeometry()
        fw, fh = frame.width(), frame.height()
        screen_centre = QDesktopWidget().availableGeometry().center()
        centre_x, centre_y = screen_centre.x(), screen_centre.y()
        
        self.move(
            centre_x - fw//2,
            (centre_y - fh//2) // 2)


    def add_mission(self, path):
        # Loads mission information from json file, sets information about target point
        # then makes GUI

        self.mission_path = path
        bodies, self.event_times, self.mission_cmds, target = mp.load(path)
        self.mu = target[0]
        self.target_data = target[1:]
        self.tp0 = relmo.theta2tp(target[6], target[0], target[1], target[2]) * 1000
        target_state = relmo.find_LVLH_state(target[0], target[6], target[1], target[2])
        self.target_position, self.target_velocity = target_state[:3], target_state[3:]
        self.target_h = np.sqrt(self.mu * target[1] * (1 - target[2]**2))

        self.initUI()
        self.gl.bodies = bodies
        self.gl.update()


    def begin_simulation(self):
        self.simulation_paused = False
        self.timer.start(self.simulation_dt)


    def pause_simulation(self):
        self.simulation_paused = True
        self.timer.stop()


    def reset_simulation(self):
        # Resets all variables to default
        # Can probably move sections of this to separate reset functions

        self.simulation_paused = True
        self.timer.stop()
        self.simulation_time = 0
        self.event_index = 0
        self.time_controls.display.show_time()
        self.current_warp = 0
        self.time_controls.warp_down.setIcon(QIcon("icons\\slow_warp_disabled.svg"))
        self.time_controls.warp_up.setIcon(QIcon("icons\\fast_warp.svg"))
        self.time_controls.warp_down.setEnabled(False)
        self.time_controls.warp_up.setEnabled(True)
        self.time_controls.speed_factor.setText(f"x{self.time_warp[self.current_warp]}")
        mission = mp.load(self.mission_path)
        bodies, target = mission[0], mission[3]
        self.gl.bodies = bodies
        self.target_data[5] = target[6]
        self.gl.update()
        self.left_dock.initialise_timeline()


    def increase_speed(self):
        # Increases current time warp factor
        self.current_warp += 1
        self.time_controls.warp_down.setEnabled(True)
        self.time_controls.warp_down.setIcon(QIcon("icons\\slow_warp.svg"))
        self.time_controls.speed_factor.setText(f"x{self.time_warp[self.current_warp]}")

        if self.current_warp == len(self.time_warp) - 1: # Diasable if can't warp faster
            self.time_controls.warp_up.setEnabled(False)
            self.time_controls.warp_up.setIcon(QIcon("icons\\fast_warp_disabled.svg"))


    def decrease_speed(self):
        # Decreases current time warp factor
        self.current_warp -= 1
        self.time_controls.warp_up.setEnabled(True)
        self.time_controls.warp_up.setIcon(QIcon("icons\\fast_warp.svg"))
        self.time_controls.speed_factor.setText(f"x{self.time_warp[self.current_warp]}")

        if self.current_warp == 0: # Diasble if can't warp slower
            self.time_controls.warp_down.setEnabled(False)
            self.time_controls.warp_down.setIcon(QIcon("icons\\slow_warp_disabled.svg"))
    

    def timestep(self):
        # Main simulation timestep, called executed by timer

        if (self.event_index < len(self.event_times) and
            self.simulation_time >= self.event_times[self.event_index]):
            # Execute mission commands at specificed simulation times
            mp.execute_commands(self.gl.bodies, self.mission_cmds[self.event_index])
            self.left_dock.increment_timeline()
            self.event_index += 1

        # Update true anomaly of target point, then find updated LVLH state at this point
        self.target_data[5] = relmo.tp2theta(
            (self.tp0 + self.simulation_time)/1000, 
            self.mu,
            self.target_data[0],
            self.target_data[1])
        
        target_state = relmo.find_LVLH_state(
            self.mu, 
            self.target_data[5], 
            self.target_data[0], 
            self.target_data[1])
        
        self.target_position, self.target_velocity = target_state[:3], target_state[3:]
                            
        for body in self.gl.bodies:
            # Integrate forward motion of all bodies,
            body.update_timestep(self.time_warp[self.current_warp] * self.simulation_dt,
                                 self.mu,
                                 self.target_h,
                                 self.target_position,
                                 self.target_velocity)
        
        # Update visualiser widget and increment simulation time
        self.gl.update()
        self.simulation_time += self.time_warp[self.current_warp] * self.simulation_dt
        self.time_controls.display.show_time()