
# ======================= IngeTrazo side (appended to bt_geom.py) =======================
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
for ly in ('Frame', 'Dropouts', 'Wheels', 'Hardware', 'Hitch', 'Deck'):
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
    if p['opacity'] is not None:
        for f in g.mesh.faces:
            f.attrs['opacity'] = p['opacity']
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


PARTS, META = build()
XB, XA, XE = -75.0, 0.0, 80.0
frame_only = [p for p in PARTS if p['name'].startswith('Main frame')]
scene.groups.append(container('1 Materials: two 10 ft conduits, 4 dropouts, 2 wheels, bolts, hitch',
                              by_layer(materials(), (-60.0, -95.0, 0.0))))
scene.groups.append(container('2 Main frame bent from one 10 ft conduit', by_layer(frame_only, (XB, 0.0, -ZO + RP))))
scene.groups.append(container('3 Assembled trailer (v1.0, 16 in wheels)', by_layer(PARTS, (XA, 0.0, 0.0))))
scene.groups.append(container('4 Exploded', by_layer(PARTS, (XE, 0.0, 0.0), use_ex=True)))

for x, y, z, txt in ((0.0, -85.0, 3.0, '1 Materials'), (XB, 0.0, 2.0, '2 Bent main frame (one 10 ft conduit)'),
                     (XA, 0.0, 17.0, '3 Assembled trailer'), (XE, 0.0, 36.0, '4 Exploded')):
    lb = TextLabel(q((x, y, z)), QVector3D(0.0, 0.0, 0.30), txt)
    scene.text_labels.append(lb)


def view(name, eye, tgt, hidden=(), fov=45.0):
    e = [c * IN for c in eye]; t = [c * IN for c in tgt]
    o = [e[i] - t[i] for i in range(3)]; d = math.sqrt(sum(c * c for c in o))
    return SavedView(name, target=tuple(t), distance=d, yaw=math.atan2(o[1], o[0]), pitch=math.asin(o[2] / d),
                     fov_deg=fov, hidden_layers=list(hidden))


scene.saved_views.extend([
    view('1 Overview: materials, bent frame, assembled, exploded', (60.0, -230.0, 140.0), (0.0, -20.0, 5.0)),
    view('2 Assembled trailer', (52.0, 66.0, 40.0), (0.0, 6.0, 8.0)),
    view('3 Frame without the deck', (-50.0, 62.0, 42.0), (0.0, 4.0, 8.0), hidden=('Deck',)),
    view('4 Wheel mount: long and short dropouts', (-24.0, -12.0, 14.0), (-9.0, 0.0, 8.5), hidden=('Deck',), fov=40.0),
    view('5 Exploded', (XE + 60.0, -60.0, 60.0), (XE, 4.0, 12.0)),
    view('6 Bent frame from above', (XB, 8.0, 120.0), (XB, 8.0, 0.0), fov=40.0),
    view('7 Materials', (0.0, -150.0, 70.0), (0.0, -85.0, 0.0)),
])
for g in scene.groups:
    if is_scale_figure(g) and min(v.position.x() for v in g.mesh.vertices) < 1.0:
        dd = QVector3D(-150 * IN, 40 * IN, 0.0)
        for v in list(g.mesh.vertices):
            g.mesh.move_vertex(v, dd)
if 'viewport' in globals():
    scene.saved_views[1].apply(scene, viewport.camera); viewport.update()
else:
    _v = scene.saved_views[1]
    scene.camera_home = {'target': list(_v.target), 'distance': _v.distance, 'yaw': _v.yaw, 'pitch': _v.pitch,
                         'fov_deg': _v.fov_deg, 'perspective': True, 'two_point': False}
print('built bike trailer: main conduit %.1f in, loop %.1f x %.1f in' % (META['L_main'], META['width'], META['length']))
