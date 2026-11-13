"""Bike trailer, version 4 (the hand sketch "version 4" plus a photo of the
dry-fit frame, 2026-11-13).  Loaded after bt_geom.py: it reuses that file's
tube/plate helpers and the v1 laser-cut dropouts, and overrides the frame.

Main frame: one 10 ft 1/2 in EMT conduit bent into a closed loop.  Measured
from the joint in the middle of the front cross member, going right:
    10 straight | bend 10-18 | 24 side | bend 42-50 | 20 back | bend 70-78 |
    24 side | bend 102-110 | 10 straight            = 120 in
Each 90 deg bend uses 8 in of conduit, so the centreline radius is 16/pi =
5.09 in.  The ends butt together in a set-screw coupling.

Inner bars: straight pieces from the second conduit, at the bend tangents
(x = +-10), so they run 5.09 in inside the sides (the sketch's "5").  They sit
on top of the front and back cross members and bolt down through them.

Wheels: one between each side and its inner bar, axle at mid-length, in the
v1 short (outer) and long (inner) dropouts.  26 in wheels, estimated from the
photo.  Inches, Z up, +Y forward (toward the bike), +X to the right."""

ARC = 8.0                          # conduit used by each 90 deg bend (sketch)
RB = 2.0 * ARC / math.pi           # 5.093 in bend centreline radius
HALF_FRONT, SIDE, BACK = 10.0, 24.0, 20.0
XI = HALF_FRONT                    # inner bars at the bend tangents
XO = XI + RB                       # outer sides
YS = SIDE / 2.0                    # side straights run y = -YS..+YS
YC = YS + RB                       # front / back cross members at y = +-YC
WHEEL_IN = 26
WR = 13.1                          # 26 x 2.1 tire, outside radius
TIRE_R = 1.05
RIM_R = 11.0                       # ISO 559 rim
AXLE_Z = WR
ZO = AXLE_Z + 26 * MM              # short dropout: axle 26 mm below the outer bar
ZI = ZO + OD                       # inner bars sit on the cross members
INNER_LEN = 36.0                   # each inner bar; 0.9 in past each cross member
GAP = 0.05                         # half the gap where the conduit ends butt
BENDS = [(10.0, 18.0), (42.0, 50.0), (70.0, 78.0), (102.0, 110.0)]
DECK = (21.0, 34.0)
COL.update({'mark': (0.85, 0.20, 0.15, 1.0), 'cut': (0.20, 0.20, 0.22, 1.0)})


def loop_segments(gap=GAP):
    return [('L', (gap, YC), (XI, YC)),
            ('A', (XI, YS), RB, 90.0, 0.0),
            ('L', (XO, YS), (XO, -YS)),
            ('A', (XI, -YS), RB, 0.0, -90.0),
            ('L', (XI, -YC), (-XI, -YC)),
            ('A', (-XI, -YS), RB, -90.0, -180.0),
            ('L', (-XO, -YS), (-XO, YS)),
            ('A', (-XI, YS), RB, 180.0, 90.0),
            ('L', (-XI, YC), (-gap, YC))]


def seg_len(s):
    if s[0] == 'L':
        return math.hypot(s[2][0] - s[1][0], s[2][1] - s[1][1])
    return s[2] * math.radians(abs(s[4] - s[3]))


def at(dist):
    """Centreline (x, y) and unit tangent at `dist` in along the conduit from the joint."""
    for s in loop_segments(0.0):
        L = seg_len(s)
        if dist <= L + 1e-9:
            f = dist / L
            if s[0] == 'L':
                (x0, y0), (x1, y1) = s[1], s[2]
                return (x0 + (x1 - x0) * f, y0 + (y1 - y0) * f), ((x1 - x0) / L, (y1 - y0) / L)
            c, r, a0, a1 = s[1], s[2], s[3], s[4]
            a = math.radians(a0 + (a1 - a0) * f)
            sg = 1.0 if a1 > a0 else -1.0
            return (c[0] + r * math.cos(a), c[1] + r * math.sin(a)), (-sg * math.sin(a), sg * math.cos(a))
        dist -= L
    raise ValueError('past the end of the loop')


def band(c, axis):
    """A painted mark: a thin band around the conduit."""
    return cyl(c, axis, RP + 0.03, 0.22, seg=12)


def coupling_parts(c):
    """1/2 in EMT set-screw coupling along X, centred at c."""
    out = [('EMT set-screw coupling, 1/2 in (joins the conduit ends)', 'plate', cyl(c, (1, 0, 0), 0.46, 1.8, seg=18))]
    for sx in (-1, 1):
        out.append(('Coupling set screw', 'bolt', cyl((c[0] + sx * 0.5, c[1], c[2] + 0.52), (0, 0, 1), 0.12, 0.3, seg=6)))
    return out


def wheel4(xc, yc, zc, x_lo, x_hi):
    """26 in wheel in the YZ plane; x_lo/x_hi are the bar-side faces of its two plates."""
    out = [('Tire 26 x 2.1', 'tire', torus((xc, yc, zc), WR - TIRE_R, TIRE_R, seg=48, rseg=10)),
           ('Rim 26 in', 'rim', torus((xc, yc, zc), RIM_R, 0.33, seg=48, rseg=8)),
           ('Hub, 100 mm front', 'hub', cyl((xc, yc, zc), (1, 0, 0), 0.7, OLD - 0.3))]
    sp = []
    for side in (-1, 1):
        fx = xc + side * 1.1
        for i in range(18):
            a = 2 * math.pi * (i + (0.5 if side > 0 else 0.0)) / 18
            p0 = (fx, yc + 1.15 * math.cos(a), zc + 1.15 * math.sin(a))
            a2 = a + side * 0.55
            p1 = (xc + side * 0.12, yc + (RIM_R - 0.3) * math.cos(a2), zc + (RIM_R - 0.3) * math.sin(a2))
            sp += tube([p0, p1], 0.045, 5, caps=False)
    out.append(('Spokes', 'spoke', sp))
    out.append(('Axle 3/8 in', 'bolt', cyl(((x_lo + x_hi) / 2, yc, zc), (1, 0, 0), 0.19, x_hi - x_lo + 1.0)))
    for x in (x_lo - 0.17, x_hi + 0.17):
        out.append(('Axle nut', 'bolt', cyl((x, yc, zc), (1, 0, 0), 0.32, 0.3, seg=6)))
    return out


def build():
    """Assembled trailer: list of part dicts (as in bt_geom.build) and a summary."""
    P = []

    def add(name, color, layer, faces, ex=(0, 0, 0), kind='mesh', opacity=None):
        P.append(dict(name=name, color=color, layer=layer, kind=kind, data=faces, ex=ex, opacity=opacity))
    pts, L_loop = path_points(loop_segments(), ZO)
    add('Main frame: one 10 ft 1/2 in EMT conduit, bent into a loop (120 in)', 'conduit', 'Frame', tube(pts))
    for nm, colr, faces in coupling_parts((0.0, YC, ZO)):
        add(nm, colr, 'Hardware', faces, ex=(0, 7.0, 0))
    for sx in (-1, 1):
        a, b = (sx * XI, -INNER_LEN / 2, ZI), (sx * XI, INNER_LEN / 2, ZI)
        add('Inner bar, 1/2 in EMT 36 in', 'conduit', 'Frame', tube([a, b]), ex=(0, 0, 10.0))
        for sy in (-1, 1):
            add('Bolt #10-24 x 2 1/2 (inner bar to cross member)', 'bolt', 'Hardware',
                cyl((sx * XI, sy * YC, (ZO + ZI) / 2), (0, 0, 1), 0.095, 2.5, seg=8), ex=(0, 0, 17.0))
    for sx in (-1, 1):
        for long, xb in ((False, sx * XO), (True, sx * XI)):
            ol, holes, hr, axle_v, screw_v = dropout_outline(long)
            zb = ZO if not long else ZI
            inward = -sx if not long else sx                 # toward the wheel
            x_face = xb + inward * RP
            O = (x_face, 0.0, zb - screw_v)
            N = (inward * PLATE, 0.0, 0.0)
            pl = plate_faces(ol, holes, hr, (O, (0.0, 1.0, 0.0), (0.0, 0.0, 1.0), N))
            nm = 'Dropout, %s (3.2 mm stainless, laser cut)' % ('long, inner bar' if long else 'short, outer bar')
            add(nm, 'plate', 'Dropouts', pl, ex=(0, 0, -7.0), kind='plate')
            for hu, hv in holes:
                add('Bolt #10-24 x 2 (dropout)', 'bolt', 'Hardware',
                    cyl((xb, hu, zb), (1, 0, 0), 0.095, 2.0, seg=8), ex=(-inward * 6.0, 0, -7.0))
        faces_x = sorted((sx * (XO - RP), sx * (XI + RP)))
        xw = sx * (XO + XI) / 2
        for nm, colr, faces in wheel4(xw, 0.0, AXLE_Z, faces_x[0], faces_x[1]):
            add(nm + (' (left)' if sx < 0 else ' (right)'), colr, 'Wheels', faces, ex=(sx * 20.0, 0, 0))
    add('Deck, 1/2 in plywood %g x %g in (optional)' % DECK, 'deck', 'Deck',
        box(-DECK[0] / 2, DECK[0] / 2, -DECK[1] / 2, DECK[1] / 2, ZI + RP, ZI + RP + 0.5), ex=(0, 0, 30.0))
    meta = dict(L_loop=L_loop + 2 * GAP, width=2 * XO + OD, length=2 * YC + OD, height=2 * WR,
                deck_z=ZI + RP + 0.5, clear_mm=(XO - XI - OD) / MM)
    return P, meta


def bent_frame():
    """Stage 2: the bent loop alone (lying flat), with its bend marks and coupling."""
    P = []
    pts, _L = path_points(loop_segments(), ZO)
    P.append(dict(name='Main frame: one 10 ft 1/2 in EMT conduit, bent into a loop (120 in)', color='conduit',
                  layer='Frame', kind='mesh', data=tube(pts), ex=(0, 0, 0), opacity=None))
    for b in BENDS:
        for d in b:
            (x, y), t = at(d)
            P.append(dict(name='Bend mark at %g in' % d, color='mark', layer='Marks', kind='mesh',
                          data=band((x, y, ZO), (t[0], t[1], 0.0)), ex=(0, 0, 0), opacity=None))
    for nm, colr, faces in coupling_parts((0.0, YC, ZO)):
        P.append(dict(name=nm, color=colr, layer='Hardware', kind='mesh', data=faces, ex=(0, 0, 0), opacity=None))
    return P


def materials():
    """Stage 1: what you start with, laid out flat.  Conduit 1 carries the
    bend marks; conduit 2 the cuts for the inner bars."""
    P = []

    def add(name, color, layer, faces, opacity=None, kind='mesh'):
        P.append(dict(name=name, color=color, layer=layer, kind=kind, data=faces, ex=(0, 0, 0), opacity=opacity))
    add('1/2 in EMT conduit, 10 ft: main frame', 'conduit', 'Frame', tube([(0.0, 0.0, RP), (120.0, 0.0, RP)]))
    add('1/2 in EMT conduit, 10 ft: inner bars', 'conduit', 'Frame', tube([(0.0, 5.0, RP), (120.0, 5.0, RP)]))
    for b in BENDS:
        for d in b:
            add('Bend mark at %g in' % d, 'mark', 'Marks', band((d, 0.0, RP), (1, 0, 0)))
    for d in (36.0, 72.0):
        add('Cut mark at %g in' % d, 'cut', 'Marks', band((d, 5.0, RP), (1, 0, 0)))
    for i, long in enumerate((False, False, True, True)):
        ol, holes, hr, _a, _s = dropout_outline(long)
        pl = plate_faces(ol, holes, hr, ((8.0 + i * 3.0, 16.0, 0.0), (1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, PLATE)))
        add('Dropout, %s' % ('long' if long else 'short'), 'plate', 'Dropouts', pl, kind='plate')
    for i in range(2):
        for nm, colr, faces in wheel4(0.0, 0.0, 0.0, -2.2, 2.2):
            fs = [[(36.0 + i * 29.0 + v[2], 27.0 + v[1], v[0] + TIRE_R) for v in f] for f in faces]   # lying flat
            add(nm, colr, 'Wheels', fs)
    for nm, colr, faces in coupling_parts((86.0, 16.0, 0.46)):
        add(nm, colr, 'Hardware', faces)
    for i in range(12):
        L = 2.0 if i < 8 else 2.5
        add('Bolt #10-24 x %s' % ('2' if L == 2.0 else '2 1/2'), 'bolt', 'Hardware',
            cyl((92.0 + i * 0.8, 14.0 + L / 2, 0.1), (0, 1, 0), 0.095, L, seg=8))
    return P
