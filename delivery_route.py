
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import heapq
import math

# Creating the main window
root = tk.Tk()
root.title("Smart Delivery Route Optimization System")
root.geometry("1100x720")
root.configure(bg="#eef2f7")

# Graph containing locations and road distances
graph = {
    "Warehouse": {
        "City Center": 5,
        "West Zone": 4
    },
    "City Center": {
        "Warehouse": 5,
        "North Zone": 3,
        "South Zone": 6
    },
    "North Zone": {
        "City Center": 3,
        "East Zone": 4
    },
    "South Zone": {
        "City Center": 6,
        "East Zone": 2,
        "West Zone": 5
    },
    "East Zone": {
        "North Zone": 4,
        "South Zone": 2
    },
    "West Zone": {
        "Warehouse": 4,
        "South Zone": 5
    }
}

# Positions of locations on the map
positions = {
    "Warehouse": (100, 220),
    "City Center": (300, 100),
    "North Zone": (500, 100),
    "South Zone": (500, 350),
    "East Zone": (650, 220),
    "West Zone": (100, 400)
}

# Variables for displaying routes
current_route = []
route_edges = set()


# Dijkstra's shortest path algorithm
def dijkstra(start, destination):

    distances = {node: float("inf") for node in graph}
    previous = {}

    distances[start] = 0

    priority_queue = [(0, start)]

    while priority_queue:

        current_distance, current_node = heapq.heappop(priority_queue)

        if current_distance > distances[current_node]:
            continue

        if current_node == destination:
            break

        for neighbour, weight in graph[current_node].items():

            new_distance = current_distance + weight

            if new_distance < distances[neighbour]:

                distances[neighbour] = new_distance
                previous[neighbour] = current_node

                heapq.heappush(
                    priority_queue,
                    (new_distance, neighbour)
                )

    if distances[destination] == float("inf"):
        return float("inf"), []

    # Reconstructing the shortest path
    path = []
    node = destination

    while node != start:
        path.append(node)
        node = previous[node]

    path.append(start)
    path.reverse()

    return distances[destination], path


# Drawing the graph on the canvas
def draw_map():

    canvas.delete("all")

    # Drawing roads
    for node in graph:

        for neighbour, distance in graph[node].items():

            if node < neighbour:

                x1, y1 = positions[node]
                x2, y2 = positions[neighbour]

                edge = frozenset((node, neighbour))

                if edge in route_edges:
                    color = "#e63946"
                    width = 4
                else:
                    color = "#9ca3af"
                    width = 2

                canvas.create_line(
                    x1, y1, x2, y2,
                    fill=color,
                    width=width
                )

                canvas.create_text(
                    (x1 + x2) / 2,
                    (y1 + y2) / 2 - 12,
                    text=str(distance) + " km",
                    fill="#334155",
                    font=("Arial", 9, "bold")
                )

    # Drawing locations
    for node, (x, y) in positions.items():

        if node in current_route:
            color = "#e63946"
        else:
            color = "#2563eb"

        canvas.create_oval(
            x - 15, y - 15,
            x + 15, y + 15,
            fill=color,
            outline="white",
            width=2
        )

        canvas.create_text(
            x,
            y + 28,
            text=node,
            fill="#1e293b",
            font=("Arial", 9, "bold")
        )


# Updating location dropdowns
def update_locations():

    locations = list(graph.keys())

    source_box["values"] = locations
    destination_box["values"] = locations
    source_box.set(locations[0])

    if len(locations) > 1:
        destination_box.set(locations[1])


# Displaying the shortest route
def find_shortest_route():

    start = source_box.get()
    destination = destination_box.get()

    if not start or not destination:
        messagebox.showwarning("Warning", "Select both locations.")
        return

    if start == destination:
        messagebox.showwarning(
            "Warning", "Select two different locations."
        )
        return

    distance, path = dijkstra(start, destination)

    if not path:
        messagebox.showerror(
            "Error", "No connected route found."
        )
        return

    global current_route, route_edges

    current_route = path
    route_edges = set()

    for i in range(len(path) - 1):
        route_edges.add(frozenset((path[i], path[i + 1])))

    draw_map()

    result_box.delete("1.0", tk.END)

    result_box.insert(tk.END, "SHORTEST DELIVERY ROUTE\n")
    result_box.insert(tk.END, "----------------------------\n\n")

    result_box.insert(
        tk.END, "Starting Point: " + start + "\n"
    )

    result_box.insert(
        tk.END, "Destination: " + destination + "\n\n"
    )

    result_box.insert(
        tk.END, "Route:\n" + " -> ".join(path) + "\n\n"
    )

    result_box.insert(
        tk.END, "Total Distance: " + str(distance) + " km"
    )


# Greedy approach for multiple delivery locations
def optimize_delivery_route():

    start = source_box.get()

    if not start:
        messagebox.showwarning(
            "Warning", "Select a starting location."
        )
        return

    unvisited = set(graph.keys())
    unvisited.remove(start)

    current = start
    route = [start]
    total_distance = 0

    while unvisited:

        nearest = None
        shortest_distance = float("inf")
        best_path = []

        # Finding the nearest unvisited location
        for location in unvisited:

            distance, path = dijkstra(current, location)

            if distance < shortest_distance:
                shortest_distance = distance
                nearest = location
                best_path = path

        if nearest is None or shortest_distance == float("inf"):

            messagebox.showerror(
                "Error",
                "Some locations are not connected."
            )
            return

        total_distance += shortest_distance

        # Adding the path to the complete route
        route.extend(best_path[1:])

        current = nearest
        unvisited.remove(nearest)

    global current_route, route_edges

    current_route = route
    route_edges = set()

    for i in range(len(route) - 1):
        route_edges.add(frozenset((route[i], route[i + 1])))

    draw_map()

    result_box.delete("1.0", tk.END)

    result_box.insert(tk.END, "OPTIMIZED DELIVERY ROUTE\n")
    result_box.insert(tk.END, "----------------------------\n\n")

    result_box.insert(
        tk.END, "Starting Point: " + start + "\n\n"
    )

    result_box.insert(
        tk.END, "Delivery Route:\n"
        + " -> ".join(route) + "\n\n"
    )

    result_box.insert(
        tk.END,
        "Total Distance: " + str(total_distance) + " km\n\n"
    )

    result_box.insert(
        tk.END,
        "Total Locations Visited: " + str(len(graph))
    )


# Adding a new delivery location
def add_location():

    name = simpledialog.askstring(
        "Add Location", "Enter location name:"
    )

    if not name:
        return

    name = name.strip()

    if name in graph:
        messagebox.showwarning(
            "Warning", "Location already exists."
        )
        return

    if len(graph) >= 30:
        messagebox.showwarning(
            "Limit", "Maximum 30 locations allowed."
        )
        return

    graph[name] = {}

    # Placing the new location on the map
    angle = len(graph) * 2.4

    x = 350 + 250 * math.cos(angle)
    y = 230 + 170 * math.sin(angle)

    positions[name] = (x, y)

    update_locations()
    draw_map()

    messagebox.showinfo(
        "Success", "New location added successfully."
    )


# Adding a road between two locations
def add_road():

    locations = list(graph.keys())

    start = simpledialog.askstring(
        "Add Road",
        "Enter first location:\n" + ", ".join(locations)
    )

    if not start:
        return

    end = simpledialog.askstring(
        "Add Road",
        "Enter second location:\n" + ", ".join(locations)
    )

    if not end:
        return

    start = start.strip()
    end = end.strip()

    if start not in graph or end not in graph:
        messagebox.showerror(
            "Error", "Location does not exist."
        )
        return

    if start == end:
        messagebox.showerror(
            "Error", "Select two different locations."
        )
        return

    distance = simpledialog.askfloat(
        "Road Distance",
        "Enter distance between locations (km):"
    )

    if distance is None:
        return

    if distance <= 0:
        messagebox.showerror(
            "Error", "Distance must be greater than zero."
        )
        return

    graph[start][end] = distance
    graph[end][start] = distance

    draw_map()

    messagebox.showinfo(
        "Success", "Road added successfully."
    )


# Clearing the selected route
def clear_route():

    global current_route, route_edges

    current_route = []
    route_edges = set()

    draw_map()

    result_box.delete("1.0", tk.END)
    result_box.insert(tk.END, "Select an operation to begin.")


# Main heading
heading = tk.Label(
    root,
    text="SMART DELIVERY ROUTE OPTIMIZATION SYSTEM",
    font=("Arial", 20, "bold"),
    bg="#eef2f7",
    fg="#1e3a8a"
)
heading.pack(pady=15)


# Main application frame
main_frame = tk.Frame(root, bg="#eef2f7")
main_frame.pack(fill="both", expand=True, padx=15, pady=10)


# Left control panel
control_frame = tk.Frame(
    main_frame,
    bg="white",
    width=300,
    padx=15,
    pady=15
)
control_frame.pack(side="left", fill="y", padx=(0, 15))
control_frame.pack_propagate(False)


tk.Label(
    control_frame,
    text="Route Controls",
    font=("Arial", 16, "bold"),
    bg="white",
    fg="#1e293b"
).pack(pady=10)


tk.Label(
    control_frame,
    text="Starting Location",
    bg="white",
    font=("Arial", 10, "bold")
).pack(anchor="w", pady=(10, 5))

source_box = ttk.Combobox(
    control_frame,
    state="readonly",
    width=28
)
source_box.pack(pady=5)


tk.Label(
    control_frame,
    text="Destination",
    bg="white",
    font=("Arial", 10, "bold")
).pack(anchor="w", pady=(10, 5))

destination_box = ttk.Combobox(
    control_frame,
    state="readonly",
    width=28
)
destination_box.pack(pady=5)


# Buttons
button_style = {
    "font": ("Arial", 10, "bold"),
    "fg": "white",
    "width": 27,
    "relief": "flat",
    "pady": 8,
    "cursor": "hand2"
}

tk.Button(
    control_frame,
    text="Find Shortest Route",
    bg="#2563eb",
    command=find_shortest_route,
    **button_style
).pack(pady=10)

tk.Button(
    control_frame,
    text="Optimize Delivery Route",
    bg="#16a34a",
    command=optimize_delivery_route,
    **button_style
).pack(pady=5)

tk.Button(
    control_frame,
    text="Add New Location",
    bg="#7c3aed",
    command=add_location,
    **button_style
).pack(pady=5)

tk.Button(
    control_frame,
    text="Add Road / Distance",
    bg="#ea580c",
    command=add_road,
    **button_style
).pack(pady=5)

tk.Button(
    control_frame,
    text="Clear Route",
    bg="#64748b",
    command=clear_route,
    **button_style
).pack(pady=5)


# Result display
tk.Label(
    control_frame,
    text="Route Information",
    font=("Arial", 13, "bold"),
    bg="white"
).pack(pady=(20, 5))

result_box = tk.Text(
    control_frame,
    height=10,
    width=32,
    font=("Arial", 9),
    wrap="word",
    bg="#f1f5f9",
    relief="flat"
)
result_box.pack(fill="x", pady=5)

result_box.insert(
    tk.END, "Select an operation to begin."
)


# Right side map
map_frame = tk.Frame(main_frame, bg="white", padx=10, pady=10)
map_frame.pack(side="right", fill="both", expand=True)

tk.Label(
    map_frame,
    text="Delivery Network Map",
    font=("Arial", 16, "bold"),
    bg="white",
    fg="#1e293b"
).pack(pady=10)

canvas = tk.Canvas(
    map_frame,
    width=700,
    height=480,
    bg="#f8fafc",
    highlightthickness=0
)
canvas.pack(fill="both", expand=True)


# Initializing the application
update_locations()
draw_map()

root.mainloop()
