import sys
from PyQt5.QtWidgets import QApplication

from objects import *
from time_control import *
from dock_panels import *
from mainwindow import MissionWindow

MISSION_PATH = "missions\\test_mission.json"

def main():
    # Start GUI and load in mission information
    app = QApplication(sys.argv)
    window = MissionWindow()
    window.add_mission(MISSION_PATH)

    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()