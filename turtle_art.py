"""
turtle_art.py — Turtle graphics for ShopImpact.

Why not `import turtle` directly?
Python's built-in turtle module opens a desktop window using Tkinter.
Streamlit Cloud runs on a server with no screen, so `turtle.Screen()` crashes
there. To keep real turtle-style drawing in the deployed app, this file has a
small SVGTurtle class with the SAME commands as Python's turtle
(forward, left, right, circle, penup, pendown, begin_fill, end_fill, dot ...).
Instead of drawing in a window, it records the moves as an SVG image that
Streamlit can show in the browser.

Bonus: every line is animated so it "draws itself" like a real turtle.
(turtle_local.py draws the same pictures with the real turtle module on a laptop.)
"""

import math
import base64

# Earthy palette shared with the app
MOSS = "#2F5D3A"
SAGE = "#8DB38B"
RIVER = "#3E7C98"
BARK = "#6B4F3A"
OAT = "#E9ECDD"
SUN = "#E2B33C"
CLAY = "#B5543C"


class SVGTurtle:
    """A tiny turtle that draws into SVG instead of a Tkinter window."""

    def __init__(self, width=260, height=260):
        self.width = width
        self.height = height
        self.x, self.y = 0.0, 0.0        # (0, 0) is the centre, like turtle
        self.heading = 0.0               # 0 = east, angles go anticlockwise
        self.pen_is_down = True
        self.pen_color = "#000000"
        self.fill_color = "#000000"
        self.size = 2
        self.elements = []               # finished SVG shapes, in draw order
        self._path = []                  # points of the line being drawn now
        self._fill_points = None         # points while begin_fill() is active

    # --- coordinate helper: turtle y goes up, SVG y goes down -------------
    def _svg(self, x, y):
        return (round(self.width / 2 + x, 2), round(self.height / 2 - y, 2))

    # --- pen control --------------------------------------------------------
    def penup(self):
        self._flush()
        self.pen_is_down = False

    def pendown(self):
        self.pen_is_down = True
        self._path = [(self.x, self.y)]

    def pensize(self, width):
        self._flush()
        self.size = width
        self._restart()

    def color(self, pen, fill=None):
        self._flush()
        self.pen_color = pen
        self.fill_color = fill if fill else pen
        self._restart()

    # --- movement -------------------------------------------------------------
    def forward(self, distance):
        rad = math.radians(self.heading)
        self.x += distance * math.cos(rad)
        self.y += distance * math.sin(rad)
        self._record()

    def backward(self, distance):
        self.forward(-distance)

    def left(self, angle):
        self.heading = (self.heading + angle) % 360

    def right(self, angle):
        self.left(-angle)

    def setheading(self, angle):
        self.heading = angle % 360

    def goto(self, x, y):
        self.x, self.y = x, y
        self._record()

    def circle(self, radius, extent=360, steps=None):
        """Same maths as Python's turtle.circle: arc with centre on the left."""
        steps = steps or max(12, int(abs(extent) / 6))
        w = extent / steps
        half = w / 2
        length = 2 * radius * math.sin(math.radians(half))
        if radius < 0:
            length, w, half = -length, -w, -half
        self.left(half)
        for _ in range(steps):
            self.forward(length)
            self.left(w)
        self.right(half)

    # --- fills, dots, text ----------------------------------------------------
    def begin_fill(self):
        self._fill_points = [(self.x, self.y)]

    def end_fill(self):
        if self._fill_points and len(self._fill_points) > 2:
            pts = " ".join(f"{a},{b}" for a, b in (self._svg(*p) for p in self._fill_points))
            self.elements.append(
                ("fill", f'<polygon points="{pts}" fill="{self.fill_color}" '
                         f'stroke="{self.pen_color}" stroke-width="{self.size}" '
                         f'stroke-linejoin="round"/>')
            )
        self._fill_points = None

    def dot(self, diameter, color=None):
        cx, cy = self._svg(self.x, self.y)
        self.elements.append(
            ("fill", f'<circle cx="{cx}" cy="{cy}" r="{diameter / 2}" fill="{color or self.pen_color}"/>')
        )

    def write(self, text, size=16, color=None, weight=700):
        self._flush()
        cx, cy = self._svg(self.x, self.y)
        safe = str(text).replace("&", "&amp;").replace("<", "&lt;")
        self.elements.append(
            ("fill", f'<text x="{cx}" y="{cy}" text-anchor="middle" font-size="{size}" '
                     f'font-weight="{weight}" fill="{color or self.pen_color}" '
                     f'font-family="Bricolage Grotesque, Atkinson Hyperlegible, sans-serif">{safe}</text>')
        )
        self._restart()

    # --- internal bookkeeping -------------------------------------------------
    def _record(self):
        if self._fill_points is not None:
            self._fill_points.append((self.x, self.y))
        if self.pen_is_down:
            if not self._path:
                self._path = [(self.x, self.y)]
            else:
                self._path.append((self.x, self.y))
        else:
            self._path = []

    def _restart(self):
        self._path = [(self.x, self.y)] if self.pen_is_down else []

    def _flush(self):
        """Turn the line drawn so far into an SVG path."""
        if len(self._path) > 1:
            pts = [self._svg(*p) for p in self._path]
            length = sum(math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1))
            d = "M " + " L ".join(f"{a} {b}" for a, b in pts)
            self.elements.append(
                ("stroke", f'<path d="{d}" fill="none" stroke="{self.pen_color}" '
                           f'stroke-width="{self.size}" stroke-linecap="round" stroke-linejoin="round" '
                           f'style="--len:{length:.1f}"/>')
            )
        self._path = []

    # --- output ---------------------------------------------------------------
    def to_svg(self, animate=True):
        self._flush()
        parts = []
        for i, (kind, svg) in enumerate(self.elements):
            if animate:
                delay = f"animation-delay:{i * 0.09:.2f}s"
                if 'style="' in svg:
                    svg = svg.replace('style="', f'class="{kind}" style="{delay};', 1)
                else:
                    cut = svg.index(" ")
                    svg = svg[:cut] + f' class="{kind}" style="{delay}"' + svg[cut:]
            parts.append(svg)
        style = """
        <style>
          .stroke { stroke-dasharray: var(--len); stroke-dashoffset: var(--len);
                    animation: draw .7s ease-out forwards; }
          .fill   { opacity: 0; animation: appear .45s ease-out forwards; }
          @keyframes draw   { to { stroke-dashoffset: 0; } }
          @keyframes appear { to { opacity: 1; } }
          @media (prefers-reduced-motion: reduce) {
            .stroke, .fill { animation: none; opacity: 1; stroke-dashoffset: 0; }
          }
        </style>""" if animate else ""
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.width} {self.height}" '
                f'width="100%" role="img">{style}{"".join(parts)}</svg>')


def svg_to_img_tag(svg, alt):
    """Embed SVG as a base64 <img> so Streamlit shows it reliably."""
    encoded = base64.b64encode(svg.encode("utf-8")).decode("utf-8")
    return f'<img src="data:image/svg+xml;base64,{encoded}" alt="{alt}" style="width:100%;max-width:260px;display:block;margin:0 auto;">'


# ---------------------------------------------------------------------------
# DRAWINGS
# ---------------------------------------------------------------------------

def _leaf(t, size, fill, vein):
    """Classic turtle leaf: two quarter-circle arcs, then a centre vein."""
    start_x, start_y, start_h = t.x, t.y, t.heading
    t.color(MOSS, fill)
    t.begin_fill()
    t.circle(size, 90)
    t.left(90)
    t.circle(size, 90)
    t.end_fill()
    # vein from base to tip
    t.penup()
    t.goto(start_x, start_y)
    t.setheading(start_h + 45)
    t.pendown()
    t.color(vein)
    t.forward(size * 1.41)


def draw_leaf(label="Green choice!"):
    """Drawn when the latest purchase is eco-friendly."""
    t = SVGTurtle()
    t.pensize(3)
    t.penup(); t.goto(-60, -70); t.setheading(0); t.pendown()
    _leaf(t, 120, SAGE, MOSS)
    # stem
    t.penup(); t.goto(-60, -70); t.setheading(225); t.pendown()
    t.color(BARK); t.forward(28)
    t.penup(); t.goto(0, -112); t.write(label, size=17, color=MOSS)
    return t.to_svg()


def draw_footprint(co2_kg, status):
    """Monthly footprint — colour shows how close you are to your goal."""
    colors = {"good": SAGE, "close": SUN, "over": CLAY}
    fill = colors.get(status, SAGE)
    t = SVGTurtle()
    t.pensize(3)
    t.color(BARK, fill)
    # sole: an upright oval made from arcs (small ends, big sides)
    t.penup(); t.goto(-2, -84); t.setheading(8); t.pendown()
    t.begin_fill()
    t.circle(34, 45)      # half of the heel curve
    t.circle(80, 90)      # right side
    t.circle(34, 90)      # toe end
    t.circle(80, 90)      # left side
    t.circle(34, 45)      # back to the start
    t.end_fill()
    # toes: dots along an arc above the sole, getting smaller
    toe_positions = [(-30, 66, 28), (-6, 82, 22), (16, 84, 18), (34, 78, 15), (48, 66, 12)]
    for x, y, d in toe_positions:
        t.penup(); t.goto(x, y); t.dot(d, fill)
    t.penup(); t.goto(0, -104); t.write(f"{co2_kg:.1f} kg CO₂ this month", size=15, color=BARK)
    return t.to_svg()


def draw_badge(name):
    """Medal drawn when a new badge is earned."""
    t = SVGTurtle()
    t.pensize(3)
    # ribbons
    for direction in (1, -1):
        t.color(RIVER, RIVER)
        t.penup(); t.goto(18 * direction, -20); t.setheading(270 - 20 * direction); t.pendown()
        t.begin_fill()
        t.forward(80); t.left(90 * direction); t.forward(22)
        t.left(90 * direction); t.forward(80); t.left(90 * direction); t.forward(22)
        t.end_fill()
    # medal
    t.color(BARK, SUN)
    t.penup(); t.goto(0, -15); t.setheading(0); t.pendown()
    t.begin_fill(); t.circle(60); t.end_fill()
    t.color(BARK)
    t.penup(); t.goto(0, -3); t.pendown(); t.circle(48)
    # star
    t.color(MOSS, MOSS)
    t.penup(); t.goto(-33, 55); t.setheading(0); t.pendown()
    t.begin_fill()
    for _ in range(5):
        t.forward(66)
        t.right(144)
    t.end_fill()
    t.penup(); t.goto(0, -118); t.write(name, size=15, color=MOSS)
    return t.to_svg()


def draw_sprout():
    """Empty state: a little seedling waiting for the first purchase."""
    t = SVGTurtle()
    t.pensize(3)
    # soil
    t.color(BARK, "#C9B79C")
    t.penup(); t.goto(-70, -60); t.setheading(0); t.pendown()
    t.begin_fill(); t.forward(140); t.left(90); t.forward(18); t.left(90); t.forward(140); t.left(90); t.forward(18); t.end_fill()
    # stem
    t.color(MOSS)
    t.penup(); t.goto(0, -42); t.setheading(90); t.pendown(); t.forward(60)
    # two small leaves
    t.penup(); t.goto(0, 0); t.setheading(10); t.pendown()
    _leaf(t, 45, SAGE, MOSS)
    t.penup(); t.goto(0, 0); t.setheading(80); t.pendown()
    _leaf(t, 45, SAGE, MOSS)
    t.penup(); t.goto(0, -100); t.write("Log a purchase to start", size=15, color=MOSS)
    return t.to_svg()
