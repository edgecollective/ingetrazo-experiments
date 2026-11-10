"""Treehouse on an example oak, framed from Home Depot dimensional lumber.

Pure Python (math only): the same file drives IngeTrazo (run_python) and the
shopping list.  Inches, Z up.  Trunk at (0, 0).  Platform x -24..168,
y -72..72, deck surface 96 in (8 ft).  The porch wraps the trunk; the cabin
(three rooms) sits on x 48..168.
"""
import math

ZD = 96.0                                   # deck surface
S = 8.0 / 12.0                              # roof pitch 8:12
COS = 12.0 / math.hypot(12.0, 8.0)
RD = 5.5 / COS                              # 2x6 rafter, vertical depth
SH = 0.5 / COS                              # 1/2 in roof sheathing
MT = 0.35 / COS                             # metal panel
X0, X1, Y0, Y1 = -24.0, 168.0, -72.0, 72.0
CX = 48.0                                   # cabin front wall, outer face of framing
TOP = ZD + 72.0                             # wall top (6 ft walls)
BY = 54.0                                   # beam centre lines y = +-54
SIDING = 0.625

COL = {
    'pt': (0.66, 0.60, 0.44, 1.0), 'deck': (0.72, 0.60, 0.43, 1.0), 'spf': (0.90, 0.78, 0.57, 1.0),
    'siding': (0.58, 0.38, 0.24, 1.0), 'trim': (0.94, 0.91, 0.82, 1.0), 'roof': (0.27, 0.40, 0.31, 1.0),
    'roof2': (0.22, 0.33, 0.25, 1.0), 'ply': (0.88, 0.78, 0.60, 1.0), 'door': (0.66, 0.22, 0.17, 1.0),
    'glass': (0.70, 0.86, 0.96, 1.0), 'steel': (0.42, 0.43, 0.46, 1.0), 'concrete': (0.72, 0.71, 0.68, 1.0),
    'bark': (0.42, 0.32, 0.23, 1.0), 'leaf1': (0.33, 0.52, 0.23, 1.0), 'leaf2': (0.27, 0.45, 0.19, 1.0),
    'leaf3': (0.42, 0.60, 0.27, 1.0), 'grass': (0.56, 0.68, 0.40, 1.0), 'mattress': (0.52, 0.68, 0.86, 1.0),
    'cushion': (0.90, 0.58, 0.28, 1.0),
}

# system -> layer, in build order
SYSTEMS = [
    ('Footings and posts', 'Structure'), ('Tree attachment (TABs, header, knee braces)', 'Structure'),
    ('Beams', 'Structure'), ('Floor joists', 'Structure'), ('Decking', 'Deck and railing'),
    ('Porch railing', 'Deck and railing'), ('Ladder', 'Ladder and hatch'), ('Floor hatch', 'Ladder and hatch'),
    ('Wall framing', 'Framing'), ('Roof framing', 'Roof framing'), ('Siding and trim', 'Walls and siding'),
    ('Interior walls', 'Walls and siding'), ('Windows', 'Windows and door'), ('Door', 'Windows and door'),
    ('Roofing', 'Roof'), ('Furnishings', 'Furnishings'),
]

ACT = {'2x2': (1.5, 1.5), '2x4': (1.5, 3.5), '2x6': (1.5, 5.5), '2x8': (1.5, 7.25), '2x12': (1.5, 11.25),
       '4x4': (3.5, 3.5), '6x6': (5.5, 5.5), '1x4': (0.75, 3.5), '1x6': (0.75, 5.5)}

items = []


def add(sys_, name, color, kind, data, lumber=None, sub=None, opacity=None):
    items.append(dict(sys=sys_, name=name, color=color, kind=kind, data=data,
                      lumber=lumber, sub=sub, opacity=opacity))


def B(sys_, name, color, b, lumber=None, sub=None, opacity=None):
    x0, x1, y0, y1, z0, z1 = b
    assert x1 > x0 + 1e-6 and y1 > y0 + 1e-6 and z1 > z0 + 1e-6, (name, b)
    add(sys_, name, color, 'box', tuple(float(c) for c in b), lumber, sub, opacity)


def PR(sys_, name, color, loop, vec, holes=(), lumber=None, sub=None, opacity=None):
    add(sys_, name, color, 'prism', ([tuple(p) for p in loop], tuple(vec), [[tuple(p) for p in h] for h in holes]),
        lumber, sub, opacity)


def yz(loop, x0, x1):
    return [(x0, y, z) for y, z in loop], (x1 - x0, 0.0, 0.0)


def xz(loop, y0, y1):
    return [(x, y0, z) for x, z in loop], (0.0, y1 - y0, 0.0)


def band(p1, p2, w):
    """Rectangle of width w along the 2D segment p1->p2 (square-cut ends)."""
    dx, dy = p2[0] - p1[0], p2[1] - p1[1]
    L = math.hypot(dx, dy); nx, ny = -dy / L * w / 2, dx / L * w / 2
    return [(p1[0] - nx, p1[1] - ny), (p2[0] - nx, p2[1] - ny), (p2[0] + nx, p2[1] + ny), (p1[0] + nx, p1[1] + ny)]


def cyl(sys_, name, color, c, axis, r, z0, z1, seg=18, lumber=None, sub=None):
    loop = []
    for i in range(seg):
        a = 2 * math.pi * (i + 0.5) / seg
        u, v = r * math.cos(a), r * math.sin(a)
        loop.append({'z': (c[0] + u, c[1] + v, z0), 'x': (z0, c[0] + u, c[1] + v), 'y': (c[0] + u, z0, c[1] + v)}[axis])
    vec = {'z': (0, 0, z1 - z0), 'x': (z1 - z0, 0, 0), 'y': (0, z1 - z0, 0)}[axis]
    PR(sys_, name, color, loop, vec, lumber=lumber, sub=sub)


def zb(y):
    """Underside of the rafters (2x6, birdsmouth at the inside of the top plate)."""
    return TOP + (68.5 - abs(y)) * S


def zt(y):
    return zb(y) + RD


# ---------------------------------------------------------------- structure
def structure():
    for px in (96.0, 156.0):
        for py in (-BY, BY):
            cyl('Footings and posts', 'Concrete pier, 12 in tube', 'concrete', (px, py), 'z', 6.0, -6.0, 2.0, seg=20)
            B('Footings and posts', 'Post 6x6 PT', 'pt', (px - 2.75, px + 2.75, py - 2.75, py + 2.75, 2.0, 76.0),
              lumber=[('6x6', 74.0, 'PT')])
            # knee braces along the beam (4x4, 45 deg, 24 in legs)
            for sgn in ((-1, 1) if px == 96.0 else (-1,)):
                xf = px + sgn * 2.75
                L, d = 24.0, 3.5 * math.sqrt(2)
                prof = [(xf, 76.0 - L), (xf + sgn * L, 76.0), (xf + sgn * (L - d), 76.0), (xf, 76.0 - L + d)]
                lp, v = xz(prof, py - 1.75, py + 1.75)
                PR('Footings and posts', 'Knee brace 4x4 PT', 'pt', lp, v, lumber=[('4x4', L * math.sqrt(2), 'PT')])
        # cross bracing between the post pair, one diagonal on each face
        for face, (za, zb_) in ((px + 2.75, (12.0, 70.0)), (px - 2.75 - 1.5, (70.0, 12.0))):
            lp, v = yz(band((-BY - 2.75, za), (BY + 2.75, zb_), 5.5), face, face + 1.5)
            PR('Footings and posts', 'Cross brace 2x6 PT', 'pt', lp, v,
               lumber=[('2x6', math.hypot(2 * BY + 5.5, 58.0), 'PT')])

    # tree attachment: header on two TABs, V knee braces down to a third TAB
    B('Tree attachment (TABs, header, knee braces)', 'Tree header, 3 x 2x12 PT', 'pt',
      (18.0, 22.5, -60.0, 60.0, 64.75, 76.0), lumber=[('2x12', 120.0, 'PT')] * 3)
    for y in (-10.0, 10.0):
        cyl('Tree attachment (TABs, header, knee braces)', 'Treehouse attachment bolt (TAB) 1-1/4 in', 'steel',
            (y, 70.375), 'x', 1.0, 6.0, 18.0)
    cyl('Tree attachment (TABs, header, knee braces)', 'TAB for knee braces', 'steel', (0.0, 24.0), 'x', 1.0, 8.0, 18.5)
    B('Tree attachment (TABs, header, knee braces)', 'Brace bracket (steel)', 'steel', (18.5, 22.0, -4.0, 4.0, 19.0, 29.0))
    for sgn in (-1, 1):
        lp, v = yz(band((sgn * 2.5, 26.0), (sgn * 44.0, 64.75), 3.5), 18.5, 22.0)
        PR('Tree attachment (TABs, header, knee braces)', 'Header knee brace 4x4 PT', 'pt', lp, v,
           lumber=[('4x4', math.hypot(41.5, 38.75), 'PT')])

    for py in (-BY, BY):
        B('Beams', 'Beam, 2 x 2x12x16 PT', 'pt', (X0, X1, py - 1.5, py + 1.5, 76.0, 87.25),
          lumber=[('2x12', 192.0, 'PT')] * 2)

    # joists 2x8 on the beams, framed around the trunk and the hatch
    zj = (87.25, 94.5)
    for x in (-24.0, -17.5, -0.75, 16.0, 32.0, 48.0, 64.0, 80.0, 96.0, 112.0, 128.0, 144.0, 160.0, 166.5):
        segs = [(-70.5, -50.42), (16.5, 70.5)] if x == -0.75 else [(-70.5, 70.5)]
        nm = 'Trimmer joist 2x8 PT' if x in (-17.5, 16.0) else 'Joist 2x8 PT'
        for a, b in segs:
            B('Floor joists', nm, 'pt', (x, x + 1.5, a, b) + zj, lumber=[('2x8', b - a, 'PT')])
    for y in (-72.0, 70.5):
        B('Floor joists', 'Rim joist 2x8x16 PT', 'pt', (X0, X1, y, y + 1.5) + zj, lumber=[('2x8', 192.0, 'PT')])
    for a, nm in ((-50.42, 'Hatch header 2x8 PT'), (-26.1, 'Ladder header 2x8 PT'), (15.0, 'Trunk header 2x8 PT')):
        B('Floor joists', nm, 'pt', (-16.0, 16.0, a, a + 1.5) + zj, lumber=[('2x8', 32.0, 'PT')])
    for x in (-16.0, 14.5):
        B('Floor joists', 'Hatch ledger 2x2', 'pt', (x, x + 1.5, -48.92, -26.1, 93.0, 94.5),
          lumber=[('2x2', 22.8, 'PT')])


def decking():
    g = (144.0 - 25 * 5.5) / 24
    for k in range(25):
        y0 = -72.0 + k * (5.5 + g); y1 = y0 + 5.5
        if 4 <= k <= 7 or 10 <= k <= 14:
            segs = [(X0, -16.0), (16.0, X1)]
        else:
            segs = [(X0, X1)]
        for a, b in segs:
            B('Decking', 'Deck board 2x6 PT', 'deck', (a, b, y0, y1, 94.5, 96.0), lumber=[('2x6', b - a, 'PT')])
        if 4 <= k <= 7:
            B('Floor hatch', 'Hatch board 2x6 PT', 'deck', (-15.875, 15.875, y0, y1, 94.5, 96.0),
              lumber=[('2x6', 31.75, 'PT')], sub='hatch')
    for x in (-11.75, 8.25):
        B('Floor hatch', 'Hatch cleat 2x4 PT', 'pt', (x, x + 3.5, -48.6, -26.4, 93.0, 94.5),
          lumber=[('2x4', 22.2, 'PT')], sub='hatch')
    # grab handle beside the hatch
    for x in (-6.0, 6.0):
        cyl('Floor hatch', 'Grab handle (galvanized)', 'steel', (x, -23.0), 'z', 0.6, 96.0, 110.0)
    cyl('Floor hatch', 'Grab handle (galvanized)', 'steel', (-23.0, 110.0), 'x', 0.6, -6.6, 6.6)


def railing():
    zc = 132.0
    # (axis, post band lo/hi, rail band, baluster band, post positions along)
    spans = [('y', (-27.5, -24.0), (-25.5, -24.0), (-27.0, -25.5), [-75.5, -1.75, 72.0]),
             ('x', (72.0, 75.5), (72.0, 73.5), (73.5, 75.0), [-27.5, 42.5]),
             ('x', (-75.5, -72.0), (-73.5, -72.0), (-75.0, -73.5), [-27.5, 42.5])]

    def bb(ax, band, a, b):
        return (band[0], band[1], a, b) if ax == 'y' else (a, b, band[0], band[1])
    seen = set()
    for ax, pb, rb, bl, posts in spans:
        for p in posts:
            b = bb(ax, pb, p, p + 3.5)
            if b in seen:
                continue
            seen.add(b)
            B('Porch railing', 'Railing post 4x4 PT', 'pt', b + (87.25, zc), lumber=[('4x4', zc - 87.25, 'PT')])
        lo, hi = (posts[0] - 1.0 if ax == 'y' else -23.0), posts[-1] + 3.5 + (1.0 if ax == 'y' else 0.5)
        B('Porch railing', 'Rail cap 2x6 PT', 'pt', bb(ax, (pb[0] - 1.0, pb[1] + 1.0), lo, hi) + (zc, zc + 1.5),
          lumber=[('2x6', hi - lo, 'PT')])
        for i in range(len(posts) - 1):
            a, b = posts[i] + 3.5, posts[i + 1]
            for z0 in (98.0, 128.5):
                B('Porch railing', 'Rail 2x4 PT', 'pt', bb(ax, rb, a, b) + (z0, z0 + 3.5), lumber=[('2x4', b - a, 'PT')])
            n = int(math.ceil((b - a - 4.0) / 5.5))
            gap = (b - a - n * 1.5) / (n + 1)
            for j in range(n):
                s = a + gap + j * (1.5 + gap)
                B('Porch railing', 'Baluster 2x2x36', 'pt', bb(ax, bl, s, s + 1.5) + (97.0, zc),
                  lumber=[('2x2', 36.0, 'baluster')])


def ladder():
    a = math.radians(75.0)
    d = (math.cos(a), math.sin(a)); n = (-math.sin(a), math.cos(a))
    pb = (-26.1, 94.5)
    w = 5.5

    def at(base, z):
        t = (z - base[1]) / d[1]
        return (base[0] + t * d[0], z)
    pf = (pb[0] + w * n[0], pb[1] + w * n[1])
    top = 92.75
    prof = [at(pb, 0.0), at(pb, top), at(pf, top), at(pf, 0.0)]
    L = math.hypot(prof[1][0] - prof[0][0], top)
    for x0 in (-9.5, 8.0):
        lp, v = yz(prof, x0, x0 + 1.5)
        PR('Ladder', 'Ladder rail 2x6 PT', 'pt', lp, v, lumber=[('2x6', L, 'PT')])
    pc = (pb[0] + w / 2 * n[0], pb[1] + w / 2 * n[1])
    for k in range(1, 8):
        z = 12.0 * k
        yc = at(pc, z)[0]
        B('Ladder', 'Ladder tread 2x4 PT', 'pt', (-8.0, 8.0, yc - 1.75, yc + 1.75, z - 1.5, z),
          lumber=[('2x4', 16.0, 'PT')])


# ---------------------------------------------------------------- cabin
# openings: (c0, c1, sill_z, head_z)
WIN = dict(sill=ZD + 30.0, head=ZD + 54.0)
OPEN = {
    'front': [(-42.0, -18.0, WIN['sill'], WIN['head']), (24.0, 48.0, ZD, ZD + 54.0)],
    'back': [(-48.0, -24.0, WIN['sill'], WIN['head']), (24.0, 48.0, WIN['sill'], WIN['head'])],
    'left': [(66.0, 90.0, WIN['sill'], WIN['head']), (126.0, 150.0, WIN['sill'], WIN['head'])],
    'right': [(66.0, 90.0, WIN['sill'], WIN['head']), (124.0, 160.0, ZD + 24.0, WIN['head'])],
}
WALLS = {   # along-axis, extent, framing depth range
    'front': ('y', (-68.5, 68.5), (CX, CX + 3.5)),
    'back': ('y', (-68.5, 68.5), (X1 - 3.5, X1)),
    'left': ('x', (CX, X1), (-72.0, -68.5)),
    'right': ('x', (CX, X1), (68.5, 72.0)),
}


def frame_wall(key):
    ax, (a0, a1), (f0, f1) = WALLS[key]
    ops = OPEN[key]
    sysn = 'Wall framing'

    def put(s0, s1, z0, z1, nm, lum):
        if z1 - z0 < 0.5 or s1 - s0 < 0.1:
            return
        b = (s0, s1, f0, f1, z0, z1) if ax == 'x' else (f0, f1, s0, s1, z0, z1)
        B(sysn, nm, 'spf', b, lumber=lum)
    # bottom plate, cut at the door
    cuts = sorted((c0, c1) for c0, c1, s, h in ops if s <= ZD + 1e-6)
    p = a0
    for c0, c1 in cuts:
        put(p, c0 - 1.5, ZD, ZD + 1.5, 'Bottom plate 2x4 PT', [('2x4', c0 - 1.5 - p, 'PT')]); p = c1 + 1.5
    put(p, a1, ZD, ZD + 1.5, 'Bottom plate 2x4 PT', [('2x4', a1 - p, 'PT')])
    for z0 in (TOP - 3.0, TOP - 1.5):
        put(a0, a1, z0, z0 + 1.5, 'Top plate 2x4', [('2x4', a1 - a0, 'KD')])
    stud = ('2x4', TOP - 3.0 - ZD - 1.5, 'KD')
    pos = []
    p = a0
    while p < a1 - 1.5 - 1e-6:
        pos.append(p); p += 16.0
    pos.append(a1 - 1.5)
    for p in pos:
        hit = [o for o in ops if p + 1.5 > o[0] - 3.0 and p < o[1] + 3.0]
        if not hit:
            put(p, p + 1.5, ZD + 1.5, TOP - 3.0, 'Stud 2x4', [stud])
            continue
        c0, c1, s, h = hit[0]
        if p >= c0 and p + 1.5 <= c1:
            put(p, p + 1.5, h + 5.5, TOP - 3.0, 'Cripple 2x4', [('2x4', TOP - 3.0 - h - 5.5, 'KD')])
            if s > ZD + 1e-6:
                put(p, p + 1.5, ZD + 1.5, s - 1.5, 'Cripple 2x4', [('2x4', s - 1.5 - ZD - 1.5, 'KD')])
    for c0, c1, s, h in ops:
        for k0 in (c0 - 3.0, c1 + 1.5):
            put(k0, k0 + 1.5, ZD + 1.5, TOP - 3.0, 'King stud 2x4', [stud])
        for j0 in (c0 - 1.5, c1):
            put(j0, j0 + 1.5, ZD + (0.0 if s <= ZD + 1e-6 else 1.5), h, 'Jack stud 2x4', [('2x4', h - ZD, 'KD')])
        put(c0 - 1.5, c1 + 1.5, h, h + 5.5, 'Header 2 x 2x6', [('2x6', c1 - c0 + 3.0, 'KD')] * 2)
        if s > ZD + 1e-6:
            put(c0, c1, s - 1.5, s, 'Rough sill 2x4', [('2x4', c1 - c0, 'KD')])
    if key in ('front', 'back'):                      # gable studs up to the end rafter
        for p in pos[1:-1]:
            top = zb(max(abs(p), abs(p + 1.5)))
            if top - TOP > 3.0:
                put(p, p + 1.5, TOP, top, 'Gable stud 2x4', [('2x4', top - TOP, 'KD')])


def siding_and_trim():
    sysn = 'Siding and trim'
    zt_e = zt(72.0)
    # side walls: down over the rim joist
    for key, yo in (('left', -72.0 - SIDING), ('right', 72.0)):
        holes = [[(c0, s), (c1, s), (c1, h), (c0, h)] for c0, c1, s, h in OPEN[key]]
        lp, v = xz([(CX - SIDING, 87.25), (X1 + SIDING, 87.25), (X1 + SIDING, TOP), (CX - SIDING, TOP)], yo, yo + SIDING)
        PR(sysn, 'T1-11 siding 5/8 in', 'siding', lp, v, holes=[[(x, yo, z) for x, z in h] for h in holes])
    # gable ends: pentagon, front stops on the deck, back laps the rim
    for key, xo, zbot in (('front', CX - SIDING, ZD), ('back', X1, 87.25)):
        outline = [(-72.0, zbot)]
        holes = []
        for c0, c1, s, h in sorted(OPEN[key]):
            if s <= ZD + 1e-6 and key == 'front':
                outline += [(c0, zbot), (c0, h), (c1, h), (c1, zbot)]
            else:
                holes.append([(c0, s), (c1, s), (c1, h), (c0, h)])
        outline += [(72.0, zbot), (72.0, zt_e), (0.0, zt(0.0)), (-72.0, zt_e)]
        lp, v = yz(outline, xo, xo + SIDING)
        PR(sysn, 'T1-11 siding 5/8 in', 'siding', lp, v, holes=[[(xo, y, z) for y, z in h] for h in holes])
    # corner boards
    for xs, xe, zbot in ((CX - SIDING, CX - SIDING + 3.5, 87.25), (X1 + SIDING - 3.5, X1 + SIDING, 87.25)):
        for ys in ((-72.0 - SIDING - 0.75, -72.0 - SIDING), (72.0 + SIDING, 72.0 + SIDING + 0.75)):
            B(sysn, 'Corner board 1x4', 'trim', (xs, xe) + ys + (zbot, TOP), lumber=[('1x4', TOP - zbot, 'trim')])
    for x0, x1, zbot in ((CX - SIDING - 0.75, CX - SIDING, ZD), (X1 + SIDING, X1 + SIDING + 0.75, 87.25)):
        for y0, y1 in ((-72.0 - SIDING, -72.0 - SIDING + 3.5), (72.0 + SIDING - 3.5, 72.0 + SIDING)):
            B(sysn, 'Corner board 1x4', 'trim', (x0, x1, y0, y1, zbot, TOP), lumber=[('1x4', TOP - zbot, 'trim')])
    # window and door casing
    for key, ops in OPEN.items():
        for c0, c1, s, h in ops:
            door = s <= ZD + 1e-6
            pieces = [(c0 - 3.5, c1 + 3.5, h, h + 3.5)] + ([] if door else [(c0 - 3.5, c1 + 3.5, s - 3.5, s)])
            pieces += [(c0 - 3.5, c0, s, h), (c1, c1 + 3.5, s, h)]
            for a, b, z0, z1 in pieces:
                if key in ('left', 'right'):
                    yo = -72.0 - SIDING - 0.75 if key == 'left' else 72.0 + SIDING
                    bb = (a, b, yo, yo + 0.75, z0, z1)
                else:
                    xo = CX - SIDING - 0.75 if key == 'front' else X1 + SIDING
                    bb = (xo, xo + 0.75, a, b, z0, z1)
                B(sysn, 'Casing 1x4', 'trim', bb, lumber=[('1x4', max(b - a, z1 - z0), 'trim')])
    # glazing
    for key, ops in OPEN.items():
        for c0, c1, s, h in ops:
            if s <= ZD + 1e-6:
                continue
            if key in ('left', 'right'):
                yc = -70.25 if key == 'left' else 70.25
                bb = (c0, c1, yc - 0.125, yc + 0.125, s, h)
            else:
                xc = CX + 1.75 if key == 'front' else X1 - 1.75
                bb = (xc - 0.125, xc + 0.125, c0, c1, s, h)
            B('Windows', 'Acrylic window pane 1/4 in', 'glass', bb, opacity=0.35)
            # window stop strips inside the opening
            if key in ('left', 'right'):
                for zz in ((s, s + 0.75), (h - 0.75, h)):
                    B('Windows', 'Window stop 1x2', 'trim', (c0, c1, yc + 0.125, yc + 0.875) + zz)
            else:
                for zz in ((s, s + 0.75), (h - 0.75, h)):
                    B('Windows', 'Window stop 1x2', 'trim', (xc + 0.125, xc + 0.875, c0, c1) + zz)


def interior():
    out = [(-68.5, ZD), (-48.0, ZD), (-48.0, ZD + 60.0), (-26.0, ZD + 60.0), (-26.0, ZD), (26.0, ZD),
           (26.0, ZD + 60.0), (48.0, ZD + 60.0), (48.0, ZD), (68.5, ZD), (68.5, TOP), (-68.5, TOP)]
    lp, v = yz(out, 110.0, 114.0)
    PR('Interior walls', 'Interior wall: 2x4 frame, 1/4 in plywood both sides', 'ply', lp, v,
       lumber=[('2x4', 72.0, 'KD')] * 11 + [('2x4', 137.0, 'KD')] * 3)
    lp, v = xz([(114.0, ZD), (164.5, ZD), (164.5, TOP), (114.0, TOP)], -2.0, 2.0)
    hole = [(140.0, -2.0, ZD + 30.0), (152.0, -2.0, ZD + 30.0), (152.0, -2.0, ZD + 42.0), (140.0, -2.0, ZD + 42.0)]
    PR('Interior walls', 'Interior wall with pass-through: 2x4 frame, 1/4 in plywood both sides', 'ply', lp, v,
       holes=[hole], lumber=[('2x4', 72.0, 'KD')] * 5 + [('2x4', 50.5, 'KD')] * 3)
    # furnishings
    f = 'Furnishings'
    B(f, 'Bunk platform 3/4 in plywood', 'ply', (134.0, 164.5, -68.5, -2.0, ZD + 15.25, ZD + 16.0))
    for y0 in (-68.5, -3.5):
        B(f, 'Bunk rail 2x4', 'spf', (134.0, 164.5, y0, y0 + 1.5, ZD + 11.75, ZD + 15.25), lumber=[('2x4', 30.5, 'KD')])
    for y0 in (-68.5, -3.5):
        B(f, 'Bunk leg 2x4', 'spf', (134.0, 137.5, y0, y0 + 1.5, ZD, ZD + 11.75), lumber=[('2x4', 11.75, 'KD')])
    B(f, 'Mattress (kid size)', 'mattress', (135.0, 164.0, -67.5, -3.0, ZD + 16.0, ZD + 20.0))
    B(f, 'Window-seat bench 3/4 in plywood', 'ply', (148.0, 164.5, 2.0, 68.5, ZD + 15.25, ZD + 16.0))
    B(f, 'Bench front 3/4 in plywood', 'ply', (148.0, 148.75, 2.0, 68.5, ZD, ZD + 15.25))
    B(f, 'Bench cushion', 'cushion', (148.5, 164.0, 2.5, 68.0, ZD + 16.0, ZD + 19.0))
    B(f, 'Table top 3/4 in plywood', 'ply', (70.0, 94.0, 40.0, 68.0, ZD + 27.25, ZD + 28.0))
    for x0 in (71.0, 91.5):
        for y0 in (41.0, 65.5):
            B(f, 'Table leg 2x2', 'spf', (x0, x0 + 1.5, y0, y0 + 1.5, ZD, ZD + 27.25), lumber=[('2x2', 27.25, 'KD')])


def door():
    # plank door 23-1/2 x 53-1/2, outswing; Z brace inside
    y0, y1, z0, z1 = 24.25, 47.75, ZD + 0.25, ZD + 53.75
    w = (y1 - y0) / 4
    for i in range(4):
        B('Door', 'Door plank 1x6', 'door', (CX, CX + 0.75, y0 + i * w + 0.03, y0 + (i + 1) * w - 0.03, z0, z1),
          lumber=[('1x6', z1 - z0, 'trim')], sub='door')
    for zz in (z0 + 5.0, z1 - 8.5):
        B('Door', 'Door brace 1x4', 'door', (CX + 0.75, CX + 1.5, y0 + 1.0, y1 - 1.0, zz, zz + 3.5),
          lumber=[('1x4', y1 - y0 - 2.0, 'trim')], sub='door')
    lp, v = yz(band((y1 - 2.5, z0 + 8.5), (y0 + 2.5, z1 - 8.5), 3.5), CX + 0.75, CX + 1.5)
    PR('Door', 'Door brace 1x4', 'door', lp, v, lumber=[('1x4', 44.0, 'trim')], sub='door')
    cyl('Door', 'Door pull', 'steel', (y0 + 3.0, ZD + 30.0), 'x', 0.5, CX - 3.0, CX)
    for zz in (z0 + 6.0, z1 - 10.0):
        B('Door', 'T-hinge strap', 'steel', (CX - 0.1, CX, y1 - 9.0, y1, zz, zz + 1.25), sub='door')


def roof():
    fr, rf = 'Roof framing', 'Roofing'
    for x in (36.0, 48.0, 72.0, 96.0, 120.0, 144.0, 166.5, 178.5):
        nm = 'Barge rafter 2x6' if x in (36.0, 178.5) else 'Rafter 2x6'
        for sg in (1, -1):
            prof = [(0.75, zb(0.75)), (68.5, TOP), (72.0, TOP), (72.0, zb(72.0)), (84.0, zb(84.0)),
                    (84.0, zt(84.0)), (0.75, zt(0.75))]
            lp, v = yz([(sg * y, z) for y, z in prof], x, x + 1.5)
            PR(fr, nm, 'spf', lp, v, lumber=[('2x6', (84.0 - 0.75) / COS, 'KD')])
    for x in (72.0, 96.0, 120.0, 144.0):
        zc = ZD + 96.0
        half = 68.5 - (zc + 3.5 - TOP) / S
        B(fr, 'Collar tie 2x4', 'spf', (x + 1.5, x + 3.0, -half, half, zc, zc + 3.5), lumber=[('2x4', 2 * half, 'KD')])
    B(fr, 'Ridge board 2x8', 'spf', (36.0, 180.0, -0.75, 0.75, zt(0.75) - 7.25, zt(0.75)), lumber=[('2x8', 144.0, 'KD')])
    for sg in (1, -1):
        y0 = 84.0 if sg > 0 else -84.75
        B(rf, 'Fascia 1x6', 'trim', (36.0, 180.0, y0, y0 + 0.75, zt(84.0) - 5.5, zt(84.0)), lumber=[('1x6', 144.0, 'trim')])
    rake = [(-84.75, zt(84.75)), (0.0, zt(0.0)), (84.75, zt(84.75)), (84.75, zt(84.75) - RD),
            (0.0, zt(0.0) - RD), (-84.75, zt(84.75) - RD)]
    for x0 in (35.25, 180.0):
        lp, v = yz(rake, x0, x0 + 0.75)
        PR(rf, 'Rake board 1x6', 'trim', lp, v, lumber=[('1x6', 102.0, 'trim')] * 2)
    for sg in (1, -1):
        sheath = [(0.0, zt(0.0)), (sg * 84.75, zt(84.75)), (sg * 84.75, zt(84.75) + SH), (0.0, zt(0.0) + SH)]
        lp, v = yz(sheath, 35.25, 180.75)
        PR(rf, 'Roof sheathing 1/2 in plywood', 'ply', lp, v)
        top = lambda y: zt(y) + SH
        metal = [(0.0, top(0.0)), (sg * 85.75, top(85.75)), (sg * 85.75, top(85.75) + MT), (0.0, top(0.0) + MT)]
        lp, v = yz(metal, 34.5, 181.5)
        PR(rf, 'Metal roof panel (corrugated)', 'roof', lp, v)
        x = 36.0
        while x < 181.0:
            rib = [(sg * 1.0, top(1.0) + MT), (sg * 85.5, top(85.5) + MT), (sg * 85.5, top(85.5) + MT + 0.45),
                   (sg * 1.0, top(1.0) + MT + 0.45)]
            lp, v = yz(rib, x, x + 0.75)
            PR(rf, 'Panel rib', 'roof', lp, v)
            x += 9.0
    t = lambda y: zt(y) + SH + MT
    cap = [(-8.0, t(8.0) + 0.45), (0.0, t(0.0) + 1.0), (8.0, t(8.0) + 0.45), (8.0, t(8.0) + 0.8),
           (0.0, t(0.0) + 1.35), (-8.0, t(8.0) + 0.8)]
    lp, v = yz(cap, 34.5, 181.5)
    PR(rf, 'Ridge cap', 'roof2', lp, v)


# ---------------------------------------------------------------- the tree
def _basis(d):
    L = math.sqrt(sum(c * c for c in d)); d = [c / L for c in d]
    ref = (0, 0, 1.0) if abs(d[2]) < 0.9 else (1.0, 0, 0)
    u = [d[1] * ref[2] - d[2] * ref[1], d[2] * ref[0] - d[0] * ref[2], d[0] * ref[1] - d[1] * ref[0]]
    lu = math.sqrt(sum(c * c for c in u)); u = [c / lu for c in u]
    w = [d[1] * u[2] - d[2] * u[1], d[2] * u[0] - d[0] * u[2], d[0] * u[1] - d[1] * u[0]]
    return d, u, w


def rings_mesh(rings, seg, cap0=True, cap1=True):
    """rings: list of (centre, axis, radius, wobble fn(theta) or None) -> faces."""
    pts = []
    for c, ax, r, wob in rings:
        _, u, w = _basis(ax)
        ring = []
        for i in range(seg):
            a = 2 * math.pi * i / seg
            rr = r * (wob(a) if wob else 1.0)
            ring.append(tuple(c[k] + rr * (math.cos(a) * u[k] + math.sin(a) * w[k]) for k in range(3)))
        pts.append(ring)
    faces = []
    for j in range(len(pts) - 1):
        a, b = pts[j], pts[j + 1]
        for i in range(seg):
            i2 = (i + 1) % seg
            faces.append([a[i], a[i2], b[i2], b[i]])
    if cap0:
        faces.append(list(reversed(pts[0])))
    if cap1:
        faces.append(list(pts[-1]))
    return faces


def limb(p0, p1, r0, r1, seg=10, bend=(0, 0, 0)):
    n = 4
    rings = []
    d = [p1[k] - p0[k] for k in range(3)]
    for i in range(n + 1):
        t = i / n
        c = [p0[k] + d[k] * t + bend[k] * math.sin(math.pi * t) for k in range(3)]
        rings.append((c, d, r0 + (r1 - r0) * t, None))
    return rings_mesh(rings, seg)


_ICO = None


def _icosphere(level=2):
    global _ICO
    if _ICO:
        return _ICO
    t = (1 + 5 ** 0.5) / 2
    v = [(-1, t, 0), (1, t, 0), (-1, -t, 0), (1, -t, 0), (0, -1, t), (0, 1, t), (0, -1, -t), (0, 1, -t),
         (t, 0, -1), (t, 0, 1), (-t, 0, -1), (-t, 0, 1)]
    v = [tuple(c / math.sqrt(sum(k * k for k in p)) for c in p) for p in v]
    f = [(0, 11, 5), (0, 5, 1), (0, 1, 7), (0, 7, 10), (0, 10, 11), (1, 5, 9), (5, 11, 4), (11, 10, 2), (10, 7, 6),
         (7, 1, 8), (3, 9, 4), (3, 4, 2), (3, 2, 6), (3, 6, 8), (3, 8, 9), (4, 9, 5), (2, 4, 11), (6, 2, 10),
         (8, 6, 7), (9, 8, 1)]
    for _ in range(level):
        cache, nf = {}, []

        def mid(i, j):
            k = (min(i, j), max(i, j))
            if k not in cache:
                p = [(v[i][n] + v[j][n]) / 2 for n in range(3)]
                L = math.sqrt(sum(c * c for c in p))
                v.append(tuple(c / L for c in p)); cache[k] = len(v) - 1
            return cache[k]
        for a_, b_, c_ in f:
            ab, bc, ca = mid(a_, b_), mid(b_, c_), mid(c_, a_)
            nf += [(a_, ab, ca), (b_, bc, ab), (c_, ca, bc), (ab, bc, ca)]
        f = nf
    _ICO = (v, f)
    return _ICO


def blob(c, R, seed):
    v, f = _icosphere(2)
    pts = []
    for x, y, z in v:
        k = 1 + 0.11 * math.sin(3.1 * x + seed) * math.sin(2.7 * y + 2 * seed) + 0.07 * math.sin(4.3 * z + 3 * seed)
        pts.append((c[0] + R * k * x, c[1] + R * k * y, c[2] + 0.84 * R * k * z))
    return [[pts[a_], pts[b_], pts[c_]] for a_, b_, c_ in f]


def cluster(c, R, seed):
    pat = [(0.0, 0.0, 0.18, 0.70), (0.52, 0.18, -0.08, 0.58), (-0.46, 0.30, 0.0, 0.60),
           (0.06, -0.52, -0.04, 0.58), (-0.22, -0.16, 0.48, 0.52), (0.30, 0.40, 0.40, 0.48)]
    ca, sa = math.cos(seed), math.sin(seed)
    faces = []
    for i, (dx, dy, dz, rr) in enumerate(pat):
        ox, oy = dx * ca - dy * sa, dx * sa + dy * ca
        faces += blob((c[0] + ox * R, c[1] + oy * R, c[2] + dz * R), rr * R, seed + 0.9 * i)
    return faces


TREE = []     # (name, color, faces, layer)


def tree():
    zs = [(0, 22.0), (5, 17.5), (16, 15.2), (40, 13.6), (96, 12.5), (140, 11.8), (180, 11.0), (200, 10.2)]
    rings = []
    for z, r in zs:
        cx = -0.05 * max(0.0, z - 120.0)
        fl = max(0.0, 1.0 - z / 20.0)
        wob = (lambda a, fl=fl: 1 + 0.16 * fl * math.cos(5 * a + 0.4) + 0.03 * math.sin(3 * a))
        rings.append(((cx, 0.0, float(z)), (0, 0, 1.0), r, wob))
    TREE.append(('Trunk (white oak, about 25 in)', 'bark', rings_mesh(rings, 18, cap0=True, cap1=True), 'Tree'))
    limbs = [((-4, 2, 176), (-72, 46, 318), 8.0, 3.5, (0, 0, 14)), ((-4, -3, 178), (-42, -76, 308), 7.0, 3.0, (0, 0, 12)),
             ((0, 1, 186), (96, 24, 338), 7.5, 3.2, (0, 0, 16)), ((-5, 1, 192), (6, -8, 420), 9.0, 3.0, (8, 0, 0)),
             ((-9, 2, 150), (-116, -26, 228), 6.0, 2.4, (0, 0, 10)),
             ((62, 16, 300), (122, -42, 332), 3.4, 1.4, (0, 0, 6)), ((-52, 34, 290), (-22, 92, 332), 3.0, 1.4, (0, 0, 6)),
             ((-32, -60, 285), (-92, -84, 330), 3.0, 1.3, (0, 0, 6))]
    for i, (a, b, r0, r1, bend) in enumerate(limbs):
        TREE.append(('Limb %d' % (i + 1), 'bark', limb(a, b, r0, r1, bend=bend), 'Tree'))
    blobs = [((-76, 48, 336), 48), ((-44, -80, 326), 44), ((100, 28, 352), 46), ((8, -10, 428), 50),
             ((-120, -28, 242), 34), ((126, -46, 342), 34), ((-22, 96, 342), 36), ((-96, -86, 336), 32),
             ((40, 50, 398), 42), ((-40, 0, 398), 46), ((62, -56, 388), 38), ((-110, 40, 290), 30)]
    for i, (c, R) in enumerate(blobs):
        TREE.append(('Canopy %d' % (i + 1), ('leaf1', 'leaf2', 'leaf3')[i % 3], cluster(c, R, 1.3 * i + 0.5), 'Tree canopy'))
    g = []
    seg = 40
    for i in range(seg):
        a0, a1 = 2 * math.pi * i / seg, 2 * math.pi * (i + 1) / seg
        g.append([(0.0, 0.0, -0.25), (300 * math.cos(a0), 300 * math.sin(a0), -0.25),
                  (300 * math.cos(a1), 300 * math.sin(a1), -0.25)])
    TREE.append(('Ground (25 ft radius)', 'grass', g, 'Ground'))


def build_all():
    del items[:]
    del TREE[:]
    structure(); decking(); railing(); ladder()
    for k in ('front', 'back', 'left', 'right'):
        frame_wall(k)
    siding_and_trim(); interior(); door(); roof(); tree()
    return items, TREE


MOVES = {'hatch': ('rx', (-48.92, ZD), 100.0), 'door': ('rz', (CX, 47.75), -70.0)}


def boxes_overlap(a, b, tol=0.05):
    return all(min(a[2 * k + 1], b[2 * k + 1]) - max(a[2 * k], b[2 * k]) > tol for k in range(3))


def check():
    """Overlapping box solids (prisms skipped): a quick framing clash test."""
    bx = [(i['sys'] + ':' + i['name'], i['data'], i['sub']) for i in items if i['kind'] == 'box']
    bad = []
    for i in range(len(bx)):
        for j in range(i + 1, len(bx)):
            if boxes_overlap(bx[i][1], bx[j][1]):
                bad.append((bx[i][0], bx[j][0]))
    return bad
