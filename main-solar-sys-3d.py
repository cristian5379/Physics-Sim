from vpython import sphere, vector, color, rate, canvas, button, slider, wtext, checkbox
import numpy as np

# G = 4*pi^2 / (365.25^2). This makes AU and days work out so the Earth 
# is basically at 1 AU and moves at a sane speed.
G = 0.00029591220828559 
dt = 0.25 # base step. If to fast, Mercury flies away.
eps = 1e-8 # softening factor so if planets collide we don't get infinite accelerations.
t = 0.0
paused = False

# --- DATA ---
# [name, mass, dist, inc, color, size]
data = [
    ["Sun",     1.0,        0.0,    0.0,  color.yellow, 0.06],
    ["Mercury", 1.65e-7,    0.387,  7.0,  color.gray(0.7), 0.01],
    ["Venus",   2.45e-6,    0.723,  3.39, color.orange, 0.013],
    ["Earth",   3.00e-6,    1.0,    0.0,  color.blue, 0.014],
    ["Mars",    3.23e-7,    1.524,  1.85, color.red, 0.012],
    ["Jupiter", 9.55e-4,    5.203,  1.3,  color.white, 0.03],
    ["Saturn",  2.86e-4,    9.537,  2.49, color.cyan, 0.027],
    ["Uranus",  4.37e-5,    19.191, 0.77, color.green, 0.024],
    ["Neptune", 5.15e-5,    30.07,  1.77, color.magenta, 0.024]
]

n = len(data)
m = np.array([p[1] for p in data])
r = np.zeros((n, 3))
v = np.zeros((n, 3))

# --- SETUP POSITIONS AND VELOCITIES ---
for i in range(n):
    a = data[i][2]
    inc = np.radians(data[i][3])
    if i == 0: continue # Sun at 0,0,0
    
    r[i] = [a, 0, 0]
    # v = sqrt(GM/r). Since M_sun approx 1 and G is calibrated, 
    # we just use the 2*pi/T formula but for days.
    v_mag = (2 * np.pi / np.sqrt(a)) / 365.25
    v[i] = [0, v_mag * np.cos(inc), v_mag * np.sin(inc)]

# Fix the Sun's velocity so the whole system doesn't drift off screen
p_total = np.sum(m[:, None] * v, axis=0)
v[0] = -p_total / m[0]

# --- VISUALS ---
scene = canvas(title="Solar System", width=1000, height=600, background=color.black)
scene.range = 30
balls = []
for i in range(n):
    b = sphere(pos=vector(*r[i]), radius=data[i][5], color=data[i][4], make_trail=True)
    balls.append(b)

# ---  UI ---
txt = wtext(text="Days: 0")
def p_btn(b): 
    global paused
    paused = not paused
pause_click = button(text="Pause/Go", bind=p_btn)

def r_btn(b):
    global r, v, t
    r, v, t = np.copy(r0), np.copy(v0), 0.0
    for i in range(n):
        balls[i].pos = vector(*r[i])
        balls[i].clear_trail()
reset_click = button(text="Reset", bind=r_btn)

# --- PHYSICS ENGINE ---
# I'm using Leapfrog here (Kick-Drift-Kick).
# Pre-calculate first 'a' for the first half-kick
diff = r[:, None, :] - r[None, :, :]
dist3 = (np.sum(diff**2, axis=-1) + eps)**1.5
inv_r3 = 1.0 / dist3
np.fill_diagonal(inv_r3, 0)
a_vec = -G * np.sum(m[None, :, None] * diff * inv_r3[:, :, None], axis=1)

# Initial half-kick
v += 0.5 * a_vec * dt

# Main Loop
while True:
    rate(200)
    if not paused:
        # 1. DRIFT: update positions
        r += v * dt
        
        # 2. UPDATE VISUALS
        for i in range(n):
            balls[i].pos = vector(*r[i])
        
        # 3. KICK: recalculate acceleration and update velocity
        # Standard N-body gravity: a = G * sum(m_j * r_ij / |r_ij|^3)
        diff = r[:, None, :] - r[None, :, :]
        dist3 = (np.sum(diff**2, axis=-1) + eps)**1.5
        inv_r3 = 1.0 / dist3
        np.fill_diagonal(inv_r3, 0)
    
        a_vec = -G * np.sum(m[None, :, None] * diff * inv_r3[:, :, None], axis=1)
        v += a_vec * dt
        
        t += dt
        txt.text = f"Days: {int(t)}"

    if t > 1000000: break