import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from scipy.optimize import least_squares

# Function to calculate the residuals for circle fitting
def calc_residuals(params, x, y):
    xc, yc, r = params
    return np.sqrt((x - xc)**2 + (y - yc)**2) - r

# Fit a perfect circle through three points
def fit_circle(points):
    x, y = zip(*points)
    x0, y0 = np.mean(x), np.mean(y)  # Initial guess for center
    r0 = np.mean(np.sqrt((np.array(x) - x0)**2 + (np.array(y) - y0)**2))  # Initial guess for radius
    result = least_squares(calc_residuals, [x0, y0, r0], args=(np.array(x), np.array(y)))
    return result.x  # xc, yc, r

# Function to validate circle with the 1-1 constraint
def validate_circle(circle, points):
    xc, yc, r = circle
    distances = np.sqrt((points[:, 0] - xc)**2 + (points[:, 1] - yc)**2)
    inside = np.sum(distances < r)
    outside = np.sum(distances > r)
    return inside == 1 and outside == 1

# Generate 5 random points
np.random.seed(42)
points = np.random.rand(5, 2) * 100

# Find a valid circle
from itertools import combinations
circle_params = None
chosen_combination = None

for comb in combinations(points, 3):
    circle = fit_circle(comb)
    if validate_circle(circle, points):
        circle_params = circle
        chosen_combination = comb
        break

if circle_params is None:
    raise ValueError("No valid circle found.")

# Plot the points and circle, enable interactive adjustments
fig, ax = plt.subplots()
sc = ax.scatter(points[:, 0], points[:, 1], color='blue', s=100, picker=True)
circle_patch = Circle((circle_params[0], circle_params[1]), circle_params[2], 
                      color='orange', fill=False, lw=2)
ax.add_patch(circle_patch)

# Set equal aspect ratio for both axes
ax.set_aspect('equal', adjustable='datalim')
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)

selected_point = None

def update_circle():
    global circle_params
    circle_params = fit_circle(chosen_combination)
    circle_patch.center = (circle_params[0], circle_params[1])
    circle_patch.set_radius(circle_params[2])

def on_pick(event):
    global selected_point
    selected_point = event.ind[0]

def on_motion(event):
    global selected_point
    if selected_point is None:
        return
    if event.xdata is None or event.ydata is None:
        return
    points[selected_point] = [event.xdata, event.ydata]
    sc.set_offsets(points)

    update_circle()
    fig.canvas.draw_idle()

def on_release(event):
    global selected_point
    selected_point = None

fig.canvas.mpl_connect('pick_event', on_pick)
fig.canvas.mpl_connect('motion_notify_event', on_motion)
fig.canvas.mpl_connect('button_release_event', on_release)

plt.show()
