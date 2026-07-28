from PyQt5.QtWidgets import (QLabel, 
                             QWidget,
                             QVBoxLayout,
                             QHBoxLayout,
                             QScrollArea,
                             QComboBox,
                             )
from PyQt5.QtCore import Qt
from numpy import insert


# CSS styling for the mission timeline panel
# Could move to dedicated CSS file in future
time_neutral_style = (
            "background-color: gray;"
            "color: #f5f5f5;"
            "font-size: 19px;"
            "font-family: 'Lucida Console';"
            "border: 2px outset #444444;"
            "padding: 5px 0px 5px 0px;")

cmd_neutral_style = ("background-color: gray;"
                     "color: #f5f5f5;"
                     "font-size: 17px; "
                     "font-family: 'Lucida Console';"
                     "border: 2px outset #444444;"
                     "padding: 3px;")


time_active_style = (
            "background-color: #BBBBBB; "
            "color: #000000;"
            "font-size: 19px; "
            "font-family: 'Lucida Console';"
            "border: 2px outset #444444;"
            "padding: 5px 0px 5px 0px;")

cmd_active_style = (
            "background-color: #BBBBBB; "
            "color: #000000;"
            "font-size: 17px; "
            "font-family: 'Lucida Console';"
            "border: 2px outset #444444;"
            "padding: 5px;")


time_inactive_style = (
            "background-color: #555555; "
            "color: #f5f5f5;"
            "font-size: 19px; "
            "font-family: 'Lucida Console';"
            "border: 2px inset #444444;"
            "padding: 5px 0px 5px 0px;")

cmd_inactive_style = (
            "background-color: #555555; "
            "color: #f5f5f5;"
            "font-size: 17px; "
            "font-family: 'Lucida Console';"
            "border: 2px inset #444444;"
            "padding: 5px;")


class LeftDock(QLabel):
    # Widget creation for the left dock on the screen
    # Contains information about the mission timeline, which commands
    # are being run when etc.
    # Defined as a QLabel to set a background color for the whole panel

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setFixedWidth(500)
        self.setContentsMargins(0,0,0,0)
        self.setStyleSheet("background-color: gray;")

        # Adding timeline widget to the top centre of the dock
        self.timeline = MissionTimeline(self)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter) 
        layout.setSpacing(0)
        layout.addWidget(self.timeline)
        self.setLayout(layout)

    def initialise_timeline(self):
        # Resetting CSS for all timeline events to neutral, then first event to active
        for row in self.timeline.event_table:
            row.time_label.setStyleSheet(time_neutral_style)
            row.cmd_label.setStyleSheet(cmd_neutral_style)
        
        self.timeline.event_table[0].time_label.setStyleSheet(time_active_style)
        self.timeline.event_table[0].cmd_label.setStyleSheet(cmd_active_style)

    def increment_timeline(self):
        # When mission event occurs, set the current event to inactive (ie. completed)
        # then if another event is planned, set it to active
        curr_event = self.timeline.event_table[self.parent.event_index]
        curr_event.time_label.setStyleSheet(time_inactive_style)
        curr_event.cmd_label.setStyleSheet(cmd_inactive_style)

        if self.parent.event_index < len(self.parent.event_times) - 1:
            next_event = self.timeline.event_table[self.parent.event_index + 1] 
            next_event.time_label.setStyleSheet(time_active_style)
            next_event.cmd_label.setStyleSheet(cmd_active_style)


class MissionTimeline(QWidget):
    # Main widget for the left dock
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        
        self.setFixedWidth(480)
        timeline_layout = QVBoxLayout()
        timeline_layout.setContentsMargins(0,0,0,0)
        timeline_layout.setSpacing(0)

        event_widget = QWidget()
        event_layout = QVBoxLayout()
        event_layout.setContentsMargins(0,0,0,0)

        event_scroll = QScrollArea()
        event_scroll.setFixedHeight(600)

        title = QLabel("SIMULATION TIMELINE")
        title.setFixedHeight(60)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("background-color:gray;" # Will probably also be moved into dedicated CSS file
                           "font-size: 30px;"
                           "color: #f5f5f5;"
                           "font-family:'Lucida Console';"
                           "border: 2px outset #444444;"
                           "font-weight: bold;")
        timeline_layout.addWidget(title)

        event_times = self.parent.parent.event_times
        events = self.parent.parent.mission_cmds
        self.event_table = [TableRow(self, event_times[i], events[i]) for i in range(len(events))]

        # First event should always be at 00:00:00.00, so add comment that it is initialisation
        self.event_table[0].cmd_label.setText("INITIALISATION\n"+self.event_table[0].cmd_label.text()) 

        for row in self.event_table:
            event_layout.addWidget(row)

        event_widget.setLayout(event_layout)
        event_scroll.setWidget(event_widget)
        timeline_layout.addWidget(event_scroll)

        
        self.setLayout(timeline_layout)
        self.setFixedHeight(self.minimumSizeHint().height()) # Keeps widget compact on screen

class TableRow(QWidget):
    # Row for timeline table containing time at which an event occurs
    # and the commands used in the event
    def __init__(self, parent, time, cmds):
        super().__init__()
        self.parent = parent
        self.setContentsMargins(0,0,0,0)
        
        # Convert time in milliseconds to time string for display
        cs = str(int((time % 1000) // 10))
        ss = str(int((time // 1000)  % 60))
        mm = str(int((time // 1000 // 60)  % 60))
        hh = str(int((time // 1000 // 60 // 60)  % 60))
        if len(cs) != 2:
            cs = "0" + cs
        if len(ss) != 2:
            ss = "0" + ss
        if len(mm) != 2:
            mm = "0" + mm
        if len(hh) != 2:
            hh = "0" + hh

        formatted_time = f"{hh}:{mm}:{ss}.{cs}"
        formatted_events =  "\n".join([e.strip() for e in cmds.split(";")]) # Write each command on new line
        
        no_of_events = len(cmds.split(";"))
        if no_of_events == 1: # Resizing row height based on number of commands to execute
            self.setFixedHeight(60)
        else:
            self.setFixedHeight(40 * no_of_events)
        
    
        self.time_label = QLabel(formatted_time)
        self.time_label.setStyleSheet(time_neutral_style)
        self.time_label.setFixedWidth(140)

        self.cmd_label = QLabel(formatted_events)
        self.cmd_label.setStyleSheet(cmd_neutral_style)

        row_layout = QHBoxLayout()
        row_layout.setSpacing(0)
        row_layout.setContentsMargins(0,2,0,0)
        row_layout.addWidget(self.time_label)
        row_layout.addWidget(self.cmd_label)

        self.setLayout(row_layout)

    def active(self):
        self.time_label.setStyleSheet(time_active_style)
        self.cmd_label.setStyleSheet(cmd_active_style)
    
    def inactive(self):
        self.time_label.setStyleSheet(time_inactive_style)
        self.cmd_label.setStyleSheet(cmd_inactive_style)






class RightDock(QLabel):
    """
    Use to show information about current state of selected object
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setStyleSheet("background-color:gray; font-size:22px")
        self.setFixedWidth(400)

        self.info = ObjectInfo(self)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter) 
        layout.setSpacing(0)
        layout.addWidget(self.info)
        self.setLayout(layout)


class ObjectInfo(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.cur_index = 0

        self.setFixedWidth(380)

        info_layout = QVBoxLayout()
        title = QLabel()
        self.combo = QComboBox()
        self.info = QLabel()

        title.setText("OBJECT INFORMATION")
        title.setFixedHeight(60)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("background-color:gray;" # Will probably also be moved into dedicated CSS file
                            "font-size: 30px;"
                            "color: #f5f5f5;"
                            "font-family:'Lucida Console';"
                            "border: 2px outset #444444;"
                            "font-weight: bold;")

        for b in self.parent.parent.bodies:
            self.combo.addItem(b.name)

        def update_index(i):
            self.cur_index = i
            self.view_info()
            
        self.combo.currentIndexChanged.connect(update_index)
        self.combo.setFixedHeight(40)
        self.combo.setStyleSheet(
            "QComboBox{"
            "color: #f5f5f5;"
            "font-family: 'Lucida Console';"
            "selection-background-color: gray;"
            "border: 2px outset #444444;"
            "}"

            "QComboBox QAbstractItemView{"
            "selection-background-color: #BBBBBB;"
            "color: #f5f5f5;"
            "selection-color: #000000;"
            "}"
        )

        self.info.setFixedWidth(360)
        self.info.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.info.setStyleSheet("border: 2px outset #444444;"
                                "font-size: 19px;"
                                "font-family: 'Lucida Console';"
                                "color: #f5f5f5;")
        
        info_layout.addWidget(title)
        info_layout.addWidget(self.combo)
        info_layout.addWidget(self.info)
        self.view_info()

        self.setLayout(info_layout)
        self.setFixedHeight(self.minimumSizeHint().height())

    def view_info(self):
        selected_body = self.parent.parent.bodies[self.cur_index]
        name = selected_body.name
        position = [round(p, 4) for p in selected_body.position]
        velocity = [round(v, 4) for v in selected_body.velocity]
        mass = round(selected_body.mass, 4)

        self.info.setText(f"Name: {name}\n\n"
                          
                          f"Mass [kg]: {mass}\n\n"

                          f"              X = {position[0]}\n"
                          f"Position [m]: Y = {position[1]}\n"
                          f"              Z = {position[2]}\n\n"

                          f"                VX = {velocity[0]}\n"
                          f"Velocity [m/s]: VY = {velocity[1]}\n"
                          f"                VZ = {velocity[2]}\n"
                          )