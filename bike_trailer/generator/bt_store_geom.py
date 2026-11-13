
"""Mobile hardware store: a variation on the version 4 trailer (2026-11-13).
Loaded after bt_geom.py and bt4_geom.py.  The trailer is unchanged; its
21 x 34 in deck becomes the floor of a plywood cabinet:
  back face (customer side, -Y): 14 drawers, 12 small-parts and 2 wide,
      with label cards; one is shown pulled out
  top, back half: two-step display of 8 open-front hopper bins
  top, over the axle: a double-sided pegboard in a 1x2 frame with a sign;
      tools and carded parts on the customer face, rope and cord on the other
  top, front half: lidded stock tote and cash box
  front face (+Y, tow side): door to the bulk storage behind the drawers
  4 prop legs clamp to the cross members to hold it level when unhitched.
A first sketch: sizes are picked to fit the deck, not measured."""

DECK_TOP = ZI + RP + 0.5
CX, CY = DECK[0] / 2.0, DECK[1] / 2.0     # cabinet footprint = the deck
CAB_H = 16.0
TOP = DECK_TOP + CAB_H                     # counter (cabinet top)
PLY = 0.5
YP = 0.0                                   # pegboard centre plane, over the axle
PH = 22.0                                  # pegboard frame height above the counter
DG = 0.12                                  # gap between drawer fronts
DRAWER_ROWS = [(4.6, 2), (3.4, 4), (3.4, 4), (3.4, 4)]   # (height, columns), bottom up
OPEN = (2, 1)                              # the drawer shown pulled out
PULL = 6.0
BIN_X = (-7.875, -2.625, 2.625, 7.875)
SIGN_Z = (TOP + PH + 0.75, TOP + PH + 4.75)
COL.update({
    'ply': (0.87, 0.76, 0.58, 1.0), 'drawer': (0.72, 0.19, 0.14, 1.0), 'card': (0.96, 0.95, 0.90, 1.0),
    'knob': (0.14, 0.14, 0.15, 1.0), 'bin': (0.15, 0.36, 0.72, 1.0), 'peg': (0.58, 0.42, 0.27, 1.0),
    'steel': (0.63, 0.65, 0.68, 1.0), 'red': (0.82, 0.16, 0.12, 1.0), 'yellow': (0.96, 0.76, 0.10, 1.0),
    'blue': (0.18, 0.40, 0.78, 1.0), 'wood': (0.74, 0.54, 0.32, 1.0), 'zinc': (0.72, 0.74, 0.76, 1.0),
    'brass': (0.80, 0.64, 0.28, 1.0), 'black': (0.22, 0.22, 0.23, 1.0), 'rope': (0.86, 0.80, 0.64, 1.0),
    'cord': (0.96, 0.50, 0.10, 1.0), 'tote': (0.34, 0.36, 0.40, 1.0), 'sign': (0.72, 0.19, 0.14, 1.0),
    'letter': (0.97, 0.96, 0.92, 1.0), 'rubber': (0.10, 0.10, 0.11, 1.0)})


def ext(poly, O, U, V, N):
    """Prism: polygon (u, v) in the plane O + uU + vV, extruded by the vector N."""
    P = lambda u, v, t: tuple(O[k] + U[k] * u + V[k] * v + N[k] * t for k in range(3))
    a = [P(u, v, 0.0) for u, v in poly]
    b = [P(u, v, 1.0) for u, v in poly]
    n = len(poly)
    return [list(reversed(a)), b] + [[a[i], a[(i + 1) % n], b[(i + 1) % n], b[i]] for i in range(n)]


def torus_y(c, R, r, seg=28, rseg=8):
    """Torus with its axis along Y: a coil hanging flat against the pegboard."""
    return [[(c[0] + (v[1] - c[1]), c[1] + (v[0] - c[0]), v[2]) for v in f] for f in torus(c, R, r, seg, rseg)]


def hook(x, z, L, s):
    """Pegboard hook at grid point (x, z), sticking out L in on side s (-1 customer face, +1 front)."""
    yf = YP + s * 0.125
    return tube([(x, yf, z), (x, yf + s * L, z + 0.3)], 0.08, 6)


LETTERS = {
    'H': [((0, 0), (0, 6)), ((4, 0), (4, 6)), ((0, 3), (4, 3))],
    'A': [((0, 0), (2, 6)), ((2, 6), (4, 0)), ((0.9, 2.4), (3.1, 2.4))],
    'R': [((0, 0), (0, 6)), ((0, 6), (3, 6)), ((3, 6), (4, 5)), ((4, 5), (4, 4)), ((4, 4), (3, 3)), ((3, 3), (0, 3)),
          ((1.6, 3), (4, 0))],
    'D': [((0, 0), (0, 6)), ((0, 6), (2.8, 6)), ((2.8, 6), (4, 4.8)), ((4, 4.8), (4, 1.2)), ((4, 1.2), (2.8, 0)),
          ((2.8, 0), (0, 0))],
    'W': [((0, 6), (1, 0)), ((1, 0), (2, 4)), ((2, 4), (3, 0)), ((3, 0), (4, 6))],
    'E': [((0, 0), (0, 6)), ((0, 6), (4, 6)), ((0, 3), (3, 3)), ((0, 0), (4, 0))],
}


def lettering(text, zc, height, y_face, s):
    """Block letters standing 0.12 in proud of a sign face at y_face, readable from side s."""
    u = height / 6.0
    w = 0.75 * u
    pitch = 5.6
    x_start = -(len(text) * pitch - 1.6) / 2.0
    faces = []
    for i, ch in enumerate(text):
        for p, q in LETTERS[ch]:
            p = ((x_start + i * pitch + p[0]) * u, zc + (p[1] - 3.0) * u)
            q = ((x_start + i * pitch + q[0]) * u, zc + (q[1] - 3.0) * u)
            if s > 0:                                   # read from +Y: mirror
                p, q = (-p[0], p[1]), (-q[0], q[1])
            dx, dz = q[0] - p[0], q[1] - p[1]
            L = math.hypot(dx, dz)
            ux, uz = dx / L, dz / L
            nx, nz = -uz * w / 2, ux * w / 2
            a = (p[0] - ux * w / 2, p[1] - uz * w / 2)
            b = (q[0] + ux * w / 2, q[1] + uz * w / 2)
            poly = [(a[0] + nx, a[1] + nz), (b[0] + nx, b[1] + nz), (b[0] - nx, b[1] - nz), (a[0] - nx, a[1] - nz)]
            faces += ext(poly, (0.0, y_face, 0.0), (1, 0, 0), (0, 0, 1), (0.0, s * 0.12, 0.0))
    return faces


def hopper_bin(xc, y0, z0, stock):
    """Open-front hopper bin, front edge at y0 (customer side), standing on z0."""
    BW, BD, HB, HF, t = 5.0, 6.6, 4.5, 2.4, 0.1
    x0, x1 = xc - BW / 2, xc + BW / 2
    prof = [(0.0, 0.0), (BD, 0.0), (BD, HB), (2.2, HB), (0.0, HF)]
    shell = (box(x0, x1, y0, y0 + BD, z0, z0 + t) + box(x0, x1, y0 + BD - t, y0 + BD, z0, z0 + HB)
             + box(x0 + t, x1 - t, y0, y0 + t, z0, z0 + HF)
             + ext(prof, (x0, y0, z0), (0, 1, 0), (0, 0, 1), (t, 0, 0))
             + ext(prof, (x1 - t, y0, z0), (0, 1, 0), (0, 0, 1), (t, 0, 0)))
    heap = ext([(t, t), (BD - t, t), (BD - t, 3.0), (t, 1.9)], (x0 + t, y0, z0), (0, 1, 0), (0, 0, 1),
               (BW - 2 * t, 0, 0))
    card = box(xc - 1.1, xc + 1.1, y0 - 0.03, y0, z0 + 0.5, z0 + 1.6)
    return [('Hopper bin, 5 x 6.6 x 4.5 in, open front', 'bin', 'Display', shell),
            ('Bin stock (%s fasteners)' % stock, stock, 'Stock', heap),
            ('Bin label', 'card', 'Display', card)]


def pegboard_plate():
    x0, x1, z0, z1 = -CX + 0.75, CX - 0.75, TOP + 0.75, TOP + PH
    y0 = YP - 0.125
    holes = []
    for i in range(19):
        for j in range(20):
            x, z = -9.0 + i, TOP + 1.5 + j
            holes.append([(x + 0.125 * math.cos(math.pi * k / 3), y0, z + 0.125 * math.sin(math.pi * k / 3))
                          for k in range(6)])
    return dict(loop=[(x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1)], vec=(0.0, 0.25, 0.0), holes=holes)


def drawer_parts():
    """Drawer fronts and pulls on the back face; the OPEN one with its box and some bolts."""
    out = []
    xa, xb = -CX + PLY, CX - PLY
    yfr = -CY - 0.1                     # outer face of the fronts (0.1 in proud of the carcass)
    z = DECK_TOP + DG
    for ri, (h, ncol) in enumerate(DRAWER_ROWS):
        w = (xb - xa - (ncol + 1) * DG) / ncol
        for ci in range(ncol):
            x0 = xa + DG + ci * (w + DG)
            x1 = x0 + w
            xc, zc = (x0 + x1) / 2, z + h / 2
            dy = -PULL if (ri, ci) == OPEN else 0.0
            S = lambda faces, dy=dy: [[(v[0], v[1] + dy, v[2]) for v in f] for f in faces]
            small = ncol == 4
            out.append(('Drawer front, %s, 1/2 in ply painted' % ('small parts' if small else 'wide'), 'drawer',
                        'Drawers', S(box(x0, x1, yfr, yfr + 0.5, z, z + h))))
            if small:
                out.append(('Knob', 'knob', 'Drawers', S(cyl((xc, yfr - 0.3, zc - 0.6), (0, 1, 0), 0.27, 0.6, seg=10))))
                out.append(('Label card', 'card', 'Drawers', S(box(xc - 1.0, xc + 1.0, yfr - 0.03, yfr, zc + 0.1, zc + 1.0))))
            else:
                out.append(('Bar pull', 'knob', 'Drawers', S(cyl((xc, yfr - 0.55, zc - 0.5), (1, 0, 0), 0.14, 4.4, seg=8))))
                for sx in (-1, 1):
                    out.append(('Bar pull post', 'knob', 'Drawers',
                                S(cyl((xc + sx * 1.9, yfr - 0.3, zc - 0.5), (0, 1, 0), 0.12, 0.6, seg=8))))
                out.append(('Label card', 'card', 'Drawers', S(box(xc - 1.4, xc + 1.4, yfr - 0.03, yfr, zc + 0.5, zc + 1.6))))
            if (ri, ci) == OPEN:
                t = 0.25
                bx0, bx1 = x0 + 0.15, x1 - 0.15
                by0, by1 = yfr + 0.5, yfr + 0.5 + 14.0
                bz0, bz1 = z + 0.1, z + h - 0.35
                faces = (box(bx0, bx1, by0, by1, bz0, bz0 + t) + box(bx0, bx0 + t, by0, by1, bz0, bz1)
                         + box(bx1 - t, bx1, by0, by1, bz0, bz1) + box(bx0, bx1, by1 - t, by1, bz0, bz1))
                out.append(('Drawer box, 1/4 in ply, 14 in deep (shown pulled out)', 'ply', 'Drawers', S(faces)))
                bolts = []
                for k in range(9):
                    bx = bx0 + 0.9 + (k % 3) * (bx1 - bx0 - 1.8) / 2
                    by = by0 + 0.9 + (k // 3) * 1.5
                    ax = (1, 0, 0) if (k + k // 3) % 2 else (0, 1, 0)
                    bolts += cyl((bx, by, bz0 + t + 0.13), ax, 0.12, 1.0, seg=6)
                out.append(('Bolts in the open drawer', 'zinc', 'Stock', S(bolts)))
        z += h + DG
    return out


def build_store():
    """The v4 trailer (not exploded) plus the store.  ex offsets explode only the store."""
    P, meta = build()
    for p in P:
        p['ex'] = (0.0, 0.0, 0.0)
        if p['layer'] == 'Deck':
            p['name'] = 'Deck, 1/2 in plywood %g x %g in (the cabinet floor)' % DECK

    def add(name, color, layer, faces, ex=(0.0, 0.0, 0.0), kind='mesh'):
        P.append(dict(name=name, color=color, layer=layer, kind=kind, data=faces, ex=ex, opacity=None))

    # cabinet carcass and door
    EC = (0.0, 0.0, 14.0)
    for sx in (-1, 1):
        add('Cabinet side, 1/2 in ply %g x %g in' % (2 * CY, CAB_H - PLY), 'ply', 'Cabinet',
            box(min(sx * CX, sx * (CX - PLY)), max(sx * CX, sx * (CX - PLY)), -CY, CY, DECK_TOP, TOP - PLY), EC)
    add('Cabinet top (counter), 1/2 in ply %g x %g in' % (2 * CX, 2 * CY), 'ply', 'Cabinet',
        box(-CX, CX, -CY, CY, TOP - PLY, TOP), EC)
    add('Divider behind the drawers, 1/2 in ply', 'ply', 'Cabinet',
        box(-CX + PLY, CX - PLY, -1.25, -0.75, DECK_TOP, TOP - PLY), EC)
    add('Door to the bulk storage, 1/2 in ply', 'ply', 'Cabinet',
        box(-CX + PLY + 0.06, CX - PLY - 0.06, CY - PLY, CY, DECK_TOP + 0.06, TOP - PLY - 0.06), EC)
    for zh in (DECK_TOP + 2.5, TOP - 3.0):
        add('Door hinge', 'steel', 'Cabinet', cyl((-CX + PLY + 0.1, CY + 0.15, zh), (0, 0, 1), 0.15, 2.0, seg=8), EC)
    add('Door knob', 'knob', 'Cabinet', cyl((CX - PLY - 1.5, CY + 0.3, (DECK_TOP + TOP) / 2), (0, 1, 0), 0.3, 0.6, seg=10), EC)
    # drawers
    for nm, colr, ly, faces in drawer_parts():
        add(nm, colr, ly, faces, (0.0, -14.0, 14.0))
    # bin display
    ED = (0.0, 0.0, 30.0)
    add('Display riser, 1/2 in ply box %g x 6.8 x 3 in' % (2 * CX), 'ply', 'Display', box(-CX, CX, -10.0, -3.2, TOP, TOP + 3.0), ED)
    stock = ['zinc', 'brass', 'black', 'zinc', 'black', 'zinc', 'brass', 'zinc']
    k = 0
    for y0, z0 in ((-CY + 0.2, TOP), (-10.0, TOP + 3.0)):
        for xc in BIN_X:
            for nm, colr, ly, faces in hopper_bin(xc, y0, z0, stock[k]):
                add(nm, colr, ly, faces, ED)
            k += 1
    add('Stock tote, 9 x 12.4 x 7 in', 'tote', 'Stock', box(-9.8, -0.8, 4.0, 16.4, TOP, TOP + 7.0), (0.0, 10.0, 30.0))
    add('Stock tote lid', 'yellow', 'Stock', box(-10.0, -0.6, 3.8, 16.6, TOP + 7.0, TOP + 7.6), (0.0, 10.0, 30.0))
    add('Cash box', 'blue', 'Stock', box(2.5, 9.0, 9.5, 15.0, TOP, TOP + 3.0), (0.0, 10.0, 30.0))
    add('Cash box handle', 'knob', 'Stock', cyl((5.75, 12.25, TOP + 3.15), (1, 0, 0), 0.15, 3.0, seg=8), (0.0, 10.0, 30.0))
    # pegboard frame, board and sign
    EP = (0.0, 0.0, 44.0)
    for sx in (-1, 1):
        add('Pegboard upright, 1x2 (0.75 x 1.5 in) x %g in' % PH, 'ply', 'Pegboard',
            box(min(sx * CX, sx * (CX - 0.75)), max(sx * CX, sx * (CX - 0.75)), YP - 0.75, YP + 0.75, TOP, TOP + PH), EP)
        gx = CX - 1.25 if sx > 0 else -CX + 0.75
        for sy, L in ((1, 3.0), (-1, 2.4)):
            add('Gusset, 1/2 in ply triangle (screwed to the counter)', 'ply', 'Pegboard',
                ext([(0.0, 0.0), (L, 0.0), (0.0, L)], (gx, YP + sy * 0.75, TOP), (0, sy, 0), (0, 0, 1), (0.5, 0, 0)), EP)
    add('Pegboard top rail, 1x2', 'ply', 'Pegboard', box(-CX, CX, YP - 0.75, YP + 0.75, TOP + PH, TOP + PH + 0.75), EP)
    add('Pegboard bottom rail, 1x2', 'ply', 'Pegboard',
        box(-CX + 0.75, CX - 0.75, YP - 0.75, YP + 0.75, TOP, TOP + 0.75), EP)
    add('Pegboard, 1/4 in hardboard %g x %g in, 1 in hole grid (both faces used)' % (2 * CX - 1.5, PH - 0.75), 'peg',
        'Pegboard', pegboard_plate(), EP, kind='plate')
    add('Sign board, 1/2 in ply painted, 21 x 4 in', 'sign', 'Sign', box(-CX, CX, YP - 0.25, YP + 0.25, SIGN_Z[0], SIGN_Z[1]), EP)
    for s in (-1, 1):
        add('Sign lettering, HARDWARE (%s face)' % ('customer' if s < 0 else 'tow side'), 'letter', 'Sign',
            lettering('HARDWARE', sum(SIGN_Z) / 2, 2.6, YP + s * 0.25, s), EP)
    # customer face: tools and carded parts
    ET = (0.0, -8.0, 44.0)
    hooks = []
    tz = lambda dz: TOP + dz
    for x in (-9.0, -7.0):                                           # hammer: head on two hooks
        hooks += hook(x, tz(19.5), 2.0, -1)
    add('Claw hammer head', 'steel', 'Tools', box(-9.3, -6.9, -1.9, -0.9, tz(19.6), tz(20.6))
        + cyl((-6.65, -1.4, tz(20.1)), (1, 0, 0), 0.5, 0.5, seg=12), ET)
    add('Claw hammer handle', 'wood', 'Tools', cyl((-8.0, -1.4, tz(19.6 - 5.25)), (0, 0, 1), 0.42, 10.5, seg=12), ET)
    for i, Lw in enumerate((5.0, 6.0, 7.0, 8.0)):                    # combination wrenches
        x = -5.0 + i
        hooks += hook(x, tz(20.5), 1.6, -1)
        zr = tz(20.36)
        add('Combination wrench, %g in' % Lw, 'steel', 'Tools',
            torus_y((x, -1.2, zr), 0.32, 0.1, seg=16, rseg=6) + box(x - 0.2, x + 0.2, -1.28, -1.12, zr - Lw, zr - 0.3)
            + cyl((x, -1.2, zr - Lw), (0, 1, 0), 0.36, 0.16, seg=12), ET)
    add('Screwdriver rack, wood strip', 'wood', 'Tools', box(0.0, 5.4, -2.3, -0.125, tz(17.5), tz(18.0)), ET)
    for i, Ls in enumerate((3.5, 4.5, 5.5, 4.5, 3.5)):
        x = 0.6 + i * 1.05
        add('Screwdriver handle', 'red' if i % 2 == 0 else 'yellow', 'Tools',
            cyl((x, -1.3, tz(18.0 + 1.4)), (0, 0, 1), 0.36, 2.8, seg=12), ET)
        add('Screwdriver shaft', 'steel', 'Tools', cyl((x, -1.3, tz(18.0 - Ls / 2)), (0, 0, 1), 0.09, Ls, seg=6), ET)
    hooks += hook(7.0, tz(20.5), 1.6, -1)                            # tape measure
    add('Tape measure, 25 ft', 'yellow', 'Tools', cyl((7.0, -1.25, tz(19.15)), (0, 1, 0), 1.25, 1.1, seg=20), ET)
    add('Tape measure blade tip', 'steel', 'Tools', box(8.1, 8.4, -1.5, -1.0, tz(18.0), tz(18.3)), ET)
    hooks += hook(7.0, tz(15.5), 1.6, -1)                            # pliers
    add('Pliers jaws', 'steel', 'Tools', box(6.8, 7.2, -1.4, -1.15, tz(13.6), tz(15.7)), ET)
    add('Pliers handles', 'red', 'Tools', tube([(6.95, -1.27, tz(13.6)), (6.3, -1.27, tz(9.2))], 0.17, 8)
        + tube([(7.05, -1.27, tz(13.6)), (7.7, -1.27, tz(9.2))], 0.17, 8), ET)
    for x, colr in ((-4.0, 'yellow'), (0.0, 'blue'), (4.0, 'red')):  # carded parts on long hooks
        hooks += hook(x, tz(11.5), 4.4, -1)
        for y in (-1.4, -2.4, -3.4):
            zb = tz(11.85 - 4.0)
            add('Carded parts (blister pack)', colr, 'Tools', box(x - 1.5, x + 1.5, y - 0.04, y + 0.04, zb, zb + 4.0), ET)
            add('Blister with parts', 'steel', 'Tools', box(x - 0.8, x + 0.8, y - 0.45, y - 0.04, zb + 0.6, zb + 2.6), ET)
    add('Pegboard hooks (customer face)', 'steel', 'Tools', hooks, ET)
    # tow-side face: rope and an extension cord
    EF = (0.0, 8.0, 44.0)
    hooks = hook(-5.0, tz(18.5), 2.0, 1) + hook(4.0, tz(18.5), 2.0, 1)
    add('Pegboard hooks (tow-side face)', 'steel', 'Tools', hooks, EF)
    add('Rope, 50 ft coil', 'rope', 'Tools', torus_y((-5.0, 1.3, tz(18.58 - 2.05)), 2.6, 0.55), EF)
    add('Extension cord, 25 ft coil', 'cord', 'Tools', torus_y((4.0, 1.3, tz(18.58 - 2.35)), 2.8, 0.45), EF)
    # prop legs for parking
    for sy in (-1, 1):
        yl = sy * (YC + OD)
        for sx in (-1, 1):
            x = sx * 6.0
            add('Prop leg, 1/2 in EMT (slides up for towing)', 'conduit', 'Legs', tube([(x, yl, 0.4), (x, yl, ZO + 1.2)]))
            add('Prop leg foot', 'rubber', 'Legs', cyl((x, yl, 0.2), (0, 0, 1), 0.9, 0.4, seg=14))
            y_lo, y_hi = sorted((sy * (YC - RP - 0.1), yl + sy * (RP + 0.1)))
            add('Prop leg clamp (two-hole strap pair, wing nut)', 'bolt', 'Legs', box(x - 0.5, x + 0.5, y_lo, y_hi, ZO - 0.5, ZO + 0.5))
    meta.update(counter=TOP, top=SIGN_Z[1], cab_h=CAB_H, n_drawers=sum(n for _h, n in DRAWER_ROWS))
    return P, meta
