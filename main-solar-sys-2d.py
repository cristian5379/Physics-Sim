import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

view_range = 5.0  # AU (set to 5-20-35 for inner planets)
dt = 4.5           # Days per step. If Mercury flies away, make this smaller.
g_const = 0.0002959122  # G in AU^3 / (day^2 * Msun). Derived from 4*pi^2 / 365.25^2
soften = 1e-8      # To stop the divide by zero if planets collide
trail_limit = 2000 # How many points to keep before the line gets too long
paused = False
show_trails = True

# --- PLANET DATA (Mass in Solar Masses, Distance in AU) ---
# Sun, Merc, Ven, Earth, Mars, Jup, Sat, Ura, Nep
m = np.array([1.0, 1.65e-7, 2.44e-6, 3.00e-6, 3.22e-7, 9.54e-4, 2.85e-4, 4.36e-5, 5.15e-5])
a = np.array([0.0, 0.387, 0.723, 1.0, 1.524, 5.203, 9.537, 19.191, 30.07])
colors = ["gold", "gray", "orange", "blue", "red", "white", "cyan", "green", "magenta"]
names = ["Sun", "Mercury", "Venus", "Earth", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune"]

# --- INITIAL STATE ---
n = len(m)
r = np.zeros((n, 2))
v = np.zeros((n, 2))

for i in range(n):
    if i == 0: continue
    r[i, 0] = a[i]
    # Circular orbit velocity formula: v = sqrt(G*M/r)
    # I'm assuming M_sun >> M_planet so I just use M=1.0
    v_mag = np.sqrt(g_const * 1.0 / a[i])
    v[i, 1] = v_mag

# Center of mass correction so the Sun doesn't drift off screen immediately
v_sum = np.sum(v * m[:, np.newaxis], axis=0)
v[0] = -v_sum / m[0]

# --- SETUP PLOT ---
fig = plt.figure(figsize=(8, 8))
ax = plt.axes(xlim=(-view_range, view_range), ylim=(-view_range, view_range))
ax.set_facecolor('black')
dots = ax.scatter(r[:, 0], r[:, 1], c=colors, s=[80, 10, 15, 15, 12, 40, 35, 30, 30])
trails = [ax.plot([], [], color=colors[i], lw=0.5)[0] for i in range(n)]
history = [([], []) for _ in range(n)]

# --- PHYSICS AND KEYBOARD HACKS ---
def on_press(event):
    global paused, show_trails
    if event.key == ' ': paused = not paused
    if event.key == 't': show_trails = not show_trails

fig.canvas.mpl_connect('key_press_event', on_press)

def update(frame):
    global r, v, paused
    
    if not paused:
        # LEAPFROG INTEGRATOR (Kick-Drift-Kick)
        # 1. Half-kick velocity
        for _ in range(2): # Doing this twice for the half-steps
            acc = np.zeros((n, 2))
            for i in range(n):
                for j in range(n):
                    if i == j: continue
                    dx = r[j, 0] - r[i, 0]
                    dy = r[j, 1] - r[i, 1]
                    dist_sq = dx**2 + dy**2 + soften
                    # F = G*m1*m2 / r^2 -> a = G*m2 / r^2
                    f_mag = g_const * m[j] / (dist_sq**1.5)
                    acc[i, 0] += f_mag * dx
                    acc[i, 1] += f_mag * dy
            
            if _ == 0:
                v += acc * (dt / 2.0)
                r += v * dt  # 2. Drift position
            else:
                v += acc * (dt / 2.0) # 3. Final half-kick

    # Update the dots
    dots.set_offsets(r)
    
    # Update trails
    for i in range(n):
        if show_trails:
            history[i][0].append(r[i, 0])
            history[i][1].append(r[i, 1])
            # Safety break so the memory doesn't explode if you leave it running
            if len(history[i][0]) > trail_limit:
                history[i][0].pop(0)
                history[i][1].pop(0)
            trails[i].set_data(history[i][0], history[i][1])
            trails[i].set_visible(True)
        else:
            trails[i].set_visible(False)

    return [dots] + trails

ani = FuncAnimation(fig, update, frames=200, interval=20)
plt.title("Solar System (Space to Pause, T for Trails)")
plt.show()