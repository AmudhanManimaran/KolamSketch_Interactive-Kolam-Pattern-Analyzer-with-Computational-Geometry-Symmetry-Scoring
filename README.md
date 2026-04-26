# KolamSketch — Interactive Kolam Pattern Analyzer with Symmetry Scoring

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=flat-square&logo=python)
![Flask](https://img.shields.io/badge/Flask-2.x-black?style=flat-square&logo=flask)
![OpenCV](https://img.shields.io/badge/OpenCV-4.x-green?style=flat-square&logo=opencv)
![JavaScript](https://img.shields.io/badge/JavaScript-ES6-yellow?style=flat-square&logo=javascript)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)

> A web-based interactive tool for drawing, classifying, and analyzing **Kolam** — the traditional South Indian dot-based floor art form. Combines **computational geometry**, **convex hull analysis**, **spatial reasoning**, and **OpenCV-based rotational symmetry scoring** to provide structural analysis of hand-drawn Kolam patterns.

---

## 🎯 Key Features

- **Interactive drawing canvas** — draw Kolam patterns on a configurable dot grid in the browser
- **4 Kolam type classifiers** — Pulli, Kambi, Neli, Sikku (geometry-driven rule engine)
- **Grid type classifier** — Square, Rectangle, Triangle, Hexagon, Circle (Convex Hull + angle/side analysis)
- **Spatial reasoning analysis** — path continuity, curvilinearity, and directionality detection
- **Rotational symmetry scorer** — OpenCV image rotation comparison, returns a 0–1 symmetry score
- **Turtle visualization** — replays the drawn pattern programmatically
- **JSON persistence** — saves each drawing session with full dot/path/analysis metadata
- **Flask web backend** — RESTful API serving the interactive front end

---

## 🏗️ System Architecture

```
Browser Canvas (Interactive Drawing)
            │
            ▼
  User places dots + draws path
            │
            ▼
┌───────────────────────────────────┐
│        Flask Backend              │
│                                   │
│  /save_and_classify               │
│  ├── classify_pattern()           │  ← Pulli/Kambi/Neli/Sikku
│  ├── classify_grid_type()         │  ← Convex Hull + geometry
│  └── spatial_reasoning_analysis() │  ← Continuity, curvature,
│                                   │    directionality
│  /api/rotational_score            │
│  └── rotational_symmetry_score()  │  ← OpenCV rotation diff (0–1)
└───────────────────────────────────┘
            │
            ▼
  JSON saved to saved_patterns/
  + Turtle visualization window
  + Analysis returned to browser
```

---

## 🧠 Technical Details

### Kolam Type Classification (Rule-Based)
| Kolam Type | Rule |
|-----------|------|
| Pulli Kolam | Single dot |
| Kambi Kolam | All dots in one row or one column |
| Neli Kolam | Exactly 4 dots |
| Sikku Kolam | Multiple dots in 2D arrangement |

### Grid Type Classification (Convex Hull + Geometry)
The `classify_grid_type()` function:
1. Computes the **Convex Hull** of all dot coordinates (Graham Scan implementation from scratch)
2. Counts hull vertices (n) to identify shape
3. For n=4: computes side lengths and interior angles to distinguish Square vs Rectangle vs Quadrilateral
4. For n≥5: checks radii variance from centroid to detect Circle Grid

| Hull Vertices | Classification |
|--------------|----------------|
| 3 | Triangle Grid |
| 4 (equal sides + angles) | Square Grid |
| 4 (equal angles) | Rectangle Grid |
| 4 (other) | Quadrilateral Grid |
| 6 | Hexagon Grid |
| ≥5 (uniform radii) | Circle Grid |

### Spatial Reasoning Analysis
Three properties computed per drawing:
- **Continuity** — checks if consecutive path points are within 10px distance
- **Curvilinearity** — detects direction changes via cross-product of consecutive vectors
- **Directionality** — determines start dot, movement direction (down/left), dot coverage, and loop closure

### Rotational Symmetry Scorer
```
For angles [30°, 60°, 90°, ..., 330°]:
  1. Rotate image by angle around center (OpenCV warpAffine)
  2. Compute pixel-level absolute difference (absdiff)
  3. Match score = 1 - (sum(diff) / (255 × total_pixels))
Final score = mean of all match scores (0 = no symmetry, 1 = perfect symmetry)
```

---

## 📁 Project Structure

```
KolamSketch/
│
├── kolam_app/
│   ├── app.py                      # Flask backend + geometry + routing
│   ├── kolam_drawer.py             # Turtle visualization module
│   │
│   ├── utils/
│   │   └── symmetry_utils.py       # OpenCV rotational symmetry scorer
│   │
│   ├── static/
│   │   ├── index.html              # Main interactive drawing canvas
│   │   ├── symmetry_area.html      # Symmetry analysis interface
│   │   ├── json_to_analysis.html   # Saved pattern analysis viewer
│   │   ├── css/style.css           # Styling
│   │   └── js/script.js            # Canvas drawing logic
│   │
│   └── saved_patterns/             # JSON session files (auto-generated)
│
├── .gitignore
├── LICENSE
└── README.md
```

---

## ⚙️ Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/AmudhanManimaran/KolamSketch.git
cd KolamSketch/kolam_app
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate      # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Application
```bash
python app.py
```
Visit `http://localhost:5000` in your browser.

---

## 🚀 Usage

### Drawing Interface (`/`)
1. Configure grid size (e.g., 5×5)
2. Place dots on the canvas
3. Draw your Kolam pattern by connecting dots
4. Click **Analyze** to get:
   - Kolam type (Pulli / Kambi / Neli / Sikku)
   - Grid type (Square / Triangle / Hexagon etc.)
   - Spatial reasoning report
   - Turtle visualization replay

### Symmetry Analyzer (`/symmetry_area`)
1. Draw or upload a Kolam pattern
2. Get a **rotational symmetry score** (0–1)
   - 1.0 = perfect rotational symmetry
   - 0.0 = no rotational symmetry

### Pattern Viewer (`/json_to_analysis`)
- Load and review previously saved JSON pattern sessions

---

## 📦 Requirements

```
flask>=2.0.0
opencv-python>=4.5.0
numpy>=1.21.0
```

---

## 🎨 About Kolam

**Kolam** is a traditional South Indian art form drawn using rice flour on the ground, typically at the entrance of homes. Different Kolam types have distinct structural properties:
- **Pulli Kolam** — single dot patterns
- **Kambi Kolam** — line-based patterns
- **Neli Kolam** — interlaced loop patterns
- **Sikku Kolam** — complex interlocking patterns

This project applies computational geometry to formalize and analyze the structural properties of these patterns digitally.

---

## 📄 License

This project is licensed under the **MIT License** — see [LICENSE](LICENSE) for details.

---

## 👤 Author

**Amudhan Manimaran**
- 🌐 Portfolio: [amudhanmanimaran.github.io/Portfolio](https://amudhanmanimaran.github.io/Portfolio/)
- 💼 LinkedIn: [linkedin.com/in/amudhan-manimaran-3621bb32a](https://www.linkedin.com/in/amudhan-manimaran-3621bb32a)
- 🐙 GitHub: [github.com/AmudhanManimaran](https://github.com/AmudhanManimaran)
