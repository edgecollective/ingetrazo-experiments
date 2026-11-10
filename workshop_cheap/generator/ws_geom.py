"""Cheapest viable workshop roof: a lean-to beside the shipping container,
Suntuf polycarbonate on recycled-2x4 trusses, posts on ballast bases.
Pure Python (math only).  Inches, Z up.  Container at x 0..96, y 0..240.
Workshop: outside of posts x 102..230, y 0..240; roof slopes down toward +x
at 1-1/2:12 (Suntuf's minimum)."""
import math

SL = 1.5 / 12.0
TCD = 3.5 * math.sqrt(1 + SL * SL)          # vertical depth of the sloped top chord
XH0, XH1, XL0, XL1 = 102.0, 105.5, 226.5, 230.0
ZPAD, ZBC, ZBCT = 14.0, 84.0, 87.5           # pad top, bottom chord underside / top
YC = [1.5, 60.75, 120.0, 179.25, 238.5]      # bent centre lines
TX0, TX1 = 94.0, 236.0                       # top chord ends (8 in over the container, 6 in eave)
OSB = 0.4375
MODE = 'strapped'

COL = {'strap': (0.95, 0.55, 0.10, 1.0), 'dark': (0.18, 0.20, 0.22, 1.0), 'container': (0.42, 0.50, 0.56, 1.0), 'concrete': (0.72, 0.71, 0.68, 1.0), 'spf': (0.90, 0.78, 0.57, 1.0),
       'spf2': (0.84, 0.71, 0.50, 1.0), 'osb': (0.80, 0.66, 0.42, 1.0), 'panel': (0.86, 0.94, 1.0, 1.0)}
SYSTEMS = [('Shipping container (existing)', 'Container'), ('Ballast bases', 'Bases'),
           ('Posts and bracing', 'Posts and bracing'), ('Trusses', 'Trusses'), ('Purlins', 'Purlins'),
           ('Suntuf roof panels', 'Roof panels')]

items = []


def add(sys_, name, color, kind, data, lumber=None, opacity=None):
    items.append(dict(sys=sys_, name=name, color=color, kind=kind, data=data, lumber=lumber, opacity=opacity))


def B(sys_, name, color, b, lumber=None, opacity=None):
    x0, x1, y0, y1, z0, z1 = b
    assert x1 > x0 and y1 > y0 and z1 > z0, (name, b)
    add(sys_, name, color, 'box', tuple(float(c) for c in b), lumber, opacity)


def xzp(sys_, name, color, prof, y0, y1, lumber=None):
    add(sys_, name, color, 'prism', ([(x, y0, z) for x, z in prof], (0.0, y1 - y0, 0.0), []), lumber)


def yzp(sys_, name, color, prof, x0, x1, lumber=None):
    add(sys_, name, color, 'prism', ([(x0, y, z) for y, z in prof], (x1 - x0, 0.0, 0.0), []), lumber)


def zb(x):
    """Underside of the top chord."""
    return 91.0 + (XL1 - x) * SL


def zt(x):
    return zb(x) + TCD


def band(p1, p2, w):
    dx, dy = p2[0] - p1[0], p2[1] - p1[1]
    L = math.hypot(dx, dy); nx, ny = -dy / L * w / 2, dx / L * w / 2
    return [(p1[0] - nx, p1[1] - ny), (p2[0] - nx, p2[1] - ny), (p2[0] + nx, p2[1] + ny), (p1[0] + nx, p1[1] + ny)]


def bent(yc):
    T, P = 'Trusses', 'Posts and bracing'
    y0, y1 = yc - 0.75, yc + 0.75
    if MODE == 'ballast':
        for x0, x1 in ((98.0, 122.0), (XL1 - 13.75, XL1 + 10.25)):
            B('Ballast bases', 'Ballast base 24x24x14 in (about 680 lb)', 'concrete',
              (x0, x1, yc - 12.0, yc + 12.0, 0.0, ZPAD))
    else:
        for x0, x1 in ((97.0, 113.0), (XL0 - 6.25, XL1 + 6.25)):
            B('Bearing pads', 'Bearing pad: 16 x 16 in paver or flat stone', 'concrete',
              (x0, x1, yc - 8.0, yc + 8.0, 0.0, ZPAD))
    for xa, xb in ((XH0, XH1), (XL0, XL1)):
        for ya, yb in ((yc - 1.5, yc), (yc, yc + 1.5)):
            B(P, 'Post ply 2x4 (doubled post)', 'spf', (xa, xb, ya, yb, ZPAD, ZBC), lumber=[ZBC - ZPAD])
    # chords
    for a, b in ((XH0, 198.0), (198.0, XL1)):
        B(T, 'Bottom chord 2x4', 'spf', (a, b, y0, y1, ZBC, ZBCT), lumber=[b - a])
    for a, b in ((TX0, 166.0), (166.0, TX1)):
        xzp(T, 'Top chord 2x4', 'spf', [(a, zb(a)), (b, zb(b)), (b, zt(b)), (a, zt(a))], y0, y1,
            lumber=[(b - a) * math.sqrt(1 + SL * SL)])
    # verticals
    for c in (103.75, 134.0, 166.0, 198.0, 228.25):
        a, b = c - 1.75, c + 1.75
        xzp(T, 'Web 2x4 (vertical)', 'spf2', [(a, ZBCT), (b, ZBCT), (b, zb(b)), (a, zb(a))], y0, y1,
            lumber=[zb(a) - ZBCT])
    # diagonals (Pratt), the shallow heel panel gets an OSB web instead
    for L, R, down_right in ((105.5, 132.25, True), (135.75, 164.25, True), (167.75, 196.25, False)):
        h = zb((L + R) / 2) - ZBCT
        wh = 3.5 * math.hypot(h, R - L) / h
        if down_right:
            prof = [(R - wh, ZBCT), (R, ZBCT), (L + wh, zb(L + wh)), (L, zb(L))]
        else:
            prof = [(L, ZBCT), (L + wh, ZBCT), (R, zb(R)), (R - wh, zb(R - wh))]
        xzp(T, 'Web 2x4 (diagonal)', 'spf2', prof, y0, y1, lumber=[math.hypot(h, R - L) + 4])
    # OSB gussets both faces
    for a, b in ((XH0, 110.75), (127.0, 141.0), (159.0, 173.0), (192.0, XL1)):
        nm = 'OSB heel web plate 7/16 in' if a == 192.0 else 'OSB gusset 7/16 in'
        for ga, gb in ((y1, y1 + OSB), (y0 - OSB, y0)):
            xzp(T, nm, 'osb', [(a, ZBC), (b, ZBC), (b, zt(b)), (a, zt(a))], ga, gb)
    # knee braces in the bent, 24 in legs
    d = 3.5 * math.sqrt(2)
    for xf, s in ((XH1, 1), (XL0, -1)):
        prof = [(xf, ZBC - 24.0), (xf, ZBC - 24.0 + d), (xf + s * (24.0 - d), ZBC), (xf + s * 24.0, ZBC)]
        xzp(P, 'Knee brace 2x4', 'spf2', prof, y0, y1, lumber=[24.0 * math.sqrt(2)])


def strap(name, p1, p2, w=2.0, t=0.08):
    d = [p2[i] - p1[i] for i in range(3)]
    L = math.sqrt(sum(c * c for c in d)); u = [c / L for c in d]
    ref = (0.0, 1.0, 0.0) if abs(u[1]) < 0.9 else (1.0, 0.0, 0.0)
    a = [u[1] * ref[2] - u[2] * ref[1], u[2] * ref[0] - u[0] * ref[2], u[0] * ref[1] - u[1] * ref[0]]
    la = math.sqrt(sum(c * c for c in a)); a = [c / la for c in a]
    b = [u[1] * a[2] - u[2] * a[1], u[2] * a[0] - u[0] * a[2], u[0] * a[1] - u[1] * a[0]]
    loop = [tuple(p1[i] + a[i] * sa * t / 2 + b[i] * sb * w / 2 for i in range(3))
            for sa, sb in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    add('Container tie-downs', name, 'strap', 'prism', (loop, tuple(d), []))


def build_all(mode=None):
    global MODE, YC, ZPAD, SYSTEMS
    MODE = mode or MODE
    if MODE == 'strapped':
        YC = [1.5, 80.0, 160.0, 238.5]          # frames on the corner castings and the forklift pockets
        ZPAD = 2.0
        SYSTEMS = [(('Bearing pads', 'Bases') if s_[0] == 'Ballast bases' else s_) for s_ in SYSTEMS
                   if s_[0] != 'Container tie-downs'] + [('Container tie-downs', 'Container tie-downs')]
    else:
        YC = [1.5, 60.75, 120.0, 179.25, 238.5]
        ZPAD = 14.0
    del items[:]
    B('Shipping container (existing)', 'Shipping container 8 x 20 ft (existing, not attached)', 'container',
      (0.0, 96.0, 0.0, 240.0, 0.0, 105.0))
    if MODE == 'strapped':
        for y0 in (0.0, 233.0):
            for z0 in (0.0, 100.5):
                B('Shipping container (existing)', 'Corner casting', 'dark', (89.0, 96.1, y0 - 0.1 if y0 < 1 else y0, y0 + 7.0 if y0 < 1 else 240.1, z0, z0 + 4.5 + (0.1 if z0 > 1 else 0.0)))
        for yc in (79.65, 160.35):
            B('Shipping container (existing)', 'Forklift pocket (check yours has them)', 'dark',
              (95.9, 96.05, yc - 7.0, yc + 7.0, 0.8, 5.8))
        for yc in YC:
            ya = 3.5 if yc < 10 else 236.5 if yc > 230 else (79.65 if yc < 120 else 160.35)
            strap('Ratchet strap: post down to ' + ('bottom corner casting' if yc < 10 or yc > 230 else 'forklift pocket'),
                  (101.9, yc, 46.0), (96.1, ya, 3.0))
            B('Container tie-downs', 'Bearing block 2x4: truss pushes on container wall', 'spf2',
              (96.05, XH0, yc - 1.75, yc + 1.75, ZBC, ZBCT), lumber=[6.0])
            if yc < 10 or yc > 230:
                strap('Ratchet strap: truss down to top corner casting', (97.0, yc, zt(97.0) + 0.1), (93.0, ya, 104.0))
    for yc in YC:
        bent(yc)
    # purlins blocked in between the trusses (Suntuf "integrated purlins"), 7 lines at about 23 in
    xs = [95.5 + k * (234.5 - 95.5) / 6 for k in range(7)]
    for x in xs:
        top = zt(x - 0.75)
        for i in range(len(YC) - 1):
            B('Purlins', 'Purlin 2x4 on edge', 'spf', (x - 0.75, x + 0.75, YC[i] + 1.25, YC[i + 1] - 1.25, top - 3.5, top),
              lumber=[YC[i + 1] - YC[i] - 2.5])
    P = 'Posts and bracing'
    # container side: one diagonal per bay on the outside face of the posts
    for i in range(len(YC) - 1):
        ya, yb = YC[i] + 1.5, YC[i + 1] - 1.5
        p1, p2 = ((ya, 16.0), (yb, 82.0)) if i % 2 == 0 else ((yb, 16.0), (ya, 82.0))
        yzp(P, 'Diagonal brace 2x4', 'spf2', band(p1, p2, 3.5), XH0 - 1.5, XH0, lumber=[96.0])
    # open side: eave strut on the post faces and longitudinal knee braces
    for a, b in ((0.0, 96.0), (96.0, 192.0), (192.0, 240.0)):
        B(P, 'Eave strut 2x4', 'spf2', (XL1, XL1 + 1.5, a, b, ZBC - 3.5, ZBC), lumber=[b - a])
    d = 3.5 * math.sqrt(2)
    for i, yc in enumerate(YC):
        for s in ((1,) if i == 0 else (-1,) if i == len(YC) - 1 else (1, -1)):
            yf = yc + s * 1.5
            zt_ = ZBC - 3.5
            prof = [(yf, zt_ - 24.0), (yf, zt_ - 24.0 + d), (yf + s * (24.0 - d), zt_), (yf + s * 24.0, zt_)]
            yzp(P, 'Knee brace 2x4 (lengthwise)', 'spf2', prof, XL1, XL1 + 1.5, lumber=[24.0 * math.sqrt(2)])
    # Suntuf panels: 26 in wide, 12 ft long, lapped one rib (23 in coverage), last one ripped
    run = 144.0 / math.sqrt(1 + SL * SL)
    xa = (TX0 + TX1) / 2 - run / 2
    za = zt(xa)
    vec = (run, 0.0, -run * SL)
    for i in range(11):
        y0 = -1.0 + 23.0 * i
        w = min(26.0, 241.0 - y0)
        dz = 0.06 * (i % 2)
        # flat envelope of the 5/8 in corrugation (the ribs only add clutter on screen)
        prof = [(y0, za + dz), (y0 + w, za + dz), (y0 + w, za + dz + 0.63), (y0, za + dz + 0.63)]
        loop = [(xa, yy, zz) for yy, zz in prof]
        add('Suntuf roof panels', 'Suntuf 26 in x 12 ft clear' + (' (ripped)' if w < 26.0 else ''), 'panel', 'prism',
            (loop, vec, []), None, 0.33)
    return items


def check():
    bx = [(i['sys'] + ':' + i['name'], i['data']) for i in items if i['kind'] == 'box']
    bad = []
    for i in range(len(bx)):
        for j in range(i + 1, len(bx)):
            a, b = bx[i][1], bx[j][1]
            if all(min(a[2 * k + 1], b[2 * k + 1]) - max(a[2 * k], b[2 * k]) > 0.05 for k in range(3)):
                bad.append((bx[i][0], bx[j][0]))
    return bad
