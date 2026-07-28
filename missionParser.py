from objects import *
import json
from numpy import array

def load_body(b):
    # Convert json data into a Body object for use in simulation
    body = Body()
    body.name = b["name"]
    body.position = b["position"]
    body.velocity = b["velocity"]

    for s in b["shapes"]:
        if s["type"].lower() == "cube":
            shape = Cube()
        elif s["type"].lower() == "cylinder":
            shape = Cylinder()
        elif s["type"].lower() == "sphere":
            shape = Sphere()

        shape.scale(s["scale"])
        if type(s["rotate"]) == list:
            shape.rotate(s["rotate"][:3], s["rotate"][3])
        if type(s["move"]) == list:
            shape.move(s["move"])

        body.add(shape)

    for t in b["thrusters"]:
        thruster = Thruster(t["name"])
        thruster.position = t["position"]
        body.add(thruster)


    if type(b["rotate"]) == list:
        body.rotate(b["rotate"][:3], b["rotate"][3])
    
    if type(b["H"]) == list:
        body.dH(b["H"])

    return body


def load_timeline(events):
    # Loads timeline data from json file
    ts = len(events) * [0]
    es = len(events) * [""]
    for i, time in enumerate(events):
        t_list = [float(i) for i in time.split(":")]
        # Converts time string from HH:MM:SS.SSS into integer milliseconds
        t_ms = 1000 * (t_list[2] + 60 * (t_list[1] + 60 * t_list[0]))
        ts[i] = t_ms
        es[i] = events[time]
    
    return ts, es

def load_target(data):
    # Loads data about the target point from json file
    target_data = [data[key] for key in data]
    return target_data


def load(path):
    # Loads and returns relevent mission data from json file
    with open(path) as f:
        mission_data = json.load(f)
    
    mission_objects = array([load_body(b) for b in mission_data["bodies"]])
    event_times, mission_events = load_timeline(mission_data["events"])
    target_data = load_target(mission_data["target"])

    return mission_objects, event_times, mission_events, target_data
