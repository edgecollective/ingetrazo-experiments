"""Shopping list for the treehouse, from the same parts the 3D model is built
from.  Usage: python th_export.py OUT.csv"""
import csv
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import th_geom as T

STOCK = {'6x6': [96, 120], '4x4': [96, 120], '2x12': [96, 120, 144, 192], '2x8': [96, 120, 144, 192],
         '2x6': [96, 120, 144, 192], '2x4': [96, 120, 144, 192], '2x2': [96], '1x4': [96, 120, 144, 192],
         '1x6': [96, 120, 144, 192]}
GRADE = {'PT': 'pressure-treated', 'KD': 'KD framing (SPF/SYP)', 'trim': 'exterior trim (PT, cedar or primed)',
         'baluster': 'PT baluster'}
KERF = 0.25


def pack(lengths, stock):
    """First-fit decreasing into stock boards; returns {stock_len: count}."""
    boards = []                                  # [stock, remaining]
    for L in sorted(lengths, reverse=True):
        L += KERF
        for b in boards:
            if b[1] >= L:
                b[1] -= L
                break
        else:
            s = next((s for s in stock if s + KERF >= L), None)
            if s is None:
                raise ValueError('piece %.1f longer than stock %s' % (L, stock))
            boards.append([s, s - L])
    out = {}
    for s, _r in boards:
        out[s] = out.get(s, 0) + 1
    return out


def area(loop):
    pts = [tuple(p) for p in loop]
    spans = [max(p[k] for p in pts) - min(p[k] for p in pts) for k in range(3)]
    k = spans.index(min(spans))
    a, b = [i for i in range(3) if i != k]
    s = 0.0
    for i in range(len(pts)):
        p, q = pts[i], pts[(i + 1) % len(pts)]
        s += p[a] * q[b] - q[a] * p[b]
    return abs(s) / 2


def main(out):
    items, _tree = T.build_all()
    pieces = {}
    for it in items:
        for nom, L, grade in it['lumber'] or ():
            pieces.setdefault((nom, grade), []).append(L)
    rows = []
    for (nom, grade), Ls in sorted(pieces.items()):
        if grade == 'baluster':
            rows.append(('Lumber', '2x2 x 36 in %s' % GRADE[grade], len(Ls), 'railing'))
            continue
        for s, n in sorted(pack(Ls, STOCK[nom]).items()):
            rows.append(('Lumber', '%s x %d ft %s' % (nom, s // 12, GRADE[grade]), n,
                         '%d cut pieces' % len(Ls)))
    siding = sum(area(it['data'][0]) - sum(area(h) for h in it['data'][2])
                 for it in items if it['name'].startswith('T1-11'))
    roof = 2 * 146.25 * (85.75 / T.COS)
    inner = 2 * (137.0 * 72.0 - 2 * 22 * 60) + 2 * (50.5 * 72.0 - 144)
    sheets = [('Sheet goods', 'T1-11 siding 5/8 in, 4 x 8 ft', math.ceil(siding / 4608.0 * 1.15),
               '%.0f sq ft net + 15%%' % (siding / 144)),
              ('Sheet goods', 'Plywood 1/2 in, 4 x 8 ft (roof sheathing)', math.ceil(roof / 4608.0 * 1.1),
               '%.0f sq ft net + 10%%' % (roof / 144)),
              ('Sheet goods', 'Plywood 1/4 in, 4 x 8 ft (interior wall skins)', math.ceil(inner / 4608.0 * 1.1), ''),
              ('Sheet goods', 'Plywood 3/4 in, 4 x 8 ft (bunk, bench, table)', 2, ''),
              ('Sheet goods', 'Acrylic sheet 1/4 in, 24 x 48 in (cut into 6 panes, 24 x 24)', 3, 'windows'),
              ('Sheet goods', 'Acrylic sheet 1/4 in, 36 x 48 in (reading window, 36 x 30)', 1, '')]
    per_side = math.ceil(147.0 / 24.0)
    roofing = [('Roofing', 'Corrugated metal roof panel, 26 in x 8 ft', 2 * per_side, '24 in coverage'),
               ('Roofing', 'Metal ridge cap, 10 ft', 2, ''),
               ('Roofing', 'Roofing screws with washers, bag of 250', 1, ''),
               ('Roofing', 'Foam closure strips, pack', 2, 'eaves and ridge')]
    concrete = [('Concrete', 'Concrete form tube 12 in x 4 ft', 4, 'dig below your frost depth'),
                ('Concrete', 'Concrete mix, 80 lb bag', 22, 'about 5 per pier'),
                ('Concrete', 'Post base for 6x6 (e.g. Simpson ABU66Z)', 4, '')]
    hardware = [('Hardware', 'Treehouse attachment bolt (TAB) 1-1/4 in with floating bracket', 3,
                 'specialty: treehouse supplier, not Home Depot; have an arborist check the tree'),
                ('Hardware', 'Post cap for 6x6 with double 2x12 beam', 4, ''),
                ('Hardware', 'Joist hanger 2x8 (e.g. LUS28Z)', 12, 'headers and trimmers'),
                ('Hardware', 'Hurricane tie (e.g. H2.5AZ)', 12, 'rafters to walls'),
                ('Hardware', 'Carriage bolt 1/2 x 8 in with nut and washers', 30, 'railing posts, braces, beams'),
                ('Hardware', 'Structural wood screws 5 in, box of 50', 2, ''),
                ('Hardware', 'Exterior deck screws 3 in, 5 lb box', 3, 'decking, railing'),
                ('Hardware', 'Framing nails or screws 3 in, 5 lb box', 2, 'walls, roof framing'),
                ('Hardware', 'T-hinge 6 in', 4, 'door (2), hatch (2)'),
                ('Hardware', 'Gate latch or hasp', 1, 'door'),
                ('Hardware', 'Galvanized grab handle 12-18 in', 1, 'at the hatch'),
                ('Finish', 'Exterior stain or paint, 1 gal', 2, 'siding, trim, door'),
                ('Finish', 'Exterior caulk', 3, 'windows, trim')]
    with open(out, 'w', newline='') as fh:
        w = csv.writer(fh)
        w.writerow(['Category', 'Item (Home Depot stock size)', 'Qty', 'Notes'])
        for r in rows + sheets + roofing + concrete + hardware:
            w.writerow(r)
    return rows, sheets


if __name__ == '__main__':
    rows, sheets = main(sys.argv[1])
    for r in rows + sheets:
        print('%-60s %4s  %s' % (r[1], r[2], r[3]))
