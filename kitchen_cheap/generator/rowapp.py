
# ======================= IngeTrazo side (appended to rowgen.py) =======================
from core.saved_views import SavedView
from core import units
from core.insert import is_scale_figure

IN = 0.0254
if scene._edit_stack:
    raise RuntimeError('a group is open for editing; not building')
others = [g for g in scene.groups if not is_scale_figure(g)]
if others or scene.mesh.faces or viewport.window()._current_path is not None:
    raise RuntimeError('not an empty new document; not building')
units.apply_units(scene, {'length': 'in', 'precision': 2})
LAYERS = ['Context (container, shed)', 'Bases', 'Posts and bracing', 'Trusses', 'Purlins', 'Roof panels', 'Tie-downs']
for ly in LAYERS:
    if not any(l.name == ly for l in layers):
        layers.append(Layer(ly))
LAYER_OF = {'Bases': 'Bases', 'Posts and bracing': 'Posts and bracing', 'Trusses': 'Trusses', 'Purlins': 'Purlins',
            'Suntuf roof panels': 'Roof panels', 'Tie-downs to the container': 'Tie-downs',
            'Tie-downs to the shed': 'Tie-downs', 'Context': 'Context (container, shed)'}
ORDER = ['Bases', 'Posts and bracing', 'Trusses', 'Purlins', 'Suntuf roof panels', 'Tie-downs to the container',
         'Tie-downs to the shed']


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
        for e in g.mesh.edges:
            e.soft = True
    g.layer = LAYER_OF[it['sys']]
    return g


def container(name, kids, layer=None):
    g = Group(Mesh(), name=name)
    g.adopt(kids)
    g.component = False
    if layer:
        g.layer = layer
    return g


ctx = context_items()
cont = [make(i) for i in ctx if 'hed' not in i['name']]
shed = [make(i) for i in ctx if 'hed' in i['name']]
scene.groups.append(container('Shipping container 8 x 20 ft (existing)', cont, 'Context (container, shed)'))
scene.groups.append(container('Shed 10 x 20 ft (existing; placeholder, check its wall heights)', shed,
                              'Context (container, shed)'))
for lean in (workshop(), kitchen()):
    items = lean.build()
    kids = []
    for sysn in ORDER:
        gs = [make(i) for i in items if i['sys'] == sysn]
        if gs:
            kids.append(container(sysn, gs, LAYER_OF[sysn]))
    scene.groups.append(container(lean.title, kids))


def view(name, eye, tgt, hidden=(), fov=45.0):
    eye = [c * IN for c in eye]; tgt = [c * IN for c in tgt]
    o = [eye[i] - tgt[i] for i in range(3)]; d = math.sqrt(sum(c * c for c in o))
    return SavedView(name, target=tuple(tgt), distance=d, yaw=math.atan2(o[1], o[0]), pitch=math.asin(o[2] / d),
                     fov_deg=fov, hidden_layers=list(hidden))


scene.saved_views.extend([
    view('1 The row: container, workshop, shed, kitchen', (700.0, -520.0, 330.0), (300.0, 120.0, 50.0)),
    view('2 Kitchen from the open side', (760.0, -230.0, 200.0), (470.0, 120.0, 60.0)),
    view('3 Kitchen: one frame and its arms to the shed', (480.0, -215.0, 62.0), (480.0, 0.0, 62.0), fov=40.0),
    view('4 Kitchen framing (panels hidden)', (760.0, -230.0, 200.0), (470.0, 120.0, 60.0), hidden=('Roof panels',)),
    view('5 Workshop (open-side ballast added)', (430.0, -250.0, 230.0), (150.0, 115.0, 60.0)),
])
for g in scene.groups:
    if is_scale_figure(g) and min(v.position.x() for v in g.mesh.vertices) < 1.0:
        d = QVector3D(470 * IN, 60 * IN, 0.0)
        for v in list(g.mesh.vertices):
            g.mesh.move_vertex(v, d)
scene.saved_views[0].apply(scene, viewport.camera); viewport.update()
print('built row:', len(scene.groups), 'top groups')
