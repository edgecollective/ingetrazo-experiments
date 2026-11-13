"""Black-and-white illustration set for bike trailer version 4: hidden-line
renders from IngeTrazo (shots4.py) plus to-scale drawings, one PDF.
Usage: bt4_print.py OUT_DIR RENDER_DIR"""
import math
import os
import sys
from types import SimpleNamespace

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Polygon, FancyArrowPatch, Circle, Rectangle
from PIL import Image, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
_ns = {}
exec(compile(open(os.path.join(HERE, 'bt_geom.py')).read() + open(os.path.join(HERE, 'bt4_geom.py')).read(), 'bt4', 'exec'), _ns)
B = SimpleNamespace(**_ns)

OUT, REN = sys.argv[1], sys.argv[2]
os.makedirs(os.path.join(OUT, 'pages'), exist_ok=True)
plt.rcParams.update({'font.family': 'DejaVu Sans', 'hatch.color': 'black', 'hatch.linewidth': 0.35, 'pdf.fonttype': 42})
LAND, PORT = (11.0, 8.5), (8.5, 11.0)
MM = B.MM


def frac(x, den=8):
    n = int(round(x * den)); w, r = divmod(n, den)
    if r == 0:
        return '%d' % w
    g = math.gcd(r, den)
    return ('%d %d/%d' % (w, r // g, den // g)) if w else '%d/%d' % (r // g, den // g)


def crop(path, pad=30):
    im = Image.open(path).convert('L')
    box = ImageOps.invert(im).point(lambda v: 255 if v > 12 else 0).getbbox()
    if box:
        x0, y0, x1, y1 = box
        im = im.crop((max(0, x0 - pad), max(0, y0 - pad), min(im.width, x1 + pad), min(im.height, y1 + pad)))
    return im


def page(size, title, subtitle=None):
    fig = plt.figure(figsize=size)
    fig.text(0.5, 1 - 0.45 / size[1], title, ha='center', va='top', fontsize=17, fontweight='bold')
    if subtitle:
        fig.text(0.5, 1 - 0.80 / size[1], subtitle, ha='center', va='top', fontsize=10, color='0.25')
    fig.text(0.98, 0.012, 'Bike trailer, version 4 (model)', ha='right', va='bottom', fontsize=7, color='0.4')
    return fig


def image(fig, name, left, bottom, width, height, caption=None):
    path = os.path.join(REN, name + '.png')
    sw, sh = fig.get_size_inches()
    if not os.path.exists(path):
        fig.text((left + width / 2) / sw, (bottom + height / 2) / sh, '[render missing: %s]' % name, ha='center')
        return
    im = crop(path)
    iw, ih = im.size
    s = min(width / iw, height / ih)
    w, h = iw * s, ih * s
    l, b = left + (width - w) / 2, bottom + (height - h) / 2
    ax = fig.add_axes([l / sw, b / sh, w / sw, h / sh])
    ax.imshow(im, cmap='gray', vmin=0, vmax=255, interpolation='lanczos')
    ax.axis('off')
    if caption:
        fig.text((left + width / 2) / sw, (bottom - 0.08) / sh, caption, ha='center', va='top', fontsize=9.5)


def scaled(fig, left, bottom, width, height, scale, x0, y0):
    sw, sh = fig.get_size_inches()
    ax = fig.add_axes([left / sw, bottom / sh, width / sw, height / sh])
    ax.set_xlim(x0, x0 + width * scale); ax.set_ylim(y0, y0 + height * scale)
    ax.set_aspect('equal'); ax.axis('off')
    return ax


def poly(ax, pts, hatch=None, ls='-', lw=0.9, fill='white', z=2):
    ax.add_patch(Polygon(pts, closed=True, facecolor=fill, edgecolor='black', hatch=hatch, linestyle=ls, lw=lw, zorder=z))


def rect(ax, x0, y0, w, h, z=2, **kw):
    kw.setdefault('facecolor', 'white'); kw.setdefault('edgecolor', 'black'); kw.setdefault('lw', 0.9)
    ax.add_patch(Rectangle((x0, y0), w, h, zorder=z, **kw))


def dim(ax, p1, p2, text, off, fs=8):
    dx, dy = p2[0] - p1[0], p2[1] - p1[1]
    L = math.hypot(dx, dy); nx, ny = -dy / L, dx / L
    a = (p1[0] + nx * off, p1[1] + ny * off); b = (p2[0] + nx * off, p2[1] + ny * off)
    if off:
        for p, q in ((p1, a), (p2, b)):
            ax.plot([p[0] + nx * off * 0.1, q[0] + nx * off * 0.08], [p[1] + ny * off * 0.1, q[1] + ny * off * 0.08],
                    color='black', lw=0.5, zorder=5)
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle='<->', mutation_scale=7, lw=0.6, color='black', zorder=5,
                                 shrinkA=0, shrinkB=0))
    ang = math.degrees(math.atan2(dy, dx))
    if ang > 90 or ang < -90:
        ang += 180
    ax.text((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, text, ha='center', va='center', rotation=ang, fontsize=fs, zorder=6,
            bbox=dict(facecolor='white', edgecolor='none', pad=0.6))


def note(ax, xy, xytext, text, fs=8, ha='left'):
    ax.annotate(text, xy=xy, xytext=xytext, fontsize=fs, ha=ha, va='center', zorder=7,
                bbox=dict(facecolor='white', edgecolor='none', pad=0.8),
                arrowprops=dict(arrowstyle='-', lw=0.5, color='black', shrinkA=0, shrinkB=1))


def circled(ax, xy, text, fs=9, leader_to=None):
    """A circled number like the hand sketch's marks."""
    if leader_to:
        ax.plot([xy[0], leader_to[0]], [xy[1], leader_to[1]], color='black', lw=0.6, zorder=6)
        ax.plot(*leader_to, marker='o', ms=3.2, color='black', zorder=8)
    ax.text(xy[0], xy[1], text, ha='center', va='center', fontsize=fs, fontweight='bold', zorder=9,
            bbox=dict(boxstyle='circle,pad=0.25', facecolor='white', edgecolor='black', lw=0.8))


def pipe2d(ax, pts, r=B.RP, lw=0.9, z=2):
    """Plan view of a pipe: its two edges from a centreline polyline."""
    left, right = [], []
    n = len(pts)
    for i, p in enumerate(pts):
        a = pts[max(i - 1, 0)]; b = pts[min(i + 1, n - 1)]
        tx, ty = b[0] - a[0], b[1] - a[1]
        L = math.hypot(tx, ty); nx, ny = -ty / L, tx / L
        left.append((p[0] + nx * r, p[1] + ny * r)); right.append((p[0] - nx * r, p[1] - ny * r))
    poly(ax, left + right[::-1], lw=lw, z=z)


def band2d(ax, d, half=None, lw=1.6):
    """A bend mark across the pipe at distance d along the loop."""
    (x, y), t = B.at(d)
    h = half or B.RP * 1.9
    ax.plot([x - t[1] * h, x + t[1] * h], [y + t[0] * h, y - t[0] * h], color='black', lw=lw, zorder=6,
            solid_capstyle='butt')


pts3, _L = B.path_points(B.loop_segments(), 0.0, step_deg=3.0)
LOOP = [(p[0], p[1]) for p in pts3]
XO, XI, YC, YS, RP, OD = B.XO, B.XI, B.YC, B.YS, B.RP, B.OD
W_OUT, L_OUT = 2 * XO + OD, 2 * YC + OD
CORNER = {10: 'front right', 42: 'back right', 70: 'back left', 102: 'front left'}

pdf_path = os.path.join(OUT, 'bike_trailer_v4_print.pdf')
names = []
with PdfPages(pdf_path) as pdf:
    def emit(fig, name):
        pdf.savefig(fig); fig.savefig(os.path.join(OUT, 'pages', name + '.png'), dpi=150); plt.close(fig); names.append(name)

    # 1 title
    fig = page(LAND, 'Bike Trailer, version 4',
               '1/2 in EMT conduit, closed loop  |  two inner bars  |  26 in wheels in laser-cut dropouts')
    image(fig, '00_overview', 0.4, 2.45, 10.2, 4.75, '1 Materials   >   2 Bent main frame   >   3 Assembled trailer   >   4 Exploded')
    facts = ['Main frame: one 10 ft length of 1/2 in EMT bent into a closed loop, %s x %s in outside. The two ends meet in a '
             'set-screw coupling at the front.' % (frac(W_OUT), frac(L_OUT)),
             'Bends start at the 10, 42, 70 and 102 in marks and use 8 in of conduit each, as in the hand sketch "version 4".',
             'Inner bars: two 36 in pieces from a second length, %s in inside the sides, bolted on top of the front and back.'
             % frac(XO - XI),
             'Each wheel hangs between a side (short dropout) and an inner bar (long dropout, one pipe higher), so the axle is level.',
             'Wheel size is estimated from the photo of the dry-fit frame. This version has no hitch (the sketch shows none).']
    for i, t in enumerate(facts):
        fig.text(0.6 / 11, (1.78 - i * 0.27) / 8.5, u'•  ' + t, fontsize=9.3, va='center')
    emit(fig, '01_title')

    # 2 assembled
    fig = page(LAND, 'The assembled trailer', 'With the optional plywood deck, and the bare frame')
    image(fig, '02_assembled', 0.3, 1.2, 5.1, 6.0, 'Assembled, with the deck')
    image(fig, '03_no_deck', 5.6, 1.2, 5.1, 6.0, 'Frame without the deck')
    emit(fig, '02_assembled')

    # 3 plan, front up like the sketch
    fig = page(LAND, 'Frame, from above (1:6.5)', 'Front at the top, as in the sketch. Wheels dashed; dropouts solid black')
    ax = scaled(fig, 0.6, 0.35, 9.8, 6.95, 6.5, -31.85, -24.0)
    pipe2d(ax, LOOP, z=2)
    for sx in (-1, 1):
        pipe2d(ax, [(sx * XI, -B.INNER_LEN / 2), (sx * XI, B.INNER_LEN / 2)], z=3)
        xw = sx * (XO + XI) / 2
        rect(ax, xw - B.TIRE_R, -B.WR, 2 * B.TIRE_R, 2 * B.WR, z=1, fill=False, ls=(0, (3, 2)), lw=0.7)
        for xb, inward in ((sx * XO, -sx), (sx * XI, sx)):
            xf = xb + inward * RP
            rect(ax, min(xf, xf + inward * B.PLATE), -22.5 * MM, B.PLATE, 45 * MM, z=4, facecolor='black', lw=0.3)
        for sy in (-1, 1):
            ax.plot(sx * XI, sy * YC, marker='o', ms=2.6, color='black', zorder=8)
    rect(ax, -0.9, YC - 0.46, 1.8, 0.92, z=5, hatch='||||', lw=0.7)
    ax.plot([-XO - RP - 1.0, XO + RP + 1.0], [0, 0], color='black', lw=0.45, ls='-.', zorder=1)
    dim(ax, (-XO - RP, -YC - RP), (XO + RP, -YC - RP), frac(W_OUT) + ' outside', -3.3)
    dim(ax, (-XO - RP, -YC - RP), (-XO - RP, YC + RP), frac(L_OUT) + ' outside', 3.6)
    dim(ax, (-XI, -8.0), (XI, -8.0), '%s between inner bars (centres)' % frac(2 * XI), 0.0, fs=7.5)
    dim(ax, (XI, 15.3), (XO, 15.3), frac(XO - XI), 0.0, fs=7)
    dim(ax, (-XO, 15.3), (-XI, 15.3), frac(XO - XI), 0.0, fs=7)
    dim(ax, (-XI, -B.INNER_LEN / 2), (-XI, B.INNER_LEN / 2), '36 inner bar', -2.4, fs=7.5)
    ax.text(0.0, YC + 2.3, 'FRONT (toward the bike)', ha='center', va='bottom', fontsize=9, fontweight='bold')
    ax.text(0.0, -YC - 6.6, 'back', ha='center', va='center', fontsize=8.5, color='0.25')
    note(ax, (0.9, YC + 0.3), (19.5, 19.6), 'set-screw coupling: the two\nends of the loop meet here', fs=7.5)
    note(ax, (XI, -YC), (19.5, -20.0), 'bolt #10-24 x 2 1/2: inner bar down\nthrough the cross member (4)', fs=7.5)
    note(ax, (XO - 1.0, 9.0), (19.5, 9.0), '26 in wheel (dashed), between\nthe side and the inner bar', fs=7.5)
    note(ax, (XO - RP - 0.1, 0.7), (19.5, 3.2), 'short dropout, on the side', fs=7.5)
    note(ax, (XI + RP + 0.1, -0.7), (19.5, -2.6), 'long dropout, on the inner bar', fs=7.5)
    note(ax, (-XO - RP - 1.0, 0.0), (-30.8, 0.0), 'axle line,\nmid-length', fs=7.5)
    note(ax, (XI, 12.0), (19.5, 14.2), 'inner bar sits on top of the\nfront and back cross members', fs=7.5)
    emit(fig, '03_plan')

    # 4 bending
    fig = page(LAND, 'Bending the main frame (one 10 ft conduit)',
               'Marks measured along the pipe from one end. Every bend is 90 degrees, the same way, flat in one plane')
    ax = scaled(fig, 0.5, 5.25, 10.0, 1.95, 12.6, -3.0, -12.4)
    rect(ax, 0.0, -1.2, 120.0, 2.4, lw=0.9)
    stops = [0.0]
    for k, (a, b) in enumerate(B.BENDS):
        rect(ax, a, -1.2, b - a, 2.4, hatch='//////', lw=0.6, z=3)
        ax.text((a + b) / 2, 5.6, 'B%d' % (k + 1), ha='center', va='bottom', fontsize=9, fontweight='bold')
        ax.plot([(a + b) / 2, (a + b) / 2], [1.4, 5.3], color='black', lw=0.5)
        stops += [a, b]
    stops.append(120.0)
    for i in range(0, len(stops), 2):
        a, b = stops[i], stops[i + 1]
        ax.text((a + b) / 2, 1.9, '%g' % (b - a), ha='center', va='bottom', fontsize=7.5, style='italic', color='0.2')
    for m in stops:
        ax.plot([m, m], [-1.2, -3.2], color='black', lw=0.5)
        if m in CORNER:
            ax.text(m, -5.6, '%g' % m, ha='center', va='center', fontsize=7.5, fontweight='bold',
                    bbox=dict(boxstyle='circle,pad=0.22', facecolor='white', edgecolor='black', lw=0.7))
        else:
            ax.text(m, -4.0, '%g' % m, ha='center', va='top', fontsize=7.5)
    ax.text(0.0, -9.6, 'end (joint)', ha='left', va='center', fontsize=7.5, color='0.25')
    ax.text(120.0, -9.6, 'end (joint)', ha='right', va='center', fontsize=7.5, color='0.25')
    ax.text(60.0, -9.6, 'italic numbers: straight lengths;  hatched: 8 in of pipe used by each bend;  circled: where each bend '
            'starts', ha='center', va='center', fontsize=7.5, color='0.25')
    # the loop, like the sketch
    fig.text(0.5 / 11, 4.85 / 8.5, 'Where the marks end up (1:10)', fontsize=10, fontweight='bold')
    ax = scaled(fig, 0.5, 0.35, 4.6, 4.4, 10.0, -23.0, -22.0)
    pipe2d(ax, LOOP)
    for a, b in B.BENDS:
        band2d(ax, a); band2d(ax, b)
    rect(ax, -0.9, YC - 0.46, 1.8, 0.92, z=5, hatch='||||', lw=0.7)
    for txt, (x, y) in (('10', (5.0, YC + 1.9)), ('10', (-5.0, YC + 1.9)), ('24', (XO + 2.0, 0.0)), ('24', (-XO - 2.0, 0.0)),
                        ('20', (0.0, -YC - 2.0))):
        ax.text(x, y, txt, ha='center', va='center', fontsize=8.5, style='italic')
    for d in (14.0, 46.0, 74.0, 106.0):
        (x, y), _t = B.at(d)
        ux, uy = math.copysign(1, x) * 0.7071, math.copysign(1, y) * 0.7071
        ax.text(x + ux * 2.0, y + uy * 2.0, '8', ha='center', va='center', fontsize=8.5, style='italic')
    for m, pos in ((10, (16.5, 20.0)), (42, (20.0, -12.0)), (70, (-14.5, -20.3)), (102, (-20.0, 14.0))):
        circled(ax, pos, '%d' % m, fs=8, leader_to=B.at(m)[0])
    ax.text(0.0, YC + 3.6, '0 / 120', ha='center', va='center', fontsize=8)
    ax.add_patch(FancyArrowPatch((1.5, YC - 2.0), (8.0, YC - 2.0), arrowstyle='->', mutation_scale=8, lw=0.6, color='black'))
    ax.text(4.75, YC - 3.4, 'measure this way', ha='center', va='center', fontsize=6.5, color='0.25')
    # table and render
    rows = [['Bend', 'Start (in)', 'End (in)', 'Angle', 'Corner']]
    for k, (a, b) in enumerate(B.BENDS):
        rows.append(['B%d' % (k + 1), '%g' % a, '%g' % b, '90 deg', CORNER[int(a)]])
    tab = fig.add_axes([5.45 / 11, 3.05 / 8.5, 5.1 / 11, 1.75 / 8.5]); tab.axis('off')
    t = tab.table(cellText=rows[1:], colLabels=rows[0], loc='upper center', cellLoc='left', colLoc='left',
                  colWidths=[0.12, 0.17, 0.15, 0.15, 0.41])
    t.auto_set_font_size(False); t.set_fontsize(8.5); t.scale(1.0, 1.35)
    for c_ in t.get_celld().values():
        c_.PAD = 0.03
    fig.text(5.45 / 11, 3.0 / 8.5,
             'Each bend uses 8 in of pipe, a centreline radius of about %s in. If your bender\nuses less, keep the straights at '
             '10, 24, 20, 24 and 10 in and trim what is left over.' % frac(B.RB), fontsize=7.5, color='0.2', va='top')
    image(fig, '07_bent', 5.45, 0.3, 5.1, 2.15)
    emit(fig, '04_bends')

    # 5 wheel mount
    fig = page(LAND, 'The wheel mount', 'Short dropout on the side, long dropout on the inner bar, axle level')
    image(fig, '04_wheel_mount', 0.3, 0.9, 5.3, 6.1)
    fig.text(5.75 / 11, 7.2 / 8.5, 'Section through the left axle, looking forward (1:1.6)', fontsize=10, fontweight='bold')
    ax = scaled(fig, 5.7, 0.7, 5.0, 6.2, 1.6, -17.4, 7.4)
    xw = -(XO + XI) / 2
    ax.add_patch(Rectangle((-XO - RP, B.ZO - RP), 2 * XO, OD, facecolor='white', edgecolor='black', lw=0.6,
                           ls=(0, (2.5, 1.5)), zorder=1))
    ax.add_patch(Circle((-XO, B.ZO), RP, facecolor='white', edgecolor='black', lw=0.9, hatch='////', zorder=3))
    ax.add_patch(Circle((-XI, B.ZI), RP, facecolor='white', edgecolor='black', lw=0.9, hatch='////', zorder=3))
    faces = sorted((-(XO - RP), -(XI + RP)))
    for xb, long, inward in ((-XO, False, 1), (-XI, True, -1)):
        ol, holes, hr, axle_v, screw_v = B.dropout_outline(long)
        zb = B.ZI if long else B.ZO
        vs = [p[1] for p in ol]
        z0, z1 = zb - screw_v + min(vs), zb - screw_v + max(vs)
        xf = xb + inward * RP
        rect(ax, min(xf, xf + inward * B.PLATE), z0, B.PLATE, z1 - z0, z=4, facecolor='black', lw=0.3)
        ax.plot([xb - 1.0, xb + 1.0], [zb, zb], color='black', lw=0.6, zorder=5)
    rect(ax, xw - B.OLD / 2, B.AXLE_Z - 0.7, B.OLD, 1.4, z=3, lw=0.8)
    rect(ax, faces[0] - 0.5, B.AXLE_Z - 0.19, faces[1] - faces[0] + 1.0, 0.38, z=2, lw=0.6)
    for x in (faces[0] - 0.17, faces[1] + 0.17):
        rect(ax, x - 0.15, B.AXLE_Z - 0.32, 0.3, 0.64, z=5, lw=0.6)
    rect(ax, xw - B.TIRE_R, B.AXLE_Z - B.WR, 2 * B.TIRE_R, 2 * B.WR, z=1, fill=False, ls=(0, (3, 2)), lw=0.6)
    ax.plot([xw, xw], [7.4, 17.3], color='black', lw=0.4, ls='-.')
    dim(ax, (-XO, B.ZO), (-XI, B.ZO), frac(XO - XI) + ' bar centres', -4.1, fs=7)
    dim(ax, (xw - B.OLD / 2, B.AXLE_Z - 0.7), (xw + B.OLD / 2, B.AXLE_Z - 0.7), 'hub 100 mm', -1.4, fs=7)
    ax.text(-17.2, 7.7, 'axle %s in above the ground' % frac(B.AXLE_Z), fontsize=7.5)
    note(ax, (-XI, B.ZI + RP), (-12.3, 16.75), 'inner bar, resting on\nthe cross member', fs=7.5)
    note(ax, (-XO, B.ZO + RP), (-17.2, 16.2), 'side', fs=7.5)
    note(ax, (-12.8, B.ZO + RP), (-15.0, 15.6), 'front cross member (behind, dashed)', fs=7.5)
    note(ax, (-XI - RP - 0.07, B.ZI - 2.0), (-10.25, 8.9), 'long\ndropout', fs=7.5)
    note(ax, (-XO + RP + 0.07, B.ZO - 1.3), (-17.2, 9.4), 'short\ndropout', fs=7.5)
    note(ax, (xw + B.TIRE_R, 8.3), (-11.0, 8.0), 'tire (dashed)', fs=7.5)
    emit(fig, '05_wheel_mount')

    # 6 pieces laid out flat
    fig = page(LAND, 'All the pieces, laid out flat (1:12)',
               'Letters match the parts list. Pipe width exaggerated; small parts in the box at 1:2.5')
    ax = scaled(fig, 0.35, 0.4, 10.3, 6.95, 12.0, -2.0, -4.0)
    th = 1.7
    ax.text(0.0, 74.0, 'A   Main frame: one 10 ft conduit, bend zones hatched', fontsize=9.5, fontweight='bold', va='bottom')
    rect(ax, 0.0, 69.0, 120.0, th)
    for a, b in B.BENDS:
        rect(ax, a, 69.0, b - a, th, hatch='//////', lw=0.6, z=3)
    for m in [0.0] + [v for ab in B.BENDS for v in ab] + [120.0]:
        ax.plot([m, m], [69.0, 67.4], color='black', lw=0.45)
        ax.text(m, 66.9, '%g' % m, ha='center', va='top', fontsize=6.5)
    ax.text(0.0, 58.5, 'B   Inner bars: cut a second 10 ft conduit', fontsize=9.5, fontweight='bold', va='bottom')
    for k, (a, b, lab) in enumerate(((0.0, 36.0, 'B1  inner bar, 36 in'), (36.0, 72.0, 'B2  inner bar, 36 in'),
                                     (72.0, 120.0, 'spare, 48 in'))):
        spare = k == 2
        rect(ax, a + (0.25 if k else 0.0), 53.5, b - a - (0.25 if k else 0.0), th, hatch='....' if spare else None,
             ls=(0, (3, 2)) if spare else '-', lw=0.6 if spare else 0.9)
        ax.text((a + b) / 2, 52.0, lab, ha='center', va='top', fontsize=7.5)
    for m in (36.0, 72.0):
        ax.plot([m, m], [52.6, 56.1], color='black', lw=1.0)
        ax.text(m, 56.4, 'cut', ha='center', va='bottom', fontsize=6.5)
    ax.text(0.0, 42.5, 'W   Wheels (2)', fontsize=9.5, fontweight='bold', va='bottom')
    for k, cx in enumerate((13.6, 42.0)):
        ax.add_patch(Circle((cx, 26.0), B.WR, facecolor='white', edgecolor='black', lw=0.9))
        ax.add_patch(Circle((cx, 26.0), B.WR - 2 * B.TIRE_R, facecolor='white', edgecolor='black', lw=0.6))
        ax.add_patch(Circle((cx, 26.0), B.RIM_R - 0.6, facecolor='none', edgecolor='black', lw=0.4))
        ax.add_patch(Circle((cx, 26.0), 1.0, facecolor='white', edgecolor='black', lw=0.6))
        ax.text(cx, 26.0, 'W%d' % (k + 1), ha='center', va='center', fontsize=6.5)
    ax.text(27.8, 10.6, '26 x 2.1 in tires, 100 mm front hubs\n(size estimated from the photo)', ha='center', va='top',
            fontsize=7.5)
    ax.text(60.0, 42.5, 'D   Deck (optional)', fontsize=9.5, fontweight='bold', va='bottom')
    rect(ax, 60.0, 5.5, B.DECK[0], B.DECK[1], hatch='....', lw=0.8)
    ax.text(60.0 + B.DECK[0] / 2, 4.6, '1/2 in plywood\n%g x %g in' % B.DECK, ha='center', va='top', fontsize=7.5)
    # small parts at 1:2.5
    sw_, sh_ = LAND
    bx, by, bw, bh = 7.45, 0.45, 3.25, 3.95
    fig.patches.append(Rectangle((bx / sw_, by / sh_), bw / sw_, bh / sh_, transform=fig.transFigure, fill=False,
                                 lw=0.6, edgecolor='black'))
    fig.text((bx + 0.1) / sw_, (by + bh - 0.08) / sh_, 'Small parts (1:2.5)', fontsize=9.5, fontweight='bold', va='top')
    sx_ = scaled(fig, bx + 0.05, by + 0.05, bw - 0.1, bh - 0.4, 2.5, 0.0, 0.0)
    for k, long in enumerate((False, False, True, True)):
        ol, holes, hr, axle_v, screw_v = B.dropout_outline(long)
        ys = [p[1] for p in ol]
        cx, cy = 1.05 + k * 1.95, 8.4 - max(ys)
        poly(ax=sx_, pts=[(cx + u, cy + v) for u, v in ol], lw=0.8)
        for hu, hv in holes:
            sx_.add_patch(Circle((cx + hu, cy + hv), hr, facecolor='white', edgecolor='black', lw=0.5, zorder=4))
        sx_.text(cx, cy + min(ys) - 0.25, '%s%d' % ('L' if long else 'S', k % 2 + 1), ha='center', va='top', fontsize=6.5)
    sx_.text(0.2, 4.95, 'S  short dropout (2)    L  long dropout (2)', fontsize=6.5, va='top')
    rect(sx_, 0.3, 2.35, 1.8, 0.92, hatch='||||', lw=0.7)
    for u in (0.75, 1.65):
        rect(sx_, u - 0.12, 3.27, 0.24, 0.25, lw=0.5)
    sx_.text(1.2, 2.15, 'C  coupling', ha='center', va='top', fontsize=6.5)
    for i in range(12):
        L = 2.0 if i < 8 else 2.5
        x = 3.0 + i * 0.42
        rect(sx_, x - 0.095, 0.55, 0.19, L, lw=0.5)
        rect(sx_, x - 0.17, 0.55 + L, 0.34, 0.15, lw=0.5)
    sx_.text(3.0, 0.35, 'bolts #10-24: 8 x 2 in, 4 x 2 1/2 in', fontsize=6.5, va='top')
    fig.text(0.35 / 11, 0.2 / 8.5, 'Full-size dropout templates are on the next page.', fontsize=7.5, color='0.3')
    emit(fig, '06_pieces')

    # 7 dropouts full size
    fig = page(PORT, 'Dropouts, full size (1:1)', 'Print at 100% (no scaling). 3.2 mm (0.125 in) stainless; check the squares below')
    for i, (long, ttl) in enumerate(((False, 'Short dropout (side), make 2'), (True, 'Long dropout (inner bar), make 2'))):
        ol, holes, hr, axle_v, screw_v = B.dropout_outline(long)
        cx = 2.35 + i * 3.9
        ax = scaled(fig, cx - 1.6, 3.2, 3.2, 5.0, 1.0, -1.6, -2.5)
        poly(ax, ol, lw=1.0)
        for hu, hv in holes:
            ax.add_patch(Circle((hu, hv), hr, facecolor='white', edgecolor='black', lw=0.8, zorder=4))
        ax.plot([-1.2, 1.2], [screw_v, screw_v], color='black', lw=0.3, ls='-.')
        ax.plot([0, 0], [axle_v, max(p[1] for p in ol) + 0.15], color='black', lw=0.3, ls='-.')
        w = (max(p[0] for p in ol) - min(p[0] for p in ol)); h = (max(p[1] for p in ol) - min(p[1] for p in ol))
        fig.text(cx / 8.5, 8.75 / 11, ttl, ha='center', fontsize=10, fontweight='bold')
        fig.text(cx / 8.5, 3.0 / 11, '%.0f x %.0f mm (%s x %s in)\n2 holes 4 mm (#10 bolts), %.0f mm apart\naxle slot 10 mm wide'
                 % (w / MM, h / MM, frac(w, 16), frac(h, 16), 27.0), ha='center', va='top', fontsize=8.5)
    ax = scaled(fig, 2.5, 1.0, 4.0, 1.2, 1.0, 0.0, 0.0)
    rect(ax, 0.0, 0.1, 1.0, 1.0, fill=False, lw=0.8); ax.text(1.15, 0.6, '1 in square', va='center', fontsize=8)
    rect(ax, 2.2, 0.1, 50 * MM, 0.25, fill=False, lw=0.8); ax.text(2.2, 0.5, '50 mm', va='bottom', fontsize=8)
    emit(fig, '07_dropouts')

    # 8 exploded
    fig = page(LAND, 'Every part, exploded', 'Loop and coupling, inner bars and their bolts, dropouts, wheels and deck')
    image(fig, '05_exploded', 0.4, 0.5, 10.2, 7.0)
    emit(fig, '08_exploded')

    # 9 parts list
    fig = page(LAND, 'Parts list', 'Quantities match the model')
    image(fig, '06_materials', 0.4, 4.6, 10.2, 2.8, 'Everything laid out before building')
    rows = [['', 'Part', 'Qty', 'Notes'],
            ['A, B', '1/2 in EMT conduit, 10 ft', '2', 'A is bent into the loop (all 120 in); B is cut into the two 36 in inner '
             'bars, with 48 in spare'],
            ['C', '1/2 in EMT set-screw coupling', '1', 'joins the two ends of the loop at the front'],
            ['S', 'Dropout, short (side)', '2', 'laser cut, 0.125 in stainless; same as version 1'],
            ['L', 'Dropout, long (inner bar)', '2', '18 mm longer, because the inner bar sits one pipe higher'],
            ['', 'Bolt #10-24 x 2 in + nut', '8', 'dropouts to the bars, 2 each'],
            ['', 'Bolt #10-24 x 2 1/2 in + nut', '4', 'inner bars down through the front and back cross members'],
            ['W', '26 in wheel', '2', '100 mm front hubs; size estimated from the photo'],
            ['D', 'Plywood deck, 1/2 in, 21 x 34 in', '1', 'optional'],
            ['', 'Hitch', '-', 'not in the sketch; the 48 in spare could make a tongue'],
            ['', 'Tools', '', '1/2 in EMT bender, tubing cutter or hacksaw, drill and 11/64 in bit, wrenches']]
    tab = fig.add_axes([0.6 / 11, 0.4 / 8.5, 9.8 / 11, 3.7 / 8.5]); tab.axis('off')
    t = tab.table(cellText=rows[1:], colLabels=rows[0], loc='upper center', cellLoc='left', colLoc='left',
                  colWidths=[0.05, 0.27, 0.05, 0.63])
    t.auto_set_font_size(False); t.set_fontsize(8.8); t.scale(1.0, 1.32)
    for c_ in t.get_celld().values():
        c_.PAD = 0.03
    emit(fig, '09_parts')

print('wrote', pdf_path, names)
