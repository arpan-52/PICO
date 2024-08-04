import matplotlib.pyplot as plt
import numpy as np

def read_uvw_file(filename):
    u_coords = []
    v_coords = []

    with open(filename, 'r') as file:
        for line in file:
            # Split the line into u, v, and w components
            parts = line.strip().split()
            if len(parts) == 3:
                try:
                    u = float(parts[0])
                    v = float(parts[1])
                    # w = float(parts[2])  # We don't need w for this plot
                    u_coords.append(u)
                    v_coords.append(v)
                except ValueError:
                    print(f"Skipping line due to conversion issue: {line.strip()}")
            else:
                print(f"Skipping line due to format issue: {line.strip()}")

    return u_coords, v_coords

def plot_uv(u_coords, v_coords):
    plt.figure(figsize=(10, 6))
    plt.plot(u_coords, v_coords, 'o', markersize=0.5, label='u vs v')
    plt.plot(-np.array(u_coords), -np.array(v_coords), 'o', markersize=0.5, label='-u vs -v')

    plt.xlabel('u')
    plt.ylabel('v')
    plt.title('u vs v Plot')
    plt.legend()
    plt.grid(True)
    plt.show()

# Main
filename = 'uvw_coordinates.txt'
u_coords, v_coords = read_uvw_file(filename)
plot_uv(u_coords, v_coords)
