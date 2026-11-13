
# ============ IngeTrazo side (appended to bt_geom.py + bt4_geom.py + bt_store_geom.py + bt_tackle_geom.py) ============
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
STORE_LAYERS = ('Cabinet', 'Doors', 'Trays', 'Arms', 'Stock', 'Lid', 'Tools', 'Sign')
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


PARTS, META = build_tackle(True)
CLOSED, _m = build_tackle(False)
XA, XC = 0.0, 64.0                       # open, closed
scene.groups.append(container('1 Tackle-box store on the version 4 trailer (open)', by_layer(PARTS, (XA, 0.0, 0.0))))
scene.groups.append(container('2 Closed for towing', by_layer(CLOSED, (XC, 0.0, 0.0))))


def label(anchor, off, txt, layer=None):
    scene.text_labels.append(TextLabel(q(anchor), q(off), txt, layer=layer))


label((XA, 0.0, LID_TOP + 0.5), (0.0, 0.0, 6.0), '1 Tackle-box store (open)')
label((XC, 0.0, Z_HINGE + 0.5), (0.0, 0.0, 10.0), '2 Closed for towing')
N = 'Notes'
label((-17.0, -10.0, ZB + 6.0 + TT), (-10.0, -6.0, 6.0), 'trays fan out on parallel arms, like a tackle box', N)
label((0.0, -8.0, ZB + TT), (-4.0, -12.0, 8.0), 'fixed tray, 32 compartments', N)
label((CX + 4.0, -CY - 8.0, DECK_TOP + 10.0), (10.0, -4.0, 0.0), 'doors swing out: shelves of parts jars', N)
label((0.0, -CY + 4.0, DECK_TOP + 3.0), (0.0, -14.0, -6.0), '12 cubbies behind the doors', N)
label((CX, CY - 1.3, Z_HINGE + 20.0), (10.0, 0.0, 4.0), 'lid stands up: pegboard and sign', N)
label((CX + 2 * SLIDE, CY, ZB + 7.6), (8.0, 6.0, 0.0), 'arms: 3/16 x 5/8 in flat bar, 2 per end', N)


def view(name, eye, tgt, hidden=(), fov=45.0):
    e = [c * IN for c in eye]; t = [c * IN for c in tgt]
    o = [e[i] - t[i] for i in range(3)]; d = math.sqrt(sum(c * c for c in o))
    return SavedView(name, target=tuple(t), distance=d, yaw=math.atan2(o[1], o[0]), pitch=math.asin(o[2] / d),
                     fov_deg=fov, hidden_layers=list(hidden))


HN = ('Notes',)
scene.saved_views.extend([
    view('1 Open, customer side (back)', (-62.0, -100.0, 80.0), (0.0, -2.0, 42.0), hidden=HN, fov=40.0),
    view('2 Open, from the side over the trays', (78.0, -56.0, 78.0), (6.0, 0.0, 36.0), hidden=HN, fov=40.0),
    view('3 Doors, jars and cubbies', (-16.0, -62.0, 34.0), (0.0, -18.0, 24.0), hidden=HN, fov=40.0),
    view('4 Cantilever arms, end view', (10.0, -80.0, 38.0), (10.0, -17.0, 36.0), hidden=HN, fov=36.0),
    view('5 Closed for towing', (XC - 50.0, -66.0, 52.0), (XC, 0.0, 24.0), hidden=HN, fov=40.0),
    view('6 Open and closed', (30.0, -150.0, 95.0), (32.0, 0.0, 34.0), hidden=HN, fov=42.0),
    view('7 With notes', (-70.0, -110.0, 90.0), (0.0, 0.0, 36.0), fov=45.0),
])
for g in scene.groups:
    if is_scale_figure(g) and min(v.position.x() for v in g.mesh.vertices) < 1.0:
        dd = QVector3D(-40 * IN, -36 * IN, 0.0)
        for v in list(g.mesh.vertices):
            g.mesh.move_vertex(v, dd)
if 'viewport' in globals():
    scene.saved_views[0].apply(scene, viewport.camera); viewport.update()
else:
    _v = scene.saved_views[0]
    scene.camera_home = {'target': list(_v.target), 'distance': _v.distance, 'yaw': _v.yaw, 'pitch': _v.pitch,
                         'fov_deg': _v.fov_deg, 'perspective': True, 'two_point': False}
print('built tackle-box store: closed top %.1f in, lid top %.1f in, open width %.1f in, %d tray compartments'
      % (META['top_closed'], META['lid_top'], META['width_open'], META['compartments']))
