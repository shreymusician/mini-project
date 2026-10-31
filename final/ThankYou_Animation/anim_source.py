"""AgriVision thank-you animation: farmer + rover short story, rendered with Pillow.
Pure functions of time t (seconds) -> 1920x1080 frame. 15 s story + 1 s hold.
Run:  python anim.py preview     (key-frame PNGs)
      python anim.py render OUT.mp4
"""
import math, sys, random
from PIL import Image, ImageDraw, ImageFont
import numpy as np

W, H, SS, FPS = 1920, 1080, 2, 30
DUR = 16.0
FB = 'C:/Windows/Fonts/segoeuib.ttf'
FR = 'C:/Windows/Fonts/segoeui.ttf'

# ---------------------------------------------------------------- helpers
def sm(x):
    x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
def lerp(a, b, t): return a + (b - a) * t
def K(t, pts):
    n = len(pts)
    if t <= pts[0][0]: return pts[0][1]
    if t >= pts[-1][0]: return pts[-1][1]
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    h = [xs[i + 1] - xs[i] for i in range(n - 1)]
    dl = [(ys[i + 1] - ys[i]) / h[i] for i in range(n - 1)]
    d = [0.0] * n
    d[0], d[-1] = dl[0], dl[-1]
    for i in range(1, n - 1):
        if dl[i - 1] * dl[i] > 0:
            w1 = 2 * h[i] + h[i - 1]; w2 = h[i] + 2 * h[i - 1]
            d[i] = (w1 + w2) / (w1 / dl[i - 1] + w2 / dl[i])
    for i in range(n - 1):
        if t <= xs[i + 1]:
            u = (t - xs[i]) / h[i]
            h00 = 2 * u ** 3 - 3 * u ** 2 + 1; h10 = u ** 3 - 2 * u ** 2 + u
            h01 = -2 * u ** 3 + 3 * u ** 2; h11 = u ** 3 - u ** 2
            return h00 * ys[i] + h10 * h[i] * d[i] + h01 * ys[i + 1] + h11 * h[i] * d[i + 1]
    return ys[-1]
def ob(x, c=1.70158):
    x = max(0.0, min(1.0, x)); return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2
def rot(p, deg):
    a = math.radians(deg); c, s = math.cos(a), math.sin(a)
    return (p[0] * c - p[1] * s, p[0] * s + p[1] * c)
def add(a, b): return (a[0] + b[0], a[1] + b[1])
def vec(a, l): return (math.sin(math.radians(a)) * l, math.cos(math.radians(a)) * l)
def mix(c1, c2, t): return tuple(int(lerp(a, b, t)) for a, b in zip(c1, c2))
def font(sz, bold=True): return ImageFont.truetype(FB if bold else FR, int(sz * SS))

OUT = (40, 52, 44, 255)
SKIN = (176, 112, 72, 255); SKIN_D = (150, 92, 58, 255)
KURTA = (247, 236, 208, 255); KURTA_D = (226, 212, 176, 255)
DHOTI = (252, 250, 244, 255)
TEAL = (22, 132, 134, 255); FOREST = (31, 94, 59, 255); GOLD = (232, 168, 38, 255)


class Cv:
    def __init__(s):
        s.im = Image.new('RGBA', (W * SS, H * SS), (0, 0, 0, 0))
        s.d = ImageDraw.Draw(s.im, 'RGBA')
    def P(s, pts): return [(x * SS, y * SS) for x, y in pts]
    def poly(s, pts, fill, out=None, w=0):
        s.d.polygon(s.P(pts), fill=fill)
        if out and w: s.d.line(s.P(list(pts) + [pts[0]]), fill=out, width=max(1, int(w * SS)), joint='curve')
    def ell(s, c, rx, ry, fill, out=None, w=0):
        s.d.ellipse([(c[0] - rx) * SS, (c[1] - ry) * SS, (c[0] + rx) * SS, (c[1] + ry) * SS],
                    fill=fill, outline=out, width=max(1, int(w * SS)) if out else 0)
    def line(s, pts, fill, w): s.d.line(s.P(pts), fill=fill, width=max(1, int(w * SS)), joint='curve')
    def limb(s, a, b, w, fill, out=OUT):
        if out:
            s.line([a, b], out, w + 7)
            s.ell(a, (w + 7) / 2, (w + 7) / 2, out); s.ell(b, (w + 7) / 2, (w + 7) / 2, out)
        s.line([a, b], fill, w)
        s.ell(a, w / 2, w / 2, fill); s.ell(b, w / 2, w / 2, fill)
    def rr(s, x, y, w, h, r, fill, out=None, ow=0):
        s.d.rounded_rectangle([x * SS, y * SS, (x + w) * SS, (y + h) * SS], radius=r * SS, fill=fill,
                              outline=out, width=max(1, int(ow * SS)) if out else 0)
    def text(s, xy, txt, f, fill, anchor='la'):
        s.d.text((xy[0] * SS, xy[1] * SS), txt, font=f, fill=fill, anchor=anchor)

def epoly(c, rx, ry, a=0, n=28):
    pts = []
    for i in range(n):
        th = 2 * math.pi * i / n
        p = rot((rx * math.cos(th), ry * math.sin(th)), a)
        pts.append((c[0] + p[0], c[1] + p[1]))
    return pts

def star(cv, c, r, col, rotd=0):
    pts = []
    for i in range(8):
        rr = r if i % 2 == 0 else r * 0.28
        a = math.radians(rotd + i * 45)
        pts.append((c[0] + rr * math.sin(a), c[1] - rr * math.cos(a)))
    cv.poly(pts, col)

# ---------------------------------------------------------------- background
ROWS = [(590, .42), (650, .52), (715, .62), (775, .72), (905, .95), (1050, 1.35)]
random.seed(7)
_BG = None
def background():
    global _BG
    if _BG is not None: return _BG.copy()
    cv = Cv()
    # sky
    for y in range(0, 520):
        t = y / 520
        c = mix((120, 196, 240), (214, 240, 252), t)
        cv.d.rectangle([0, y * SS, W * SS, (y + 1) * SS], fill=c + (255,))
    # sun glow
    # hills
    cv.poly([(0, 520), (0, 440), (260, 400), (520, 440), (820, 395), (1180, 450), (1500, 410), (1920, 455), (1920, 520)], (150, 205, 150, 255))
    cv.poly([(0, 540), (0, 480), (340, 455), (700, 495), (1100, 462), (1480, 500), (1920, 470), (1920, 540)], (112, 184, 112, 255))
    # trees on far hill
    for x in (120, 210, 640, 1010, 1330, 1700):
        cv.limb((x, 505), (x, 470), 8, (108, 80, 54, 255), None)
        cv.ell((x, 452), 34, 30, (72, 150, 82, 255))
        cv.ell((x - 14, 462), 22, 18, (84, 164, 94, 255))
    # ground
    for y in range(500, H):
        t = (y - 500) / (H - 500)
        c = mix((118, 196, 82), (58, 136, 52), t)
        cv.d.rectangle([0, y * SS, W * SS, (y + 1) * SS], fill=c + (255,))
    # soil strips under each row
    for y0, sc in ROWS:
        cv.poly([(0, y0 - 6), (W, y0 - 6), (W, y0 + 20 * sc + 4), (0, y0 + 20 * sc + 4)], (146, 108, 68, 255))
        cv.poly([(0, y0 + 2), (W, y0 + 2), (W, y0 + 14 * sc), (0, y0 + 14 * sc)], (120, 86, 52, 255))
    _BG = cv.im
    return _BG.copy()

def sun(cv, t):
    cx, cy = 1560, 170 + 8 * math.sin(t * 0.8)
    pulse = 1 + 0.06 * math.sin(t * 2.2)
    for r, a in ((190, 26), (140, 44), (100, 70)):
        cv.ell((cx, cy), r * pulse, r * pulse, (255, 226, 150, a))
    for i in range(16):                       # rotating rays
        ang = t * 14 + i * 22.5
        r0, r1 = 88 * pulse, (150 if i % 2 == 0 else 125) * pulse + 8 * math.sin(t * 3 + i)
        a0, a1 = math.radians(ang - 5), math.radians(ang + 5)
        cv.poly([(cx + math.sin(a0) * r0, cy - math.cos(a0) * r0), (cx + math.sin(math.radians(ang)) * r1, cy - math.cos(math.radians(ang)) * r1),
                 (cx + math.sin(a1) * r0, cy - math.cos(a1) * r0)], (255, 214, 96, 235))
    cv.ell((cx, cy), 62 * pulse, 62 * pulse, (255, 218, 110, 255))
    cv.ell((cx, cy), 50 * pulse, 50 * pulse, (255, 240, 180, 255))
    # face-less glint
    cv.ell((cx - 16, cy - 18), 12, 8, (255, 255, 255, 170))

def clouds(cv, t):
    for i, (x0, y, s, sp) in enumerate([(200, 110, 1.0, 9), (780, 70, 0.8, 6), (1200, 190, 1.2, 7), (1600, 90, 0.7, 5)]):
        x = (x0 + t * sp) % (W + 400) - 200
        for dx, dy, r in ((0, 0, 46), (46, -16, 54), (96, 0, 44), (50, 14, 50)):
            cv.ell((x + dx * s, y + dy * s), r * s, r * s * 0.8, (255, 255, 255, 235))

def plant(cv, x, y, sc, t, h=1.0, phase=0.0, hero=False):
    sway = math.sin(t * 1.7 + x * 0.013 + phase) * 5
    ht = 78 * sc * h
    top = (x + math.sin(math.radians(sway)) * ht, y - math.cos(math.radians(sway)) * ht)
    cv.line([(x, y), top], (60, 128, 54, 255), max(2, 6 * sc))
    for i, (f, side, ln) in enumerate([(0.3, -1, 0.62), (0.45, 1, 0.66), (0.62, -1, 0.5), (0.78, 1, 0.5), (0.95, -1, 0.4)]):
        bx = lerp(x, top[0], f); by = lerp(y, top[1], f)
        ang = side * (58 - i * 5) + sway * 0.6
        L = ln * ht * 1.15
        e = rot((0, -L), ang)
        mid = (bx + e[0] / 2, by + e[1] / 2)
        cv.poly(epoly(mid, L / 2, L * 0.17, ang + 90, 18), (92 + i * 10, 176 - i * 6, 70 + i * 4, 255), (42, 100, 44, 255), 1.5 * sc)
    if hero:
        cv.ell((top[0], top[1] - 10 * sc), 12 * sc, 18 * sc, (240, 200, 70, 255), OUT, 2)

def field_row(cv, idx, t, skip=None):
    y0, sc = ROWS[idx]
    x = -30 + (idx * 37) % 70
    step = 118 * sc + 22
    k = 0
    while x < W + 40:
        if not (skip and skip[0] < x < skip[1]):
            plant(cv, x, y0 + 8 * sc, sc, t, 1.0 if idx < 4 else 0.8, k * 1.3)
        x += step; k += 1

# ---------------------------------------------------------------- rover
def rover_draw(cv, gx, gy, t, mirror=1, k=1.25, sx=1.0, sy=1.0, rotd=0.0, wheel=0.0, cam_tilt=0.0, bob=0.0):
    def T(p):
        x, y = p[0] * mirror * k * sx, (p[1] + bob) * k * sy
        x, y = rot((x, y), rotd * (1 if mirror >= 0 else -1))
        return (gx + x, gy + y)
    def TP(pts): return [T(p) for p in pts]
    def E(c, rx, ry, fill, out=None, w=0, a=0): cv.poly(TP(epoly(c, rx, ry, a, 22)), fill, out, w)
    def R(x0, y0, x1, y1, fill, out=OUT, w=3): cv.poly(TP([(x0, y0), (x1, y0), (x1, y1), (x0, y1)]), fill, out, w)
    tire = (38, 40, 44, 255); rim = (244, 190, 44, 255)
    def wheel_at(c, r, col_t, col_r, ang):
        E(c, r, r, col_t, OUT, 3)
        for i in range(10):                              # tread notches
            a = math.radians(ang + i * 36)
            p0 = (c[0] + math.cos(a) * r, c[1] + math.sin(a) * r)
            p1 = (c[0] + math.cos(a) * (r - 7), c[1] + math.sin(a) * (r - 7))
            cv.line([T(p0), T(p1)], (88, 92, 98, 255), 4)
        E(c, r * 0.58, r * 0.58, col_r, OUT, 2.5)
        for i in range(4):
            a = math.radians(ang + i * 90)
            cv.line([T(c), T((c[0] + math.cos(a) * r * 0.55, c[1] + math.sin(a) * r * 0.55))], (190, 140, 20, 255), 4)
        E(c, r * 0.18, r * 0.18, (80, 80, 84, 255), OUT, 2)
    # far wheels (darker, up-and-back)
    wheel_at((-82, -66), 38, (30, 32, 36, 255), (196, 150, 36, 255), wheel)
    wheel_at((92, -66), 38, (30, 32, 36, 255), (196, 150, 36, 255), wheel)
    # chassis
    R(-156, -104, 156, -54, (62, 78, 90, 255))
    R(-156, -92, 156, -80, FOREST, None, 0)
    R(-170, -62, 170, -46, (46, 56, 66, 255))
    # soil probe prongs
    cv.line([T((120, -46)), T((120, -12))], (200, 200, 205, 255), 4)
    cv.line([T((136, -46)), T((136, -12))], (200, 200, 205, 255), 4)
    # electronics box
    cv.poly(TP([(-76, -170), (62, -170), (62, -104), (-76, -104)]), (244, 247, 247, 255), OUT, 3)
    cv.poly(TP([(-66, -160), (52, -160), (52, -150), (-66, -150)]), TEAL)
    E((-56, -128), 11, 11, (60, 170, 80, 255), OUT, 2)            # leaf badge
    cv.line([T((-62, -118)), T((-50, -138))], (255, 255, 255, 255), 3)
    # radiation shield (temperature/humidity)
    cv.line([T((-38, -170)), T((-38, -212))], (120, 128, 134, 255), 6)
    for i, yy in enumerate((-206, -194, -182)):
        E((-38, yy), 28, 7, (250, 250, 250, 255), OUT, 2)
    # rain sensor plate
    cv.poly(TP([(10, -176), (44, -182), (48, -172), (14, -166)]), (40, 70, 120, 255), OUT, 2)
    # antenna
    cv.line([T((-60, -170)), T((-74, -246))], OUT, 5)
    E((-74, -250), 6, 6, GOLD, OUT, 2)
    # mast + camera head
    cv.line([T((96, -104)), T((96, -246))], (110, 118, 126, 255), 11)
    hx, hy = 96, -258
    def CH(p): return T(add((hx, hy), rot(p, cam_tilt)))
    cv.poly([CH(p) for p in [(-34, -24), (34, -24), (34, 24), (-34, 24)]], (36, 40, 46, 255), OUT, 3)
    cv.poly([CH(p) for p in epoly((20, 0), 15, 15, 0, 20)], (20, 30, 40, 255), (96, 200, 210, 255), 4)
    cv.poly([CH(p) for p in epoly((24, -5), 4, 4, 0, 10)], (255, 255, 255, 255))
    cv.poly([CH(p) for p in [(-26, -16), (-6, -16), (-6, -6), (-26, -6)]], (70, 170, 120, 255))
    # front sensors + lights
    E((152, -90), 9, 9, (200, 206, 212, 255), OUT, 2); E((152, -68), 9, 9, (200, 206, 212, 255), OUT, 2)
    E((158, -74), 7, 7, (255, 238, 170, 255), OUT, 2)
    # near wheels
    wheel_at((-118, -48), 48, tire, rim, wheel)
    wheel_at((118, -48), 48, tire, rim, wheel)
    return T, CH

# ---------------------------------------------------------------- farmer
def farmer_pose(t):
    P = {}
    breath = math.sin(t * 2.6)
    P['theta'] = K(t, [(0, 4), (0.9, 64), (1.4, 64), (1.9, -8), (2.25, -14), (2.6, -4), (3.0, 8), (7.8, 8), (8.2, 0), (10.0, 0), (10.9, 4), (11.5, -2), (12.0, 0), (16, 0)])
    P['theta'] += 0.9 * breath
    P['sit'] = K(t, [(0, 0), (9.9, 0), (10.9, 1), (16, 1)])
    P['tilt'] = K(t, [(0, 10), (1.0, 18), (2.2, -14), (2.9, 8), (7.9, 6), (8.3, -3), (10, -3), (11.0, 2), (11.5, -7), (16, -7)])
    P['look'] = K(t, [(0, 0.5), (1.2, 0.9), (1.8, 0.0), (2.7, -0.6), (2.95, 0.5), (7.9, 0.5), (8.3, 1.0), (10.0, 0.9), (16, 0.7)])
    wob = math.sin(t * 9) * 7
    # near arm (a1 = upper arm angle, a2 = forearm angle; 0 = hanging, +ve forwards/up)
    P['a'] = (K(t, [(0, 6), (0.9, 62), (1.4, 62), (1.9, -30), (2.25, -30), (2.5, 105), (2.9, 105), (3.2, 6), (9.2, 6), (9.55, 128),
                    (10.15, 128), (10.4, 50), (10.6, 40), (11.0, 40), (11.4, 50), (11.8, 50), (12.3, 45), (13.7, 45), (14.3, 88), (16, 88)]),
              K(t, [(0, 12), (0.9, 80), (1.4, 80), (1.9, -50), (2.25, -50), (2.5, 200), (2.9, 200), (3.2, 12), (9.2, 12), (9.55, 172),
                    (10.15, 172), (10.4, 70), (10.7, 125), (11.0, 125), (11.4, 130), (11.8, 130), (12.3, 128), (13.7, 128), (14.3, 165), (16, 165)]))
    if 2.5 < t < 2.9: P['a'] = (P['a'][0], P['a'][1] + wob)
    if 0.9 < t < 1.4: P['a'] = (P['a'][0] + math.sin(t * 12) * 2, P['a'][1])
    if 9.6 <= t < 10.15:
        env = sm((t - 9.6) / 0.12) * sm((10.15 - t) / 0.12)
        P['a'] = (P['a'][0], P['a'][1] + 24 * env * math.sin((t - 9.6) * 20))
    P['b'] = (K(t, [(0, 4), (0.9, 40), (1.4, 40), (1.9, -30), (2.25, -30), (2.6, 4), (10.0, 4), (10.9, 28), (16, 28)]),
              K(t, [(0, 8), (0.9, 55), (1.4, 55), (1.9, -50), (2.25, -50), (2.6, 8), (10.0, 8), (10.9, 75), (16, 75)]))
    # expression
    P['lid'] = K(t, [(0, 0.45), (2.9, 0.5), (3.0, 0.45), (7.9, 0.45), (8.1, 0.0), (9.3, 0.0), (9.4, 0.15), (16, 0.1)])
    P['open'] = K(t, [(0, 1.0), (7.9, 1.0), (8.2, 1.45), (8.6, 1.45), (8.9, 1.0), (16, 1.0)])
    P['brow'] = K(t, [(0, -0.7), (2.2, -1.0), (2.9, -0.6), (7.9, -0.6), (8.2, 1.2), (8.6, 1.2), (9.0, 0.2), (9.4, 0.6), (16, 0.4)])
    # eye style
    if 11.0 <= t < 11.75 or 11.95 <= t < 13.6 or 14.5 <= t: P['eyes'] = 'happy'
    elif 2.0 <= t < 2.25: P['eyes'] = 'squeeze'
    else: P['eyes'] = 'open'
    blink = any(a <= t < a + 0.16 for a in (0.55, 4.8, 6.7, 8.75, 8.95, 12.6))
    if blink and P['eyes'] == 'open': P['eyes'] = 'closed'
    # mouth
    m = 'flat'
    if 1.9 <= t < 2.3: m = 'sigh'
    elif 7.95 <= t < 8.45: m = 'oh'
    elif 8.45 <= t < 9.25: m = 'flat2'
    elif 9.25 <= t < 10.0: m = 'big'
    elif 10.0 <= t < 11.1: m = 'smile'
    elif 11.1 <= t < 11.7: m = 'smile'
    elif 11.7 <= t < 13.7: m = 'content'
    elif 13.7 <= t: m = 'big'
    P['mouth'] = m
    return P

def farmer_draw(cv, t, fx, gy, plant_xy=None):
    P = farmer_pose(t)
    th, sit = P['theta'], P['sit']
    # stool + chai bag
    if t >= 9.7:
        u = ob((t - 9.7) / 0.5)
        sx = fx + 6
        cv.poly([(sx - 52 * u, gy - 126 * u), (sx + 52 * u, gy - 126 * u), (sx + 44 * u, gy), (sx - 44 * u, gy)], (186, 130, 70, 255), OUT, 4)
        cv.rr(sx - 58 * u, gy - 142 * u, 116 * u, 20 * u, 8, (214, 160, 96, 255), OUT, 4)
    # skeleton
    H0 = (fx - 10 * sit, gy - lerp(215, 132, sit))
    knee = (H0[0] + lerp(10, 104, sit), H0[1] + lerp(105, 0, sit))
    ank = (knee[0] + lerp(-2, 4, sit), gy - 10)
    # far leg then near leg
    for off, dark in ((-16, True), (10, False)):
        k2 = (knee[0] + off * 0.6 * (1 - sit) + (0 if not dark else -6), knee[1]); a2 = (ank[0] + off * 0.6 * (1 - sit) - (6 if dark else 0), ank[1])
        h2 = (H0[0] + off * 0.3, H0[1])
        col = (240, 238, 228, 255) if dark else DHOTI
        cv.limb(h2, k2, 50, col)
        cv.limb(k2, a2, 34, SKIN_D if dark else SKIN)
        cv.ell((a2[0] + 14, gy - 6), 28, 11, (92, 66, 44, 255), OUT, 3)
    # torso
    up = rot((0, -1), th)
    S = (H0[0] + up[0] * 150, H0[1] + up[1] * 150)
    Nk = (H0[0] + up[0] * 178, H0[1] + up[1] * 178)
    side = rot((1, 0), th)
    def tp(a, b): return (H0[0] + side[0] * a + up[0] * b, H0[1] + side[1] * a + up[1] * b)
    sag = -4 if (2.3 < t < 3.1 or t < 0.2) else 0
    cv.poly([tp(-40, 0), tp(40, 0), tp(46, 150), tp(30, 176), tp(-30, 176), tp(-46, 150)], KURTA, OUT, 4)
    cv.poly([tp(-40, 0), tp(40, 0), tp(37, 40), tp(-37, 40)], KURTA_D)
    cv.line([tp(-44, 156), tp(40, 128)], TEAL, 14)                        # gamcha across shoulder
    cv.line([tp(0, 176), tp(0, 120)], KURTA_D, 3)
    # head
    hc = (Nk[0] + rot((0, -74), th + P['tilt'])[0], Nk[1] + rot((0, -74), th + P['tilt'])[1])
    cv.limb(Nk, hc, 26, SKIN, None)
    head(cv, hc, th + P['tilt'], P, t)
    # arms
    def arm(a1, a2, near):
        sh = (S[0] + (4 if near else -6), S[1] + 4)
        el = add(sh, vec(a1, 82)); hd = add(el, vec(a2, 78))
        cv.limb(sh, el, 28, KURTA if near else KURTA_D)
        cv.limb(el, hd, 24, SKIN if near else SKIN_D)
        cv.ell(hd, 17, 17, SKIN if near else SKIN_D, OUT, 3)
        return hd
    arm(*P['b'], False)
    hd = arm(*P['a'], True)
    # thumbs-up
    if 9.4 <= t < 10.3:                       # open waving palm with fingers
        cv.ell((hd[0], hd[1] - 6), 21, 21, SKIN, OUT, 3)
        for i, ang in enumerate((-34, -12, 10, 32)):
            tip = add((hd[0], hd[1] - 6), vec(180 + ang, 30))
            cv.limb((hd[0], hd[1] - 6), tip, 9, SKIN, OUT)
    # smartphone in hand (replaces the chai cup)
    if 10.45 <= t:
        phone(cv, hd, t)
    return P, hd, S, hc

def phone(cv, c, t):
    x, y = c
    k = 1.4
    def q(dx, dy): return (x + dx * k, y + dy * k)
    cv.rr(*q(-14, -76), 42 * k, 78 * k, 9, (26, 32, 40, 255), OUT, 3)
    cv.rr(*q(-9, -70), 32 * k, 62 * k, 5, (22, 150, 160, 255))
    cv.rr(*q(-9, -70), 32 * k, 30 * k, 5, (88, 178, 104, 255))                # mini live-view
    cv.poly([q(-2, -52), q(14, -52), q(12, -46), q(0, -46)], (36, 46, 56, 255))
    cv.ell(q(-4, -46), 3 * k, 3 * k, (36, 46, 56, 255)); cv.ell(q(10, -46), 3 * k, 3 * k, (36, 46, 56, 255))
    if int(t * 2) % 2 == 0: cv.ell(q(-4, -65), 2.6 * k, 2.6 * k, (232, 60, 60, 255))   # LIVE dot
    jx, jy = q(7, -20)
    cv.ell((jx, jy), 11 * k, 11 * k, (255, 255, 255, 200), OUT, 2)
    tap = math.sin(t * 7)
    cv.ell((jx + 4 * tap * k, jy + 3 * math.cos(t * 5) * k), 5 * k, 5 * k, (22, 132, 134, 255))
    cv.ell(q(20, -6 + 2 * tap), 7 * k, 10 * k, SKIN, OUT, 2)                    # thumb

def bezier(p0, p1, p2, u):
    a = (1 - u) ** 2; b = 2 * (1 - u) * u; c = u * u
    return (a * p0[0] + b * p1[0] + c * p2[0], a * p0[1] + b * p1[1] + c * p2[1])

def phone_signals(cv, t, hd, rs):
    if not rs or t < 10.55 or hd is None: return
    al = sm((t - 10.55) / 0.5)
    p0 = (hd[0] + 8, hd[1] - 110)
    ant = rs['T']((-74, -250))
    p2 = (ant[0], ant[1] - 14)
    p1 = ((p0[0] + p2[0]) / 2, max(p0[1], p2[1]) + 110)
    cv.d.line([(bezier(p0, p1, p2, i / 40)[0] * SS, bezier(p0, p1, p2, i / 40)[1] * SS) for i in range(41)],
              fill=(22, 200, 210, int(70 * al)), width=3 * SS)
    for i in range(6):                         # phone -> rover (commands)
        ph = (t * 0.75 + i / 6) % 1.0
        x, y = bezier(p0, p1, p2, ph)
        r = 6 + 3 * math.sin(math.pi * ph)
        cv.ell((x, y), r, r, (22, 200, 210, int(255 * al * math.sin(math.pi * ph))), (255, 255, 255, int(200 * al * math.sin(math.pi * ph))), 2)
    for i in range(3):                         # rover -> phone (telemetry)
        ph = 1 - ((t * 0.6 + i / 3) % 1.0)
        x, y = bezier(p0, p1, p2, ph)
        r = 4.5
        cv.ell((x, y), r, r, (240, 180, 40, int(255 * al * math.sin(math.pi * ph))))
    for j in range(3):                         # radiating arcs at the phone
        u = (t * 1.4 + j / 3) % 1.0
        r = 16 + u * 38
        cv.d.arc([(p0[0] - r) * SS, (p0[1] - 6 - r) * SS, (p0[0] + r) * SS, (p0[1] - 6 + r) * SS], 215, 325,
                 fill=(22, 200, 210, int(230 * al * (1 - u))), width=4 * SS)
    pulse = 0.5 + 0.5 * math.sin(t * 6)        # rover antenna receives
    cv.ell((ant[0], ant[1] - 4), 10 + 8 * pulse, 10 + 8 * pulse, (240, 180, 40, int(120 * al * (0.4 + 0.6 * pulse))))

def head(cv, c, ang, P, t):
    HS = 1.22
    def q(dx, dy): return (c[0] + dx * HS, c[1] + dy * HS)
    look = P['look'] * 9
    cv.ell(q(-56, 6), 10 * HS, 15 * HS, SKIN_D, OUT, 3)
    cv.ell(c, 58 * HS, 62 * HS, SKIN, OUT, 4)
    cv.poly(epoly(q(0, -40), 60 * HS, 34 * HS, 0, 26), (252, 252, 248, 255), OUT, 4)
    cv.poly([q(-58, -30), q(58, -30), q(52, -14), q(-52, -14)], TEAL)
    cv.poly([q(40, -52), q(88, -24), q(80, -6), q(36, -34)], (252, 252, 248, 255), OUT, 3)
    for ex in (-22, 24):
        e = q(ex + look * 0.5, -4)
        st = P['eyes']
        if st in ('happy', 'squeeze'):
            cv.line([(e[0] - 16, e[1] + 5), (e[0] - 7, e[1] - 7), (e[0], e[1] - 10), (e[0] + 7, e[1] - 7), (e[0] + 16, e[1] + 5)], OUT, 6)
        elif st == 'closed':
            cv.line([(e[0] - 16, e[1] + 3), (e[0] + 16, e[1] + 3)], OUT, 6)
        else:
            ry = 22 * P['open']; rx = 17 * min(1.1, 0.95 + 0.1 * P['open'])
            cv.ell(e, rx, ry, (255, 255, 255, 255), OUT, 3)
            ir = 11 if P['open'] > 1.2 else 12.5
            cv.ell((e[0] + look * 0.8, e[1] + 2), ir, min(ir * 1.3, ry - 1), (58, 36, 26, 255))
            cv.ell((e[0] + look * 0.8, e[1] + 2), ir * 0.55, min(ir * 0.7, ry - 2), (20, 12, 10, 255))
            cv.ell((e[0] + look * 0.8 + 5, e[1] - 5), 4.2, 4.2, (255, 255, 255, 255))
            if P['lid'] > 0.02:
                cut = ry * 2 * P['lid']
                cv.poly([(e[0] - rx - 3, e[1] - ry - 3), (e[0] + rx + 3, e[1] - ry - 3), (e[0] + rx + 3, e[1] - ry + cut), (e[0] - rx - 3, e[1] - ry + cut)], SKIN)
                cv.line([(e[0] - rx, e[1] - ry + cut), (e[0] + rx, e[1] - ry + cut)], OUT, 4)
    bq = P['brow']; sl = -bq
    for side, ex in ((0, -22), (1, 24)):
        e = q(ex + look * 0.5, -36 - max(0, bq) * 7)
        a = sl * 5
        if side == 0: pts = [(e[0] - 17, e[1] + a), (e[0] + 17, e[1] - a)]
        else: pts = [(e[0] - 17, e[1] - a), (e[0] + 17, e[1] + a)]
        cv.line(pts, (50, 34, 26, 255), 5)
    nx = c[0] + look * 1.1
    cv.ell((nx + 4, c[1] + 16 * HS), 7, 6, SKIN_D, None)
    cv.poly([(nx - 42, c[1] + 30 * HS), (nx - 8, c[1] + 24 * HS), (nx + 4, c[1] + 28 * HS), (nx + 16, c[1] + 24 * HS), (nx + 48, c[1] + 30 * HS),
             (nx + 26, c[1] + 40 * HS), (nx + 4, c[1] + 34 * HS), (nx - 18, c[1] + 40 * HS)], (36, 28, 24, 255))
    mx, my, m = nx + 3, c[1] + 50 * HS, P['mouth']
    if m == 'flat':
        cv.line([(mx - 13, my + 4), (mx, my), (mx + 13, my + 5)], OUT, 4)
    elif m == 'flat2':
        cv.line([(mx - 11, my + 2), (mx + 11, my + 2)], OUT, 4)
    elif m == 'sigh':
        cv.ell((mx, my + 4), 11, 13, (110, 40, 40, 255), OUT, 3)
    elif m == 'oh':
        cv.ell((mx, my + 6), 15, 19, (110, 40, 40, 255), OUT, 3)
        cv.ell((mx, my + 13), 9, 6, (230, 110, 110, 255))
    elif m == 'big':
        cv.poly([(mx - 26, my - 2), (mx + 26, my - 2), (mx + 17, my + 19), (mx, my + 26), (mx - 17, my + 19)], (110, 40, 40, 255), OUT, 3)
        cv.poly([(mx - 22, my), (mx + 22, my), (mx + 20, my + 8), (mx - 20, my + 8)], (255, 255, 255, 255))
    elif m == 'smile':
        cv.line([(mx - 22, my - 1), (mx - 11, my + 10), (mx, my + 13), (mx + 11, my + 10), (mx + 22, my - 1)], OUT, 5)
    elif m == 'content':
        cv.line([(mx - 15, my + 2), (mx - 6, my + 9), (mx + 6, my + 9), (mx + 15, my + 2)], OUT, 4)
    if t > 9.3:
        cv.ell(q(-38, 24), 13, 8, (230, 120, 110, 140))
        cv.ell(q(42, 24), 13, 8, (230, 120, 110, 140))

# ---------------------------------------------------------------- rover motion
def rover_state(t):
    if t < 3.0: return None
    gy = 830
    sx = sy = 1.0; rotd = 0.0; hop = 0.0; wheel_extra = 0.0
    LAND = 980
    mirror = K(t, [(3.0, -1), (4.5, -1), (4.95, 1), (9.0, 1), (9.35, -1), (9.9, -1), (10.25, 1), (16, 1)])
    if t < 3.9:
        u = (t - 3.0) / 0.9
        x = lerp(2350, LAND, u); hop = 300 * 4 * u * (1 - u); rotd = -10 * (1 - u)
        wheel_extra = t * 700
    elif t < 4.5:
        u = (t - 3.9) / 0.6
        x = LAND
        if u < 0.2: sx, sy = lerp(1.0, 1.22, u / 0.2), lerp(1.0, 0.74, u / 0.2)
        elif u < 0.45: v = (u - 0.2) / 0.25; sx, sy = lerp(1.22, 0.94, sm(v)), lerp(0.74, 1.1, sm(v))
        else: v = (u - 0.45) / 0.55; sx, sy = lerp(0.94, 1.0, sm(v)), lerp(1.1, 1.0, sm(v))
        hop = 36 * math.sin((u - 0.45) / 0.55 * math.pi) if u > 0.45 else 0
        wheel_extra = 3.9 * 700 + (t - 3.9) * 480
    else:
        x = K(t, [(4.5, LAND), (4.95, LAND), (8.0, 1500), (10.25, 1500), (16, 1640)])
    if 5.8 < t < 6.9: rotd += 3.0 * math.sin((t - 5.8) / 1.1 * math.pi)
    if 12.6 < t < 13.4: hop += 22 * abs(math.sin((t - 12.6) / 0.8 * math.pi))
    cam = 0.0
    if 4.95 <= t < 9.0: cam = 14 + 9 * math.sin((t - 4.95) * 2.2)
    elif 9.0 <= t < 10.25: cam = -14
    elif t >= 10.25: cam = 12 + 8 * math.sin((t - 10.25) * 1.7)
    if t >= 10.6: cam += 3 * math.sin(t * 9)
    if 13.4 < t < 14.6: cam = -22 * math.sin((t - 13.4) / 1.2 * math.pi)
    return dict(x=x, gy=gy - hop, mirror=mirror, sx=sx, sy=sy, rot=rotd, cam=cam,
                wheel=(x * 57.3 / 48.0) + wheel_extra, hop=hop)

def fx_layer(cv, t, rs, fx_pos):
    # dust puffs at landing
    for t0 in (3.9, 4.35):
        if t0 <= t < t0 + 0.8 and rs:
            u = (t - t0) / 0.8
            for i in range(6):
                dx = (i - 2.5) * 34 * (1 + u)
                cv.ell((rs['x'] + dx, 830 - 10 - 28 * u * (1 + i % 2)), 22 + 26 * u, 16 + 18 * u, (236, 224, 196, int(200 * (1 - u))))
    # landing sparkles
    if 3.9 <= t < 4.9 and rs:
        u = (t - 3.9) / 1.0
        for i, (dx, dy) in enumerate(((-120, -250), (110, -280), (170, -170))):
            r = 18 * math.sin(min(1, u * 1.2 + i * 0.1) * math.pi)
            if r > 1: star(cv, (rs['x'] + dx, 830 + dy), r, (255, 232, 130, 255), t * 90)
    # scan beam + sensor icons while working
    if rs and rs['mirror'] > 0.85 and (5.1 <= t < 8.9 or 10.4 <= t < 15.0):
        T, CH = rs['T'], rs['CH']
        lens = CH((24, 0))
        dirx = 1
        sweep = math.sin(t * 2.6) * 0.22
        tip1 = (lens[0] + dirx * 300, lens[1] + 70 + 70 * sweep - 40)
        tip2 = (lens[0] + dirx * 330, lens[1] + 70 + 70 * sweep + 70)
        cv.poly([lens, tip1, tip2], (120, 230, 240, 70))
        cv.line([lens, ((tip1[0] + tip2[0]) / 2, (tip1[1] + tip2[1]) / 2)], (150, 240, 250, 150), 3)
        # sensor symbols (no readings)
        base = (rs['x'] - dirx * 10, 830 - 360)
        names = ['thermo', 'drop', 'leaf']
        i = int(t * 1.3) % 3
        a = abs(math.sin(((t * 1.3) % 1) * math.pi))
        ic = (base[0] + (i - 1) * 62, base[1] - 20 * (1 - a))
        al = int(255 * min(1, a * 1.6))
        cv.ell(ic, 25, 25, (255, 255, 255, int(al * 0.92)), (22, 132, 134, al), 3)
        if names[i] == 'thermo':
            cv.line([(ic[0], ic[1] - 12), (ic[0], ic[1] + 6)], (22, 132, 134, al), 5)
            cv.ell((ic[0], ic[1] + 10), 8, 8, (22, 132, 134, al))
        elif names[i] == 'drop':
            cv.poly([(ic[0], ic[1] - 15), (ic[0] + 10, ic[1] + 3), (ic[0], ic[1] + 12), (ic[0] - 10, ic[1] + 3)], (46, 150, 220, al))
        else:
            cv.poly(epoly((ic[0], ic[1]), 8, 14, 35, 16), (60, 170, 80, al))
        # wifi arcs near the antenna
        ant = T((-74, -250))
        n = int(t * 2.2) % 4
        for j in range(1, 4):
            if j <= n:
                r = 14 + j * 12
                cv.d.arc([(ant[0] - r) * SS, (ant[1] - 18 - r) * SS, (ant[0] + r) * SS, (ant[1] - 18 + r) * SS], 230, 310,
                         fill=(22, 132, 134, 230), width=4 * SS)
    # surprise / thumbs-up sparkles around rover
    if 9.45 <= t < 10.4 and rs:
        u = (t - 9.45) / 0.9
        for i, (dx, dy) in enumerate(((-150, -200), (140, -240), (60, -330))):
            r = 20 * math.sin(min(1, u + i * 0.08) * math.pi)
            if r > 1: star(cv, (rs['x'] + dx, 830 + dy), r, (255, 232, 130, 255), t * 70)
    # chai sparkle on first sip
    if 11.05 <= t < 11.8 and fx_pos:
        u = (t - 11.05) / 0.75
        r = 17 * math.sin(u * math.pi)
        star(cv, (fx_pos[0] + 22, fx_pos[1] - 40), r, (255, 240, 160, 255), t * 120)
        star(cv, (fx_pos[0] - 18, fx_pos[1] - 62), r * 0.6, (255, 255, 255, 255), -t * 100)

def farmer_fx(cv, t, hc, hd, P):
    # sweat drop + stress mark + sigh puff (scene 1)
    if 0.8 < t < 3.3:
        a = int(255 * min(1, (t - 0.8) / 0.4, max(0, (3.3 - t) / 0.4)))
        fall = ((t * 1.3) % 1.0) * 30
        x, y = hc[0] + 62, hc[1] - 30 + fall
        cv.poly([(x, y - 18), (x + 11, y + 4), (x, y + 14), (x - 11, y + 4)], (110, 190, 245, a), OUT, 2)
    if 2.75 < t < 3.6:
        u = ob((t - 2.75) / 0.25)
        x, y = hc[0] + 78, hc[1] - 86
        s = 26 * u
        for ang in (0, 90):
            a = math.radians(ang + 45)
            cv.line([(x - math.cos(a) * s, y - math.sin(a) * s), (x + math.cos(a) * s, y + math.sin(a) * s)], (214, 44, 44, 255), 8)
    if 1.95 < t < 2.6:
        u = (t - 1.95) / 0.65
        for i in range(3):
            cv.ell((hc[0] + 70 + i * 28 * u + 10, hc[1] + 46 - i * 6 * u), 14 + i * 7, 11 + i * 5, (255, 255, 255, int(190 * (1 - u))))
    # surprise burst marks
    if 8.0 < t < 8.5:
        u = (t - 8.0) / 0.5
        for i in range(5):
            a = math.radians(-70 + i * 35 - 90 + 90)
            p0 = (hc[0] + math.cos(a) * 80, hc[1] - 60 + math.sin(a) * 30 - 30)
            cv.line([p0, (p0[0] + math.cos(a) * 24, p0[1] - 22 * u)], (232, 168, 38, 255), 6)

# ---------------------------------------------------------------- scene assembly
FX0, FGY = 560, 960

def draw_scene(t):
    cv = Cv()
    cv.im.alpha_composite(background())
    sun(cv, t)
    clouds(cv, t)
    rs = rover_state(t)
    for i in range(0, 4): field_row(cv, i, t)
    rinfo = None
    if rs:
        T, CH = rover_draw(cv, rs['x'], rs['gy'], t, rs['mirror'], 1.25, rs['sx'], rs['sy'], rs['rot'], rs['wheel'], rs['cam'])
        rs['T'], rs['CH'] = T, CH
    field_row(cv, 4, t)
    P, hd, S, hc = farmer_draw(cv, t, FX0, FGY)
    # hero plant the farmer examines
    plant(cv, FX0 + 175, FGY + 6, 1.15, t, 1.0, 0.4, hero=True)
    field_row(cv, 5, t, skip=(FX0 - 260, FX0 + 380))
    farmer_fx(cv, t, hc, hd, P)
    fx_layer(cv, t, rs, hd)
    phone_signals(cv, t, hd, rs)
    img = cv.im
    # camera zoom (scene 1 exhaustion emphasis)
    z = K(t, [(0, 1.0), (3.0, 1.075), (4.4, 1.0), (16, 1.0)])
    if z > 1.001:
        cx, cy = FX0 + 60, 640
        cw, ch = W * SS / z, H * SS / z
        x0 = min(max(cx * SS - cw / 2, 0), W * SS - cw); y0 = min(max(cy * SS - ch / 2, 0), H * SS - ch)
        img = img.crop((int(x0), int(y0), int(x0 + cw), int(y0 + ch)))
    img = img.resize((W, H), Image.LANCZOS)
    return img

def title_layer(img, t):
    if t < 12.1: return img
    cv = Cv.__new__(Cv)
    cv.im = Image.new('RGBA', (W * SS, H * SS), (0, 0, 0, 0)); cv.d = ImageDraw.Draw(cv.im, 'RGBA')
    cx = 1215
    a = int(160 * sm((t - 12.1) / 0.5))
    cv.rr(cx - 520, 18, 1040, 488, 38, (255, 255, 255, a), None)
    u1 = sm((t - 12.2) / 0.6)
    cv.text((cx, 26 + (1 - u1) * 40), 'AgriVision', font(150), (31, 94, 59, int(255 * u1)), 'ma')
    u2 = sm((t - 12.9) / 0.6)
    cv.text((cx, 236), 'Smarter Field Monitoring. Better Farming Decisions.', font(39, False), (20, 80, 90, int(255 * u2)), 'ma')
    u3 = ob((t - 13.5) / 0.55)
    if t >= 13.5:
        sc = max(0.05, u3)
        cv.text((cx, 296 + (1 - min(1, sc)) * 70), 'THANK YOU!', font(112 * min(1.0, sc) + 1), (200, 130, 16, 255), 'ma')
    u4 = sm((t - 14.2) / 0.6)
    cv.text((cx, 452), 'Questions & Discussion', font(34, False), (60, 80, 70, int(255 * u4)), 'ma')
    out = cv.im.resize((W, H), Image.LANCZOS)
    base = img.convert('RGBA'); base.alpha_composite(out)
    return base

def frame(t):
    return title_layer(draw_scene(t), t).convert('RGB')

if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'preview':
        outdir = sys.argv[2]
        for t in [float(x) for x in sys.argv[3:]]:
            frame(t).save(f'{outdir}/f_{t:05.2f}.png')
    elif mode == 'render':
        import cv2
        outp = sys.argv[2]
        vw = cv2.VideoWriter(outp, cv2.VideoWriter_fourcc(*'avc1'), FPS, (W, H))
        n = int(DUR * FPS)
        for i in range(n):
            f = frame(min(i / FPS, DUR))
            vw.write(cv2.cvtColor(np.array(f), cv2.COLOR_RGB2BGR))
            if i % 30 == 0: print(i, '/', n, flush=True)
        vw.release()
        print('done')
