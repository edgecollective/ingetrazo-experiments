
# ======================= IngeTrazo side (appended to th_geom.py) =======================
from PySide6.QtGui import QMatrix4x4
from core.orient import orient_outward
from core.saved_views import SavedView
from core import units

IN = 0.0254
if scene._edit_stack:
    raise RuntimeError('a group is open for editing; not building')
if scene.groups or scene.mesh.faces:
    raise RuntimeError('this document is not empty (%d groups); not building' % len(scene.groups))
units.apply_units(scene, {'length': 'in', 'precision': 2})
items, TREEP = build_all()
LAYERS = []
for _s, ly in SYSTEMS:
    if ly not in LAYERS:
        LAYERS.append(ly)
LAYERS += ['Tree', 'Tree canopy', 'Ground']
for nm in LAYERS:
    if not any(l.name == nm for l in layers):
        layers.append(Layer(nm))


def q(p):
    return QVector3D(p[0] * IN, p[1] * IN, p[2] * IN)


def soften(mesh, deg=42.0):
    c = math.cos(math.radians(deg))
    for e in mesh.edges:
        if len(e.faces) == 2 and QVector3D.dotProduct(e.faces[0].normal(), e.faces[1].normal()) > c:
            e.soft = True


def make(it):
    if it['kind'] == 'box':
        x0, x1, y0, y1, z0, z1 = it['data']
        g = box((x0 * IN, y0 * IN, z0 * IN), ((x1 - x0) * IN, (y1 - y0) * IN, (z1 - z0) * IN),
                name=it['name'], color=COL[it['color']])
    else:
        loop, vec, holes = it['data']
        g = prism([q(p) for p in loop], q(vec), holes=[[q(p) for p in h] for h in holes] or None,
                  name=it['name'], color=COL[it['color']])
    scene.groups.remove(g)
    if it['opacity'] is not None:
        for f in g.mesh.faces:
            f.attrs['opacity'] = it['opacity']
    return g


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
    p, ax = ((c[0] * IN, c[1] * IN, 0.0), (0.0, 0.0, 1.0)) if kind == 'rz' else ((0.0, c[0] * IN, c[1] * IN), (1.0, 0.0, 0.0))
    m.translate(*p); m.rotate(ang, *ax); m.translate(-p[0], -p[1], -p[2])
    return m


def tag(g, layer):
    g.layer = layer
    for c in g.children or ():
        tag(c, layer)


kids = []
for sysn, ly in SYSTEMS:
    mine = [it for it in items if it['sys'] == sysn]
    if not mine:
        continue
    static = [make(it) for it in mine if not it['sub']]
    subs = {}
    for it in mine:
        if it['sub']:
            subs.setdefault(it['sub'], []).append(make(it))
    ch = list(static)
    for sub, gs in subs.items():
        nm = {'hatch': 'Hatch lid (hinged, shown open)', 'door': 'Door 24 x 54 in (hinged, shown open)'}[sub]
        ch.append(container(nm, gs, mmat(MOVES[sub])))
    c = container(sysn, ch)
    tag(c, ly)
    kids.append(c)
house = container('Treehouse: 12 x 16 ft platform, 3-room cabin (Home Depot lumber)', kids)
scene.groups.append(house)

tg = []
ground = None
for name, color, faces, ly in TREEP:
    m = Mesh()
    for f in faces:
        nf = m.add_face([q(p) for p in f])
        nf.attrs['color'] = COL[color]
    if ly != 'Ground':
        orient_outward(m)
    soften(m, 50.0 if ly != 'Ground' else 1.0)
    g = Group(m, name=name)
    g.layer = ly
    if ly == 'Ground':
        ground = g
    else:
        tg.append(g)
tree_c = container('Example tree: white oak, about 25 in trunk, 40 ft tall', tg)
for c in tree_c.children:
    pass
scene.groups.append(tree_c)
scene.groups.append(ground)


def view(name, eye, tgt, hidden=(), fov=45.0):
    eye = [c * IN for c in eye]; tgt = [c * IN for c in tgt]
    o = [eye[i] - tgt[i] for i in range(3)]; d = math.sqrt(sum(c * c for c in o))
    return SavedView(name, target=tuple(tgt), distance=d, yaw=math.atan2(o[1], o[0]), pitch=math.asin(o[2] / d),
                     fov_deg=fov, hidden_layers=list(hidden))


roofless = ('Roof', 'Roof framing', 'Tree canopy')
scene.saved_views.extend([
    view('1 Treehouse in the oak', (360.0, -640.0, 250.0), (45.0, 0.0, 200.0)),
    view('2 Porch, hatch and ladder', (-170.0, -270.0, 205.0), (5.0, -25.0, 105.0)),
    view('3 Door side, across the porch', (-175.0, 230.0, 170.0), (40.0, 20.0, 130.0)),
    view('4 Under the platform: TABs, beams, posts', (190.0, -330.0, 34.0), (55.0, 0.0, 80.0)),
    view('5 Framing (siding, roof, canopy hidden)', (330.0, -420.0, 300.0), (90.0, 0.0, 140.0),
         hidden=('Walls and siding', 'Roof', 'Tree canopy', 'Windows and door')),
    view('6 Three rooms from above (roof hidden)', (215.0, -250.0, 470.0), (100.0, 0.0, 100.0), hidden=roofless),
    view('7 Floor plan', (72.0, -2.0, 1000.0), (72.0, 0.0, 96.0), hidden=roofless + ('Tree',), fov=28.0),
])
v = scene.saved_views[0]
c = viewport.camera
c.target = QVector3D(*v.target); c.distance = v.distance; c.yaw = v.yaw; c.pitch = v.pitch; c.fov_deg = v.fov_deg
c.perspective = True
viewport.update()
print('built', len(items), 'parts in', len(kids), 'systems;', len(tg), 'tree parts;', len(scene.saved_views), 'views')
