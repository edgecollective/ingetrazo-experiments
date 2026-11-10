"""Write the CNC package: one DXF per sheet, an SVG cut sheet and a CSV cut
list per variant, and a Markdown summary.  Run with the scratchpad venv."""
import csv
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cw_geom as G
import ezdxf
from ezdxf.enums import TextEntityAlignment

OUT = sys.argv[1] if len(sys.argv) > 1 else '/home/dwblair/gitwork/ingetrazo-experiments/clamshell_desk'
SC = 6.0          # SVG px per inch

FILL = {'plyA': '#e3c595', 'plyB': '#cfae7f', 'front': '#5b9aa0', 'bin': '#eea25a', 'stool': '#dcbc8a'}

HARDWARE = {
    'V1': [('Plate caster, 3 in overall, 100 lb+ each', 4), ('Plate caster, locking', 4),
           ('Continuous (piano) hinge 1-1/2 in, cut to 44-1/2 in', 1),
           ('Continuous hinge 1-1/2 in, cut to 27-3/8 in (desk leaf)', 1),
           ('Drop-lid stay / folding desk support, pair (50 lb+)', 1),
           ('Draw latch (holds the box shut)', 2), ('Barrel bolt or hook (holds B open)', 1),
           ('Wood glue; #8 x 5/8 in pan-head screws for hardware', 1)],
    'V2': [('Plate caster, 3 in overall, 100 lb+ each', 4), ('Plate caster, locking', 4),
           ('Continuous (piano) hinge 1-1/2 in, cut to 44-1/2 in', 1),
           ('Continuous hinge 1-1/2 in, cut to 33-3/8 in (desk leaf)', 1),
           ('No-mortise or butt hinge 2-1/2 in (doors)', 4), ('Magnetic catch (doors)', 2),
           ('Screw-in leveling glide 1/2 in (door feet)', 2),
           ('Draw latch (holds the box shut)', 2), ('Barrel bolt or hook (holds B open)', 1),
           ('Pegboard hook assortment, 1/4 in', 1), ('Wood glue; #8 x 5/8 in screws for hardware', 1)],
    'V3': [('Plate caster, 3 in overall, 100 lb+ each', 4), ('Plate caster, locking', 4),
           ('Continuous (piano) hinge 1-1/2 in, cut to 44-1/2 in', 1),
           ('Continuous hinge 1-1/2 in, cut to 33-3/8 in (desk leaf)', 1),
           ('No-mortise or butt hinge 2-1/2 in (doors)', 4), ('Magnetic catch (doors)', 2),
           ('Screw-in leveling glide 1/2 in (door feet)', 2),
           ('Side-mount drawer slides 8 in, pair', 1), ('Desk grommet 2 in', 1),
           ('Power strip, flat plug, mounted in the power bay', 1),
           ('Draw latch (holds the box shut)', 2), ('Barrel bolt or hook (holds B open)', 1),
           ('Pegboard hook assortment, 1/4 in', 1), ('Wood glue; #8 x 5/8 in screws for hardware', 1)],
}


def frac(x):
    """Inches to the nearest 1/16 as a fraction string."""
    n = int(round(x * 16))
    w, r = divmod(n, 16)
    if r == 0:
        return '%d' % w
    g = math.gcd(r, 16)
    return ('%d-%d/%d' % (w, r // g, 16 // g)) if w else '%d/%d' % (r // g, 16 // g)


def svg_path(loop, f, top):
    """Closed SVG path for a bulge loop mapped through f(u,v)->(x,y) inches."""
    pts = [(f(p[0], p[1]), p[2]) for p in loop]
    d = []
    for i, ((x, y), b) in enumerate(pts):
        X, Y = x * SC, (top - y) * SC
        if i == 0:
            d.append('M%.2f %.2f' % (X, Y))
    n = len(pts)
    for i in range(n):
        (x0, y0), b = pts[i]
        x1, y1 = pts[(i + 1) % n][0]
        X1, Y1 = x1 * SC, (top - y1) * SC
        if abs(b) < 1e-9:
            d.append('L%.2f %.2f' % (X1, Y1))
        else:
            th = 4 * math.atan(b)
            c = math.hypot(x1 - x0, y1 - y0)
            r = abs(c / 2 / math.sin(th / 2)) * SC
            d.append('A%.2f %.2f 0 %d %d %.2f %.2f' % (r, r, 1 if abs(th) > math.pi else 0, 1 if b < 0 else 0, X1, Y1))
    return ' '.join(d) + ' Z'


def main():
    os.makedirs(os.path.join(OUT, 'cnc'), exist_ok=True)
    summary = []
    for v in ('V1', 'V2', 'V3'):
        model = G.build(v)
        meta = model['meta']
        inst, sheets, ids = G.cnc_layout(model)
        assert not G.collisions(model, True) and not G.collisions(model, False)
        label = {r['n']: '%s-%02d' % (v, r['n']) for r in ids}
        where = {}
        # ---- DXF, one per sheet
        for si, sh in enumerate(sheets):
            doc = ezdxf.new('R2010', setup=True)
            doc.units = ezdxf.units.IN
            doc.header['$MEASUREMENT'] = 0
            for name, color in (('SHEET', 8), ('CUT_OUTSIDE', 1), ('CUT_INSIDE', 5), ('DRILL_0.25', 3), ('LABELS', 7)):
                doc.layers.add(name, color=color)
            msp = doc.modelspace()
            msp.add_lwpolyline([(0, 0), (G.SHEET_L, 0), (G.SHEET_L, G.SHEET_W), (0, G.SHEET_W)], close=True,
                               dxfattribs={'layer': 'SHEET'})
            for key, x, y, rot in sh:
                it = inst[key]
                f = G.sheet_xy(it, x, y, rot)
                where.setdefault(it['n'], set()).add(si + 1)
                msp.add_lwpolyline([(*f(p[0], p[1]), 0, 0, p[2]) for p in it['ol']], format='xyseb', close=True,
                                   dxfattribs={'layer': 'CUT_OUTSIDE'})
                for h in it['holes']:
                    msp.add_lwpolyline([(*f(p[0], p[1]), 0, 0, p[2]) for p in h], format='xyseb', close=True,
                                       dxfattribs={'layer': 'CUT_INSIDE'})
                for du, dv, dia in it['part'].drills:
                    msp.add_circle(f(du, dv), dia / 2, dxfattribs={'layer': 'DRILL_0.25'})
                u0, v0, u1, v1 = it['bb']
                cx, cy = f((u0 + u1) / 2, (v0 + v1) / 2)
                ht = 0.9 if min(u1 - u0, v1 - v0) > 3 else 0.5
                msp.add_text(label[it['n']], height=ht, dxfattribs={'layer': 'LABELS'}).set_placement(
                    (cx, cy), align=TextEntityAlignment.MIDDLE_CENTER)
            doc.saveas(os.path.join(OUT, 'cnc', '%s_sheet%d.dxf' % (v, si + 1)))

        # ---- SVG cut sheet
        gap, head = 14.0, 7.0
        rows = []
        Ht = head + len(sheets) * (G.SHEET_W + gap) + 4
        Wt = G.SHEET_L + 70.0
        out = ['<svg xmlns="http://www.w3.org/2000/svg" width="%.0f" height="%.0f" viewBox="0 0 %.0f %.0f" '
               'font-family="Arial, Helvetica, sans-serif">' % (Wt * SC, Ht * SC, Wt * SC, Ht * SC),
               '<rect width="100%" height="100%" fill="#ffffff"/>',
               '<text x="%.0f" y="%.0f" font-size="22" font-weight="bold">%s clamshell workstation: CNC cut sheets</text>'
               % (2 * SC, 4.2 * SC, meta['title']),
               '<text x="%.0f" y="%.0f" font-size="13" fill="#444">%d sheets of 4 x 8 ft plywood, %s in thick (T). '
               'Red = outside profile, blue = inside cuts, green = 1/4 in drill. Inches.</text>'
               % (2 * SC, 6.2 * SC, len(sheets), frac(G.T))]
        for si, sh in enumerate(sheets):
            oy = head + si * (G.SHEET_W + gap) + 2
            top = oy + G.SHEET_W        # sheet y=0 at the bottom of its box
            used = sum((inst[k]['bb'][2] - inst[k]['bb'][0]) * (inst[k]['bb'][3] - inst[k]['bb'][1]) for k, *_ in sh)
            out.append('<text x="%.1f" y="%.1f" font-size="15"><tspan font-weight="bold">Sheet %d of %d</tspan>'
                       '  (%s_sheet%d.dxf: %d parts, %.0f%% of the sheet)</text>'
                       % (2 * SC, (oy + 0.2) * SC, si + 1, len(sheets), v, si + 1, len(sh),
                          100 * used / (G.SHEET_L * G.SHEET_W)))
            sx = 2.0
            out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#f6f1e7" stroke="#888" stroke-width="1"/>'
                       % (sx * SC, (oy + 1) * SC, G.SHEET_L * SC, G.SHEET_W * SC))
            used = 0.0
            for key, x, y, rot in sh:
                it = inst[key]
                f0 = G.sheet_xy(it, x, y, rot)
                f = lambda u, v, f0=f0: (f0(u, v)[0] + sx, f0(u, v)[1])
                tp = top + 1
                d = svg_path(it['ol'], f, tp) + ' ' + ' '.join(svg_path(h, f, tp) for h in it['holes'])
                out.append('<path d="%s" fill="%s" fill-rule="evenodd" stroke="#c0392b" stroke-width="1"/>'
                           % (d, FILL.get(it['part'].color, '#ddd')))
                for h in it['holes']:
                    out.append('<path d="%s" fill="none" stroke="#2c5ea8" stroke-width="0.9"/>' % svg_path(h, f, tp))
                for du, dv, dia in it['part'].drills:
                    X, Y = f(du, dv)
                    out.append('<circle cx="%.1f" cy="%.1f" r="%.2f" fill="#ffffff" stroke="#2e8b57" stroke-width="0.6"/>'
                               % (X * SC, (tp - Y) * SC, dia / 2 * SC))
                u0, v0, u1, v1 = it['bb']
                X, Y = f((u0 + u1) / 2, (v0 + v1) / 2)
                small = min(u1 - u0, v1 - v0) < 4
                vert = rot != ((u1 - u0) < (v1 - v0)) and (max(u1 - u0, v1 - v0) / min(u1 - u0, v1 - v0) > 2.2)
                tr = ' transform="rotate(-90 %.1f %.1f)"' % (X * SC, (tp - Y) * SC) if vert else ''
                out.append('<text x="%.1f" y="%.1f" font-size="%d" text-anchor="middle" dominant-baseline="middle" '
                           'font-weight="bold" fill="#222"%s>%s</text>'
                           % (X * SC, (tp - Y) * SC, 9 if small else 12, tr, label[it['n']]))
                used += (u1 - u0) * (v1 - v0)

        # legend: id -> name
        lx = (2.0 + G.SHEET_L + 2)
        ly = head + 3
        out.append('<text x="%.1f" y="%.1f" font-size="13" font-weight="bold">Parts</text>' % (lx * SC, ly * SC))
        ly += 2.8
        for r in ids:
            out.append('<text x="%.1f" y="%.1f" font-size="11"><tspan font-weight="bold">%s</tspan> %s x%d</text>'
                       % (lx * SC, ly * SC, label[r['n']], r['name'].replace('&', 'and'), r['qty']))
            ly += 2.6
        out.append('</svg>')
        with open(os.path.join(OUT, '%s_cut_sheets.svg' % v), 'w') as fh:
            fh.write('\n'.join(out))

        # ---- CSV cut list
        with open(os.path.join(OUT, '%s_cut_list.csv' % v), 'w', newline='') as fh:
            w = csv.writer(fh)
            w.writerow(['ID', 'Part', 'Qty', 'Cut length (in)', 'Cut width (in)', 'Thickness (in)',
                        'Panel body (in)', 'Sheet(s)', 'Features'])
            for r in ids:
                p = r['part']
                u0, v0, u1, v1 = r['bb']
                L, Wd = max(u1 - u0, v1 - v0), min(u1 - u0, v1 - v0)
                if p.custom:
                    body = ''
                else:
                    a, b = p.size(); body = '%s x %s' % (frac(max(a, b)), frac(min(a, b)))
                ntab = sum(1 for e in p.feat.values() for f in e if f[0] == 'tab')
                nnot = sum(1 for e in p.feat.values() for f in e if f[0] == 'notch')
                kinds = {}
                for hd in p.holes:
                    kinds[hd[0]] = kinds.get(hd[0], 0) + 1
                feats = []
                if ntab: feats.append('%d tabs' % ntab)
                if nnot: feats.append('%d edge notches' % nnot)
                if kinds.get('mortise'): feats.append('%d through slots' % kinds['mortise'])
                if kinds.get('slot'): feats.append('%d hand/cable slots' % kinds['slot'])
                if kinds.get('circle'): feats.append('grommet hole')
                if p.drills: feats.append('%d pegboard holes' % len(p.drills))
                if any(f[0] == 'arc' for e in p.feat.values() for f in e): feats.append('finger pull')
                w.writerow([label[r['n']], r['name'], r['qty'], frac(L), frac(Wd), frac(G.T), body,
                            ' '.join(str(s) for s in sorted(where[r['n']])), '; '.join(feats)])
            w.writerow([])
            w.writerow(['Hardware (buy)', '', 'Qty'])
            for name, q in HARDWARE[v]:
                w.writerow(['', name, q])
        summary.append((v, meta, len(inst), len(ids), len(sheets), sum(len(p.drills) for p in model['parts'])))
        print(v, 'parts', len(inst), 'unique', len(ids), 'sheets', len(sheets))
    return summary


if __name__ == '__main__':
    main()
