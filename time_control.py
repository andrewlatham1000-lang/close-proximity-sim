
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QWidget, 
    QLabel,
    QLCDNumber, 
    QPushButton)

class TimeControl(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.setFixedHeight(60)

        self.display = TimeDisplay(self)
        self.display.setGeometry(0,0,250, 60)
        self.setStyleSheet("background-color:black")

        button_style = (
            "QPushButton {"
            "background-color:black;"
            "border-radius:8px;"
            "}"
            "QPushButton:hover {"
            "background-color:#8B8B8B;"
            "border: 3px outset #444444;"
            "}"
            "QPushButton:pressed {"
            "background-color:#555555;"
            "border: 3px inset #444444;"
            "}")

        self.start_button = QPushButton(icon=QIcon("icons\\play_icon.svg"), parent=self)
        self.start_button.setGeometry(255,0, 60, 60)
        self.start_button.setStyleSheet(button_style)
        self.start_button.setIconSize(QSize(60, 60))
        self.start_button.clicked.connect(self.parent.begin_simulation)

        self.pause_button = QPushButton(icon=QIcon("icons\\pause_icon.svg"), parent=self)
        self.pause_button.setGeometry(320,0, 60, 60)
        self.pause_button.setStyleSheet(button_style)
        self.pause_button.setIconSize(QSize(60, 60))
        self.pause_button.clicked.connect(self.parent.pause_simulation)

        self.reset_button = QPushButton(icon=QIcon("icons\\replay_icon.svg"), parent=self)
        self.reset_button.setGeometry(385,0, 60, 60)
        self.reset_button.setStyleSheet(button_style)
        self.reset_button.setIconSize(QSize(50, 50))
        self.reset_button.clicked.connect(self.parent.reset_simulation)

        self.warp_down = QPushButton(icon=QIcon("icons\\slow_warp_disabled.svg"), parent=self)
        self.warp_down.setGeometry(450,0, 60, 60)
        self.warp_down.setStyleSheet(button_style)
        self.warp_down.setIconSize(QSize(50, 50))
        self.warp_down.clicked.connect(self.parent.decrease_speed)
        self.warp_down.setEnabled(False)
        

        self.warp_up = QPushButton(icon=QIcon("icons\\fast_warp.svg"), parent=self)
        self.warp_up.setGeometry(515,0, 60, 60)
        self.warp_up.setStyleSheet(button_style)
        self.warp_up.setIconSize(QSize(50, 50))
        self.warp_up.clicked.connect(self.parent.increase_speed)

        self.speed_factor = QLabel(parent=self)
        self.speed_factor.setText("x1")
        self.speed_factor.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        self.speed_factor.setStyleSheet(
            "background-color:black;"
            "color:white;"
            "font-size: 40px;" 
            "font-weight: bold;"
            "font-family:'Lucida Console', monospace;")
        self.speed_factor.setGeometry(585, 0, 110, 60)


class TimeDisplay(QLCDNumber):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setSegmentStyle(QLCDNumber.SegmentStyle.Filled)
        self.setDigitCount(11)
        self.setStyleSheet("background-color:black; color:#00ff00")

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