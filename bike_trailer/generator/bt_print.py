"""Black-and-white print set for the Edge Collective bike trailer v1.0:
hidden-line renders from IngeTrazo plus to-scale drawings, one PDF.
Usage: bt_print.py OUT_DIR RENDER_DIR"""
import math
import os
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Polygon, FancyArrowPatch, Circle, Rectangle
from PIL import Image, ImageOps

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bt_geom as B

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
    fig.text(0.98, 0.012, 'Edge Collective bike trailer v1.0 (model)', ha='right', va='bottom', fontsize=7, color='0.4')
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


def dim(ax, p1, p2, text, off, fs=8):
    dx, dy = p2[0] - p1[0], p2[1] - p1[1]
    L = math.hypot(dx, dy); nx, ny = -dy / L, dx / L
    a = (p1[0] + nx * off, p1[1] + ny * off); b = (p2[0] + nx * off, p2[1] + ny * off)
    for p, q in ((p1, a), (p2, b)):
        ax.plot([p[0] + nx * off * 0.1, q[0] + nx * off * 0.08], [p[1] + ny * off * 0.1, q[1] + ny * off * 0.08],
                color='black', lw=0.5, zorder=5)
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle='<->', mutation_scale=7, lw=0.6, color='black', zorder=5))
    ang = math.degrees(math.atan2(dy, dx))
    if ang > 90 or ang < -90:
        ang += 180
    ax.text((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, text, ha='center', va='center', rotation=ang, fontsize=fs, zorder=6,
            bbox=dict(facecolor='white', edgecolor='none', pad=0.6))


def note(ax, xy, xytext, text, fs=8):
    ax.annotate(text, xy=xy, xytext=xytext, fontsize=fs, ha='left', va='center', zorder=7,
                bbox=dict(facecolor='white', edgecolor='none', pad=0.8),
                arrowprops=dict(arrowstyle='-', lw=0.5, color='black', shrinkA=0, shrinkB=1))


def pipe2d(ax, pts, r=B.RP, lw=0.9):
    """Plan view of a pipe: its two edges from a centreline polyline."""
    left, right = [], []
    n = len(pts)
    for i, p in enumerate(pts):
        a = pts[max(i - 1, 0)]; b = pts[min(i + 1, n - 1)]
        tx, ty = b[0] - a[0], b[1] - a[1]
        L = math.hypot(tx, ty); nx, ny = -ty / L, tx / L
        left.append((p[0] + nx * r, p[1] + ny * r)); right.append((p[0] - nx * r, p[1] - ny * r))
    poly(ax, left + right[::-1], lw=lw)


segs, tip, xc, joint = B.main_frame_segments()
pts3, L_main = B.path_points(segs, B.ZO, step_deg=4.0)
PTS = [(p[0], p[1]) for p in pts3]

# bend schedule from the tip
sched = []
pos = 0.0
prev_heading = None
for s in segs:
    if s[0] == 'L':
        L = math.hypot(s[2][0] - s[1][0], s[2][1] - s[1][1])
        sched.append(('straight', pos, pos + L, None, None))
        pos += L
    else:
        c, r, a0, a1 = s[1:]
        L = r * math.radians(abs(a1 - a0))
        turn = 'left' if a1 > a0 else 'right'
        sched.append(('bend', pos, pos + L, abs(a1 - a0), turn, r))
        pos += L

pdf_path = os.path.join(OUT, 'bike_trailer_print.pdf')
names = []
with PdfPages(pdf_path) as pdf:
    def emit(fig, name):
        pdf.savefig(fig); fig.savefig(os.path.join(OUT, 'pages', name + '.png'), dpi=150); plt.close(fig); names.append(name)

    # 1 title
    fig = page(LAND, 'Bike Trailer v1.0 (Edge Collective)',
               '1/2 in EMT conduit frame  |  recycled 16 in wheels  |  laser-cut dropouts  |  vinyl-tube hitch')
    image(fig, '00_overview', 0.4, 2.4, 10.2, 4.8, '1 Materials   >   2 Bent main frame   >   3 Assembled trailer   >   4 Exploded')
    facts = ['Main frame: one 10 ft length of 1/2 in EMT, bent into the tongue and a loop around both wheels (about %s x %s in).'
             % (frac(2 * B.XO + B.OD), frac(2 * B.YC + B.OD)),
             'Inner bars: two %s in pieces from a second 10 ft length, bolted on top of the loop.' % frac(2 * B.YC + 2),
             'Each wheel hangs between a short dropout (outer bar) and a long dropout (inner bar, one pipe higher).',
             'Hitch: 6 in of 7/8 in braided vinyl tube over the tongue tip, to a Burley-style coupler on the bike axle.',
             'Frame sizes are estimates from the project photos; dropouts follow the project\'s SCAD files.']
    for i, t in enumerate(facts):
        fig.text(0.6 / 11, (1.75 - i * 0.27) / 8.5, u'•  ' + t, fontsize=9.5, va='center')
    emit(fig, '01_title')

    # 2 assembled
    fig = page(LAND, 'The assembled trailer', 'With the plywood deck, and the bare frame')
    image(fig, '02_assembled', 0.3, 1.2, 5.1, 6.0, 'Assembled, with the deck')
    image(fig, '03_no_deck', 5.6, 1.2, 5.1, 6.0, 'Frame without the deck')
    emit(fig, '02_assembled')

    # 3 frame plan, to scale
    fig = page(LAND, 'Frame, from above (1:7)', 'Main frame (one 10 ft conduit), inner bars, wheels dashed, dropouts')
    ax = scaled(fig, 0.6, 0.4, 9.8, 7.0, 7.0, -21.0, -25.0)
    # rotate so the tongue points right: draw (y, -x)
    R = lambda p: (p[1], -p[0])
    pipe2d(ax, [R(p) for p in PTS])
    for sx in (-1, 1):
        pipe2d(ax, [R((sx * B.XI, -B.YC - 1.0)), R((sx * B.XI, B.YC + 1.0))])
        xw = sx * (B.XO + B.XI) / 2
        a, b = R((xw - B.TIRE_W / 2, -B.WR)), R((xw + B.TIRE_W / 2, B.WR))
        ax.add_patch(Rectangle((min(a[0], b[0]), min(a[1], b[1])), abs(b[0] - a[0]), abs(b[1] - a[1]), fill=False, ls=(0, (3, 2)), lw=0.7))
        for xb, inward in ((sx * B.XO, -sx), (sx * B.XI, sx)):
            xf = xb + inward * B.RP
            p0, p1 = R((xf, -22.5 * MM)), R((xf + inward * 0.125, 22.5 * MM))
            ax.add_patch(Rectangle((min(p0[0], p1[0]), min(p0[1], p1[1])), abs(p1[0] - p0[0]), abs(p1[1] - p0[1]),
                                   facecolor='black', lw=0.3))
    for sx in (-1, 1):
        for sy in (-1, 1):
            ax.plot(*R((sx * B.XI, sy * B.YC)), marker='o', ms=2.5, color='black', zorder=8)
    ax.plot(*R(joint), marker='o', ms=2.5, color='black', zorder=8)
    tube_end = (tip[0] + math.sin(B.PHI) * 3.5, tip[1] + math.cos(B.PHI) * 3.5)
    poly(ax, [R((tip[0] - 0.6, tip[1] - 2.5)), R((tip[0] + 0.6, tip[1] - 2.5)), R((tube_end[0] + 0.6, tube_end[1])),
              R((tube_end[0] - 0.6, tube_end[1]))], hatch='xxxx', lw=0.6, z=3)
    xb_, yo_ = -B.YC - B.RP, B.XO + B.RP              # drawing coords: back edge x, outer edge |y|
    tube_x = tube_end[1]
    dim(ax, (xb_, -yo_), (xb_, yo_), frac(2 * B.XO + B.OD) + ' outside', 3.4)
    dim(ax, (xb_, -yo_), (-xb_, -yo_), frac(2 * B.YC + B.OD) + ' outside', -3.2)
    dim(ax, (xb_, -yo_), (tube_x, -yo_), frac(tube_x - xb_) + ' overall, back to hitch', -7.0)
    dim(ax, (2.0, B.XI), (2.0, B.XO), frac(B.XO - B.XI), 0.0, fs=7)
    note(ax, R((-B.XI, -B.YC)), (-9.0, 17.5), 'bolts: inner bars to the loop (4)', fs=7.5)
    note(ax, R(joint), (24.0, 17.0), 'bolt: tongue joint', fs=7.5)
    note(ax, R((tip[0], tip[1] + 1.0)), (30.0, -2.0), 'vinyl tube + hitch', fs=7.5)
    note(ax, (4.0, -(B.XO + B.XI) / 2), (16.0, -13.5), 'wheels (dashed) between their dropouts', fs=7.5)
    ax.text(xb_ - 7.0, 0.0, 'back', ha='center', va='center', fontsize=8, rotation=90, color='0.3')
    ax.text(tube_x + 2.0, 6.0, 'to bike', ha='left', va='center', fontsize=8, color='0.3')
    emit(fig, '03_plan')

    # 4 wheel mount: render + section drawing
    fig = page(LAND, 'The wheel mount', 'Short dropout on the outer bar, long dropout on the inner bar, axle level')
    image(fig, '04_wheel_mount', 0.3, 1.0, 5.6, 6.4)
    fig.text(6.3 / 11, 7.4 / 8.5, 'Section through the axle, looking forward (1:1.6)', fontsize=10, fontweight='bold')
    ax = scaled(fig, 6.2, 1.0, 4.5, 6.2, 1.6, -13.4, 3.0)
    xw = -(B.XO + B.XI) / 2
    ax.add_patch(Circle((-B.XO, B.ZO), B.RP, facecolor='white', edgecolor='black', lw=0.9, hatch='////', zorder=3))
    ax.add_patch(Circle((-B.XI, B.ZI), B.RP, facecolor='white', edgecolor='black', lw=0.9, hatch='////', zorder=3))
    ax.add_patch(Circle((-B.XI, B.ZO), B.RP, facecolor='white', edgecolor='black', lw=0.6, ls=(0, (2, 1.5)), zorder=2))
    for xb, long, inward in ((-B.XO, False, 1), (-B.XI, True, -1)):
        ol, holes, hr, axle_v, screw_v = B.dropout_outline(long)
        zb = B.ZI if long else B.ZO
        vs = [p[1] for p in ol]
        z0, z1 = zb - screw_v + min(vs), zb - screw_v + max(vs)
        xf = xb + inward * B.RP
        ax.add_patch(Rectangle((min(xf, xf + inward * B.PLATE), z0), B.PLATE, z1 - z0, facecolor='black', lw=0.3, zorder=4))
        ax.plot([xb - 1.0, xb + 1.0], [zb, zb], color='black', lw=0.6, zorder=5)
    ax.add_patch(Rectangle((xw - B.OLD / 2, B.AXLE_Z - 0.7), B.OLD, 1.4, facecolor='white', edgecolor='black', lw=0.8, zorder=3))
    ax.add_patch(Rectangle((xw - B.OLD / 2 - B.PLATE - 0.55, B.AXLE_Z - 0.19), B.OLD + 2 * B.PLATE + 1.1, 0.38,
                           facecolor='white', edgecolor='black', lw=0.6, zorder=2))
    ax.add_patch(Rectangle((xw - B.TIRE_W / 2, 0.0), B.TIRE_W, 2 * B.WR, facecolor='none', edgecolor='black', lw=0.6,
                           ls=(0, (3, 2)), zorder=1))
    ax.plot([xw, xw], [-0.3, 2 * B.WR + 0.3], color='black', lw=0.4, ls='-.')
    dim(ax, (-B.XO, B.ZO), (-B.XI, B.ZO), frac(B.XO - B.XI) + ' bar centres', -2.4, fs=7)
    dim(ax, (xw - B.OLD / 2, B.AXLE_Z - 0.7), (xw + B.OLD / 2, B.AXLE_Z - 0.7), 'hub 100 mm', -1.3, fs=7)
    ax.text(-13.2, 3.4, 'axle %s in above the ground' % frac(B.AXLE_Z), fontsize=7.5)
    note(ax, (-B.XI, B.ZI + B.RP), (-9.6, 11.9), 'inner bar, one pipe higher', fs=7.5)
    note(ax, (-B.XO, B.ZO + B.RP), (-13.2, 11.2), 'outer bar', fs=7.5)
    note(ax, (-B.XI + B.RP + 0.06, B.ZI - 1.6), (-8.4, 5.0), 'long dropout', fs=7.5)
    note(ax, (-B.XO - B.RP - 0.06, B.ZO - 1.2), (-13.2, 5.8), 'short dropout', fs=7.5)
    note(ax, (xw + B.TIRE_W / 2, 12.2), (-8.0, 12.6), 'tire (dashed)', fs=7.5)
    emit(fig, '04_wheel_mount')

    # 5 bend layout
    fig = page(LAND, 'Bending the main frame (one 10 ft conduit)',
               'Marks measured along the pipe from the tongue (hitch) end, centreline; all bends in one plane')
    ax = scaled(fig, 0.5, 4.3, 10.0, 2.2, 12.6, -3.0, -8.0)
    ax.add_patch(Rectangle((0.0, -B.RP * 3), L_main, B.OD * 3, facecolor='white', edgecolor='black', lw=0.9))
    k = 0
    for row in sched:
        if row[0] == 'bend':
            _, a, b, ang, turn, r = row
            k += 1
            ax.add_patch(Rectangle((a, -B.RP * 3), b - a, B.OD * 3, facecolor='white', edgecolor='black', hatch='////', lw=0.6))
            ax.text((a + b) / 2, 4.2 + (k % 2) * 3.2, 'B%d' % k, ha='center', va='bottom', fontsize=8, fontweight='bold')
            ax.plot([(a + b) / 2, (a + b) / 2], [B.RP * 3, 4.0 + (k % 2) * 3.2], color='black', lw=0.5)
    ax.text(0.0, -4.0, 'tongue / hitch end', ha='left', va='top', fontsize=8)
    ax.text(L_main, -4.0, 'tail end (bolts beside the tongue)', ha='right', va='top', fontsize=8)
    for x in range(0, 121, 12):
        ax.plot([x, x], [-B.RP * 3, -B.RP * 3 - 1.2], color='black', lw=0.4)
        ax.text(x, -B.RP * 3 - 1.5, '%d' % x, ha='center', va='top', fontsize=6.5)
    # table
    rows = [['', 'Start (in)', 'End (in)', 'Angle', 'Turn*', 'What it makes']]
    what = ['tongue into the left outer bar', 'back left corner', 'back right corner', 'front right corner',
            'front cross member into the tongue tail']
    k = 0
    for row in sched:
        if row[0] == 'bend':
            _, a, b, ang, turn, r = row
            rows.append(['B%d' % (k + 1), frac(a), frac(b), '%.0f deg' % ang, turn, what[k] if k < len(what) else ''])
            k += 1
    tab = fig.add_axes([0.6 / 11, 0.75 / 8.5, 9.8 / 11, 2.9 / 8.5]); tab.axis('off')
    t = tab.table(cellText=rows[1:], colLabels=rows[0], loc='upper center', cellLoc='left', colLoc='left',
                  colWidths=[0.06, 0.12, 0.12, 0.1, 0.1, 0.5])
    t.auto_set_font_size(False); t.set_fontsize(9); t.scale(1.0, 1.5)
    fig.text(0.6 / 11, 0.55 / 8.5, '* Turn direction as you walk the pipe from the tongue end, frame lying flat. Bend radius about %s in '
             '(1/2 in EMT hand bender); B1 is a gentle bend.\n  Allow for your bender\'s take-up when marking.'
             % frac(B.RB), fontsize=7.5, color='0.25', va='top')
    emit(fig, '05_bends')

    # 6 dropouts full size
    fig = page(PORT, 'Dropouts, full size (1:1)', 'Print at 100% (no scaling). 3.2 mm (0.125 in) stainless; check the squares below')
    for i, (long, ttl) in enumerate(((False, 'Short dropout (outer bar), make 2'), (True, 'Long dropout (inner bar), make 2'))):
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
    ax.add_patch(Rectangle((0.0, 0.1), 1.0, 1.0, fill=False, lw=0.8)); ax.text(1.15, 0.6, '1 in square', va='center', fontsize=8)
    ax.add_patch(Rectangle((2.2, 0.1), 50 * MM, 0.25, fill=False, lw=0.8)); ax.text(2.2, 0.5, '50 mm', va='bottom', fontsize=8)
    emit(fig, '06_dropouts')

    # 7 exploded
    fig = page(LAND, 'Every part, exploded', 'Main frame, inner bars, bolts, dropouts, wheels, hitch and deck')
    image(fig, '05_exploded', 0.4, 0.5, 10.2, 7.0)
    emit(fig, '07_exploded')

    # 8 parts list + materials
    fig = page(LAND, 'Parts list', 'From the project page; quantities match the model')
    image(fig, '06_materials', 0.4, 4.4, 10.2, 3.0, 'Everything laid out before building')
    rows = [['Part', 'Qty', 'Notes'],
            ['1/2 in EMT conduit, 10 ft', '2', 'one for the main frame (all 120 in); inner bars 2 x %s in from the other' % frac(2 * B.YC + 2)],
            ['Dropout, short (outer bar)', '2', 'laser cut, 0.125 in stainless (e.g. SendCutSend)'],
            ['Dropout, long (inner bar)', '2', 'same, one pipe diameter (18 mm) longer'],
            ['Bolt #10-24 x 2 in + nut', '8', 'dropouts to bars, 2 each'],
            ['Bolt #10-24 x 2 1/2 in + nut', '5', 'inner bars to the loop (4), tongue joint (1)'],
            ['16 in wheel', '2', 'recycled kids\' bike wheels, 100 mm hubs'],
            ['Braided vinyl tube 7/8 in', '6 in', 'over the tongue tip'],
            ['Bike trailer hitch coupler', '1', 'Burley-style, on the bike\'s rear axle'],
            ['Plywood deck 1/2 in, 15 x 27 in', '1', 'optional'],
            ['Tools', '', '1/2 in EMT bender, drill + 11/64 in bit, screwdriver, pliers']]
    tab = fig.add_axes([0.6 / 11, 0.5 / 8.5, 9.8 / 11, 3.4 / 8.5]); tab.axis('off')
    t = tab.table(cellText=rows[1:], colLabels=rows[0], loc='upper center', cellLoc='left', colLoc='left',
                  colWidths=[0.3, 0.07, 0.63])
    t.auto_set_font_size(False); t.set_fontsize(9); t.scale(1.0, 1.35)
    emit(fig, '08_parts')

print('wrote', pdf_path, names)
