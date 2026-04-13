
import tkinter as tk
import math
import random

WIDTH, HEIGHT = 1000, 700
BG = "#05060a"
NUM_PARTICLES = 900
CENTER_PULL = 0.0018
SWIRL = 0.032
FRICTION = 0.992
TRAIL_ALPHA_STEPS = 6

class Particle:
    def __init__(self):
        self.reset(initial=True)

    def reset(self, initial=False):
        angle = random.uniform(0, math.tau)
        radius = random.uniform(20, min(WIDTH, HEIGHT) * 0.48)
        speed = random.uniform(0.5, 2.8)

        self.x = WIDTH / 2 + math.cos(angle) * radius
        self.y = HEIGHT / 2 + math.sin(angle) * radius

        tangent = angle + math.pi / 2
        self.vx = math.cos(tangent) * speed
        self.vy = math.sin(tangent) * speed

        if initial:
            self.life = random.randint(80, 400)
        else:
            self.life = random.randint(140, 420)

        self.size = random.uniform(1.2, 3.6)
        hue = random.choice([
            (255, 80, 120),
            (90, 180, 255),
            (255, 210, 90),
            (180, 120, 255),
            (120, 255, 200),
        ])
        self.color = hue

    def update(self):
        cx = WIDTH / 2 - self.x
        cy = HEIGHT / 2 - self.y
        dist = math.hypot(cx, cy) + 1e-6

        # Pull towards center
        self.vx += cx * CENTER_PULL
        self.vy += cy * CENTER_PULL

        # Swirl around center
        self.vx += (-cy / dist) * SWIRL * (dist / 90)
        self.vy += (cx / dist) * SWIRL * (dist / 90)

        # Tiny noise for organic motion
        self.vx += random.uniform(-0.03, 0.03)
        self.vy += random.uniform(-0.03, 0.03)

        self.vx *= FRICTION
        self.vy *= FRICTION

        self.x += self.vx
        self.y += self.vy
        self.life -= 1

        # Reset if too close to center, too far out, or expired
        out = (
            self.x < -100 or self.x > WIDTH + 100 or
            self.y < -100 or self.y > HEIGHT + 100
        )
        if dist < 12 or out or self.life <= 0:
            self.reset()

def rgb_to_hex(rgb):
    return "#{:02x}{:02x}{:02x}".format(*rgb)

def blend(rgb, factor):
    # factor in [0,1], blends towards black
    return tuple(max(0, min(255, int(c * factor))) for c in rgb)

root = tk.Tk()
root.title("Cosmic Vortex")
root.configure(bg=BG)
canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg=BG, highlightthickness=0)
canvas.pack()

particles = [Particle() for _ in range(NUM_PARTICLES)]

title = canvas.create_text(
    WIDTH // 2, 35,
    text="COSMIC VORTEX",
    fill="#dfe7ff",
    font=("Helvetica", 22, "bold")
)
subtitle = canvas.create_text(
    WIDTH // 2, 65,
    text="Pulsa espacio para cambiar el flujo | Click para generar una explosión",
    fill="#7f8db5",
    font=("Helvetica", 11)
)

modes = [
    {"pull": 0.0018, "swirl": 0.032},
    {"pull": 0.0008, "swirl": 0.055},
    {"pull": 0.0030, "swirl": 0.018},
]
mode_idx = 0

def draw_core():
    t = root.tk.call('after', 'info')
    pulse = 18 + 5 * math.sin(root.winfo_fpixels('1i') + len(str(t)))
    cx, cy = WIDTH / 2, HEIGHT / 2
    for r, color in [(42, "#1b2340"), (26, "#3a4d99"), (10, "#e8f0ff")]:
        canvas.create_oval(cx-r, cy-r, cx+r, cy+r, fill=color, outline="")

def explode(event=None):
    mx = event.x if event else WIDTH // 2
    my = event.y if event else HEIGHT // 2
    for _ in range(120):
        p = random.choice(particles)
        angle = random.uniform(0, math.tau)
        speed = random.uniform(2, 8)
        p.x, p.y = mx, my
        p.vx = math.cos(angle) * speed
        p.vy = math.sin(angle) * speed
        p.life = random.randint(50, 180)

def switch_mode(event=None):
    global mode_idx, CENTER_PULL, SWIRL
    mode_idx = (mode_idx + 1) % len(modes)
    CENTER_PULL = modes[mode_idx]["pull"]
    SWIRL = modes[mode_idx]["swirl"]

root.bind("<space>", switch_mode)
root.bind("<Button-1>", explode)

def animate():
    canvas.delete("frame")

    # Soft fade using a translucent-like overlay simulation
    canvas.create_rectangle(0, 0, WIDTH, HEIGHT, fill=BG, outline="", tags="frame")

    # Draw glow rings
    cx, cy = WIDTH / 2, HEIGHT / 2
    for rad, outline in [(250, "#0b1020"), (170, "#101830"), (95, "#16234a")]:
        canvas.create_oval(cx-rad, cy-rad, cx+rad, cy+rad, outline=outline, width=1, tags="frame")

    for p in particles:
        oldx, oldy = p.x, p.y
        p.update()

        dx = p.x - oldx
        dy = p.y - oldy

        # Multi-line trail
        for i in range(TRAIL_ALPHA_STEPS):
            factor = (TRAIL_ALPHA_STEPS - i) / TRAIL_ALPHA_STEPS
            color = rgb_to_hex(blend(p.color, factor))
            x1 = oldx - dx * i * 0.85
            y1 = oldy - dy * i * 0.85
            x2 = p.x - dx * i * 0.45
            y2 = p.y - dy * i * 0.45
            canvas.create_line(
                x1, y1, x2, y2,
                fill=color,
                width=max(1, p.size * factor * 0.85),
                smooth=True,
                tags="frame"
            )

        # Particle head
        s = p.size
        canvas.create_oval(
            p.x - s, p.y - s, p.x + s, p.y + s,
            fill=rgb_to_hex(p.color),
            outline="",
            tags="frame"
        )

    # Core glow
    for r, color in [(40, "#101933"), (24, "#28427a"), (9, "#f2f7ff")]:
        canvas.create_oval(cx-r, cy-r, cx+r, cy+r, fill=color, outline="", tags="frame")

    # Text
    canvas.create_text(
        WIDTH // 2, 35,
        text="COSMIC VORTEX",
        fill="#dfe7ff",
        font=("Helvetica", 22, "bold"),
        tags="frame"
    )
    canvas.create_text(
        WIDTH // 2, 65,
        text="Pulsa espacio para cambiar el flujo | Click para generar una explosión",
        fill="#7f8db5",
        font=("Helvetica", 11),
        tags="frame"
    )

    root.after(16, animate)

animate()
root.mainloop()
