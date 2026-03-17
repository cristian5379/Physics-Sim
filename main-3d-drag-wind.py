from vpython import *
import math

# ---------------------------------------------------------
# 3D Projectile Sim
# ---------------------------------------------------------

# --- Variables (Just global so I don't have to pass dicts everywhere) ---
v0 = 40.0
theta = 35.0  # elevation (deg)
phi = 20.0    # azimuth (deg) - angular measurement in a spherical coordinate system
wx, wy, wz = 0.0, 0.0, 0.0
Cd = 0.47     # sphere drag coeff from the table in ch 3
A = 0.0042    # cross section area
m = 0.145     # mass of a baseball
rho = 1.225   # air density at sea level
g = 9.81
t_mult = 1.0  # time scale

# Physics state
pos = vector(0,0,0)
v = vector(0,0,0)
t = 0.0
is_flying = False
is_paused = False

# --- Scene Setup ---
scene.title = "Projectile Motion (3D + Drag + Wind)"
scene.width = 1000
scene.height = 700
scene.up = vector(0,0,1)
scene.forward = vector(-1, -1, -0.5)

# The ground and axes (colors are just defaults)
ground = box(pos=vector(50,0,-0.1), size=vector(300, 200, 0.2), color=color.green, opacity=0.3)
x_ax = arrow(axis=vector(10,0,0), color=color.red)
y_ax = arrow(axis=vector(0,10,0), color=color.blue)

ball = sphere(pos=vector(0,0,0), radius=0.3, color=color.orange, make_trail=True)
v_arr = arrow(color=color.yellow, shaftwidth=0.1)
a_arr = arrow(color=color.cyan, shaftwidth=0.1)

# HUD for output
hud = wtext(text="Ready to launch")

# --- UI Functions ---
def sync_val(name, val):
    # This updates the global and the corresponding UI elements
    global v0, theta, phi, wx, wy, wz, Cd, A, m, rho, g, t_mult
    
    globals()[name] = float(val)
    
    if name == 'v0': s_v0.value = val; i_v0.text = str(val)
    if name == 'theta': s_th.value = val; i_th.text = str(val)
    if name == 'phi': s_ph.value = val; i_ph.text = str(val)

# UI Widgets
scene.append_to_caption("\n<b>Launch Params:</b>\n")
s_v0 = slider(min=1, max=150, value=v0, bind=lambda s: sync_val('v0', s.value))
i_v0 = winput(text=str(v0), bind=lambda i: sync_val('v0', i.text))
scene.append_to_caption(" Speed (m/s)  |  ")

s_th = slider(min=0, max=90, value=theta, bind=lambda s: sync_val('theta', s.value))
i_th = winput(text=str(theta), bind=lambda i: sync_val('theta', i.text))
scene.append_to_caption(" Elev (deg)\n")

scene.append_to_caption("\n<b>Wind Control:</b>\n")
i_wx = winput(text="0", bind=lambda i: sync_val('wx', i.text)); scene.append_to_caption(" Wx ")
i_wy = winput(text="0", bind=lambda i: sync_val('wy', i.text)); scene.append_to_caption(" Wy ")
i_wz = winput(text="0", bind=lambda i: sync_val('wz', i.text)); scene.append_to_caption(" Wz\n")

def launch_btn():
    global pos, v, t, is_flying, is_paused
    # Reset everything for a new shot
    t = 0.0
    pos = vector(0,0,0)
    
    # Trig for the 3D launch vector
    rad_th = math.radians(theta)
    rad_ph = math.radians(phi)
    # v_z is opposite/hyp, v_xy is adjacent/hyp
    v_z = v0 * math.sin(rad_th)
    v_xy = v0 * math.cos(rad_th)
    v_x = v_xy * math.cos(rad_ph)
    v_y = v_xy * math.sin(rad_ph)
    
    v = vector(v_x, v_y, v_z)
    
    ball.clear_trail()
    ball.make_trail = True
    is_flying = True
    is_paused = False

button(text="LAUNCH", bind=launch_btn)
button(text="PAUSE", bind=lambda: globals().update(is_paused=not is_paused))
button(text="RESET", bind=lambda: globals().update(is_flying=False))

# --- Physics Engine ---

def get_accel(curr_v):
    # F = ma -> a = F_drag / m + g
    # Drag formula: 1/2 * rho * v^2 * Cd * A
    wind = vector(wx, wy, wz)
    v_rel = curr_v - wind
    speed_sq = v_rel.mag2
    
    if speed_sq > 0:
        f_drag = -0.5 * rho * Cd * A * speed_sq * v_rel.hat
    else:
        f_drag = vector(0,0,0)
    
    return (f_drag / m) + vector(0,0,-g)

# --- Main Loop ---
dt = 0.01

while True:
    rate(200) # Fast enough to look smooth
    
    if is_flying and not is_paused:
        # k1
        k1_v = v
        k1_a = get_accel(v)
        
        # k2
        k2_v = v + 0.5 * dt * k1_a
        k2_a = get_accel(k2_v)
        
        # k3
        k3_v = v + 0.5 * dt * k2_a
        k3_a = get_accel(k3_v)
        
        # k4
        k4_v = v + dt * k3_a
        k4_a = get_accel(k4_v)
        
        # Update state
        pos = pos + (dt/6) * (k1_v + 2*k2_v + 2*k3_v + k4_v)
        v = v + (dt/6) * (k1_a + 2*k2_a + 2*k3_a + k4_a)
        t += dt * t_mult
        
        # Update visuals
        ball.pos = pos
        v_arr.pos = pos
        v_arr.axis = v * 0.2 # scale it down
        
        a_now = get_accel(v)
        a_arr.pos = pos
        a_arr.axis = a_now * 0.5
        
        # Ground hit check
        if pos.z <= 0:
            pos.z = 0
            ball.pos = pos
            is_flying = False
            ball.make_trail = False
            hud.text = f"Landed! Time: {t:.2f}s, Dist: {math.sqrt(pos.x**2 + pos.y**2):.2f}m"
        else:
            hud.text = f"T: {t:.2f}s | Speed: {v.mag:.2f}m/s | Alt: {pos.z:.1f}m"