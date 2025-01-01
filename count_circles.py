import numpy as np
from itertools import combinations
import sys
import json

def is_inside_circle(circle, point):
    """Checks if a point is inside a circle."""
    center, radius = circle
    dist = np.linalg.norm(np.array(point) - np.array(center))
    return dist < radius

def circle_from_points(a, b, c, tolerance=1e-9):
    """Creates a circle from three points."""
    A, B, C = np.array(a), np.array(b), np.array(c)
    AB_mid, BC_mid = (A + B) / 2, (B + C) / 2
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

def count_circle_point_relationships(points):
    """Counts circles with exactly one point inside and one point outside."""
    count = 0

    for comb in combinations(points, 3):
        circle = circle_from_points(comb[0], comb[1], comb[2])
        if circle is None:
            continue

        # Remaining points
        remaining_points = [p for p in points if p not in comb]

        # Count how many points are inside and outside
        inside_points = [p for p in remaining_points if is_inside_circle(circle, p)]
        outside_points = [p for p in remaining_points if not is_inside_circle(circle, p)] 

        # Check if there is exactly one point inside and one point outside
        if len(inside_points) == 1 and len(outside_points) == 1:
            count += 1

    return count


results = {}
example_points = {}  # Store an example for each unique count
n = int(sys.argv[1])
for i in range(n):
    # Randomly generate 5 points within a 100x100 canvas
    points = np.random.uniform(0, 100, size=(5, 2)).tolist()

    count = count_circle_point_relationships(points)

    # Record the count in the results dictionary
    if count not in results:
        results[count] = 1
        example_points[count] = points  # Save this set of points as an example for the count
    else:
        results[count] += 1

# Save the results to a JSON file
filename = f'result_{n}.json'
with open(filename, 'w') as json_file:
    json.dump(results, json_file)

# Save the example points to a separate JSON file
example_filename = f'example_points_{n}.json'
with open(example_filename, 'w') as json_file:
    json.dump(example_points, json_file)
