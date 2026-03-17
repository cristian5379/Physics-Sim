import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Slider, Button

# --- PROJECTILE MOTION (WITH DRAG & WIND) Using Rk4 ---

g = 9.81
rho = 1.225
Cd = 0.47      # Standard for a sphere
area = 0.0042  # Baseball size
mass = 0.145
dt = 0.01      # Step size

def get_accel(v_vec, wind_vec):
    """
    Calculates acceleration. 
    Formula: F_drag = 0.5 * rho * v^2 * Cd * A
    Then a = F/m + gravity
    """
    # Relative velocity
    v_rel = v_vec - wind_vec
    speed_rel = np.linalg.norm(v_rel)
    
    if speed_rel > 0:
        # Drag is opposite to the relative motion
        f_drag = -0.5 * rho * Cd * area * speed_rel * v_rel
    else:
        f_drag = np.zeros(2)
        
    accel_x = f_drag[0] / mass
    accel_y = (f_drag[1] / mass) - g
    return np.array([accel_x, accel_y])

def run_simulation(v0, angle_deg, wx, wy):
    """
    This is the RK4 integrator. 
    State is [x, y, vx, vy]
    """
    angle_rad = np.radians(angle_deg)
    # Initial state
    s = np.array([0.0, 0.0, v0 * np.cos(angle_rad), v0 * np.sin(angle_rad)])
    w = np.array([wx, wy])
    
    x_hist, y_hist = [s[0]], [s[1]]
    
    # Loop until it hits the ground
    for _ in range(2000): # Safety break
        # Define the derivative function for RK4
        def deriv(state):
            pos = state[:2]
            vel = state[2:]
            a = get_accel(vel, w)
            return np.array([vel[0], vel[1], a[0], a[1]])

        # RK4 Steps
        k1 = deriv(s)
        k2 = deriv(s + 0.5 * dt * k1)
        k3 = deriv(s + 0.5 * dt * k2)
        k4 = deriv(s + dt * k3)
        
        s = s + (dt / 6.0) * (k1 + 2*k2 + 2*k3 + k4)
        
        if s[1] < 0: break # Hit ground
            
        x_hist.append(s[0])
        y_hist.append(s[1])
        
    return np.array(x_hist), np.array(y_hist)

# --- SETUP THE PLOT ---
fig, ax = plt.subplots(figsize=(8, 6))
plt.subplots_adjust(bottom=0.25) # Make room for sliders

line, = ax.plot([], [], 'b-', label='Path')
point, = ax.plot([], [], 'ro')
ax.set_title("Projectile Motion - RK4 Method")
ax.grid(True, linestyle='--')

# Sliders - positioned somewhat manually
ax_speed = plt.axes([0.15, 0.1, 0.3, 0.03])
ax_angle = plt.axes([0.15, 0.05, 0.3, 0.03])
ax_wind  = plt.axes([0.6, 0.1, 0.25, 0.03])

s_speed = Slider(ax_speed, 'Speed', 10, 100, valinit=40)
s_angle = Slider(ax_angle, 'Angle', 0, 90, valinit=45)
s_wind  = Slider(ax_wind, 'Wind X', -20, 20, valinit=0)

def update(val):
    # Just re-run the whole thing when a slider moves
    x, y = run_simulation(s_speed.val, s_angle.val, s_wind.val, 0)
    line.set_data(x, y)
    
    # Auto-adjust the view so we can see the whole arc
    ax.set_xlim(0, max(x)*1.1)
    ax.set_ylim(0, max(y)*1.1)
    fig.canvas.draw_idle()

s_speed.on_changed(update)
s_angle.on_changed(update)
s_wind.on_changed(update)

# Initial run to show something on screen
update(None)

plt.show()