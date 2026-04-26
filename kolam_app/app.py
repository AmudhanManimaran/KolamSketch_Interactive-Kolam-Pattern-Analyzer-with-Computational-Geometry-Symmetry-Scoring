from flask import Flask, request, jsonify, render_template
from multiprocessing import Process
import turtle, sys, json, os, math, base64
from datetime import datetime
import cv2, numpy as np

# ---- local utility for symmetry scoring ----
from utils.symmetry_utils import rotational_symmetry_score

app = Flask(__name__, static_folder="static", template_folder="templates")

SAVE_DIR = "saved_patterns"
os.makedirs(SAVE_DIR, exist_ok=True)

# -------------------------------------------------
# Geometry helpers
# -------------------------------------------------
def distance(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])

def angle(p1, p2, p3):
    """Return angle at p2 formed by points p1-p2-p3 in degrees."""
    v1 = (p1[0] - p2[0], p1[1] - p2[1])
    v2 = (p3[0] - p2[0], p3[1] - p2[1])
    dot = v1[0]*v2[0] + v1[1]*v2[1]
    norm1 = math.hypot(*v1)
    norm2 = math.hypot(*v2)
    if norm1 * norm2 == 0:
        return 0
    return math.degrees(math.acos(max(-1, min(1, dot/(norm1*norm2)))))

def convex_hull(points):
    pts = sorted(set(points))
    if len(pts) <= 1:
        return pts
    def cross(o,a,b): return (a[0]-o[0])*(b[1]-o[1]) - (a[1]-o[1])*(b[0]-o[0])
    lower, upper = [], []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return lower[:-1] + upper[:-1]

# -------------------------------------------------
# Kolam & Grid classification
# -------------------------------------------------
def classify_pattern(dots):
    if len(dots) < 1:
        return "Unknown"
    if len(dots) == 1:
        return "Pulli Kolam"
    elif len(dots) > 1:
        rows = [d['row'] for d in dots]
        cols = [d['col'] for d in dots]
        if len(set(rows)) == 1 or len(set(cols)) == 1:
            return "Kambi Kolam"
        elif len(dots) == 4:
            return "Neli Kolam"
        else:
            return "Sikku Kolam"
    return "Unknown"

def classify_grid_type(dots):
    if len(dots) < 3:
        return "Unknown"

    pts = [(d.get("x", d["col"]), d.get("y", d["row"])) for d in dots]
    hull = convex_hull(pts)
    n = len(hull)

    if n >= 5:
        cx = sum(p[0] for p in hull) / n
        cy = sum(p[1] for p in hull) / n
        radii = [distance((cx, cy), p) for p in hull]
        if max(radii) - min(radii) < 10:
            return "Circle Grid"

    if n == 3: return "Triangle Grid"
    if n == 6: return "Hexagon Grid"

    if n == 4:
        sides = [distance(hull[i], hull[(i + 1) % 4]) for i in range(4)]
        angles = [angle(hull[i - 1], hull[i], hull[(i + 1) % 4]) for i in range(4)]
        side_diff = max(sides) - min(sides)
        angle_diff = max(angles) - min(angles)
        if side_diff < 5 and angle_diff < 5: return "Square Grid"
        if angle_diff < 5: return "Rectangle Grid"
        return "Quadrilateral Grid"

    return "Unknown"

# -------------------------------------------------
# Spatial reasoning helpers
# -------------------------------------------------
def is_continuous(path):
    for i in range(1, len(path)):
        if distance(path[i-1], path[i]) > 10:
            return False
    return True

def is_curvilinear(path):
    if len(path) < 3:
        return False
    for i in range(1, len(path) - 1):
        x1, y1 = path[i-1]
        x2, y2 = path[i]
        x3, y3 = path[i+1]
        v1x, v1y = x2 - x1, y2 - y1
        v2x, v2y = x3 - x2, y3 - y2
        if v1x * v2y != v1y * v2x:
            return True
    return False

def analyze_directionality(path, dots):
    if not path or not dots:
        return "No path or dots provided."

    start_x, start_y = path[0]
    start_dot = min(dots, key=lambda d: math.hypot(d['x'] - start_x, d['y'] - start_y))
    top_dot = min(dots, key=lambda d: d['y'])
    is_top_dot = start_dot == top_dot

    initial_points = path[:10]
    moves_down = any(initial_points[i][1] > initial_points[i-1][1] for i in range(1, len(initial_points)))
    moves_left = any(initial_points[i][0] < initial_points[i-1][0] for i in range(1, len(initial_points)))

    connected_dots = []
    for dot in dots:
        if any(math.hypot(dot['x'] - px, dot['y'] - py) < 10 for px, py in path):
            connected_dots.append(dot)
    all_dots_connected = len(set(tuple(d.items()) for d in connected_dots)) == len(dots)

    distance_to_start = math.hypot(path[-1][0] - start_x, path[-1][1] - start_y)
    ends_near_start = distance_to_start < 10

    desc = "The path starts from the top dot, " if is_top_dot else "The path does not start from the top dot, "
    desc += "moves down and to the left, " if moves_down and moves_left else "does not move down and to the left, "
    desc += "then connects all dots " if all_dots_connected else "but does not connect all dots "
    desc += "and ends near the starting point." if ends_near_start else "and does not end near the starting point."
    return desc

def spatial_reasoning_analysis(paths, dots):
    if not paths:
        return {
            "continuous_nature": "No paths provided.",
            "path_type": "No paths provided.",
            "directionality": "No paths provided."
        }

    path = paths[0]
    return {
        "continuous_nature": "The drawing is a single, unbroken line." if is_continuous(path)
                             else "The drawing is not a single, unbroken line.",
        "path_type": "The line is curvilinear." if is_curvilinear(path)
                     else "The line is not curvilinear.",
        "directionality": analyze_directionality(path, dots)
    }

# -------------------------------------------------
# Turtle visualisation
# -------------------------------------------------
def run_kolam_drawer(paths, active_dots):
    try:
        scr = turtle.Screen()
        scr.setup(width=600, height=600)
        scr.title("Kolam Replication")
        t = turtle.Turtle()
        t.speed(0)
        t.pensize(3)
        t.hideturtle()

        t.penup()
        for d in active_dots:
            t.goto(d.get('x',0)-300, 300-d.get('y',0))
            t.dot(6, "black")

        for path in paths:
            if not path: continue
            t.penup()
            t.goto(path[0][0]-300, 300-path[0][1])
            t.pendown()
            for x, y in path[1:]:
                t.goto(x-300, 300-y)
        scr.mainloop()
    except turtle.Terminator:
        sys.exit()

# -------------------------------------------------
# Flask routes
# -------------------------------------------------
@app.route("/")
def index():
    return app.send_static_file("index.html")

@app.route("/json_to_analysis")
def json_to_analysis():
    return app.send_static_file("json_to_analysis.html")

@app.route("/save_and_classify", methods=["POST"])
def save_and_classify():
    data = request.get_json()
    dots  = data.get("dots", [])
    paths = data.get("paths", [])
    grid_size = data.get("grid_size", [])

    kolam_type  = classify_pattern(dots)
    grid_type   = classify_grid_type(dots)
    spatial_res = spatial_reasoning_analysis(paths, dots)

    filename = datetime.now().strftime("%Y%m%d_%H%M%S") + ".json"
    filepath = os.path.join(SAVE_DIR, filename)
    with open(filepath, "w") as f:
        json.dump({
            "grid_size": grid_size,
            "dots": dots,
            "paths": paths,
            "detected_type": kolam_type,
            "grid_type": grid_type,
            "spatial_reasoning": spatial_res
        }, f, indent=2)

    Process(target=run_kolam_drawer, args=(paths, dots)).start()

    return jsonify({
        "status": "success",
        "kolam_type": kolam_type,
        "grid_type": grid_type,
        "spatial_reasoning": spatial_res,
        "saved_file": filename
    })

@app.route("/reset", methods=["POST"])
def reset_drawings():
    for f in os.listdir(SAVE_DIR):
        fp = os.path.join(SAVE_DIR, f)
        if os.path.isfile(fp):
            os.remove(fp)
    return jsonify({"status": "success", "message": "All saved patterns removed."})

# ---------- Rotational symmetry checker ----------
@app.route("/symmetry_area")
def symmetry_area():
    return app.send_static_file("symmetry_area.html")

@app.route("/api/rotational_score", methods=["POST"])
def api_rotational_score():
    """
    Accepts a base64 PNG from the front end and returns a
    rotational symmetry score (0–1).
    """
    data = request.get_json()
    img_b64 = data.get("image", "").split(",")[-1]
    nparr = np.frombuffer(base64.b64decode(img_b64), np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    tmp_path = os.path.join(SAVE_DIR, "tmp_symmetry.png")
    cv2.imwrite(tmp_path, img)

    score = rotational_symmetry_score(tmp_path)
    return jsonify({"score": float(score)})

# -------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
