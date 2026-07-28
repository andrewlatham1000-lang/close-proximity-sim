import json
import numpy as np

def SET(cmd, dt):
    pass

def ADD(body, cmd, dt):
    c, b, variable, *value = cmd.split()
    value = json.loads("".join(value))
    if variable == "H":
        body.dH(value)

def BURN(body, cmd, dt):
    c, b, thruster_name, *vector, burn_time = cmd.split()
    vector = json.loads("".join(vector))
    burn_time = 1000 * float(burn_time)
    dt = float(dt)
    for thruster in body.thrusters:
        if thruster.name == thruster_name:
            if burn_time <= dt: # can do in single timestep
                body.thruster.burn(vector, burn_time)
                return None
            else:
                thruster.burn(vector, dt)
                remaining_time = (burn_time - dt) / 1000
                return_cmd = f"{c} {b} {thruster_name} {vector} {remaining_time}"
                return return_cmd
            
    Exception(f"Thruster {thruster_name} not found")

def SOLVE():
    pass

all_commands = [
    SET, # set [body] [variable] [value]
    ADD, # add [body] [variable] [value]
    BURN, # burn [body] [thruster] [vector] [duration]
    SOLVE, # later
]

def execute_commands(bodies, cmds, dt):
    body_names = np.array([b.name for b in bodies])
    cmds = cmds.split(";")
    resps = np.array([], dtype=object)
    for cmd in cmds:
        if cmd != "":
            func = cmd.strip().split()[0].upper()
            try:
                f = eval(func)
                if f in all_commands:
                    target_name = cmd.strip().split()[1]
                    if target_name in body_names:
                        body = bodies[np.where(body_names == target_name)[0][0]]
                        resp = f(body, cmd, dt)
                        resps = np.append(resps, resp)
                    else:
                        Exception(f"{target_name} cannot be found")
            except:
                Exception(f"{func} is not a recognised command")

    return resps