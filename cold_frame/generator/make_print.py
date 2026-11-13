"""Black-and-white print set for the pallet cold frame: hidden-line renders
plus to-scale 2D drawings, as one PDF and one PNG per page."""
import math
import os
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Polygon, FancyArrowPatch
from PIL import Image, ImageOps

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cf_geom as C

OUT = sys.argv[1]
REN = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'print')
os.makedirs(os.path.join(OUT, 'views'), exist_ok=True)
plt.rcParams.update({'font.family': 'DejaVu Sans', 'hatch.color': 'black', 'hatch.linewidth': 0.35,
                     'pdf.fonttype': 42})
LAND, PORT = (11.0, 8.5), (8.5, 11.0)
BW, BT, W, D, HF, HB, LV, TH = C.BW, C.BT, C.W, C.D, C.HF, C.HB, C.LV, C.TH


def frac(x):
    n = int(round(x * 8)); w, r = divmod(n, 8)
    if r == 0:
        return '%d' % w
    g = math.gcd(r, 8)
    return ('%d %d/%d' % (w, r // g, 8 // g)) if w else '%d/%d' % (r // g, 8 // g)


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
    fig.text(0.98, 0.012, 'Pallet cold frame', ha='right', va='bottom', fontsize=7, color='0.4')
    return fig


def image(fig, path, left, bottom, width, height, caption=None):
    """Place a cropped render in a box (inches), keeping its aspect."""
    im = crop(path)
    iw, ih = im.size
    sw, sh = fig.get_size_inches()
    s = min(width / iw, height / ih)
    w, h = iw * s, ih * s
    l, b = left + (width - w) / 2, bottom + (height - h) / 2
    ax = fig.add_axes([l / sw, b / sh, w / sw, h / sh])
    ax.imshow(im, cmap='gray', vmin=0, vmax=255, interpolation='lanczos')
    ax.axis('off')
    if caption:
        fig.text((left + width / 2) / sw, (bottom - 0.08) / sh, caption, ha='center', va='top', fontsize=9.5)


def scaled(fig, left, bottom, width, height, scale, x0, y0):
    """Axes where one data inch prints 1/scale inches."""
    sw, sh = fig.get_size_inches()
    ax = fig.add_axes([left / sw, bottom / sh, width / sw, height / sh])
    ax.set_xlim(x0, x0 + width * scale); ax.set_ylim(y0, y0 + height * scale)
    ax.set_aspect('equal'); ax.axis('off')
    return ax


def poly(ax, pts, hatch=None, ls='-', lw=0.9, fill='white', z=2):
    ax.add_patch(Polygon(pts, closed=True, facecolor=fill, edgecolor='black', hatch=hatch, linestyle=ls, lw=lw, zorder=z))


def rect(ax, x0, y0, w, h, **kw):
    poly(ax, [(x0, y0), (x0 + w, y0), (x0 + w, y0 + h), (x0, y0 + h)], **kw)


def dim(ax, p1, p2, text, off, fs=8):
    """Dimension line offset perpendicular to p1-p2 by `off` (data inches)."""
    dx, dy = p2[0] - p1[0], p2[1] - p1[1]
    L = math.hypot(dx, dy); nx, ny = -dy / L, dx / L
    a = (p1[0] + nx * off, p1[1] + ny * off); b = (p2[0] + nx * off, p2[1] + ny * off)
    for p, q in ((p1, a), (p2, b)):
        ax.plot([p[0] + nx * off * 0.15, q[0] + nx * off * 0.12], [p[1] + ny * off * 0.15, q[1] + ny * off * 0.12],
                color='black', lw=0.5, zorder=5)
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle='<->', mutation_scale=7, lw=0.6, color='black', zorder=5))
    ang = math.degrees(math.atan2(dy, dx))
    if ang > 90 or ang < -90:
        ang += 180
    ax.text((a[0] + b[0]) / 2 + nx * abs(off) * 0.35 * (1 if off > 0 else -1),
            (a[1] + b[1]) / 2 + ny * abs(off) * 0.35 * (1 if off > 0 else -1), text, ha='center', va='center',
            rotation=ang, fontsize=fs, zorder=6, bbox=dict(facecolor='white', edgecolor='none', pad=0.6))


def note(ax, xy, xytext, text, fs=8):
    ax.annotate(text, xy=xy, xytext=xytext, fontsize=fs, ha='left', va='center', zorder=7,
                bbox=dict(facecolor='white', edgecolor='none', pad=0.8),
                arrowprops=dict(arrowstyle='-', lw=0.5, color='black', shrinkA=0, shrinkB=1))


# ------------------------------------------------------------------ geometry for the drawings
vw = BW / math.cos(TH)
ANG = [(0.0, HF - vw), (D, HB - vw), (D, HB), (0.0, HF)]       # angled side board, side view (y, z)
POSTS_Y = [(BT, BT + C.PT), (D - BT - C.PT, D - BT)]
POSTS_X = [(BT, BT + C.PW), (W - BT - C.PW, W - BT)]

pdf_path = os.path.join(OUT, 'cold_frame_print.pdf')
pages = []
with PdfPages(pdf_path) as pdf:
    def emit(fig, name):
        pdf.savefig(fig)
        fig.savefig(os.path.join(OUT, 'views', name + '.png'), dpi=150)
        plt.close(fig)
        pages.append(name)

    # 1 Title
    fig = page(LAND, 'Pallet Cold Frame', 'Recycled pallet 1x4 deck boards and 2x4 stringers  |  40 x 40 in box  |  lapped 1x4 lid with clear plastic')
    image(fig, os.path.join(REN, '00_overview.png'), 0.4, 2.3, 10.2, 4.9,
          '1 Source pallet   >   2 Box built upside down   >   3 Finished cold frame   >   4 Exploded parts')
    facts = ['Box: front 2 boards high (%s in), back 3 boards high (%s in); sides 2 boards plus one angled board.' % (frac(HF), frac(HB)),
             'Corner posts cut from a pallet 2x4 stringer; the 1x4s nail into them.',
             'Built upside down on a flat surface so the top edges are smooth; flipped so the rough ends sit on the soil.',
             'Lid: two layers of 1x4 with the corners lapped, clamping a sheet of clear plastic between them; hinged at the back.',
             'Materials: 19 deck boards (about 2 pallets) and one stringer per frame.']
    for i, t in enumerate(facts):
        fig.text(0.6 / 11, (1.75 - i * 0.27) / 8.5, u'•  ' + t, fontsize=10, va='center')
    emit(fig, '01_title')

    # 2 Source and build
    fig = page(LAND, 'Stages 1 and 2: from pallet to box', 'Take the pallet apart; build the box upside down on a flat surface')
    image(fig, os.path.join(REN, '01_pallet.png'), 0.3, 1.2, 5.1, 6.0,
          '1  Source: one 48 x 40 in pallet\n1x4 deck boards (about 40 in) and 2x4 stringers (48 in)')
    image(fig, os.path.join(REN, '02_upside_down.png'), 5.6, 1.2, 5.1, 6.0,
          '2  Box built upside down\nsmooth top edges on the bench, posts in the corners')
    emit(fig, '02_source_and_build')

    # 3 Finished
    fig = page(LAND, 'Stage 3: the finished cold frame', 'Flipped onto the soil; the lid hinges at the high back edge')
    image(fig, os.path.join(REN, '03_finished_open.png'), 0.3, 1.2, 5.1, 6.0, 'Lid propped open')
    image(fig, os.path.join(REN, '04_finished_closed.png'), 5.6, 1.2, 5.1, 6.0, 'Lid closed')
    emit(fig, '03_finished')

    # 4 Box design: render + to-scale drawings
    fig = page(LAND, 'The box', 'Lid removed; hidden posts shown dashed')
    image(fig, os.path.join(REN, '05_box_design.png'), 0.3, 4.55, 10.4, 3.1)
    sc = 9.0
    fig.text(0.5 / 11, 4.25 / 8.5, 'Side elevation (left side)', fontsize=10, fontweight='bold')
    ax = scaled(fig, 0.5, 2.55, 5.0, 1.65, sc, -3.0, -2.5)
    rect(ax, BT, 0.0, D - 2 * BT, BW); rect(ax, BT, BW, D - 2 * BT, BW)
    rect(ax, 0.0, 0.0, BT, HF); rect(ax, D - BT, 0.0, BT, HB)
    for a, b in POSTS_Y:
        top = C.ztop(b)
        poly(ax, [(a, 0.0), (b, 0.0), (b, top), (a, C.ztop(a))], ls=(0, (3, 2)), lw=0.7, fill='none', z=3)
    poly(ax, ANG, hatch='////', z=4)
    dim(ax, (0.0, 0.0), (D, 0.0), '%s' % frac(D), -1.6)
    dim(ax, (0.0, 0.0), (0.0, HF), frac(HF), 1.6)
    dim(ax, (D, 0.0), (D, HB), frac(HB), -1.6)
    note(ax, (20.0, 8.6), (24.0, 13.2), 'angled board on the outside face, ~%.0f deg tilt' % math.degrees(TH), fs=7.5)
    note(ax, (1.5, 1.5), (5.0, 12.0), 'posts behind (dashed)', fs=7.5)
    fig.text(0.5 / 11, 2.25 / 8.5, 'Front elevation', fontsize=10, fontweight='bold')
    ax = scaled(fig, 0.5, 0.45, 5.0, 1.75, sc, -4.0, -2.5)
    rect(ax, 0.0, HF, W, HB - HF, lw=0.6)                             # back wall top board, seen above the front
    for x0 in (-BT, W):
        rect(ax, x0, HF - vw, BT, HB - (HF - vw), hatch='////', lw=0.6)
    rect(ax, 0.0, 0.0, W, BW); rect(ax, 0.0, BW, W, BW)
    for a, b in POSTS_X:
        rect(ax, a, 0.0, b - a, C.ztop(BT + C.PT), ls=(0, (3, 2)), lw=0.7, fill='none', z=3)
    dim(ax, (0.0, 0.0), (W, 0.0), frac(W), -1.6)
    dim(ax, (W + BT, 0.0), (W + BT, HF), frac(HF), -1.9)
    fig.text(6.0 / 11, 4.25 / 8.5, 'Plan (top view), front at the bottom', fontsize=10, fontweight='bold')
    ax = scaled(fig, 6.2, 0.35, 4.5, 3.8, 12.5, -4.0, -4.5)
    rect(ax, 0.0, 0.0, W, BT); rect(ax, 0.0, D - BT, W, BT)
    rect(ax, 0.0, BT, BT, D - 2 * BT); rect(ax, W - BT, BT, BT, D - 2 * BT)
    for x0 in (-BT, W):
        rect(ax, x0, 0.0, BT, D, hatch='////', lw=0.6)
    for a, b in POSTS_X:
        for c, d in POSTS_Y:
            rect(ax, a, c, b - a, d - c, hatch='xxxx', lw=0.7)
    dim(ax, (0.0, 0.0), (W, 0.0), frac(W), -2.0)
    dim(ax, (W + BT, 0.0), (W + BT, D), frac(D), -2.0)
    note(ax, (BT + 1.75, BT + 0.75), (8.0, 9.0), '2x4 corner posts', fs=7.5)
    ax.text(W / 2, D / 2, 'growing bed', ha='center', va='center', fontsize=8, color='0.35')
    fig.text(0.5 / 11, 0.2 / 8.5, 'Elevations at 1:9, plan at 1:12.5. Boards 3 1/2 x 3/4 in.', fontsize=7.5, color='0.3')
    emit(fig, '04_box')

    # 5 Lid design: render + plans + section
    fig = page(LAND, 'The lid', 'Two layers of 1x4 with lapped corners clamp a clear plastic sheet between them')
    image(fig, os.path.join(REN, '06_lid_design.png'), 0.3, 4.6, 6.6, 3.0, 'Exploded: top layer, plastic, bottom layer')
    sc = 13.0
    layer1 = [(0.0, 0.0, W, BW), (0.0, LV - BW, W, BW), (0.0, BW, BW, LV - 2 * BW), (W - BW, BW, BW, LV - 2 * BW)]
    layer2 = [(0.0, 0.0, BW, LV), (W - BW, 0.0, BW, LV), (BW, 0.0, W - 2 * BW, BW), (BW, LV - BW, W - 2 * BW, BW)]
    specs = [('Bottom layer: rails run full width', layer1, '////', None),
             ('Top layer: sides run full length', layer2, '\\\\\\\\', None),
             ('Assembled: joints of the two layers cross', layer2, None, layer1)]
    for i, (ttl, boards, hatch, under) in enumerate(specs):
        x = 0.4 + i * 3.55
        fig.text(x / 11, 4.15 / 8.5, ttl, fontsize=9.5, fontweight='bold')
        ax = scaled(fig, x, 0.75, 3.3, 3.3, sc, -1.5, -2.0)
        if under:
            rect(ax, 0.0, 0.0, W, LV, hatch='....', lw=0.4, fill='white', z=1)
            for b in under:
                rect(ax, *b, ls=(0, (2.5, 1.8)), lw=0.7, fill='none', z=3)
            for b in boards:
                rect(ax, *b, lw=1.0, fill='none', z=4)
            ax.text(W / 2, LV / 2, 'plastic sheet\n(dotted)', ha='center', va='center', fontsize=7.5,
                    bbox=dict(facecolor='white', edgecolor='none', pad=1.0), zorder=6)
            note(ax, (BW / 2, BW), (8.0, 9.0), 'bottom-layer joint (dashed)', fs=7)
            note(ax, (BW + 0.2, BW / 2), (8.0, 4.5), 'top-layer joint', fs=7)
        else:
            for b in boards:
                rect(ax, *b, hatch=hatch)
        dim(ax, (0.0, 0.0), (W, 0.0), frac(W), -1.3, fs=7)
    # section
    fig.text(7.25 / 11, 7.1 / 8.5, 'Section through the lid edge (1:2)', fontsize=9.5, fontweight='bold')
    ax = scaled(fig, 7.25, 4.45, 3.4, 2.5, 2.0, -1.0, -2.2)
    rect(ax, 0.0, 0.0, BW, BT, hatch='////')
    ax.plot([-0.5, BW + 0.9], [BT + 0.03, BT + 0.03], color='black', lw=2.2, zorder=6)
    rect(ax, 0.0, BT + 0.06, BW, BT, hatch='\\\\\\\\')
    rect(ax, 0.0, -1.7, BT, 1.6, hatch='xxxx', lw=0.7)
    note(ax, (BW, BT * 1.5 + 0.06), (BW + 0.6, 2.4), 'top layer 1x4', fs=7.5)
    note(ax, (BW + 0.6, BT + 0.03), (BW + 0.9, 1.4), 'plastic sheet', fs=7.5)
    note(ax, (BW, BT / 2), (BW + 0.6, 0.2), 'bottom layer 1x4', fs=7.5)
    note(ax, (BT, -0.9), (BW + 0.6, -1.2), 'box wall below', fs=7.5)
    dim(ax, (-0.2, 0.0), (-0.2, 2 * BT + 0.06), '1 1/2', 0.6, fs=7)
    fig.text(0.4 / 11, 0.2 / 8.5, 'Plans at 1:13. Nail or screw through both layers all round to clamp the plastic.',
             fontsize=7.5, color='0.3')
    emit(fig, '05_lid')

    # 6 Exploded
    fig = page(LAND, 'Every part, exploded', 'Front and back boards, sides, angled boards, corner posts, and the two lid layers with the plastic')
    image(fig, os.path.join(REN, '07_exploded.png'), 0.4, 0.5, 10.2, 7.0)
    emit(fig, '06_exploded')

    # 7 Pieces laid out flat, to scale
    fig = page(LAND, 'All the pieces, laid out flat (1:10)', 'One row per piece; letters match the list. 1x4 = 3 1/2 x 3/4 in pallet deck board')
    sc = 10.0
    sw, sh = LAND
    ax = scaled(fig, 0.35, 0.45, 10.3, 7.0, sc, 0.0, 0.0)
    groups = [
        ('BOX', [('A', 'Front board', W, 2, None), ('B', 'Back board', W, 3, None), ('C', 'Side board', D - 2 * BT, 4, None),
                 ('D', 'Angled side board (ends cut plumb)', LV, 2, '....')]),
        ('LID', [('E', 'Bottom layer rail', W, 2, '////'), ('F', 'Bottom layer side', LV - 2 * BW, 2, '////'),
                 ('G', 'Top layer side', LV, 2, '\\\\\\\\'), ('H', 'Top layer rail', W - 2 * BW, 2, '\\\\\\\\')]),
    ]
    rowh, gap = BW, 1.25
    cols = [(1.0, 63.0), (54.0, 63.0)]
    for (gname, items), (x0, ytop) in zip(groups, cols):
        y = ytop
        ax.text(x0, y + 2.6, gname + ' (%d boards)' % sum(i[3] for i in items), fontsize=10, fontweight='bold', va='bottom')
        for code, name, L, n, hatch in items:
            for k in range(n):
                if code == 'D':
                    off = BW * math.tan(TH)
                    pts = [(x0, y - rowh), (x0 + L - off, y - rowh), (x0 + L, y), (x0 + off, y)]
                else:
                    pts = [(x0, y - rowh), (x0 + L, y - rowh), (x0 + L, y), (x0, y)]
                poly(ax, pts, hatch=hatch)
                ax.text(x0 + L / 2, y - rowh / 2, '%s%d' % (code, k + 1), ha='center', va='center', fontsize=6.5,
                        bbox=dict(facecolor='white', edgecolor='none', pad=0.3), zorder=6)
                y -= rowh + 0.45
            ax.text(x0 + 41.5, y + (rowh + 0.45) * n / 2 + 0.2, '%s  %s\n%d x %s in' % (code, name, n, frac(L)),
                    fontsize=7, va='center')
            y -= gap
    # posts and plastic in the lower right
    x0, y0 = 54.0, 11.5
    ax.text(x0, y0 + 4.0, 'POSTS (one 2x4 stringer)', fontsize=10, fontweight='bold', va='bottom')
    xp = x0
    for code, L in (('P1', C.ztop(BT + C.PT)), ('P2', C.ztop(BT + C.PT)), ('P3', C.ztop(D - BT)), ('P4', C.ztop(D - BT))):
        rect(ax, xp, y0 - L + 3.5, C.PW, L, hatch='xxxx')
        ax.text(xp + C.PW / 2, y0 - L + 2.6, code, ha='center', va='top', fontsize=6.5)
        xp += C.PW + 1.5
    ax.text(x0, y0 - 9.5, 'P1, P2  front posts, %s in\nP3, P4  back posts, %s in\ntops cut to the slope'
            % (frac(C.ztop(BT + C.PT)), frac(C.ztop(D - BT))), fontsize=7, va='top')
    ax.text(x0 + 36.0, y0 + 4.0, 'PLASTIC', fontsize=10, fontweight='bold', va='bottom')
    rect(ax, x0 + 36.0, y0 - 8.0, 10.0, 10.0, hatch='....', lw=0.7)
    ax.text(x0 + 41.0, y0 - 9.0, 'S  40 x %s in sheet\n(drawn at 1:40)' % frac(LV), ha='center', va='top', fontsize=7)
    fig.text(0.35 / 11, 0.2 / 8.5, 'Hatching: lid bottom layer ////, top layer \\\\\\\\, angled boards dotted, posts crossed.',
             fontsize=7.5, color='0.3')
    emit(fig, '07_pieces')

print('wrote', pdf_path, pages)
