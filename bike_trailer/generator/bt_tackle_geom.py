
"""Tackle-box hardware store: a second variation on the version 4 trailer
(2026-11-13).  Loaded after bt_geom.py, bt4_geom.py and bt_store_geom.py; it
reuses their helpers and the pegboard tool set from the first store.

Closed for towing it is a plain box on the deck.  Open:
  back (customer side, -Y): two doors swing out 115 deg.  Each door is a
      shallow tray with three lipped shelves of parts jars; behind them a grid
      of 12 cubbies with parts boxes
  top: like a cantilever tackle box.  A fixed tray of 32 compartments sits on
      the cabinet; on each side two trays of 24 compartments ride on parallel
      arms and fan out over the wheels in steps (7 in out per tier, level)
  lid: hinged at the front edge, stands up as a pegboard backboard with the
      sign, held by two stays
Arms: each tier's pivots are 4.61 in apart on the arm, which swings from 49
deg inboard (closed) to 49 deg outboard (open), so every tray moves straight
out by 7 in per tier and stays level (two parallel arms per end)."""
import random

TB_H = 15.0
ZB = DECK_TOP + TB_H               # cabinet top
TT = 3.0                           # tray depth = tier spacing
SLIDE = 7.0                        # tier 1 moves out 7 in, tier 2 14 in
ARM_L = math.hypot(SLIDE / 2.0, TT)
ARM_A = math.atan2(SLIDE / 2.0, TT)
ARM_P = (10.25, ZB + 1.6)          # body pivot (right side), on the end walls
ARM_D = (0.0, -1.45)               # the second, parallel arm
DOOR_OPEN = 115.0
DOOR_Z = (DECK_TOP + 0.1, ZB - 0.6)
RECESS = 3.5                       # door trays fold into this
Z_HINGE = ZB + 3 * TT + 1.25       # lid hinge axis, along the front top edge
LID_TOP = Z_HINGE + 2 * CY
T0_X = 7.0                         # fixed top tray spans x = +-7
STOCK_COLS = ['zinc', 'brass', 'black', 'red', 'blue', 'yellow', 'copper', 'zinc', 'black', 'brass']
COL.update({'tray': (0.20, 0.42, 0.32, 1.0), 'copper': (0.74, 0.42, 0.24, 1.0), 'jar': (0.83, 0.87, 0.90, 1.0)})


def rot_z(faces, c, deg):
    a = math.radians(deg)
    ca, sa = math.cos(a), math.sin(a)
    return [[(c[0] + (v[0] - c[0]) * ca - (v[1] - c[1]) * sa, c[1] + (v[0] - c[0]) * sa + (v[1] - c[1]) * ca, v[2])
             for v in f] for f in faces]


def mirror_x(faces):
    return [[(-v[0], v[1], v[2]) for v in f] for f in faces]


def lid_closed_pt(v):
    """Open (standing) lid -> closed (lying on the trays): 90 deg about the hinge axis."""
    return (v[0], CY - (v[2] - Z_HINGE), Z_HINGE + (v[1] - CY))


def lid_close(data):
    if isinstance(data, dict):
        return dict(loop=[lid_closed_pt(v) for v in data['loop']], vec=(data['vec'][0], -data['vec'][2], data['vec'][1]),
                    holes=[[lid_closed_pt(v) for v in h] for h in data['holes']])
    return [[lid_closed_pt(v) for v in f] for f in data]


def tray(x0, x1, y0, y1, z0, ncol, nrow, rng, floor=True, w=0.25):
    """Compartment tray: shell (floor, walls, dividers) and stock heaps by colour."""
    fl = 0.25 if floor else 0.0
    shell = box(x0, x1, y0, y1, z0, z0 + fl) if floor else []
    shell += (box(x0, x0 + w, y0, y1, z0, z0 + TT) + box(x1 - w, x1, y0, y1, z0, z0 + TT)
              + box(x0 + w, x1 - w, y0, y0 + w, z0, z0 + TT) + box(x0 + w, x1 - w, y1 - w, y1, z0, z0 + TT))
    cw, ch = (x1 - x0 - 2 * w) / ncol, (y1 - y0 - 2 * w) / nrow
    for i in range(1, ncol):
        xd = x0 + w + i * cw
        shell += box(xd - 0.06, xd + 0.06, y0 + w, y1 - w, z0 + fl, z0 + TT - 0.3)
    for j in range(1, nrow):
        yd = y0 + w + j * ch
        shell += box(x0 + w, x1 - w, yd - 0.06, yd + 0.06, z0 + fl, z0 + TT - 0.3)
    heaps = {}
    for i in range(ncol):
        for j in range(nrow):
            hx0, hy0 = x0 + w + i * cw + 0.12, y0 + w + j * ch + 0.12
            c = rng.choice(STOCK_COLS)
            heaps.setdefault(c, []).extend(box(hx0, hx0 + cw - 0.24, hy0, hy0 + ch - 0.24, z0 + fl,
                                               z0 + fl + rng.uniform(0.5, 1.7)))
    return shell, heaps


def arm_points(sx, opened):
    u = (sx * math.sin(ARM_A) * (1.0 if opened else -1.0), math.cos(ARM_A))
    P = (sx * ARM_P[0], ARM_P[1])
    return [[(P[0] + k * ARM_L * u[0] + d[0] * sx, P[1] + k * ARM_L * u[1] + d[1]) for k in range(3)] for d in ((0.0, 0.0), ARM_D)]


def flat_bar(p, q, y0, y1, w=0.6, ext_=0.35):
    dx, dz = q[0] - p[0], q[1] - p[1]
    L = math.hypot(dx, dz)
    ux, uz = dx / L, dz / L
    nx, nz = -uz * w / 2, ux * w / 2
    a = (p[0] - ux * ext_, p[1] - uz * ext_)
    b = (q[0] + ux * ext_, q[1] + uz * ext_)
    poly = [(a[0] + nx, a[1] + nz), (b[0] + nx, b[1] + nz), (b[0] - nx, b[1] - nz), (a[0] - nx, a[1] - nz)]
    return ext(poly, (0.0, y0, 0.0), (1, 0, 0), (0, 0, 1), (0.0, y1 - y0, 0.0))


def door_faces():
    """Right-hand door, closed, as (name, colour, faces); hinge at (CX, -CY)."""
    x0, x1 = 0.06, CX - 0.06
    z0, z1 = DOOR_Z
    yo, yi = -CY, -CY + RECESS - 0.25            # outer face, open (inner) side of the tray
    out = [('Door skin, 1/2 in ply', 'ply', box(x0, x1, yo, yo + 0.5, z0, z1))]
    rim = (box(x0, x0 + 0.25, yo + 0.5, yi, z0, z1) + box(x1 - 0.25, x1, yo + 0.5, yi, z0, z1)
           + box(x0 + 0.25, x1 - 0.25, yo + 0.5, yi, z1 - 0.25, z1))
    h = (z1 - z0) / 3.0
    jars, lids = [], {}
    for k in range(3):
        zs = z0 + k * h
        rim += box(x0 + 0.25, x1 - 0.25, yo + 0.5, yi, zs, zs + 0.25)                       # shelf
        rim += box(x0 + 0.25, x1 - 0.25, yi - 0.25, yi, zs + 0.25, zs + 1.3)               # lip
        for i in range(4):
            xc = x0 + 0.25 + (i + 0.5) * (x1 - x0 - 0.5) / 4
            jars += cyl((xc, yo + 0.5 + 1.15, zs + 0.25 + 1.5), (0, 0, 1), 1.0, 3.0, seg=14)
            lids.setdefault(['red', 'yellow', 'blue', 'black'][(i + k) % 4], []).extend(
                cyl((xc, yo + 0.5 + 1.15, zs + 0.25 + 3.2), (0, 0, 1), 1.05, 0.45, seg=14))
    out.append(('Door tray: rim and 3 lipped shelves', 'ply', rim))
    out.append(('Parts jars (12 per door)', 'jar', jars))
    for c, f in lids.items():
        out.append(('Jar lids', c, f))
    out.append(('Door knob', 'knob', cyl((x0 + 1.2, yo - 0.3, (z0 + z1) / 2), (0, 1, 0), 0.3, 0.6, seg=10)))
    for zh in (z0 + 2.0, z1 - 2.0):
        out.append(('Door hinge', 'steel', cyl((CX + 0.05, yo - 0.05, zh), (0, 0, 1), 0.15, 2.0, seg=8)))
    return out


def lid_faces():
    """Lid in its OPEN pose (standing at the front edge, inner face toward -Y)."""
    zt = LID_TOP
    sign_z0 = zt - 5.75
    out = [('Lid skin, 1/2 in ply 21 x 34 in', 'ply', 'Lid', box(-CX, CX, CY - 0.5, CY, Z_HINGE, zt), 'mesh'),
           ('Lid frame, 1x2 furring', 'ply', 'Lid',
            box(-CX, -CX + 0.5, CY - 1.0, CY - 0.5, Z_HINGE, zt) + box(CX - 0.5, CX, CY - 1.0, CY - 0.5, Z_HINGE, zt)
            + box(-CX + 0.5, CX - 0.5, CY - 1.0, CY - 0.5, Z_HINGE, Z_HINGE + 0.5), 'mesh')]
    x0, x1, z0, z1, y0 = -CX + 0.5, CX - 0.5, Z_HINGE + 0.5, sign_z0, CY - 1.25
    holes = []
    for i in range(19):
        for j in range(int(z1 - z0 - 1.0)):
            x, z = -9.0 + i, z0 + 1.0 + j
            holes.append([(x + 0.125 * math.cos(math.pi * k / 3), y0, z + 0.125 * math.sin(math.pi * k / 3)) for k in range(6)])
    out.append(('Pegboard, 1/4 in hardboard, lid lining', 'peg', 'Lid',
                dict(loop=[(x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1)], vec=(0.0, 0.25, 0.0), holes=holes), 'plate'))
    out.append(('Sign board, 1/2 in ply painted', 'sign', 'Sign', box(-CX + 0.5, CX - 0.5, CY - 1.25, CY - 0.5, sign_z0, zt), 'mesh'))
    out.append(('Sign lettering, HARDWARE', 'letter', 'Sign', lettering('HARDWARE', sign_z0 + 2.9, 2.5, CY - 1.25, -1), 'mesh'))
    out.append(('Lid piano hinge', 'steel', 'Lid', cyl((0.0, CY + 0.12, Z_HINGE), (1, 0, 0), 0.15, 2 * CX - 1.0, seg=8), 'mesh'))
    return out


def build_tackle(opened=True):
    P, meta = build()
    for p in P:
        p['ex'] = (0.0, 0.0, 0.0)
        if p['layer'] == 'Deck':
            p['name'] = 'Deck, 1/2 in plywood %g x %g in (the cabinet floor)' % DECK

    def add(name, color, layer, faces, kind='mesh'):
        P.append(dict(name=name, color=color, layer=layer, kind=kind, data=faces, ex=(0.0, 0.0, 0.0), opacity=None))
    rng = random.Random(4)
    # cabinet
    for sx in (-1, 1):
        add('Cabinet side, 1/2 in ply', 'ply', 'Cabinet',
            box(min(sx * CX, sx * (CX - PLY)), max(sx * CX, sx * (CX - PLY)), -CY, CY, DECK_TOP, ZB - PLY))
    add('Cabinet top, 1/2 in ply 21 x 34 in', 'ply', 'Cabinet', box(-CX, CX, -CY, CY, ZB - PLY, ZB))
    add('Front door (bulk storage), 1/2 in ply', 'ply', 'Cabinet',
        box(-CX + PLY + 0.06, CX - PLY - 0.06, CY - PLY, CY, DECK_TOP + 0.06, ZB - PLY - 0.06))
    add('Front door knob', 'knob', 'Cabinet', cyl((CX - PLY - 1.5, CY + 0.3, (DECK_TOP + ZB) / 2), (0, 1, 0), 0.3, 0.6, seg=10))
    # cubbies behind the back doors
    xa, xb = -CX + PLY, CX - PLY
    yb0, yb1 = -CY + RECESS, -CY + RECESS + 10.0
    z0, z1 = DECK_TOP, ZB - PLY
    shell = box(xa, xb, yb1, yb1 + 0.25, z0, z1)
    for i in (1, 2, 3):
        x = xa + i * (xb - xa) / 4
        shell += box(x - 0.125, x + 0.125, yb0, yb1, z0, z1)
    for j in (1, 2):
        z = z0 + j * (z1 - z0) / 3
        shell += box(xa, xb, yb0, yb1, z - 0.125, z + 0.125)
    add('Cubby grid, 1/4 in ply, 12 cubbies 4.8 x 4.7 x 10 in', 'ply', 'Cabinet', shell)
    boxes, cards = {}, []
    for i in range(4):
        for j in range(3):
            cx0 = xa + i * (xb - xa) / 4 + 0.4
            cx1 = xa + (i + 1) * (xb - xa) / 4 - 0.4
            cz0 = z0 + j * (z1 - z0) / 3 + 0.2
            c = ['blue', 'red', 'yellow', 'tote'][(i + j) % 4]
            boxes.setdefault(c, []).extend(box(cx0, cx1, yb0 + 0.4, yb0 + 8.4, cz0, cz0 + 3.4))
            cards += box((cx0 + cx1) / 2 - 1.0, (cx0 + cx1) / 2 + 1.0, yb0 + 0.37, yb0 + 0.4, cz0 + 1.6, cz0 + 2.6)
    for c, f in boxes.items():
        add('Parts boxes in the cubbies', c, 'Stock', f)
    add('Parts box labels', 'card', 'Stock', cards)
    # back doors
    for sx in (-1, 1):
        for nm, colr, faces in door_faces():
            f = faces if sx > 0 else mirror_x(faces)
            if opened:
                f = rot_z(f, (sx * CX, -CY), sx * DOOR_OPEN)
            add(nm + (' (right door)' if sx > 0 else ' (left door)'), colr,
                'Stock' if nm.startswith(('Parts jars', 'Jar lids')) else 'Doors', f)
    # top trays: fixed tier 0, then two tiers per side on the arms
    sh, heaps = tray(-T0_X, T0_X, -CY, CY, ZB, 4, 8, rng, floor=False)
    add('Fixed top tray, 32 compartments (walls on the cabinet top)', 'ply', 'Trays', sh)
    for c, f in heaps.items():
        add('Tray stock (fixed tray)', c, 'Stock', f)
    for sx in (-1, 1):
        for k in (1, 2):
            s = k * SLIDE if opened else 0.0
            x0, x1 = 0.15 + s, 10.35 + s
            if sx < 0:
                x0, x1 = -x1, -x0
            sh, heaps = tray(x0, x1, -CY, CY, ZB + k * TT, 3, 8, rng)
            side = 'right' if sx > 0 else 'left'
            add('Cantilever tray, tier %d %s, 24 compartments, 10.2 x 34 x 3 in' % (k, side), 'tray', 'Trays', sh)
            for c, f in heaps.items():
                add('Tray stock (tier %d %s)' % (k, side), c, 'Stock', f)
        for sy in (-1, 1):
            y0, y1 = sorted((sy * (CY + 0.05), sy * (CY + 0.24)))
            pivots = []
            for pts in arm_points(sx, opened):
                add('Cantilever arm, 3/16 x 5/8 in steel flat bar', 'steel', 'Arms', flat_bar(pts[0], pts[2], y0, y1))
                for x, z in pts:
                    pivots += cyl((x, sy * (CY + 0.3), z), (0, 1, 0), 0.2, 0.7, seg=8)
            add('Arm pivot bolts, 1/4 in shoulder bolts', 'bolt', 'Arms', pivots)
    # lid
    for nm, colr, ly, data, kind in lid_faces():
        if not opened and not nm.startswith('Lid piano hinge'):
            data = lid_close(data)
        add(nm, colr, ly, data, kind)
    if opened:
        for sx in (-1, 1):
            add('Lid stay, pinned at both ends', 'steel', 'Lid',
                tube([(sx * 6.875, CY - 1.3, Z_HINGE + 9.0), (sx * 6.875, 9.0, ZB + TT + 0.2)], 0.2, 8))
        # tools from the first store's pegboard, moved onto the lid lining
        tools, _m = build_store()
        dy, dz = (CY - 1.25) - (YP - 0.125), (Z_HINGE + 4.0) - TOP
        for p in tools:
            if p['layer'] == 'Tools' and p['ex'][1] < 0:
                add(p['name'], p['color'], 'Tools', [[(v[0], v[1] + dy, v[2] + dz) for v in f] for f in p['data']])
        hooks = []                                          # a lower row of carded parts
        for x, colr in ((-5.0, 'red'), (-2.0, 'yellow'), (2.0, 'blue'), (5.0, 'yellow')):
            zh = Z_HINGE + 6.5
            hooks += tube([(x, CY - 1.25, zh), (x, CY - 1.25 - 3.4, zh + 0.3)], 0.08, 6)
            for y in (CY - 2.4, CY - 3.4):
                add('Carded parts (blister pack)', colr, 'Tools', box(x - 1.3, x + 1.3, y - 0.04, y + 0.04, zh - 3.65, zh + 0.35))
                add('Blister with parts', 'steel', 'Tools', box(x - 0.7, x + 0.7, y - 0.4, y - 0.04, zh - 3.1, zh - 1.2))
        add('Pegboard hooks (lower row)', 'steel', 'Tools', hooks)
    # prop legs: down when open, slid up for towing
    lift = 0.0 if opened else 12.0
    for sy in (-1, 1):
        yl = sy * (YC + OD)
        for sx in (-1, 1):
            x = sx * 6.0
            add('Prop leg, 1/2 in EMT', 'conduit', 'Legs', tube([(x, yl, 0.4 + lift), (x, yl, ZO + 1.2 + lift)]))
            add('Prop leg foot', 'rubber', 'Legs', cyl((x, yl, 0.2 + lift), (0, 0, 1), 0.9, 0.4, seg=14))
            y_lo, y_hi = sorted((sy * (YC - RP - 0.1), yl + sy * (RP + 0.1)))
            add('Prop leg clamp', 'bolt', 'Legs', box(x - 0.5, x + 0.5, y_lo, y_hi, ZO - 0.5, ZO + 0.5))
    n_comp = 32 + 4 * 24
    meta.update(top_closed=Z_HINGE, lid_top=LID_TOP, width_open=2 * (10.35 + 2 * SLIDE), compartments=n_comp)
    return P, meta
