import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from itertools import combinations

# Function to calculate a circle from three points
def circle_from_points(a, b, c, tolerance=1e-9):
    A = np.array(a)
    B = np.array(b)
    C = np.array(c)

    AB_mid = (A + B) / 2
    BC_mid = (B + C) / 2

    AB_slope = -(A[0] - B[0]) / (A[1] - B[1] + tolerance) if abs(A[1] - B[1]) > tolerance else None
    BC_slope = -(B[0] - C[0]) / (B[1] - C[1] + tolerance) if abs(B[1] - C[1]) > tolerance else None

    if AB_slope is not None and BC_slope is not None:
        A_intercept = AB_mid[1] - AB_slope * AB_mid[0]
        B_intercept = BC_mid[1] - BC_slope * BC_mid[0]

        if abs(AB_slope - BC_slope) < tolerance:
            return None  # We cannot form a circle

        x_center = (B_intercept - A_intercept) / (AB_slope - BC_slope)
        y_center = AB_slope * x_center + A_intercept
    else:
        return None

    center = (x_center, y_center)
    radius = np.linalg.norm(A - np.array(center))
    return center, radius

# Load example points JSON
with open('example_points_1000.json', 'r') as json_file:
    example_points = json.load(json_file)

canvas_limit = 100

for count, points in example_points.items():
    points = [tuple(point) for point in points]
    num_circles = 4

    fig, axs = plt.subplots(1, num_circles, figsize=(5 * num_circles, 5))
    fig.suptitle(f'Visualization for Count = {count}', fontsize=16)

    circle_counter = 0
    circle_points_label_added = False

    for comb in combinations(points, 3):
        if circle_counter >= num_circles:
            break

        circle = circle_from_points(comb[0], comb[1], comb[2])
        if circle is None:
            continue  # Skip if circle is not valid

        center, radius = circle
        
        circle_points = [comb[0], comb[1], comb[2]]

        # Plot points for the current circle
        x_coords, y_coords = zip(*circle_points)
        axs[circle_counter].scatter(
            x_coords, y_coords, color='purple', marker='s', 
            label='Circle Points' if not circle_points_label_added else ""
        )
        circle_points_label_added = True

        # Remaining points (only two), exclude circle points from inside/outside check
        remaining_points = [p for p in points if p not in circle_points]
        inside = [p for p in remaining_points if np.linalg.norm(np.array(p) - np.array(center)) < radius]
        outside = [p for p in remaining_points if np.linalg.norm(np.array(p) - np.array(center)) > radius]

        # Draw the circle only if exactly one point is inside and one outside
        if len(inside) == 1 and len(outside) == 1:
            circle_patch = Circle(center, radius, color='green', fill=False, linestyle='--', linewidth=1)
            axs[circle_counter].add_patch(circle_patch)

            # Inside point (red)
            inside_x, inside_y = zip(*inside)
            axs[circle_counter].scatter(
                inside_x, inside_y, color='red', marker='s', label='Inside Point' if circle_counter == 0 else ""
            )

            # Outside point (blue)
            outside_x, outside_y = zip(*outside)
            axs[circle_counter].scatter(
                outside_x, outside_y, color='blue', marker='s', label='Outside Point' if circle_counter == 0 else ""
            )

            axs[circle_counter].set_title(f'Circle {circle_counter + 1}')
            axs[circle_counter].set_xlim(0, canvas_limit)
            axs[circle_counter].set_ylim(0, canvas_limit)
            axs[circle_counter].set_aspect('equal', adjustable='box')
            axs[circle_counter].grid(True)

            circle_counter += 1


    handles, labels = axs[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='upper right')

    plt.show()
