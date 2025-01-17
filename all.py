import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from itertools import combinations

# Function to calculate a circle from three points
def circle_from_points(a, b, c, tolerance=1e-9):
    A, B, C = np.array(a), np.array(b), np.array(c)
    AB_mid = (A + B) / 2
    BC_mid = (B + C) / 2

    AB_slope = -(A[0] - B[0]) / (A[1] - B[1] + tolerance) if abs(A[1] - B[1]) > tolerance else None
    BC_slope = -(B[0] - C[0]) / (B[1] - C[1] + tolerance) if abs(B[1] - C[1]) > tolerance else None

    if AB_slope is not None and BC_slope is not None:
        A_intercept = AB_mid[1] - AB_slope * AB_mid[0]
        B_intercept = BC_mid[1] - BC_slope * BC_mid[0]

        if abs(AB_slope - BC_slope) < tolerance:
            return None

        x_center = (B_intercept - A_intercept) / (AB_slope - BC_slope)
        y_center = AB_slope * x_center + A_intercept
    else:
        return None

    center = (x_center, y_center)
    radius = np.linalg.norm(A - np.array(center))
    return center, radius

# Function to classify circles
def analyze_circles(points):
    results = []
    for comb in combinations(points, 3):
        circle = circle_from_points(comb[0], comb[1], comb[2])
        if circle is None:
            continue

        center, radius = circle
        remaining_points = [p for p in points if not any(np.array_equal(p, c) for c in comb)]

        # Check for exactly one inside and one outside point
        inside = [p for p in remaining_points if np.linalg.norm(np.array(p) - np.array(center)) < radius]
        outside = [p for p in remaining_points if np.linalg.norm(np.array(p) - np.array(center)) > radius]

        valid = len(inside) == 1 and len(outside) == 1
        results.append((center, radius, comb, valid))

    return results

# Initialize points
#np.random.seed(42)
points = np.random.uniform(0, 100, (5, 2))  # 5 blue points
red_points = np.random.uniform(0, 100, (5, 2))  # 5 red points

# Overlap the first two blue points with the first two red points
red_points[:2] = points[:2]

# Set up the main canvas
fig, ax_main = plt.subplots(figsize=(8, 8))
fig.subplots_adjust(bottom=0.3)

ax_main.set_xlim(0, 100)
ax_main.set_ylim(0, 100)
ax_main.set_aspect('equal')

# Plot points
sc = ax_main.scatter(points[:, 0], points[:, 1], color='blue', s=200)
for i, red_point in enumerate(red_points):
    if i < 2:  # Avoid plotting duplicate red circles for overlapping points
        continue
    ax_main.add_patch(Circle(red_point, radius=2, edgecolor='red', facecolor='none', linewidth=2))

# Highlight A1 and A2 with red outlines
highlighted_indices = [0, 1]
highlight_patches = []
for i in highlighted_indices:
    patch = Circle(points[i], radius=3, edgecolor='red', facecolor='none', linewidth=2)
    ax_main.add_patch(patch)
    highlight_patches.append(patch)

# Interactive Point Movement
selected_index = None

def update_main_plot():
    global circle_results
    # Recalculate valid and invalid circles based on the updated points
    circle_results = analyze_circles(points)
    update_subplots()

def on_press(event):
    global selected_index
    if event.inaxes != ax_main:
        return
    mouse_point = np.array([event.xdata, event.ydata])
    distances = np.linalg.norm(points - mouse_point, axis=1)
    if np.min(distances) < 5:  # Select the point if within a small distance
        idx = np.argmin(distances)
        if idx >= 2:  # Only allow movement for non-overlapping points
            selected_index = idx

def on_motion(event):
    global selected_index
    if selected_index is None or event.inaxes != ax_main:
        return
    points[selected_index] = [event.xdata, event.ydata]
    sc.set_offsets(points)
    for patch, i in zip(highlight_patches, highlighted_indices):
        patch.set_center(points[i])  # Update highlighted points
    update_main_plot()  # Dynamically re-analyze and update subplots
    fig.canvas.draw_idle()  # Redraw the main canvas

def on_release(event):
    global selected_index
    selected_index = None

fig.canvas.mpl_connect('button_press_event', on_press)
fig.canvas.mpl_connect('motion_notify_event', on_motion)
fig.canvas.mpl_connect('button_release_event', on_release)

# Subplots for valid and invalid circles
fig_subplots, axs = plt.subplots(2, 5, figsize=(20, 8))
axs = axs.flatten()

# Analyze circles
circle_results = analyze_circles(points)

def update_subplots():
    for ax, (center, radius, comb, valid) in zip(axs, circle_results):
        ax.clear()
        ax.set_xlim(0, 100)
        ax.set_ylim(0, 100)
        ax.set_aspect('equal')

        ax.scatter(points[:, 0], points[:, 1], color='black', s=100)

        # Highlight the 3 points forming the circle
        point_color = 'green' if valid else 'red'
        ax.scatter([p[0] for p in comb], [p[1] for p in comb], color=point_color, s=150)

        # Draw the circle formed by the 3 points
        if center is not None and len(comb) == 3:
            circle_patch = Circle(center, radius, color='green' if valid else 'red', fill=False, linestyle='--', linewidth=1)
            ax.add_patch(circle_patch)

        # Add a title indicating validity
        ax.set_title('Valid' if valid else 'Invalid', fontsize=10)

    fig_subplots.canvas.draw_idle()

update_main_plot()
plt.show()
