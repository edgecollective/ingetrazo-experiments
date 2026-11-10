
# ======================= IngeTrazo side (appended to ws_geom.py) =======================
from core.saved_views import SavedView
from core import units
from core.insert import is_scale_figure

IN = 0.0254
REPLACE = globals().get('REPLACE', False)
if scene._edit_stack:
    raise RuntimeError('a group is open for editing; not building')
others = [g for g in scene.groups if not is_scale_figure(g)]
if REPLACE:      # rebuilding over an earlier lean-to in this tab: only ever touch our own groups
    mine = [g for g in others if g.name.startswith(('Cheap lean-to', 'Shipping container'))]
    if len(mine) != len(others):
        raise RuntimeError('unexpected groups in this tab: %s' % [g.name for g in others if g not in mine])
    for g in mine:
        scene.groups.remove(g)
    del scene.saved_views[:]
    others = []
if others or scene.mesh.faces:
    raise RuntimeError('this document is not empty (%d groups); not building' % len(others))
units.apply_units(scene, {'length': 'in', 'precision': 2})
items = build_all()
for _s, ly in SYSTEMS:
    if not any(l.name == ly for l in layers):
        layers.append(Layer(ly))


def q(p):
    return QVector3D(p[0] * IN, p[1] * IN, p[2] * IN)


def make(it):
    if it['kind'] == 'box':
        x0, x1, y0, y1, z0, z1 = it['data']
        g = box((x0 * IN, y0 * IN, z0 * IN), ((x1 - x0) * IN, (y1 - y0) * IN, (z1 - z0) * IN),
                name=it['name'], color=COL[it['color']])
    else:
        loop, vec, holes = it['data']
        g = prism([q(p) for p in loop], q(vec), name=it['name'], color=COL[it['color']])
    scene.groups.remove(g)
    if it['opacity'] is not None:
        for f in g.mesh.faces:
            f.attrs['opacity'] = it['opacity']
        for e in g.mesh.edges:          # corrugation creases would draw as dense black lines
            e.soft = True
    return g


def container(name, kids):
    g = Group(Mesh(), name=name)
    g.adopt(kids)
    g.component = False
    return g


def tag(g, layer):
    g.layer = layer
    for c in g.children or ():
        tag(c, layer)


kids = []
for sysn, ly in SYSTEMS:
    gs = [make(it) for it in items if it['sys'] == sysn]
    if sysn.startswith('Shipping'):
        g = gs[0] if len(gs) == 1 else container('Shipping container 8 x 20 ft (existing, not attached)', gs)
        tag(g, ly); scene.groups.append(g)
        continue
    c = container(sysn, gs); tag(c, ly); kids.append(c)
scene.groups.append(container('Cheap lean-to: Suntuf on 2x4 trusses, 128 x 240 in' + (', strapped to the container' if MODE == 'strapped' else ''), kids))


def view(name, eye, tgt, hidden=(), fov=45.0):
    eye = [c * IN for c in eye]; tgt = [c * IN for c in tgt]
    o = [eye[i] - tgt[i] for i in range(3)]; d = math.sqrt(sum(c * c for c in o))
    return SavedView(name, target=tuple(tgt), distance=d, yaw=math.atan2(o[1], o[0]), pitch=math.asin(o[2] / d),
                     fov_deg=fov, hidden_layers=list(hidden))


scene.saved_views.extend([
    view('1 Overview from the open side', (430.0, -250.0, 230.0), (150.0, 115.0, 60.0)),
    view('2 Under the roof, along the bays', (200.0, -95.0, 66.0), (150.0, 160.0, 82.0), fov=55.0),
    view('3 One bent: truss, posts, ballast', (166.0, -205.0, 62.0), (166.0, 0.0, 62.0), fov=40.0),
    view('4 Framing only (panels hidden)', (430.0, -250.0, 230.0), (150.0, 115.0, 60.0), hidden=('Roof panels',)),
    view('5 From above', (300.0, 40.0, 560.0), (165.0, 120.0, 90.0)),
] + ([view('6 Tie-downs in the gap: straps, bearing blocks', (150.0, -70.0, 64.0), (98.0, 70.0, 40.0), fov=50.0)]
     if MODE == 'strapped' else []))
for g in scene.groups:
    if is_scale_figure(g) and min(v.position.x() for v in g.mesh.vertices) < 1.0:
        d = QVector3D(175 * IN, 60 * IN, 0.0)
        for v in list(g.mesh.vertices):
            g.mesh.move_vertex(v, d)
v = scene.saved_views[0]
v.apply(scene, viewport.camera); viewport.update()
print('built', len(items), 'parts')
