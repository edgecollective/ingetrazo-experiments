
# ======================= IngeTrazo side (appended to bt_geom.py + bt4_geom.py) =======================
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
for ly in ('Frame', 'Dropouts', 'Wheels', 'Hardware', 'Marks', 'Deck', 'Notes'):
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
MX, MY = -60.0, -100.0             # materials offset
XB, XA, XE = -80.0, 0.0, 90.0       # bent frame, assembled, exploded
scene.groups.append(container('1 Materials: two 10 ft conduits, 4 dropouts, 2 wheels, bolts, coupling',
                              by_layer(materials(), (MX, MY, 0.0))))
scene.groups.append(container('2 Main frame: one 10 ft conduit, four 90 deg bends, ends joined at the front',
                              by_layer(bent_frame(), (XB, 0.0, -ZO + RP))))
scene.groups.append(container('3 Assembled trailer (version 4, %d in wheels)' % WHEEL_IN, by_layer(PARTS, (XA, 0.0, 0.0))))
scene.groups.append(container('4 Exploded', by_layer(PARTS, (XE, 0.0, 0.0), use_ex=True)))


def label(anchor, off, txt, layer=None):
    scene.text_labels.append(TextLabel(q(anchor), q(off), txt, layer=layer))


label((MX + 50.0, MY + 27.0, 2.2), (0.0, 0.0, 14.0), '1 Materials')
label((XB, 0.0, 2.0), (0.0, 0.0, 12.0), '2 Bent main frame (one 10 ft conduit)')
label((XA, 0.0, ZI + RP + 0.5), (0.0, 0.0, 14.0), '3 Assembled trailer')
label((XE, 0.0, ZI + RP + 31.0), (0.0, 0.0, 10.0), '4 Exploded')
for a, b in BENDS:                                   # bend marks on the straight conduit
    label((MX + (a + b) / 2, MY, 2 * RP), (0.0, -8.0, 0.0), 'bend %g-%g' % (a, b), 'Notes')
label((MX + 72.0, MY + 5.0, 2 * RP), (5.0, 0.0, 8.0), 'cut at 36 and 72 in (48 in spare)', 'Notes')
for a, _b in BENDS:                                  # the sketch's circled numbers, on the bent loop
    (x, y), t = at(a)
    o = (math.copysign(4.0, x), math.copysign(4.0, y))
    label((XB + x, y, RP), (o[0], o[1], 2.0), '%g in' % a, 'Notes')
label((XB, YC, RP), (0.0, 6.0, 2.0), 'ends meet: 0 / 120 in, coupling', 'Notes')


def view(name, eye, tgt, hidden=(), fov=45.0):
    e = [c * IN for c in eye]; t = [c * IN for c in tgt]
    o = [e[i] - t[i] for i in range(3)]; d = math.sqrt(sum(c * c for c in o))
    return SavedView(name, target=tuple(t), distance=d, yaw=math.atan2(o[1], o[0]), pitch=math.asin(o[2] / d),
                     fov_deg=fov, hidden_layers=list(hidden))


N = ('Notes',)
scene.saved_views.extend([
    view('1 Overview: materials, bent frame, assembled, exploded', (47.0, -222.0, 123.0), (12.0, -42.0, 8.0), hidden=N),
    view('2 Assembled trailer', (49.0, 63.0, 44.0), (0.0, 2.0, 11.0), hidden=N, fov=40.0),
    view('3 Frame without the deck', (-50.0, 62.0, 45.0), (0.0, 2.0, 11.0), hidden=N + ('Deck',), fov=40.0),
    view('4 Wheel mount: long and short dropouts', (-40.0, -34.0, 22.0), (-12.5, 0.0, 13.2), hidden=N + ('Deck',), fov=23.0),
    view('5 Exploded', (XE + 70.0, -74.0, 74.0), (XE, 0.0, 21.0), hidden=N, fov=45.0),
    view('6 Bent frame from above, with the bend marks', (XB, -0.5, 105.0), (XB, 0.0, 0.0), fov=32.0),
    view('7 Materials', (0.0, -190.0, 70.0), (0.0, -88.0, 0.0), fov=45.0),
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
print('built bike trailer v4: loop %.2f in, outside %.1f x %.1f in, wheel gap %.1f mm clear, deck at %.1f in'
      % (META['L_loop'], META['width'], META['length'], META['clear_mm'], META['deck_z']))
