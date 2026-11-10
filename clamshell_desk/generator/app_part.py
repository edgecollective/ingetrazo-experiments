
# ======================= IngeTrazo side (appended to cw_geom.py) =======================
from PySide6.QtGui import QMatrix4x4
from core.textlabel import TextLabel
from core.insert import is_scale_figure

VARIANT = '%%VARIANT%%'
IN = 0.0254
COLX = {'V1': 12.0, 'V2': 132.0, 'V3': 252.0}     # x of each variant's hinge corner
CLOSED_DX = 52.0                                  # closed copy sits to the right
SHEETS_Y0 = -60.0                                 # flat sheets start this far in front

if scene._edit_stack:
    raise RuntimeError('a group is open for editing; not building')
others = [g for g in scene.groups if not g.name.startswith('Clamshell ') and not is_scale_figure(g)]
if others or scene.mesh.faces:
    raise RuntimeError('this document already holds other geometry (%d groups, %d loose faces); not building'
                       % (len(others), len(scene.mesh.faces)))
if any(g.name.startswith('Clamshell %s' % VARIANT) for g in scene.groups):
    raise RuntimeError('%s is already built' % VARIANT)
for nm in ('Clamshell open', 'Clamshell closed', 'CNC sheets'):
    if not any(l.name == nm for l in layers):
        layers.append(Layer(nm))


def q(p):
    return QVector3D(p[0] * IN, p[1] * IN, p[2] * IN)


def soften(mesh, deg=42.0):
    c = math.cos(math.radians(deg))
    for e in mesh.edges:
        if len(e.faces) == 2 and QVector3D.dotProduct(e.faces[0].normal(), e.faces[1].normal()) > c:
            e.soft = True


def mk_prism(name, loop, vec, holes, color):
    g = prism([q(p) for p in loop], q(vec), holes=[[q(p) for p in h] for h in holes], name=name,
              color=COLORS[color])
    scene.groups.remove(g)
    return g


def drill_squares(f, drills):
    s = 0.11
    return [[f(du - s, dv - s), f(du + s, dv - s), f(du + s, dv + s), f(du - s, dv + s)] for du, dv, _d in drills]


def part_group(p, label):
    O, Uv, Vv, Nv = p.frame()
    ol, hl = part_geometry(p, False)
    f = lambda u, v: tuple(O[i] + Uv[i] * u + Vv[i] * v for i in range(3))
    holes = [[f(u, v) for u, v in expand(h, 10)] for h in hl] + drill_squares(f, p.drills)
    return mk_prism(label, [f(u, v) for u, v in expand(ol, 10)], Nv, holes, p.color)


def hw_group(name, items):
    m = Mesh()
    for h in items:
        if h['kind'] == 'box':
            x0, x1, y0, y1, z0, z1 = h['box']
            g = box((x0 * IN, y0 * IN, z0 * IN), ((x1 - x0) * IN, (y1 - y0) * IN, (z1 - z0) * IN),
                    color=COLORS[h['color']])
        else:
            g = prism([q(p) for p in h['loop']], q(h['vec']), color=COLORS[h['color']])
        scene.groups.remove(g)
        for fc in g.mesh.faces:
            nf = m.add_face(list(fc.vertices))
            nf.attrs.update(fc.attrs)
    soften(m)
    return Group(m, name=name)


def container(name, kids, xf=None):
    g = Group(Mesh(), name=name)
    g.adopt(kids)
    if xf is not None:
        g.xform = xf
    g.component = False
    return g


def mmat(mv):
    kind, c, ang = mv
    m = QMatrix4x4()
    if kind == 't':
        m.translate(c[0] * IN, c[1] * IN, c[2] * IN)
        return m
    p, ax = ((c[0] * IN, c[1] * IN, 0.0), (0.0, 0.0, 1.0)) if kind == 'rz' else ((0.0, c[0] * IN, c[1] * IN), (1.0, 0.0, 0.0))
    m.translate(*p); m.rotate(ang, *ax); m.translate(-p[0], -p[1], -p[2])
    return m


def tag(g, layer):
    g.layer = layer
    for c in g.children or ():
        tag(c, layer)


model = build(VARIANT)
meta = model['meta']
inst, sheets, ids = cnc_layout(model)
lab = {id(it['part']): '%s-%02d %s' % (VARIANT, it['n'], ids[it['n'] - 1]['name']) for it in inst}
SUBNAME = {'leaf': 'Desk leaf (folds down)', 'doorL': 'Door, hinge side (swings out as a desk leg)',
           'doorR': 'Door, free side (swings out as a desk leg)', 'bins': 'Bins', 'drawer': 'Pencil drawer'}


def config(opened):
    st = 'open' if opened else 'closed'
    pb, hb = {}, {}
    for p in model['parts']:
        pb.setdefault((p.asm, p.sub), []).append(part_group(p, lab[id(p)]))
    for h in model['hw']:
        if h['state'] and h['state'] != st:
            continue
        hb.setdefault((h['asm'], h['sub']), []).append(h)
    a_kids = list(pb.get(('A', None), []))
    if hb.get(('A', None)):
        a_kids.append(hw_group('Half A hardware (casters, hinges%s)' % (', stays' if VARIANT == 'V1' else ''),
                               hb[('A', None)]))
    for sub in ('leaf', 'doorL', 'doorR', 'bins', 'drawer'):
        if ('A', sub) in pb:
            mv = model['moves'].get(sub) if opened else None
            a_kids.append(container(SUBNAME[sub], pb[('A', sub)], mmat(mv) if mv else None))
    halfA = container('Half A (desk half)', a_kids)
    b_kids = list(pb[('B', None)]) + [hw_group('Half B hardware (casters, hinge leaf)', hb[('B', None)])]
    halfB = container('Half B (storage half, swings on the hinge)', b_kids, mmat(model['moves']['B']) if opened else None)
    kids = [halfA, halfB]
    if ('Stool', None) in pb:
        kids.append(container('Flat-pack stool (CNC, no hardware)', pb[('Stool', None)]))
    if opened and ('Chair', None) in hb:
        kids.append(hw_group('Office chair (not part of the kit)', hb[('Chair', None)]))
    ox = COLX[VARIANT] + (0.0 if opened else CLOSED_DX)
    xf = QMatrix4x4(); xf.translate(ox * IN, 0.0, 0.0)
    top = container('Clamshell %s %s (%s)' % (VARIANT, meta['title'][3:], st), kids, xf)
    tag(top, 'Clamshell ' + st)
    scene.groups.append(top)
    W, DA, DB, H = meta['W'], meta['DA'], meta['DB'], meta['H']
    txt = ('%s, open' % meta['title']) if opened else \
        ('%s, closed: %s x %s x %s in' % (meta['title'], frac(W), frac(DA + DB), frac(H + HC)))
    lbl = TextLabel(q((ox + W / 2, DB + DA, HC + H)), QVector3D(0.0, 0.0, 0.40 if opened else 0.25), txt)
    lbl.layer = 'Clamshell ' + st
    scene.text_labels.append(lbl)


def frac(x):
    n = int(round(x * 16)); w, r = divmod(n, 16)
    if r == 0:
        return '%d' % w
    g = math.gcd(r, 16)
    return '%d-%d/%d' % (w, r // g, 16 // g)


config(True)
config(False)

# flat CNC sheets, laid out in front of the variant
sheet_groups = []
for si, sh in enumerate(sheets):
    oxs, oys = COLX[VARIANT] - 12.0, SHEETS_Y0 - SHEET_W - si * (SHEET_W + 12.0)
    slab = box((oxs * IN, oys * IN, 0.0), (SHEET_L * IN, SHEET_W * IN, 0.1 * IN), name='Plywood sheet 4 x 8 ft',
               color=COLORS['sheet'])
    scene.groups.remove(slab)
    kids = [slab]
    for key, x, y, rot in sh:
        it = inst[key]
        fxy = sheet_xy(it, x, y, rot)
        f = lambda u, v, fxy=fxy: (oxs + fxy(u, v)[0], oys + fxy(u, v)[1], 0.1)
        holes = [[f(u, v) for u, v in expand(h, 6)] for h in it['holes']] + drill_squares(f, it['part'].drills)
        kids.append(mk_prism(lab[id(it['part'])], [f(u, v) for u, v in expand(it['ol'], 6)], (0, 0, T), holes,
                             it['part'].color))
    sheet_groups.append(container('%s sheet %d of %d (%s_sheet%d.dxf)' % (VARIANT, si + 1, len(sheets), VARIANT, si + 1),
                                  kids))
    lbl = TextLabel(q((oxs, oys + SHEET_W, 0.1)), QVector3D(-0.15, 0.0, 0.25),
                    '%s sheet %d of %d' % (VARIANT, si + 1, len(sheets)))
    lbl.layer = 'CNC sheets'
    scene.text_labels.append(lbl)
top = container('Clamshell %s CNC sheets (%d x 4x8 ft, %s in ply)' % (VARIANT, len(sheets), frac(T)), sheet_groups)
tag(top, 'CNC sheets')
scene.groups.append(top)
print('%s built: %d parts (%d unique), %d sheets' % (VARIANT, len(inst), len(ids), len(sheets)))
