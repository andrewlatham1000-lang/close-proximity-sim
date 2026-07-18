from PyQt5.QtWidgets import (QLabel, 
                             QWidget,
                             QVBoxLayout,
                             QHBoxLayout,
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
        self.setFixedWidth(450)
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
        
        self.setFixedWidth(400)
        timeline_layout = QVBoxLayout()
        timeline_layout.setContentsMargins(0,0,0,0)

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
            timeline_layout.addWidget(row)

        timeline_layout.setSpacing(0)
        self.setLayout(timeline_layout)
        self.setFixedSize(self.minimumSizeHint()) # Keeps widget compact on screen


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
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setText("Right dock")
        self.setStyleSheet("background-color:gray; font-size:22px")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFixedWidth(400)