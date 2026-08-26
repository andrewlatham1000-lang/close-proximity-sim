from numpy import sin, cos, tan, pi, dot, sqrt, arctan, array, concatenate
from numpy.linalg import norm

def orbit_radius(theta, a, e):
    return (a * (1-e**2)) / (1 + e * cos(theta))

def orbit_rotation(omega, i, w):
    return array([
    [cos(omega)*cos(w) - sin(omega)*cos(i)*sin(w), -cos(omega)*sin(w) - sin(omega)*cos(i)*cos(w), sin(omega)*sin(i)],
    [sin(omega)*cos(w) + cos(omega)*cos(i)*sin(w), cos(omega)*cos(i)*cos(w) - sin(omega)*sin(w), -cos(omega)*sin(i)],
    [sin(i)*sin(w), sin(i)*cos(w), cos(i)]
    ])


def relative_acceleration(state, mu, h, R, V):
    x, y, z, vx, vy, vz = state
    R_abs = norm(R)
    
    Ax = (2*mu / R_abs**3) + (h**2 / R_abs**4)
    Ay = (mu / R_abs**3) - (h**2 / R_abs**4)
    B = 2 * dot(V, R) * h / R_abs**4
    C = 2 * h / R_abs**2
    Cz = mu / R_abs**3
    
    accel_x = Ax*x - B*y + C*vy
    accel_y = -Ay*y + B*x - C*vx
    accel_z = -Cz * z
    
    return array([accel_x, accel_y, accel_z])



def tp2theta(tp, mu, a, e, tol=1e-8, nmax=10):
    Me = tp * sqrt(mu/a**3)
    tau = 2 * pi * sqrt(a**3 / mu)
    tp = tp % tau

    E0 = 0.5
    err = 1
    n = 0
    while (err > tol) and (n < nmax):
        E = E0 - (E0 - e * sin(E0) - Me)/(1 - e * cos(E0))
        err = abs(E - E0)
        E0 = E
        
    theta = 2 * arctan(sqrt((1 + e) / (1 - e)) * tan(E0/2))
    if theta < 0:
        theta += pi
    
    return theta

def theta2tp(theta, mu, a, e):
    E = 2 * arctan(sqrt((1 - e) / (1 + e)) * tan(theta/2))
    Me = E - e * sin(E)
    tp = sqrt(a**3 / mu) * Me
    return tp

def find_LVLH_state(mu, theta, a, e):
    r = orbit_radius(theta, a, e)
    h = sqrt(mu * a * (1 - e**2))
    vr = mu/h * e * sin(theta)
    vp = h/r
    
    state = array([r, 0, 0,
                   vr, vp, 0])
    
    return state
    
def CW_prop(state0, mu, a, t):
    n = sqrt(mu / a**3)
    nt = n * t
    r0, v0 = state0[:3], state0[3:]
    
    phi_rr = array([[  4 - 3 * cos(nt)   ,   0   ,    0    ],
                    [6 * (sin(nt) - nt)  ,   1   ,    0    ],
                    [         0          ,   0   , cos(nt) ]])
                       
    phi_rv = array([[    (1 / n) * sin(nt)   ,      (2 / n) * (1 - cos(nt))      ,        0     ],
                    [(2 / n) * (cos(nt) - 1) ,  (1 / n) * (4 * sin(nt) - 3 * nt) ,        0     ],
                    [            0           ,                 0                 , (1/n)*sin(nt)]])
    
    phi_vr = array([[    3 * n * sin(nt)    ,  0  ,       0     ],
                    [6 * n * (cos(nt) - 1)  ,  0  ,       0     ],
                    [           0           ,  0  , -n * sin(nt)]])
                       
    phi_vv = array([[   cos(nt)  ,    2 * sin(nt)   ,    0   ],
                   [-2 * sin(nt) ,  4 * sin(nt) - 3 ,    0   ],
                   [       0     ,         0        , cos(nt)]])
    
    r1 = dot(phi_rr, r0) + dot(phi_rv, v0)
    v1 = dot(phi_vr, r0) + dot(phi_vv, v0)
    return concatenate((r1, v1))