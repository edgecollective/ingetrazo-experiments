"""Pallet-wood cold frame: 1x4 deck boards run horizontally, 2x4 stringer
offcuts as corner posts, a lapped two-layer 1x4 lid sandwiching plastic.
Pure Python.  Inches, Z up.  Box front at y = 0 (low side), back at y = D."""
import math

BW, BT = 3.5, 0.75          # pallet 1x4 deck board: width, thickness
PW, PT = 3.5, 1.5           # pallet 2x4 stringer
BL = 40.0                   # deck board length on a 48 x 40 pallet
W, D = 40.0, 40.0           # box outside: full-length boards front/back, sides cut to fit between
NF, NB, NS = 2, 3, 2        # boards high: front, back, sides (plus the angled board)
HF, HB = NF * BW, NB * BW   # 7 and 10.5
TH = math.atan2(HB - HF, D)
LV = math.hypot(D, HB - HF)  # lid length along the slope
SHADES = [(0.74, 0.64, 0.50, 1.0), (0.69, 0.58, 0.44, 1.0), (0.78, 0.68, 0.54, 1.0), (0.65, 0.55, 0.42, 1.0),
          (0.72, 0.60, 0.45, 1.0)]
COL = {'post': (0.60, 0.48, 0.34, 1.0), 'plastic': (0.86, 0.94, 0.98, 1.0), 'soil': (0.30, 0.22, 0.16, 1.0),
       'metal': (0.40, 0.41, 0.44, 1.0)}

_n = [0]


def shade():
    _n[0] += 1
    return SHADES[(_n[0] * 7) % len(SHADES)]


def ztop(y):
    return HF + (HB - HF) * y / D


def part(parts, layer, name, color, kind, data, sub=None, opacity=None, length=None, stock=None):
    parts.append(dict(layer=layer, name=name, color=color, kind=kind, data=data, sub=sub, opacity=opacity,
                      length=length, stock=stock))


def box_parts():
    P = []

    def B(layer, name, color, b, **kw):
        part(P, layer, name, color, 'box', tuple(b), **kw)
    for k in range(NF):
        B('Box', 'Front board 1x4 x %g' % W, shade(), (0, W, 0, BT, k * BW, (k + 1) * BW), length=W, stock='1x4')
    for k in range(NB):
        B('Box', 'Back board 1x4 x %g' % W, shade(), (0, W, D - BT, D, k * BW, (k + 1) * BW), length=W, stock='1x4')
    for x0 in (0.0, W - BT):
        for k in range(NS):
            B('Box', 'Side board 1x4 x %g (cut to fit)' % (D - 2 * BT), shade(), (x0, x0 + BT, BT, D - BT, k * BW, (k + 1) * BW),
              length=D - 2 * BT, stock='1x4')
    vw = BW / math.cos(TH)
    prof = [(0.0, HF - vw), (D, HB - vw), (D, HB), (0.0, HF)]
    for x0 in (-BT, W):
        part(P, 'Box', 'Angled side board 1x4 (sets the tilt)', shade(), 'prism',
             ([(x0, y, z) for y, z in prof], (BT, 0.0, 0.0)), length=LV, stock='1x4')
    for xa in (BT, W - BT - PW):
        for ya in (BT, D - BT - PT):
            yb = ya + PT
            prof = [(ya, 0.0), (yb, 0.0), (yb, ztop(yb)), (ya, ztop(ya))]
            part(P, 'Posts', 'Corner post 2x4 (pallet stringer) %.1f in' % ztop(yb), COL['post'], 'prism',
                 ([(xa, y, z) for y, z in prof], (PW, 0.0, 0.0)), length=ztop(yb), stock='2x4')
    return P


def lid_point(u, v, w):
    c, s = math.cos(TH), math.sin(TH)
    return (u, v * c - w * s, HF + v * s + w * c)


def lid_parts():
    """Two lapped 1x4 frames with the plastic between; built in lid
    coordinates (u across, v up the slope, w out of the lid)."""
    P = []
    c, s = math.cos(TH), math.sin(TH)

    def L(layer, name, color, u0, u1, v0, v1, w0, t, **kw):
        loop = [lid_point(u0, v0, w0), lid_point(u1, v0, w0), lid_point(u1, v1, w0), lid_point(u0, v1, w0)]
        part(P, layer, name, color, 'prism', (loop, (0.0, -s * t, c * t)), sub='lid', **kw)
    wa, wp, wb = 0.0, BT, BT + 0.03
    for v0 in (0.0, LV - BW):           # bottom layer: rails run the full width
        L('Lid', 'Lid rail, bottom layer 1x4 x %g' % W, shade(), 0.0, W, v0, v0 + BW, wa, BT, length=W, stock='1x4')
    for u0 in (0.0, W - BW):
        L('Lid', 'Lid stile, bottom layer 1x4 x %.1f' % (LV - 2 * BW), shade(), u0, u0 + BW, BW, LV - BW, wa, BT,
          length=LV - 2 * BW, stock='1x4')
    L('Plastic', 'Clear plastic sheet (6 mil greenhouse film or polycarbonate)', COL['plastic'], 0.0, W, 0.0, LV, wp, 0.03,
      opacity=0.35)
    for u0 in (0.0, W - BW):            # top layer: stiles run the full length, so every corner laps
        L('Lid', 'Lid stile, top layer 1x4 x %.1f' % LV, shade(), u0, u0 + BW, 0.0, LV, wb, BT, length=LV, stock='1x4')
    for v0 in (0.0, LV - BW):
        L('Lid', 'Lid rail, top layer 1x4 x %g' % (W - 2 * BW), shade(), BW, W - BW, v0, v0 + BW, wb, BT,
          length=W - 2 * BW, stock='1x4')
    for u0 in (6.0, W - 9.0):           # two hinges at the back (high) edge
        part(P, 'Lid', 'Strap hinge', COL['metal'], 'box', (u0, u0 + 3.0, D - 0.1, D + 0.05, HB - 3.0, HB))
        L('Lid', 'Strap hinge (lid leaf)', COL['metal'], u0, u0 + 3.0, LV - 5.0, LV, 2 * BT + 0.03, 0.06)
    return P


def pallet_parts():
    """A GMA 48 x 40 pallet: three stringers, 7 top and 5 bottom deck boards."""
    P = []
    for y0 in (0.0, 20.0 - PT / 2, 40.0 - PT):
        part(P, 'Pallet (source)', 'Stringer 2x4 x 48', COL['post'], 'box', (0.0, 48.0, y0, y0 + PT, BT, BT + PW))
    for n, z0 in ((7, BT + PW), (5, 0.0)):
        for i in range(n):
            x0 = i * (48.0 - BW) / (n - 1)
            part(P, 'Pallet (source)', 'Deck board 1x4 x 40', shade(), 'box', (x0, x0 + BW, 0.0, 40.0, z0, z0 + BT))
    return P


def cut_list():
    rows = {}
    for p in box_parts() + lid_parts():
        if p['stock']:
            key = (p['stock'], p['name'].split(' 1x4')[0].split(' 2x4')[0], round(p['length'], 1))
            rows[key] = rows.get(key, 0) + 1
    return rows
