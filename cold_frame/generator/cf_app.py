
# ======================= IngeTrazo side (appended to cf_geom.py) =======================
from PySide6.QtGui import QMatrix4x4
from core.saved_views import SavedView
from core.textlabel import TextLabel
from core import units
from core.insert import is_scale_figure

IN = 0.0254
if scene._edit_stack:
    raise RuntimeError('a group is open for editing')
others = [g for g in scene.groups if not is_scale_figure(g)]
if others or scene.mesh.faces or viewport.window()._current_path is not None:
    raise RuntimeError('not an empty new document; not building')
units.apply_units(scene, {'length': 'in', 'precision': 2})
for ly in ('Box', 'Posts', 'Lid', 'Plastic', 'Pallet (source)', 'Soil'):
    if not any(l.name == ly for l in layers):
        layers.append(Layer(ly))


def q(p):
    return QVector3D(p[0] * IN, p[1] * IN, p[2] * IN)


def make(p, d=(0.0, 0.0, 0.0)):
    col = p['color'] if isinstance(p['color'], tuple) else COL[p['color']]
    if p['kind'] == 'box':
        x0, x1, y0, y1, z0, z1 = p['data']
        g = box(((x0 + d[0]) * IN, (y0 + d[1]) * IN, (z0 + d[2]) * IN), ((x1 - x0) * IN, (y1 - y0) * IN, (z1 - z0) * IN),
                name=p['name'], color=col)
    else:
        loop, vec = p['data']
        g = prism([q((a + d[0], b + d[1], c + d[2])) for a, b, c in loop], q(vec), name=p['name'], color=col)
    scene.groups.remove(g)
    if p['opacity'] is not None:
        for f in g.mesh.faces:
            f.attrs['opacity'] = p['opacity']
    g.layer = p['layer']
    return g


def container(name, kids, xf=None, layer=None):
    g = Group(Mesh(), name=name)
    g.adopt(kids)
    if xf is not None:
        g.xform = xf
    g.component = False
    if layer:
        g.layer = layer
    return g


def by_layer(parts, d=(0.0, 0.0, 0.0), delta=None):
    out = {}
    for p in parts:
        dd = delta(p) if delta else (0.0, 0.0, 0.0)
        out.setdefault(p['layer'], []).append(make(p, (d[0] + dd[0], d[1] + dd[1], d[2] + dd[2])))
    return [container(ly, gs, layer=ly) for ly, gs in out.items()]


BOX, LID = box_parts(), lid_parts()

# 3 Finished, lid propped open 45 deg on its back hinges
hinge = QMatrix4x4(); hinge.translate(0.0, D * IN, HB * IN); hinge.rotate(-45.0, 1.0, 0.0, 0.0); hinge.translate(0.0, -D * IN, -HB * IN)
lid_open = container('Lid: lapped 1x4 frame with plastic between (hinged at the back)',
                     by_layer([p for p in LID if p['sub'] == 'lid']), hinge)
fin = container('3 Finished cold frame, lid propped open', by_layer(BOX + [p for p in LID if p['sub'] != 'lid']) + [lid_open])
soil = make(dict(layer='Soil', name='Soil bed', color='soil', kind='box', data=(-10.0, W + 10.0, -12.0, D + 10.0, -0.6, 0.0),
                 opacity=None))
scene.groups.append(fin)
scene.groups.append(container('Soil bed', [soil], layer='Soil'))


# 4 Exploded
def explode(p):
    n = p['name']
    if n.startswith('Front'):
        return (0.0, -10.0, 0.0)
    if n.startswith('Back'):
        return (0.0, 10.0, 0.0)
    if n.startswith('Side'):
        return (-10.0 if p['data'][0] < W / 2 else 10.0, 0.0, 0.0)
    if n.startswith('Angled'):
        return (-18.0 if p['data'][0][0][0] < W / 2 else 18.0, 0.0, 0.0)
    if n.startswith('Strap hinge') and p['sub'] != 'lid':
        return (0.0, 10.0, 0.0)
    if p['sub'] == 'lid' or p['layer'] == 'Plastic':
        if 'bottom layer' in n:
            return (0.0, 0.0, 16.0)
        if p['layer'] == 'Plastic':
            return (0.0, 0.0, 23.0)
        return (0.0, 0.0, 30.0)
    return (0.0, 0.0, 0.0)


XE = 92.0
scene.groups.append(container('4 Cold frame, exploded', by_layer(BOX + LID, (XE, 0.0, 0.0), explode)))

# 2 Built upside down on a flat bench: smooth top edges down, rough ends up
a = 180.0 - math.degrees(TH)
ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
pts = [(y * ca - z * sa, y * sa + z * ca) for y in (0.0, D) for z in (0.0, HF if y == 0 else HB)]
ty, tz = -min(p[0] for p in pts), -min(p[1] for p in pts)
XU = -100.0
flip = QMatrix4x4(); flip.translate(XU * IN, ty * IN, tz * IN); flip.rotate(a, 1.0, 0.0, 0.0)
scene.groups.append(container('2 Box built upside down (smooth top edges on the bench)', by_layer(BOX), flip))

# 1 Source pallet
XP = -190.0
scene.groups.append(container('1 Source: one 48 x 40 pallet', by_layer(pallet_parts(), (XP, 0.0, 0.0))))

for x, z, txt in ((XP + 24.0, 6.0, '1 Pallet: 1x4 deck boards (40 in), 2x4 stringers (48 in)'),
                  (XU + 20.0, 11.0, '2 Build upside down, then flip'),
                  (20.0, 24.0, '3 Finished: 2 boards front, 3 back, lapped lid'),
                  (XE + 20.0, 42.0, '4 Exploded')):
    scene.text_labels.append(TextLabel(q((x, 20.0, z)), QVector3D(0.0, 0.0, 0.30), txt))


def view(name, eye, tgt, hidden=(), fov=45.0):
    e = [c * IN for c in eye]; t = [c * IN for c in tgt]
    o = [e[i] - t[i] for i in range(3)]; d = math.sqrt(sum(c * c for c in o))
    return SavedView(name, target=tuple(t), distance=d, yaw=math.atan2(o[1], o[0]), pitch=math.asin(o[2] / d),
                     fov_deg=fov, hidden_layers=list(hidden))


scene.saved_views.extend([
    view('1 Overview: pallet, build, finished, exploded', (-30.0, -230.0, 140.0), (-30.0, 20.0, 6.0)),
    view('2 Finished cold frame, lid propped open', (78.0, -46.0, 48.0), (20.0, 18.0, 8.0)),
    view('3 Inside: corner posts and the angled side boards', (20.0, -24.0, 58.0), (20.0, 22.0, 2.0)),
    view('4 Exploded parts', (160.0, -75.0, 72.0), (XE + 20.0, 20.0, 14.0)),
    view('5 Built upside down', (-40.0, -62.0, 42.0), (XU + 20.0, 20.0, 4.0)),
    view('6 Source pallet', (-125.0, -55.0, 48.0), (XP + 24.0, 20.0, 3.0)),
])
for g in scene.groups:
    if is_scale_figure(g) and min(v.position.x() for v in g.mesh.vertices) < 1.0:
        dd = QVector3D(190 * IN, 70 * IN, 0.0)
        for v in list(g.mesh.vertices):
            g.mesh.move_vertex(v, dd)
scene.saved_views[0].apply(scene, viewport.camera); viewport.update()
print('built cold frame display')
