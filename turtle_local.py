"""
turtle_local.py — the same ShopImpact drawings using Python's REAL turtle module.

Run this on your own laptop (it opens a window, so it won't run on Streamlit Cloud):
    python turtle_local.py

It draws the leaf, footprint and badge one after another, using exactly the
same commands as turtle_art.py. Handy for screenshots and for showing that the
in-app SVG drawings are genuine turtle logic.
"""

import turtle

MOSS, SAGE, RIVER, BARK, SUN = "#2F5D3A", "#8DB38B", "#3E7C98", "#6B4F3A", "#E2B33C"


def leaf(t, size, x, y, heading):
    t.penup(); t.goto(x, y); t.setheading(heading); t.pendown()
    t.color(MOSS, SAGE)
    t.begin_fill()
    t.circle(size, 90)
    t.left(90)
    t.circle(size, 90)
    t.end_fill()
    t.penup(); t.goto(x, y); t.setheading(heading + 45); t.pendown()
    t.forward(size * 1.41)


def footprint(t, x_off):
    t.color(BARK, SAGE)
    t.penup(); t.goto(x_off - 2, -84); t.setheading(8); t.pendown()
    t.begin_fill()
    t.circle(34, 45); t.circle(80, 90); t.circle(34, 90); t.circle(80, 90); t.circle(34, 45)
    t.end_fill()
    for x, y, d in [(-30, 66, 28), (-6, 82, 22), (16, 84, 18), (34, 78, 15), (48, 66, 12)]:
        t.penup(); t.goto(x_off + x, y); t.dot(d, SAGE)


def badge(t, x_off):
    for direction in (1, -1):
        t.color(RIVER, RIVER)
        t.penup(); t.goto(x_off + 18 * direction, -20); t.setheading(270 - 20 * direction); t.pendown()
        t.begin_fill()
        t.forward(80); t.left(90 * direction); t.forward(22)
        t.left(90 * direction); t.forward(80); t.left(90 * direction); t.forward(22)
        t.end_fill()
    t.color(BARK, SUN)
    t.penup(); t.goto(x_off, -15); t.setheading(0); t.pendown()
    t.begin_fill(); t.circle(60); t.end_fill()
    t.penup(); t.goto(x_off, -3); t.pendown(); t.circle(48)
    t.color(MOSS, MOSS)
    t.penup(); t.goto(x_off - 33, 55); t.setheading(0); t.pendown()
    t.begin_fill()
    for _ in range(5):
        t.forward(66)
        t.right(144)
    t.end_fill()


def label(t, x, text):
    t.penup(); t.goto(x, -130); t.color(MOSS)
    t.write(text, align="center", font=("Arial", 14, "bold"))


if __name__ == "__main__":
    screen = turtle.Screen()
    screen.title("ShopImpact — Turtle drawings")
    screen.bgcolor("#E9ECDD")
    screen.setup(900, 400)
    t = turtle.Turtle()
    t.speed(6)
    t.pensize(3)

    leaf(t, 120, -340, -70, 0)
    label(t, -280, "Green choice")
    footprint(t, 0)
    label(t, 0, "Monthly footprint")
    badge(t, 300)
    label(t, 300, "Eco Saver badge")

    t.hideturtle()
    screen.mainloop()
