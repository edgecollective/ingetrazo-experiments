"""Clamshell mobile workstation: parametric parts, CNC joinery, flat nesting.

Pure Python (math only) so the same file drives IngeTrazo (run_python) and the
DXF / SVG / cut-list export.  Units: inches, Z up.

Closed box: two half-cabinets that meet face to face.  Half A (desk half) sits
at y in [DB, DB+DA]; half B (storage half) at y in [0, DB].  Both are hinged on
the vertical edge x=0, y=DB with a continuous hinge; B swings 90 deg to form
an L, or 180 deg to stand beside A.
"""
import math

T = 0.75          # sheet thickness: SET TO THE MEASURED THICKNESS before cutting
CLR = 0.012       # extra width/length of every slot (DXF only) for a glue fit
BIT = 0.25        # end mill diameter, sets the dog-bone size
HC = 3.0          # caster mounting height: floor to underside of each half
DESK = 29.0       # desk surface above the floor
GAP = 0.0625      # reveal around the leaf and doors
SHEET_L, SHEET_W = 96.0, 48.0
MARGIN, SPACE = 0.5, 0.45

COLORS = {
    'plyA': (0.87, 0.76, 0.57, 1.0), 'plyB': (0.80, 0.68, 0.49, 1.0),
    'front': (0.22, 0.45, 0.48, 1.0), 'bin': (0.93, 0.62, 0.28, 1.0),
    'stool': (0.86, 0.73, 0.52, 1.0), 'metal': (0.62, 0.63, 0.66, 1.0),
    'dark': (0.22, 0.22, 0.24, 1.0), 'rubber': (0.10, 0.10, 0.11, 1.0),
    'chair': (0.16, 0.17, 0.19, 1.0), 'chair2': (0.32, 0.33, 0.36, 1.0),
    'sheet': (0.95, 0.93, 0.88, 1.0), 'power': (0.92, 0.92, 0.90, 1.0),
}

SPECS = {
    'V1': dict(title='V1 Basic', W=30.0, DA=12.0, DB=12.0, H=46.5, support='stays',
               blurb='Two plain half-boxes, drop-front desk on folding stays, fixed shelves.'),
    'V2': dict(title='V2 Studio', W=36.0, DA=12.0, DB=12.0, H=46.5, support='doors',
               blurb='Wider; lower doors swing out to hold up the desk, cubbies, bins, lipped shelves, pegboard.'),
    'V3': dict(title='V3 Pro', W=36.0, DA=12.0, DB=12.0, H=46.5, support='doors',
               blurb='Adds pencil drawer, mail-slot organizer, cable grommet and power bay, file slots, more pegboard, flat-pack stool.'),
}


class Part:
    """A flat CNC part.  Box parts are axis-aligned panels: ``box`` is the
    panel body (x0,x1,y0,y1,z0,z1) in closed-box coordinates, ``axis`` its
    thickness direction; uv are the other two axes in x,y,z order measured
    from the box minimum.  Tabs stick out of the body, so the drawn outline
    can be bigger than the box."""

    def __init__(self, name, asm, box, axis, color, sub=None):
        self.name, self.asm, self.box, self.axis = name, asm, [float(c) for c in box], axis
        self.color, self.sub = color, sub
        self.feat = {'u0': [], 'u1': [], 'v0': [], 'v1': []}
        self.holes, self.drills = [], []
        self.custom = None      # (outline_fn(cnc), holes_fn(cnc), frame) for non-rect parts
        self.pid = None

    def lo(self, i): return self.box[2 * i]
    def hi(self, i): return self.box[2 * i + 1]

    def axes(self):
        a = [i for i in (0, 1, 2) if i != self.axis]
        return a[0], a[1]

    def size(self):
        U, V = self.axes()
        return self.hi(U) - self.lo(U), self.hi(V) - self.lo(V)

    def frame(self):
        """(origin, u-dir, v-dir, thickness vector) in closed-box inches."""
        if self.custom:
            return self.custom[2]
        U, V = self.axes()
        e = [(1.0, 0, 0), (0, 1.0, 0), (0, 0, 1.0)]
        n = list(e[self.axis]); n = tuple(c * T for c in n)
        return (tuple(self.lo(i) for i in range(3)), e[U], e[V], n)


# ---- joinery ----------------------------------------------------------------

def tab_layout(a, b, n=None, tw=None):
    L = b - a
    if tw is None:
        tw = 1.0 if L < 4 else (1.75 if L < 9 else 2.5)
    if n is None:
        n = 1 if L < 6 else max(2, int(round(L / 10.0)))
    tw = min(tw, 0.5 * L / n)
    return [(a + L * (i + 0.5) / n - tw / 2, a + L * (i + 0.5) / n + tw / 2) for i in range(n)]


def joint(P, Q, n=None, tw=None):
    """P's edge butts into Q's face: tabs on P go through Q.  Where the tab
    would leave a sliver at Q's edge the slot becomes an open notch (a box
    joint)."""
    k = Q.axis
    if abs(P.hi(k) - Q.lo(k)) < 1e-6:
        sgn = 1
    elif abs(P.lo(k) - Q.hi(k)) < 1e-6:
        sgn = -1
    else:
        raise ValueError('%s does not touch %s' % (P.name, Q.name))
    U, V = P.axes()
    if k == U:
        edge, m = ('u1' if sgn > 0 else 'u0'), V
    elif k == V:
        edge, m = ('v1' if sgn > 0 else 'v0'), U
    else:
        raise ValueError('parallel panels %s / %s' % (P.name, Q.name))
    j = P.axis
    if P.lo(j) < Q.lo(j) - 1e-6 or P.hi(j) > Q.hi(j) + 1e-6:
        raise ValueError('%s overhangs %s' % (P.name, Q.name))
    a, b = max(P.lo(m), Q.lo(m)), min(P.hi(m), Q.hi(m))
    if b - a < 0.5:
        raise ValueError('no overlap %s / %s' % (P.name, Q.name))
    QU, QV = Q.axes()
    wq, hq = Q.size()
    for s0, s1 in tab_layout(a, b, n, tw):
        P.feat[edge].append(('tab', s0 - P.lo(m), s1 - P.lo(m)))
        ext = {j: (P.lo(j), P.hi(j)), m: (s0, s1)}
        u0, u1 = ext[QU][0] - Q.lo(QU), ext[QU][1] - Q.lo(QU)
        v0, v1 = ext[QV][0] - Q.lo(QV), ext[QV][1] - Q.lo(QV)
        if u0 < 1e-6:
            Q.feat['u0'].append(('notch', v0, v1, u1))
        elif u1 > wq - 1e-6:
            Q.feat['u1'].append(('notch', v0, v1, wq - u0))
        elif v0 < 1e-6:
            Q.feat['v0'].append(('notch', u0, u1, v1))
        elif v1 > hq - 1e-6:
            Q.feat['v1'].append(('notch', u0, u1, hq - v0))
        else:
            Q.holes.append(('mortise', u0, v0, u1, v1))


# ---- 2D geometry (vertex lists [u, v, bulge]; bulge -1 = half circle to the left) ----

def _clean(pts):
    out = []
    for p in pts:
        if out and abs(p[0] - out[-1][0]) < 1e-9 and abs(p[1] - out[-1][1]) < 1e-9:
            out[-1][2] = p[2]
            continue
        out.append(list(p))
    if len(out) > 1 and abs(out[0][0] - out[-1][0]) < 1e-9 and abs(out[0][1] - out[-1][1]) < 1e-9:
        out[0][2] = out[-1][2] if out[0][2] == 0 else out[0][2]
        out.pop()
    return out


def rect_outline(p, cnc):
    w, h = p.size()
    frames = [('v0', (0.0, 0.0), (1.0, 0.0), (0.0, -1.0), w, False),
              ('u1', (w, 0.0), (0.0, 1.0), (1.0, 0.0), h, False),
              ('v1', (w, h), (-1.0, 0.0), (0.0, 1.0), w, True),
              ('u0', (0.0, h), (0.0, -1.0), (-1.0, 0.0), h, True)]
    pts = []
    for key, st, d, out, L, rev in frames:
        def base(t, o=0.0, st=st, d=d, out=out):
            return [st[0] + d[0] * t + out[0] * o, st[1] + d[1] * t + out[1] * o, 0.0]
        pts.append(base(0.0))
        items = []
        for f in p.feat[key]:
            if f[0] in ('tab', 'notch'):
                s0, s1 = f[1], f[2]
                if f[0] == 'notch' and cnc:
                    s0, s1 = s0 - CLR / 2, s1 + CLR / 2
                t0, t1 = (L - s1, L - s0) if rev else (s0, s1)
                items.append((t0, f[0], t1, f[3] if f[0] == 'notch' else T))
            elif f[0] == 'arc':
                tc = L - f[1] if rev else f[1]
                items.append((tc - f[2], 'arc', tc + f[2], f[2]))
        items.sort()
        for t0, kind, t1, dep in items:
            if kind == 'arc':
                a = base(t0); a[2] = -1.0
                pts += [a, base(t1)]
            else:
                o = dep if kind == 'tab' else -dep
                pts += [base(t0), base(t0, o), base(t1, o), base(t1)]
    return _clean(pts)


def hole_loops(holes, cnc):
    loops = []
    for hd in holes:
        if hd[0] == 'mortise':
            u0, v0, u1, v1 = hd[1:]
            if cnc:
                u0, v0, u1, v1 = u0 - CLR / 2, v0 - CLR / 2, u1 + CLR / 2, v1 + CLR / 2
            loops.append([[u0, v1, 0.0], [u1, v1, 0.0], [u1, v0, 0.0], [u0, v0, 0.0]])
        elif hd[0] == 'slot':
            cu, cv, Ln, wd, horiz = hd[1:]
            a, r = (Ln - wd) / 2, wd / 2
            if horiz:
                loops.append([[cu - a, cv + r, 0.0], [cu + a, cv + r, -1.0],
                              [cu + a, cv - r, 0.0], [cu - a, cv - r, -1.0]])
            else:
                loops.append([[cu - r, cv - a, 0.0], [cu - r, cv + a, -1.0],
                              [cu + r, cv + a, 0.0], [cu + r, cv - a, -1.0]])
        elif hd[0] == 'circle':
            cu, cv, r = hd[1:]
            loops.append([[cu - r, cv, -1.0], [cu + r, cv, -1.0]])
    return loops


def dogbone(loop):
    """Overcut every 90 deg inside corner so square tabs seat fully.  Works
    for CCW outlines and CW holes alike (material always on the left)."""
    r = BIT / 2.0
    k = r * math.sqrt(2.0)
    n, out = len(loop), []
    for i in range(n):
        pv, cu, nx = loop[i - 1], loop[i], loop[(i + 1) % n]
        if pv[2] == 0 and cu[2] == 0:
            d1 = (cu[0] - pv[0], cu[1] - pv[1]); l1 = math.hypot(*d1)
            d2 = (nx[0] - cu[0], nx[1] - cu[1]); l2 = math.hypot(*d2)
            if l1 > k + 1e-6 and l2 > k + 1e-6:
                d1 = (d1[0] / l1, d1[1] / l1); d2 = (d2[0] / l2, d2[1] / l2)
                cr = d1[0] * d2[1] - d1[1] * d2[0]
                if cr < -0.999:
                    out.append([cu[0] - d1[0] * k, cu[1] - d1[1] * k, -1.0])
                    out.append([cu[0] + d2[0] * k, cu[1] + d2[1] * k, 0.0])
                    continue
        out.append(list(cu))
    return out


def part_geometry(p, cnc):
    """(outline, holes) in the part's uv; cnc adds slot clearance and dog-bones."""
    if p.custom:
        ol, hl = p.custom[0](cnc), p.custom[1](cnc)
    else:
        ol, hl = rect_outline(p, cnc), hole_loops(p.holes, cnc)
    if cnc:
        ol, hl = dogbone(ol), [dogbone(h) for h in hl]
    return ol, hl


def expand(loop, seg=12):
    """Bulges to straight segments (for meshes and bounding boxes)."""
    pts, n = [], len(loop)
    for i in range(n):
        x0, y0, b = loop[i]
        x1, y1 = loop[(i + 1) % n][:2]
        pts.append((x0, y0))
        if abs(b) > 1e-9:
            th = 4 * math.atan(b)
            c = math.hypot(x1 - x0, y1 - y0)
            dx, dy = (x1 - x0) / c, (y1 - y0) / c
            off = (c / 2) * (1 - b * b) / (2 * b)
            cx, cy = (x0 + x1) / 2 - dy * off, (y0 + y1) / 2 + dx * off
            R = math.hypot(x0 - cx, y0 - cy)
            a0 = math.atan2(y0 - cy, x0 - cx)
            N = max(2, int(round(abs(th) / math.pi * seg)))
            for k in range(1, N):
                a = a0 + th * k / N
                pts.append((cx + R * math.cos(a), cy + R * math.sin(a)))
    return pts


def bbox2(pts):
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    return min(xs), min(ys), max(xs), max(ys)


def pegboard(p, u0, u1, v0, v1, step=1.0, dia=0.25):
    u = u0
    while u <= u1 + 1e-9:
        v = v0
        while v <= v1 + 1e-9:
            p.drills.append((u, v, dia))
            v += step
        u += step


# ---- hardware (not cut) -------------------------------------------------------

def hw_box(name, asm, color, b, sub=None, state=None):
    return dict(name=name, asm=asm, sub=sub, color=color, state=state, kind='box', box=b)


def hw_cyl(name, asm, color, c, axis, r, length, sub=None, state=None, seg=16):
    loop = []
    for i in range(seg):
        a = 2 * math.pi * i / seg
        p, q = r * math.cos(a), r * math.sin(a)
        if axis == 'x':
            loop.append((c[0] - length / 2, c[1] + p, c[2] + q)); vec = (length, 0, 0)
        elif axis == 'y':
            loop.append((c[0] + p, c[1] - length / 2, c[2] + q)); vec = (0, length, 0)
        else:
            loop.append((c[0] + p, c[1] + q, c[2] - length / 2)); vec = (0, 0, length)
    return dict(name=name, asm=asm, sub=sub, color=color, state=state, kind='prism', loop=loop, vec=vec)


def hw_bar(name, asm, color, p1, p2, w, t, sub=None, state=None):
    d = [p2[i] - p1[i] for i in range(3)]
    L = math.sqrt(sum(c * c for c in d)); d = [c / L for c in d]
    ref = (0, 0, 1.0) if abs(d[2]) < 0.9 else (1.0, 0, 0)
    a = [d[1] * ref[2] - d[2] * ref[1], d[2] * ref[0] - d[0] * ref[2], d[0] * ref[1] - d[1] * ref[0]]
    la = math.sqrt(sum(c * c for c in a)); a = [c / la for c in a]
    bvec = [d[1] * a[2] - d[2] * a[1], d[2] * a[0] - d[0] * a[2], d[0] * a[1] - d[1] * a[0]]
    loop = []
    for su, sv in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
        loop.append(tuple(p1[i] + a[i] * su * w / 2 + bvec[i] * sv * t / 2 for i in range(3)))
    return dict(name=name, asm=asm, sub=sub, color=color, state=state, kind='prism', loop=loop,
                vec=tuple(c * L for c in d))


def hw_rbox(name, asm, color, center, size, yaw, sub=None, state=None):
    cx, cy, z0 = center; sx, sy, sz = size
    c, s = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
    loop = []
    for px, py in ((-sx / 2, -sy / 2), (sx / 2, -sy / 2), (sx / 2, sy / 2), (-sx / 2, sy / 2)):
        loop.append((cx + px * c - py * s, cy + px * s + py * c, z0))
    return dict(name=name, asm=asm, sub=sub, color=color, state=state, kind='prism', loop=loop, vec=(0, 0, sz))


def caster(asm, sx, sy, locking):
    """3 in plate caster; (sx, sy) is the swivel stem, wheel trails toward +x."""
    wx = sx + 0.35
    out = [hw_box('Caster plate', asm, 'dark', (sx - 1.25, sx + 1.25, sy - 1.75, sy + 1.75, HC - 0.12, HC)),
           hw_box('Caster swivel', asm, 'dark', (sx - 0.8, sx + 0.8, sy - 0.8, sy + 0.8, HC - 0.55, HC - 0.12))]
    for dy in (-0.45, 0.45):
        out.append(hw_box('Caster fork', asm, 'metal', (wx - 0.4, wx + 0.4, sy + dy - 0.06, sy + dy + 0.06,
                                                        0.9, HC - 0.55)))
    out.append(hw_cyl('Caster wheel' + (' (locking)' if locking else ''), asm, 'rubber', (wx, sy, 1.0), 'y', 1.0, 0.75))
    return out


# ---- the three variants -------------------------------------------------------

def build(v):
    """All parts and hardware for variant ``v`` in the CLOSED position, plus
    the moves that open it.  Returns dict(parts, hw, moves, meta)."""
    S = SPECS[v]
    W, DA, DB, H = S['W'], S['DA'], S['DB'], S['H']
    zd = DESK - HC                      # deck top in half-local z
    LEAF = 19.5
    doors = S['support'] == 'doors'
    parts, hw = [], []

    def mapA(b):
        x0, x1, y0, y1, z0, z1 = b; return (x0, x1, DB + y0, DB + y1, HC + z0, HC + z1)

    def mapB(b):
        x0, x1, y0, y1, z0, z1 = b; return (x0, x1, DB - y1, DB - y0, HC + z0, HC + z1)

    MAP = {'A': mapA, 'B': mapB}

    def P(half, name, b, axis, color=None, sub=None, prefix=True):
        p = Part((half + ' ' + name) if prefix else name, half, MAP[half](b), axis, color or ('plyA' if half == 'A' else 'plyB'), sub)
        parts.append(p)
        return p

    def carcass(half, D, inset):
        c = {'back': P(half, 'Back', (0, W, D - T, D, 0, H), 1),
             'bottom': P(half, 'Bottom', (0, W, T if inset else 0.0, D - T, 0, T), 2),
             'sideH': P(half, 'Side, hinge', (0, T, 0, D - T, T, H), 0),
             'sideF': P(half, 'Side, free', (W - T, W, 0, D - T, T, H), 0),
             'top': P(half, 'Top', (T, W - T, 0, D - T, H - T, H), 2)}
        for k in ('sideH', 'sideF', 'bottom', 'top'):
            joint(c[k], c['back'])
        joint(c['sideH'], c['bottom']); joint(c['sideF'], c['bottom'])
        joint(c['top'], c['sideH']); joint(c['top'], c['sideF'])
        c['sideF'].holes.append(('slot', (D - T) / 2, H - 5.0 - T, 4.5, 1.25, True))  # hand hold
        return c

    def shelf(half, c, name, z, y0, D, x0=T, x1=None, left=None, right=None):
        s = P(half, name, (x0, W - T if x1 is None else x1, y0, D - T, z, z + T), 2)
        joint(s, left or c['sideH']); joint(s, right or c['sideF']); joint(s, c['back'])
        return s

    def divider(half, c, name, x, y0, D, lower, upper, zlo, zhi):
        d = P(half, name, (x, x + T, y0, D - T, zlo, zhi), 0)
        joint(d, lower); joint(d, upper); joint(d, c['back'])
        return d

    def lip(half, c, name, sh, ztop, ht=2.0):
        l = P(half, name, (T, W - T, 0, T, ztop, ztop + ht), 1)
        joint(l, sh); joint(l, c['sideH']); joint(l, c['sideF'])
        return l

    def openbox(half, name, x0, y0, z0, w, d, h, color, sub, pull):
        bt = P(half, name + ' bottom', (x0, x0 + w, y0, y0 + d, z0, z0 + T), 2, color, sub, False)
        fr = P(half, name + ' front', (x0, x0 + w, y0, y0 + T, z0 + T, z0 + h), 1, color, sub, False)
        bk = P(half, name + ' back', (x0, x0 + w, y0 + d - T, y0 + d, z0 + T, z0 + h), 1, color, sub, False)
        sl = P(half, name + ' side', (x0, x0 + T, y0 + T, y0 + d - T, z0 + T, z0 + h), 0, color, sub, False)
        sr = P(half, name + ' side', (x0 + w - T, x0 + w, y0 + T, y0 + d - T, z0 + T, z0 + h), 0, color, sub, False)
        for q in (fr, bk, sl, sr):
            joint(q, bt)
        for s in (sl, sr):
            joint(s, fr); joint(s, bk)
        if pull == 'slot':
            fr.holes.append(('slot', w / 2, (h - T) - 1.6, 4.0, 1.1, True))
        else:
            fr.feat['v1'].append(('arc', w / 2, 1.1))
        return fr

    # -- half A: the desk half
    A = carcass('A', DA, inset=doors)
    deck = shelf('A', A, 'Desk deck', zd - T, T, DA)
    lw = W - 2 * T - 2 * GAP
    leaf = P('A', 'Desk leaf', (T + GAP, W - T - GAP, 0, T, zd, zd + LEAF), 1, 'front', 'leaf')
    leaf.feat['v1'].append(('arc', lw / 2, 1.25))

    if v == 'V1':
        shelf('A', A, 'Lower shelf', 12.5, 0.0, DA)
        shelf('A', A, 'Upper shelf', 36.0, 3.0, DA)
    else:
        wd = (W - 2 * T - 3 * GAP) / 2
        zb = -(HC - 0.75)
        hd = zd - T - zb
        dL = P('A', 'Door, hinge side', (T + GAP, T + GAP + wd, 0, T, zb, zd - T), 1, 'front', 'doorL')
        dR = P('A', 'Door, free side', (W - T - GAP - wd, W - T - GAP, 0, T, zb, zd - T), 1, 'front', 'doorR')
        dL.holes.append(('slot', wd - 1.75, hd - 4.5, 4.0, 1.25, False))
        dR.holes.append(('slot', 1.75, hd - 4.5, 4.0, 1.25, False))
        mid = shelf('A', A, 'Mid shelf', 12.5, T, DA)
        bw = (W - 2 * T - 0.75) / 2
        for i in range(2):
            openbox('A', 'Bin', T + 0.25 + i * (bw + 0.25), T + 0.25, T, bw, 10.0, 9.5, 'bin', 'bins', 'slot')
        if v == 'V2':
            up = shelf('A', A, 'Upper shelf', 36.5, 1.0, DA)
            cw = (W - 2 * T - 3 * T) / 4
            for i in range(1, 4):
                divider('A', A, 'Cubby divider', T + i * cw + (i - 1) * T, 1.0, DA, deck, up, zd, 36.5)
        else:
            xdiv = W - T - 12.0 - T
            main = divider('A', A, 'Organizer divider', xdiv, 1.0, DA, deck, A['top'], zd, H - T)
            rs = shelf('A', A, 'Organizer shelf', 36.5, 1.0, DA, x0=xdiv + T, left=main)
            sw = (12.0 - 3 * T) / 4
            for i in range(1, 4):
                divider('A', A, 'Mail-slot divider', xdiv + T + i * sw + (i - 1) * T, 1.0, DA, deck, rs, zd, 36.5)
            deck.holes.append(('circle', 2.75, (DA - T - 1.5) - T, 1.0))          # cable grommet
            A['back'].holes.append(('slot', 6.0, 17.0, 4.0, 1.25, True))         # power cord exit
            pegboard(A['back'], 2.0, 21.0, 28.0, 45.0)
            # pencil drawer: narrow enough to pull out between the open doors; slides on cleats
            openbox('A', 'Drawer', 2 * T + 0.5, 1.0, 21.5, W - 4 * T - 1.0, 7.5, 3.5, 'bin', 'drawer', 'notch')
            for x in (T, W - 2 * T):
                P('A', 'Slide cleat', (x, x + T, 1.0, 9.0, 21.25, 24.25), 0)

    # -- half B: the storage half (swings open)
    B = carcass('B', DB, inset=False)
    if v == 'V1':
        for z in (12.0, 24.0, 35.5):
            shelf('B', B, 'Shelf', z, 0.0, DB)
    else:
        s1 = shelf('B', B, 'Shelf, lower', 13.0, 0.0, DB)
        s2 = shelf('B', B, 'Shelf, counter', 25.25, 0.0, DB)
        lip('B', B, 'Lip', B['bottom'], T)
        lip('B', B, 'Lip', s1, 13.75)
        lip('B', B, 'Lip', s2, 26.0)
        divider('B', B, 'Divider', W / 2 - T / 2, T, DB, B['bottom'], s1, T, 13.0)
        pegboard(B['back'], 2.0, W - 2.0, 29.0, 45.0)
        if v == 'V3':
            for i in range(3):
                divider('B', B, 'File-slot divider', W - T - (i + 1) * (3.0 + T), T, DB, B['bottom'], s1, T, 13.0)

    # -- hardware
    for half, D in (('A', DA), ('B', DB)):
        m = MAP[half]
        for i, (lx, ly) in enumerate(((2.0, 3.5), (W - 3.0, 3.5), (2.0, D - 2.25), (W - 3.0, D - 2.25))):
            b = m((lx, lx, ly, ly, 0, 0))
            hw.extend(caster(half, b[0], b[2], i < 2))
    hw.append(hw_box('Continuous hinge, leaf A', 'A', 'metal', (-0.06, 0.0, DB, DB + 0.7, HC + 1, HC + H - 1)))
    hw.append(hw_box('Continuous hinge, leaf B', 'B', 'metal', (-0.06, 0.0, DB - 0.7, DB, HC + 1, HC + H - 1)))
    hw.append(hw_cyl('Continuous hinge, knuckle', 'A', 'metal', (-0.04, DB, HC + H / 2), 'z', 0.09, H - 2))
    hw.append(hw_cyl('Desk-leaf hinge, knuckle', 'A', 'metal', (W / 2, DB + T, HC + zd), 'x', 0.08, lw - 1.0))
    if doors:
        for x in (T, W - T):
            for z in (HC + 0.5, HC + 21.5):
                hw.append(hw_cyl('Door hinge', 'A', 'metal', (x, DB, z), 'z', 0.12, 2.5))
    else:
        for x in (T + 0.12, W - T - 0.12):
            hw.append(hw_box('Lid stay (folded)', 'A', 'metal',
                             (x - 0.1, x + 0.1, DB + T + 0.2, DB + T + 0.7, HC + zd + 7, HC + zd + 17), state='closed'))
            hw.append(hw_bar('Lid stay', 'A', 'metal', (x, DB + T - 10.0, HC + zd + 0.1),
                             (x, DB + T + 0.45, HC + zd + 8.5), 0.5, 0.12, state='open'))
    if v == 'V3':
        for x in (2 * T, W - 2 * T - 0.5):
            hw.append(hw_box('Drawer slide', 'A', 'metal', (x, x + 0.5, DB + 1.0, DB + 9.0, HC + 22.25, HC + 23.75)))
        hw.append(hw_box('Power strip', 'A', 'power', (4.0, 20.0, DB + 8.4, DB + 10.4, HC + 13.25, HC + 14.75)))

    moves = {'B': ('rz', (0.0, DB), -90.0),
             'leaf': ('rx', (DB + T, HC + zd), 90.0)}
    if doors:
        moves['doorL'] = ('rz', (T, DB), -90.0)
        moves['doorR'] = ('rz', (W - T, DB), 90.0)
    if v == 'V3':
        moves['drawer'] = ('t', (0.0, -5.0, 0.0), 0.0)

    # -- seating, in front of the desk (open position only)
    seat_c = (W / 2, DB + T - LEAF - 7.0)
    if v == 'V3':
        parts.extend(stool(seat_c))
    else:
        hw.extend(office_chair(seat_c))
    meta = dict(W=W, DA=DA, DB=DB, H=H, zd=zd, LEAF=LEAF, seat=seat_c, title=S['title'], blurb=S['blurb'])
    return dict(parts=parts, hw=hw, moves=moves, meta=meta)


def office_chair(c):
    cx, cy = c
    out = []
    for i in range(5):
        a = 90 + 72 * i
        r = 6.5
        out.append(hw_rbox('Chair base arm', 'Chair', 'chair', (cx + r * math.cos(math.radians(a)),
                                                            cy + r * math.sin(math.radians(a)), 2.0),
                           (13.0, 1.6, 1.4), a, state='open'))
        out.append(hw_cyl('Chair caster', 'Chair', 'rubber', (cx + 12.5 * math.cos(math.radians(a)),
                                                           cy + 12.5 * math.sin(math.radians(a)), 1.0),
                          'z', 1.0, 2.0, state='open'))
    out.append(hw_cyl('Chair column', 'Chair', 'metal', (cx, cy, 9.5), 'z', 1.1, 12.0, state='open'))
    out.append(hw_rbox('Chair seat', 'Chair', 'chair2', (cx, cy, 15.5), (19.0, 18.0, 3.0), 0, state='open'))
    out.append(hw_box('Chair back post', 'Chair', 'metal', (cx - 1.0, cx + 1.0, cy - 9.8, cy - 8.8, 15.5, 24.0), state='open'))
    out.append(hw_rbox('Chair back', 'Chair', 'chair2', (cx, cy - 10.3, 22.0), (17.0, 2.5, 16.0), 0, state='open'))
    return out


def stool(c):
    """Flat-pack X stool: two halved legs and a round seat, no hardware."""
    cx, cy = c
    Hs, bw, tw_ = 17.25, 15.0, 10.0
    uc = bw / 2
    tabs = ((uc + 2.75, uc + 4.25), (uc - 4.25, uc - 2.75))

    def leg(slot_top, cnc):
        sw = T + (CLR if cnc else 0.0)
        top = [[bw - (bw - tw_) / 2, Hs, 0.0]]
        seq = sorted([('tab',) + tabs[0], ('tab',) + tabs[1]] +
                     ([('slot', uc - sw / 2, uc + sw / 2)] if slot_top else []), key=lambda f: -f[1])
        for f in seq:
            a, b = f[1], f[2]
            if f[0] == 'tab':
                top += [[b, Hs, 0.0], [b, Hs + T, 0.0], [a, Hs + T, 0.0], [a, Hs, 0.0]]
            else:
                top += [[b, Hs, 0.0], [b, Hs / 2, 0.0], [a, Hs / 2, 0.0], [a, Hs, 0.0]]
        top.append([(bw - tw_) / 2, Hs, 0.0])
        bottom = [[0.0, 0.0, 0.0]]
        if not slot_top:
            bottom += [[uc - sw / 2, 0.0, 0.0], [uc - sw / 2, Hs / 2, 0.0], [uc + sw / 2, Hs / 2, 0.0], [uc + sw / 2, 0.0, 0.0]]
        bottom.append([bw, 0.0, 0.0])
        return _clean(bottom + top)

    def leg_holes(slot_top):
        return lambda cnc: hole_loops([('slot', uc, 4.5 if slot_top else 12.5, 5.0, 1.4, True)], cnc)

    def seat_ol(cnc):
        return [[0.0, 7.0, 1.0], [14.0, 7.0, 1.0]]

    def seat_holes(cnc):
        hs = []
        for a, b in tabs:
            o0, o1 = a - uc + 7.0, b - uc + 7.0
            hs.append(('mortise', o0, 7.0 - T / 2, o1, 7.0 + T / 2))     # leg A tabs (along x)
            hs.append(('mortise', 7.0 - T / 2, o0, 7.0 + T / 2, o1))     # leg B tabs (along y)
        return hole_loops(hs, cnc)

    la = Part('Stool leg A (slot from top)', 'Stool', (cx - uc, cx + uc, cy - T / 2, cy + T / 2, 0, Hs), 1, 'stool')
    la.custom = (lambda cnc: leg(True, cnc), leg_holes(True),
                 ((cx - uc, cy - T / 2, 0.0), (1.0, 0, 0), (0, 0, 1.0), (0, T, 0)))
    lb = Part('Stool leg B (slot from bottom)', 'Stool', (cx - T / 2, cx + T / 2, cy - uc, cy + uc, 0, Hs), 0, 'stool')
    lb.custom = (lambda cnc: leg(False, cnc), leg_holes(False),
                 ((cx - T / 2, cy - uc, 0.0), (0, 1.0, 0), (0, 0, 1.0), (T, 0, 0)))
    st = Part('Stool seat', 'Stool', (cx - 7, cx + 7, cy - 7, cy + 7, Hs, Hs + T), 2, 'stool')
    st.custom = (seat_ol, seat_holes, ((cx - 7, cy - 7, Hs), (1.0, 0, 0), (0, 1.0, 0), (0, 0, T)))
    return [la, lb, st]


# ---- moves (articulation) -----------------------------------------------------

def move_point(mv, p):
    kind, c, ang = mv
    x, y, z = p
    if kind == 't':
        return (x + c[0], y + c[1], z + c[2])
    a = math.radians(ang); ca, sa = round(math.cos(a), 12), round(math.sin(a), 12)
    if kind == 'rz':
        dx, dy = x - c[0], y - c[1]
        return (c[0] + dx * ca - dy * sa, c[1] + dx * sa + dy * ca, z)
    if kind == 'rx':
        dy, dz = y - c[0], z - c[1]
        return (x, c[0] + dy * ca - dz * sa, c[1] + dy * sa + dz * ca)
    raise ValueError(kind)


def placed_box(b, mv):
    if mv is None:
        return tuple(b)
    pts = [move_point(mv, (x, y, z)) for x in b[0:2] for y in b[2:4] for z in b[4:6]]
    return (min(p[0] for p in pts), max(p[0] for p in pts), min(p[1] for p in pts),
            max(p[1] for p in pts), min(p[2] for p in pts), max(p[2] for p in pts))


def item_move(model, asm, sub, opened):
    if not opened:
        return None
    mv = model['moves']
    if asm == 'B':
        return mv['B']
    if sub in mv:
        return mv[sub]
    return None


def collisions(model, opened):
    """Pairs of solids whose bodies overlap (tabs excluded, so a clean model
    gives none)."""
    items = []
    for p in model['parts']:
        if p.asm == 'Stool' and not opened:
            continue
        items.append((p.asm + ':' + p.name, placed_box(p.box, item_move(model, p.asm, p.sub, opened)),
                      p.asm))
    for h in model['hw']:
        if h['kind'] != 'box' or (h['state'] and h['state'] != ('open' if opened else 'closed')):
            continue
        if h['asm'] == 'Chair' and not opened:
            continue
        items.append((h['asm'] + ':' + h['name'], placed_box(h['box'], item_move(model, h['asm'], h['sub'], opened)),
                      h['asm']))
    bad = []
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            a, b = items[i][1], items[j][1]
            ov = [min(a[2 * k + 1], b[2 * k + 1]) - max(a[2 * k], b[2 * k]) for k in range(3)]
            if items[i][2] == items[j][2] == 'Stool' or ('hinge' in items[i][0] and 'hinge' in items[j][0]):
                continue
            if all(o > 0.02 for o in ov):
                bad.append((items[i][0], items[j][0], [round(o, 3) for o in ov]))
    return bad


# ---- nesting onto sheets (MaxRects, best short side fit) ----------------------

def nest(items, L=SHEET_L, Wd=SHEET_W, margin=MARGIN, space=SPACE):
    """items: (key, w, h).  Returns sheets: lists of (key, x, y, rotated)."""
    UW, UH = L - 2 * margin + space, Wd - 2 * margin + space
    sheets = []
    order = sorted(items, key=lambda it: (-(it[1] * it[2]), -max(it[1], it[2])))
    for key, w, h in order:
        ww, hh = w + space, h + space
        if min(ww, hh) > min(UW, UH) + 1e-9 or max(ww, hh) > max(UW, UH) + 1e-9:
            raise ValueError('part %s (%.1f x %.1f) does not fit a sheet' % (key, w, h))
        placed = False
        for sh in sheets + [None]:
            if sh is None:
                sh = {'free': [(0.0, 0.0, UW, UH)], 'parts': []}
                sheets.append(sh)
            best = None
            for fx, fy, fw, fh in sh['free']:
                for rot, (a, b) in ((False, (ww, hh)), (True, (hh, ww))):
                    if a <= fw + 1e-9 and b <= fh + 1e-9:
                        sc = (min(fw - a, fh - b), max(fw - a, fh - b), fy, fx)
                        if best is None or sc < best[0]:
                            best = (sc, fx, fy, a, b, rot)
            if best is None:
                continue
            _, x, y, a, b, rot = best
            sh['parts'].append((key, margin + x, margin + y, rot))
            nf = []
            for f in sh['free']:
                fx, fy, fw, fh = f
                if x >= fx + fw or x + a <= fx or y >= fy + fh or y + b <= fy:
                    nf.append(f); continue
                if x > fx: nf.append((fx, fy, x - fx, fh))
                if x + a < fx + fw: nf.append((x + a, fy, fx + fw - x - a, fh))
                if y > fy: nf.append((fx, fy, fw, y - fy))
                if y + b < fy + fh: nf.append((fx, y + b, fw, fy + fh - y - b))
            pr = []
            for i, f in enumerate(nf):
                if any(i != j and g[0] <= f[0] + 1e-9 and g[1] <= f[1] + 1e-9 and
                       g[0] + g[2] >= f[0] + f[2] - 1e-9 and g[1] + g[3] >= f[1] + f[3] - 1e-9 and
                       (g != f or j < i) for j, g in enumerate(nf)):
                    continue
                pr.append(f)
            sh['free'] = pr
            placed = True
            break
        assert placed
    return [sh['parts'] for sh in sheets]


def cnc_layout(model):
    """Every part instance in CNC form, ids assigned, nested.  Returns
    (instances, sheets, ids) where an instance is dict(part, id, ol, holes, bb)."""
    inst, sig_ids, ids = [], {}, []
    for p in model['parts']:
        ol, hl = part_geometry(p, True)
        pts = expand(ol)
        bb = bbox2(pts)
        sig = (p.name, tuple(round(c, 3) for v in ol for c in v), len(hl), len(p.drills))
        if sig not in sig_ids:
            sig_ids[sig] = len(sig_ids) + 1
            ids.append(dict(n=sig_ids[sig], name=p.name, part=p, qty=0, bb=bb, ol=ol, holes=hl))
        rec = ids[sig_ids[sig] - 1]
        rec['qty'] += 1
        inst.append(dict(part=p, n=sig_ids[sig], ol=ol, holes=hl, bb=bb))
    names = {}
    for r in ids:
        names.setdefault(r['name'], []).append(r)
    for nm, rs in names.items():
        if len(rs) > 1:
            for i, r in enumerate(rs):
                r['name'] = '%s (%s)' % (nm, 'abcdefgh'[i])
    sheets = nest([(i, it['bb'][2] - it['bb'][0], it['bb'][3] - it['bb'][1]) for i, it in enumerate(inst)])
    return inst, sheets, ids


def sheet_xy(it, x, y, rot):
    """Map a part's uv to sheet coordinates for its nest placement."""
    u0, v0, u1, v1 = it['bb']
    if not rot:
        return lambda u, v: (x + (u - u0), y + (v - v0))
    return lambda u, v: (x + (v1 - v), y + (u - u0))
