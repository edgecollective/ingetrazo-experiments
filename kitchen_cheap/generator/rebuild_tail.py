
# ======================= IngeTrazo side (appended to rowgen.py) =======================
from core.saved_views import SavedView
from core import units
from core.insert import is_scale_figure

IN = 0.0254
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


w = viewport.window()
if str(w._current_path) != '/home/dwblair/gitwork/ingetrazo-experiments/kitchen_cheap/site_row_cheap.igz':
    raise RuntimeError('unexpected tab: %s' % w._current_path)
if scene._edit_stack:
    raise RuntimeError('a group is open for editing')
pref = ('Shed 10 x 20 ft', 'Workshop lean-to', 'Kitchen lean-to')
old = [g for g in scene.groups if g.name.startswith(pref)]
if len(old) != 3:
    raise RuntimeError('expected shed, workshop and kitchen groups; found %s' % [g.name for g in old])
pos = {g.name.split(' ')[0]: scene.groups.index(g) for g in old}
shed = [make(i) for i in context_items(with_container=False, with_shed=True)]
new = {'Shed': container('Shed 10 x 20 ft, gable roof, door on the front (existing; placeholder, check heights)', shed,
                         'Context (container, shed)')}
for lean in (workshop(), kitchen()):
    items = lean.build()
    kids = []
    for sysn in ORDER:
        gs = [make(i) for i in items if i['sys'] == sysn]
        if gs:
            kids.append(container(sysn, gs, LAYER_OF[sysn]))
    new[lean.title.split(' ')[0]] = container(lean.title, kids)
for key, i in pos.items():
    scene.groups[i] = new[key]
viewport.update()
print('rebuilt:', sorted(new))
