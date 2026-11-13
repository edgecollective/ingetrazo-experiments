"""Edge Collective bike trailer, version 1.0 (edgecollective.io/projects/biketrailer).
1/2 in EMT conduit frame bent from one 10 ft length, two inner bars from a
second length, 16 in kids' wheels in laser-cut dropouts, vinyl-tube hitch.
Pure Python.  Inches, Z up, +Y forward (toward the bike), +X to the right.
Frame sizes are estimates from the photos; the dropouts follow the
project's own OpenSCAD files (v0.3)."""
import math

MM = 1.0 / 25.4
OD = 0.706                     # 1/2 in EMT outside diameter
RP = OD / 2
RB = 4.5                       # bender centreline radius
WR = 8.125                     # 16 in tire, outside radius
TIRE_W = 2.1
OLD = 100 * MM                 # hub locknut width
PLATE = 3.2 * MM               # 0.125 in stainless
XO = 11.5                      # outer bars (x = +-XO)
XI = XO - (OLD + 2 * PLATE + OD)   # inner bars, ~4.9 in inside
YS = 7.0                       # outer bar straight: y -YS..+YS
YC = YS + RB                   # cross members at y = +-YC
AXLE_Z = WR
ZO = AXLE_Z + 26 * MM          # outer bar centre (short dropout: axle 26 mm below the bar)
ZI = ZO + OD                   # inner bars sit on the cross members
PHI = math.radians(15.4)       # tongue angle in from straight ahead
TIP_Y = YC + 27.0

COL = {'conduit': (0.74, 0.76, 0.78, 1.0), 'plate': (0.60, 0.62, 0.65, 1.0), 'tire': (0.10, 0.10, 0.11, 1.0),
       'rim': (0.80, 0.81, 0.83, 1.0), 'hub': (0.55, 0.56, 0.58, 1.0), 'spoke': (0.78, 0.79, 0.80, 1.0),
       'bolt': (0.45, 0.46, 0.48, 1.0), 'vinyl': (0.86, 0.92, 0.96, 1.0), 'deck': (0.78, 0.63, 0.43, 1.0),
       'cap': (0.85, 0.20, 0.15, 1.0), 'hitch': (0.25, 0.26, 0.28, 1.0)}


# ---------------------------------------------------------------- paths and tubes
def path_points(segs, z, step_deg=8.0):
    """segs: ('L', (x0,y0), (x1,y1)) or ('A', centre, r, a0, a1) in degrees.
    Returns centreline points (x, y, z) and the total length."""
    pts, length = [], 0.0
    for s in segs:
        if s[0] == 'L':
            p0, p1 = s[1], s[2]
            if not pts:
                pts.append((p0[0], p0[1], z))
            pts.append((p1[0], p1[1], z))
            length += math.hypot(p1[0] - p0[0], p1[1] - p0[1])
        else:
            c, r, a0, a1 = s[1], s[2], s[3], s[4]
            n = max(2, int(abs(a1 - a0) / step_deg))
            for k in range(0 if not pts else 1, n + 1):
                a = math.radians(a0 + (a1 - a0) * k / n)
                pts.append((c[0] + r * math.cos(a), c[1] + r * math.sin(a), z))
            length += r * math.radians(abs(a1 - a0))
    clean = [pts[0]]
    for p in pts[1:]:
        if math.dist(p, clean[-1]) > 1e-6:
            clean.append(p)
    return clean, length


def tube(pts, r=RP, seg=12, caps=True):
    """Sweep a circle along a polyline (planar paths: binormal = Z unless
    the path is vertical-ish, then X)."""
    rings = []
    n = len(pts)
    for i, p in enumerate(pts):
        a = pts[max(i - 1, 0)]; b = pts[min(i + 1, n - 1)]
        t = [b[k] - a[k] for k in range(3)]
        L = math.sqrt(sum(c * c for c in t)); t = [c / L for c in t]
        up = (0.0, 0.0, 1.0) if abs(t[2]) < 0.9 else (1.0, 0.0, 0.0)
        nrm = [t[1] * up[2] - t[2] * up[1], t[2] * up[0] - t[0] * up[2], t[0] * up[1] - t[1] * up[0]]
        ln = math.sqrt(sum(c * c for c in nrm)); nrm = [c / ln for c in nrm]
        bi = [t[1] * nrm[2] - t[2] * nrm[1], t[2] * nrm[0] - t[0] * nrm[2], t[0] * nrm[1] - t[1] * nrm[0]]
        # mitre the ring at corners so the radius holds through polyline joints
        sc = 1.0
        if 0 < i < n - 1:
            t1 = [p[k] - pts[i - 1][k] for k in range(3)]; t2 = [pts[i + 1][k] - p[k] for k in range(3)]
            l1 = math.sqrt(sum(c * c for c in t1)); l2 = math.sqrt(sum(c * c for c in t2))
            cosang = sum(t1[k] * t2[k] for k in range(3)) / (l1 * l2)
            sc = 1.0 / max(0.5, math.cos(math.acos(max(-1, min(1, cosang))) / 2))
        ring = []
        for j in range(seg):
            th = 2 * math.pi * j / seg
            ring.append(tuple(p[k] + r * (math.cos(th) * nrm[k] * sc + math.sin(th) * bi[k]) for k in range(3)))
        rings.append(ring)
    faces = []
    for i in range(n - 1):
        A, B = rings[i], rings[i + 1]
        for j in range(seg):
            j2 = (j + 1) % seg
            faces.append([A[j], A[j2], B[j2], B[j]])
    if caps:
        faces.append(list(reversed(rings[0])))
        faces.append(list(rings[-1]))
    return faces


def cyl(c, axis, r, length, seg=14):
    """Closed cylinder centred at c along unit axis vector."""
    ax = [axis[k] / math.sqrt(sum(a * a for a in axis)) for k in range(3)]
    p0 = [c[k] - ax[k] * length / 2 for k in range(3)]
    p1 = [c[k] + ax[k] * length / 2 for k in range(3)]
    return tube([tuple(p0), tuple(p1)], r, seg)


def torus(c, R, r, seg=36, rseg=10):
    """Torus in the YZ plane (axis along X), centred at c."""
    rings = []
    for i in range(seg):
        a = 2 * math.pi * i / seg
        ring = []
        for j in range(rseg):
            b = 2 * math.pi * j / rseg
            rr = R + r * math.cos(b)
            ring.append((c[0] + r * math.sin(b), c[1] + rr * math.cos(a), c[2] + rr * math.sin(a)))
        rings.append(ring)
    faces = []
    for i in range(seg):
        A, B = rings[i], rings[(i + 1) % seg]
        for j in range(rseg):
            j2 = (j + 1) % rseg
            faces.append([A[j], A[j2], B[j2], B[j]])
    return faces


def box(x0, x1, y0, y1, z0, z1):
    v = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0), (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
    q = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    return [[v[i] for i in f] for f in q]


# ---------------------------------------------------------------- the main frame
def main_frame_segments():
    """One 10 ft conduit: tongue tip -> tongue -> left outer bar -> back ->
    right outer bar -> front cross member -> curves forward, bolted beside
    the tongue."""
    s, c_ = math.sin(PHI), math.cos(PHI)
    rt = 9.0                                         # gentle bend from the left bar into the tongue
    ctr = (-XO + rt, YS + 2.0)
    bend_end = (ctr[0] - rt * c_, ctr[1] + rt * s)
    tl = (TIP_Y - bend_end[1]) / c_
    tip = (bend_end[0] + s * tl, TIP_Y)
    segs = [('L', tip, bend_end),
            ('A', ctr, rt, 180.0 - math.degrees(PHI), 180.0),
            ('L', (-XO, YS + 2.0), (-XO, -YS)),
            ('A', (-XO + RB, -YS), RB, 180.0, 270.0),
            ('L', (-XO + RB, -YC), (XO - RB, -YC)),
            ('A', (XO - RB, -YS), RB, 270.0, 360.0),
            ('L', (XO, -YS), (XO, YS)),
            ('A', (XO - RB, YS), RB, 0.0, 90.0)]
    # front cross member heading -x, then a right turn into a tail beside the tongue
    d = (s, c_)                                      # tongue direction, toward the tip
    nr = (c_, -s)                                    # tongue's right-hand side
    off = OD                                         # tail centreline one pipe diameter inside the tongue
    # turn centre at (xc, YC + RB); turn ends heading d at (xc, YC + RB) - RB * nr
    # that point must lie on the tongue line shifted by `off` along nr
    p0 = (tip[0] + off * nr[0], tip[1] + off * nr[1])
    # solve xc: (xc - RB*c_ - p0x, YC + RB + RB*s - p0y) parallel to d
    ey = YC + RB + RB * s
    xc = p0[0] + d[0] * (ey - p0[1]) / d[1] + RB * c_
    end = (xc - RB * c_, ey)
    a_end = math.degrees(math.atan2(end[1] - (YC + RB), end[0] - xc))   # clockwise from 270 deg
    segs += [('L', (XO - RB, YC), (xc, YC)),
             ('A', (xc, YC + RB), RB, 270.0, a_end if a_end < 270.0 else a_end - 360.0)]
    tail_len = 4.5
    segs.append(('L', end, (end[0] + d[0] * tail_len, end[1] + d[1] * tail_len)))
    joint = (end[0] + d[0] * tail_len / 2 - off / 2 * nr[0], end[1] + d[1] * tail_len / 2 - off / 2 * nr[1])
    return segs, tip, xc, joint


# ---------------------------------------------------------------- dropouts
def dropout_outline(long):
    """Plate outline in (u along the bar, v up), inches, centred on the
    plate; slot open at the bottom.  From ver_0.3_wide_*.scad."""
    w, h = 35.0, 45.0 + (18.0 if long else 0.0)
    rr = 5.0
    hw, hh = w / 2 + rr, h / 2 + rr
    slot_w, slot_head = 10.0, -h / 2 + 20.0 - rr        # head centre v
    pts = []

    def arc(cx, cy, a0, a1, n=5):
        for k in range(n + 1):
            a = math.radians(a0 + (a1 - a0) * k / n)
            pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    # bottom edge left to the slot
    pts.append((-hw + rr, -hh))
    pts.append((-slot_w / 2, -hh))
    pts.append((-slot_w / 2, slot_head))
    for k in range(1, 8):                                # rounded slot head (semicircle, radius 5)
        a = math.radians(180 - 180 * k / 8)
        pts.append((slot_w / 2 * math.cos(a), slot_head + slot_w / 2 * math.sin(a)))
    pts.append((slot_w / 2, slot_head))
    pts.append((slot_w / 2, -hh))
    pts.append((hw - rr, -hh))
    arc(hw - rr, -hh + rr, -90, 0)
    arc(hw - rr, hh - rr, 0, 90)
    arc(-hw + rr, hh - rr, 90, 180)
    arc(-hw + rr, -hh + rr, 180, 270)
    screw_v = h / 2 - 18.0 / 2 + rr
    screw_u = w / 2 - 4.0
    axle_v = slot_head
    return ([(u * MM, v * MM) for u, v in pts], [(su * screw_u * MM, screw_v * MM) for su in (-1, 1)], 2.0 * MM,
            axle_v * MM, screw_v * MM)


def plate_faces(outline, holes, hr, frame):
    """Extrude the plate: frame = (origin, u_dir, v_dir, n_vec)."""
    O, U, V, N = frame
    P = lambda u, v, t=0.0: tuple(O[k] + U[k] * u + V[k] * v + N[k] * t for k in range(3))
    return dict(loop=[P(u, v) for u, v in outline], vec=tuple(N),
                holes=[[P(hu + hr * math.cos(2 * math.pi * j / 10), hv + hr * math.sin(2 * math.pi * j / 10))
                        for j in range(10)] for hu, hv in holes])


# ---------------------------------------------------------------- wheel
def wheel_parts(xc, yc, zc):
    out = []
    out.append(('Tire 16 x 2.125', 'tire', torus((xc, yc, zc), WR - 1.0, 1.0)))
    out.append(('Rim', 'rim', torus((xc, yc, zc), 6.1, 0.32, seg=36, rseg=8)))
    out.append(('Hub', 'hub', cyl((xc, yc, zc), (1, 0, 0), 0.7, OLD - 0.3)))
    sp = []
    for side in (-1, 1):
        fx = xc + side * 1.2
        for i in range(14):
            a = 2 * math.pi * (i + (0.5 if side > 0 else 0.0)) / 14
            p0 = (fx, yc + 1.15 * math.cos(a), zc + 1.15 * math.sin(a))
            a2 = a + side * 0.9
            p1 = (xc + side * 0.15, yc + 6.0 * math.cos(a2), zc + 6.0 * math.sin(a2))
            sp += tube([p0, p1], 0.045, 5, caps=False)
    out.append(('Spokes', 'spoke', sp))
    out.append(('Axle 3/8 in', 'bolt', cyl((xc, yc, zc), (1, 0, 0), 0.19, OLD + 2 * PLATE + 1.1)))
    for side in (-1, 1):
        out.append(('Axle nut', 'bolt', cyl((xc + side * (OLD / 2 + PLATE + 0.22), yc, zc), (1, 0, 0), 0.32, 0.3, seg=6)))
    return out


# ---------------------------------------------------------------- whole trailer
def build():
    """List of parts: dict(name, color, layer, kind 'mesh'|'plate', faces|plate, explode=(dx,dy,dz))."""
    P = []

    def add(name, color, layer, faces, ex=(0, 0, 0), kind='mesh', opacity=None):
        P.append(dict(name=name, color=color, layer=layer, kind=kind, data=faces, ex=ex, opacity=opacity))
    segs, tip, xc, joint = main_frame_segments()
    pts, L_main = path_points(segs, ZO)
    add('Main frame: one 10 ft 1/2 in EMT conduit, bent (%.0f in used)' % L_main, 'conduit', 'Frame', tube(pts))
    for sx in (-1, 1):
        a, b = (sx * XI, -YC - 1.0, ZI), (sx * XI, YC + 1.0, ZI)
        add('Inner bar, 1/2 in EMT %.0f in' % (2 * YC + 2), 'conduit', 'Frame', tube([a, b]), ex=(0, 0, 9.0))
    # bolts: inner bars down through the cross members (#10-24 x 2.5)
    for sx in (-1, 1):
        for sy in (-1, 1):
            yb = sy * YC
            if sx < 0 and sy > 0 and -XI < xc:           # left front: the bar crosses the turn into the tongue tail
                yb = YC + RB - math.sqrt(max(0.0, RB * RB - (-XI - xc) ** 2))
            add('Bolt #10-24 x 2 1/2 (inner bar to cross member)', 'bolt', 'Hardware',
                cyl((sx * XI, yb, (ZO + ZI) / 2), (0, 0, 1), 0.095, 2.5, seg=8), ex=(0, 0, 14.0))
    s, c_ = math.sin(PHI), math.cos(PHI)
    add('Bolt #10-24 x 2 1/2 (tongue joint)', 'bolt', 'Hardware',
        cyl((joint[0], joint[1], ZO), (c_, -s, 0), 0.095, 2.5, seg=8), ex=(-6.0, 0, 0))
    # dropouts and wheels
    for sx in (-1, 1):
        for long, xb in ((False, sx * XO), (True, sx * XI)):
            ol, holes, hr, axle_v, screw_v = dropout_outline(long)
            zb = ZO if not long else ZI
            # plate on the wheel side of its bar
            inward = -sx if not long else sx
            x_face = xb + inward * RP
            O = (x_face, 0.0, zb - screw_v)
            N = (inward * PLATE, 0.0, 0.0)
            pl = plate_faces(ol, holes, hr, (O, (0.0, 1.0, 0.0), (0.0, 0.0, 1.0), N))
            nm = 'Dropout, %s (3.2 mm stainless, laser cut)' % ('long, inner bar' if long else 'short, outer bar')
            add(nm, 'plate', 'Dropouts', pl, ex=(inward * 5.0, 0, -4.0), kind='plate')
            for hu, hv in holes:
                add('Bolt #10-24 x 2 (dropout)', 'bolt', 'Hardware',
                    cyl((xb, hu, zb), (1, 0, 0), 0.095, 2.0, seg=8), ex=(-inward * 6.0, 0, 0))
        xw = sx * (XO + XI) / 2
        for nm, colr, faces in wheel_parts(xw, 0.0, AXLE_Z):
            add(nm + (' (left)' if sx < 0 else ' (right)'), colr, 'Wheels', faces, ex=(sx * 14.0, 0, 0))
    # hitch: vinyl tube over the tongue tip, coupler bracket
    d = (s, c_, 0.0)
    tc = (tip[0], tip[1], ZO)
    add('Braided vinyl tube 7/8 in, 6 in long', 'vinyl', 'Hitch',
        cyl((tc[0] + d[0] * 0.5, tc[1] + d[1] * 0.5, ZO), d, 0.58, 6.0, seg=14), ex=(0, 8.0, 0), opacity=0.55)
    hx, hy = tc[0] + d[0] * 3.6, tc[1] + d[1] * 3.6
    add('Hitch coupler (Burley-style, on the bike axle)', 'hitch', 'Hitch',
        box(hx - 0.9, hx + 0.9, hy - 0.08, hy + 0.08, ZO - 1.5, ZO + 2.6), ex=(0, 12.0, 0))
    add('Coupler strap', 'hitch', 'Hitch', torus((hx, hy, ZO), 0.75, 0.1, seg=16, rseg=6), ex=(0, 12.0, 0))
    # optional deck
    add('Deck, 1/2 in plywood 15 x 27 in (optional)', 'deck', 'Deck',
        box(-7.5, 7.5, -YC - 1.0, YC + 1.0, ZI + RP, ZI + RP + 0.5), ex=(0, 0, 24.0))
    meta = dict(L_main=L_main, tip=tip, xc=xc, inner_len=2 * YC + 2, width=2 * XO + OD, length=2 * YC + OD,
                overall=TIP_Y + YC + RP)
    return P, meta


def materials():
    """Stage 1: what you start with, laid out flat."""
    P = []
    for i in range(2):
        P.append(dict(name='1/2 in EMT conduit, 10 ft', color='conduit', layer='Frame', kind='mesh',
                      data=tube([(0.0, i * 4.0, RP), (120.0, i * 4.0, RP)]), ex=(0, 0, 0), opacity=None))
    for i, long in enumerate((False, False, True, True)):
        ol, holes, hr, _a, _s = dropout_outline(long)
        pl = plate_faces(ol, holes, hr, ((8.0 + i * 3.0, 14.0, 0.0), (1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, PLATE)))
        P.append(dict(name='Dropout, %s' % ('long' if long else 'short'), color='plate', layer='Dropouts', kind='plate',
                      data=pl, ex=(0, 0, 0), opacity=None))
    for i in range(2):
        for nm, colr, faces in wheel_parts(0.0, 0.0, 0.0):
            fs = [[(30.0 + i * 20.0 + v[2], 20.0 + v[1], v[0] + 1.1) for v in f] for f in faces]   # lying flat
            P.append(dict(name=nm, color=colr, layer='Wheels', kind='mesh', data=fs, ex=(0, 0, 0), opacity=None))
    P.append(dict(name='Braided vinyl tube 7/8 in, 6 in', color='vinyl', layer='Hitch', kind='mesh',
                  data=cyl((80.0, 16.0, 0.58), (1, 0, 0), 0.58, 6.0), ex=(0, 0, 0), opacity=0.55))
    for i in range(13):
        L = 2.0 if i < 8 else 2.5
        P.append(dict(name='Bolt #10-24 x %s' % ('2' if L == 2.0 else '2 1/2'), color='bolt', layer='Hardware', kind='mesh',
                      data=cyl((90.0 + i * 0.8, 14.0 + L / 2, 0.1), (0, 1, 0), 0.095, L, seg=8), ex=(0, 0, 0),
                      opacity=None))
    return P
