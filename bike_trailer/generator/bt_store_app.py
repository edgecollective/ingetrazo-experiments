
# ============ IngeTrazo side (appended to bt_geom.py + bt4_geom.py + bt_store_geom.py) ============
from core.saved_views import SavedView
from core.textlabel import TextLabel
from core import units
from core.insert import is_scale_figure
from core.orient import orient_outward

IN = 0.0254
if scene._edit_stack:
    raise RuntimeError('a group is open for editing')
others = [g for g in scene.groups if not is_scale_figure(g)]
if others or scene.mesh.faces or ('viewport' in globals() and viewport.window()._current_path is not None):
    raise RuntimeError('not an empty new document; not building')
units.apply_units(scene, {'length': 'in', 'precision': 2})
STORE_LAYERS = ('Cabinet', 'Drawers', 'Display', 'Stock', 'Pegboard', 'Tools', 'Sign')
for ly in ('Frame', 'Dropouts', 'Wheels', 'Hardware', 'Deck', 'Legs') + STORE_LAYERS + ('Notes',):
    if not any(l.name == ly for l in layers):
        layers.append(Layer(ly))


def q(p):
    return QVector3D(p[0] * IN, p[1] * IN, p[2] * IN)


def soften(mesh, deg=40.0):
    c = math.cos(math.radians(deg))
    for e in mesh.edges:
        if len(e.faces) == 2 and QVector3D.dotProduct(e.faces[0].normal(), e.faces[1].normal()) > c:
            e.soft = True


def make(p, d=(0.0, 0.0, 0.0), use_ex=False):
    if use_ex:
        d = (d[0] + p['ex'][0], d[1] + p['ex'][1], d[2] + p['ex'][2])
    sh = lambda v: (v[0] + d[0], v[1] + d[1], v[2] + d[2])
    col = COL[p['color']]
    if p['kind'] == 'plate':
        pl = p['data']
        g = prism([q(sh(v)) for v in pl['loop']], q(pl['vec']), holes=[[q(sh(v)) for v in h] for h in pl['holes']],
                  name=p['name'], color=col)
        scene.groups.remove(g)
    else:
        m = Mesh()
        for f in p['data']:
            nf = m.add_face([q(sh(v)) for v in f])
            nf.attrs['color'] = col
        orient_outward(m)
        soften(m)
        g = Group(m, name=p['name'])
    g.layer = p['layer']
    return g


def container(name, kids, layer=None):
    g = Group(Mesh(), name=name)
    g.adopt(kids)
    g.component = False
    if layer:
        g.layer = layer
    return g


def by_layer(parts, d, use_ex=False):
    out = {}
    for p in parts:
        out.setdefault(p['layer'], []).append(make(p, d, use_ex))
    return [container(ly, gs, ly) for ly, gs in out.items()]


PARTS, META = build_store()
XA, XE = 0.0, 64.0                       # assembled, exploded
scene.groups.append(container('1 Mobile hardware store on the version 4 trailer (open)', by_layer(PARTS, (XA, 0.0, 0.0))))
scene.groups.append(container('2 Exploded: trailer, cabinet and drawers, bin display, pegboard and tools',
                              by_layer(PARTS, (XE, 0.0, 0.0), use_ex=True)))


def label(anchor, off, txt, layer=None):
    scene.text_labels.append(TextLabel(q(anchor), q(off), txt, layer=layer))


label((XA, 0.0, SIGN_Z[1] + 0.5), (0.0, 0.0, 8.0), '1 Mobile hardware store')
label((XE, 0.0, SIGN_Z[1] + 44.5), (0.0, 0.0, 6.0), '2 Exploded')
N = 'Notes'
label((-CX, -CY - 0.1, DECK_TOP + 6.0), (-9.0, -6.0, -4.0), '14 drawers: 12 small parts, 2 wide', N)
label((CX, -13.0, TOP + 3.0), (9.0, -6.0, 3.0), '8 hopper bins on two steps', N)
label((CX, YP, TOP + 12.0), (10.0, 0.0, 4.0), 'pegboard, both faces', N)
label((0.0, CY, DECK_TOP + 9.0), (0.0, 9.0, -2.0), 'door to bulk storage (tow side)', N)
label((6.0, -YC - OD, 4.0), (8.0, -8.0, -2.0), 'prop legs (4), up for towing', N)
label((-5.0, 10.0, TOP + 7.6), (-10.0, 6.0, 6.0), 'stock tote, cash box', N)
label((0.0, -CY, TOP), (0.0, -10.0, 1.0), 'counter %.0f in above the ground' % TOP, N)


def view(name, eye, tgt, hidden=(), fov=45.0):
    e = [c * IN for c in eye]; t = [c * IN for c in tgt]
    o = [e[i] - t[i] for i in range(3)]; d = math.sqrt(sum(c * c for c in o))
    return SavedView(name, target=tuple(t), distance=d, yaw=math.atan2(o[1], o[0]), pitch=math.asin(o[2] / d),
                     fov_deg=fov, hidden_layers=list(hidden))


HN = ('Notes',)
scene.saved_views.extend([
    view('1 Customer side (back): drawers, bins, pegboard', (-46.0, -80.0, 58.0), (0.0, -4.0, 30.0), hidden=HN, fov=40.0),
    view('2 Tow side (front): door, tote, rope and cord', (48.0, 76.0, 56.0), (0.0, 2.0, 30.0), hidden=HN, fov=40.0),
    view('3 Drawers and bins, close up', (-22.0, -54.0, 40.0), (0.0, -15.0, 28.0), hidden=HN, fov=40.0),
    view('4 Pegboard, customer face', (6.0, -44.0, 50.0), (0.0, 0.0, 44.0), hidden=HN, fov=40.0),
    view('5 With notes', (-60.0, -95.0, 70.0), (0.0, 0.0, 28.0), fov=42.0),
    view('6 Exploded', (XE + 80.0, -110.0, 105.0), (XE, 0.0, 46.0), hidden=HN, fov=42.0),
    view('7 Trailer only (store layers hidden)', (49.0, 63.0, 44.0), (0.0, 2.0, 11.0), hidden=HN + STORE_LAYERS + ('Legs',), fov=40.0),
])
for g in scene.groups:
    if is_scale_figure(g) and min(v.position.x() for v in g.mesh.vertices) < 1.0:
        dd = QVector3D(-34 * IN, -30 * IN, 0.0)
        for v in list(g.mesh.vertices):
            g.mesh.move_vertex(v, dd)
if 'viewport' in globals():
    scene.saved_views[0].apply(scene, viewport.camera); viewport.update()
else:
    _v = scene.saved_views[0]
    scene.camera_home = {'target': list(_v.target), 'distance': _v.distance, 'yaw': _v.yaw, 'pitch': _v.pitch,
                         'fov_deg': _v.fov_deg, 'perspective': True, 'two_point': False}
print('built hardware store: counter %.1f in, sign top %.1f in, %d drawers, %d parts'
      % (META['counter'], META['top'], META['n_drawers'], len(PARTS)))
