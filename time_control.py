
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QWidget, 
    QLabel,
    QLCDNumber, 
    QPushButton)

with open("stylesheets\\time_controls.css") as f:
    TIME_CSS = f.read()

class TimeControl(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.setFixedHeight(60)

        self.display = TimeDisplay(self)
        self.display.setGeometry(0,0,250, 60)
        self.setStyleSheet(TIME_CSS)

        self.start_button = QPushButton(icon=QIcon("icons\\play_icon.svg"), parent=self)
        self.start_button.setGeometry(255,0, 60, 60)
        self.start_button.setIconSize(QSize(60, 60))
        self.start_button.clicked.connect(self.parent.begin_simulation)

        self.pause_button = QPushButton(icon=QIcon("icons\\pause_icon.svg"), parent=self)
        self.pause_button.setGeometry(320,0, 60, 60)
        self.pause_button.setIconSize(QSize(60, 60))
        self.pause_button.clicked.connect(self.parent.pause_simulation)

        self.reset_button = QPushButton(icon=QIcon("icons\\replay_icon.svg"), parent=self)
        self.reset_button.setGeometry(385,0, 60, 60)
        self.reset_button.setIconSize(QSize(50, 50))
        self.reset_button.clicked.connect(self.parent.reset_simulation)

        self.warp_down = QPushButton(icon=QIcon("icons\\slow_warp_disabled.svg"), parent=self)
        self.warp_down.setGeometry(450,0, 60, 60)
        self.warp_down.setIconSize(QSize(50, 50))
        self.warp_down.clicked.connect(self.parent.decrease_speed)
        self.warp_down.setEnabled(False)
        

        self.warp_up = QPushButton(icon=QIcon("icons\\fast_warp.svg"), parent=self)
        self.warp_up.setGeometry(515,0, 60, 60)
        self.warp_up.setIconSize(QSize(50, 50))
        self.warp_up.clicked.connect(self.parent.increase_speed)

        self.speed_factor = QLabel(parent=self)
        self.speed_factor.setProperty("class", "speed_factor")
        self.speed_factor.setText("x1")
        self.speed_factor.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        self.speed_factor.setGeometry(585, 0, 110, 60)

        self.zoom_level = QLabel(self)
        self.zoom_level.setProperty("class", "zoom_level")
        self.zoom_level.setText("Zoom: x1.00")
        self.zoom_level.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        self.zoom_level.setGeometry(750, 0, 350, 60)

    def set_zoom(self, zoom):
        self.zoom_level.setText(f"Zoom: x{zoom:.2f}")

    def reset(self):
        self.display.show_time()
        self.warp_down.setIcon(QIcon("icons\\slow_warp_disabled.svg"))
        self.warp_up.setIcon(QIcon("icons\\fast_warp.svg"))
        self.warp_down.setEnabled(False)
        self.warp_up.setEnabled(True)
        self.speed_factor.setText(f"x1")


class TimeDisplay(QLCDNumber):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setSegmentStyle(QLCDNumber.SegmentStyle.Filled)
        self.setDigitCount(11)
        self.setStyleSheet(TIME_CSS)

        self.show_time()

    def show_time(self):
        t_in_ms = self.parent.parent.simulation_time
        cs = str((t_in_ms % 1000) // 10)
        ss = str((t_in_ms // 1000)  % 60)
        mm = str((t_in_ms // 1000 // 60)  % 60)
        hh = str((t_in_ms // 1000 // 60 // 60)  % 60)
        if len(cs) != 2:
            cs = "0" + cs
        if len(ss) != 2:
            ss = "0" + ss
        if len(mm) != 2:
            mm = "0" + mm
        if len(hh) != 2:
            hh = "0" + hh
        
        time = f"{hh}:{mm}:{ss}.{cs}"
        self.display(time)