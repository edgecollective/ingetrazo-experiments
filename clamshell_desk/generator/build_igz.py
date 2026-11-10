"""Build the 3D sketch headlessly with IngeTrazo's own engine and save it as
an .igz.  Run inside the Flatpak (see README).  Usage: build_igz.py OUT.igz"""
import math
import os
import sys
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, '/app/ingetrazo')
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
from PySide6.QtGui import QGuiApplication, QVector3D  # noqa: E402

app = QGuiApplication(sys.argv[:1])
from core.ai import _recipe_helpers  # noqa: E402
from core.group import Group, iter_placements  # noqa: E402
from core.layers import Layer  # noqa: E402
from core.mesh import Mesh  # noqa: E402
from core.saved_views import SavedView  # noqa: E402
from core.scene import Scene  # noqa: E402
from core import units  # noqa: E402
from formats.igz import save_scene  # noqa: E402

out = Path(sys.argv[1])
if out.exists():
    sys.exit('%s exists; not overwriting' % out)
scene = Scene()
units.apply_units(scene, {'length': 'in', 'precision': 2})
geom = open(os.path.join(HERE, 'cw_geom.py'), encoding='utf-8').read()
appside = open(os.path.join(HERE, 'app_part.py'), encoding='utf-8').read()
for v in ('V1', 'V2', 'V3'):
    ns = dict(scene=scene, layers=scene.layers, Group=Group, Mesh=Mesh, Layer=Layer, QVector3D=QVector3D,
              __name__='__ai__')
    ns.update(_recipe_helpers(scene))
    exec(compile(geom + appside.replace('%%VARIANT%%', v), 'clamshell_%s' % v, 'exec'), ns)


def view(name, eye, tgt, fov=45.0, persp=True):
    o = [eye[i] - tgt[i] for i in range(3)]
    d = math.sqrt(sum(c * c for c in o))
    return SavedView(name, target=tgt, distance=d, yaw=math.atan2(o[1], o[0]), pitch=math.asin(o[2] / d),
                     fov_deg=fov, perspective=persp)


IN = 0.0254
views = [view('Overview', (1.4, -8.6, 4.4), (4.3, -1.4, 0.35))]
for v, x0, w in (('V1 Basic', 12 * IN, 30 * IN), ('V2 Studio', 132 * IN, 36 * IN), ('V3 Pro', 252 * IN, 36 * IN)):
    views.append(view(v + ', open', (x0 + w + 1.15, -2.55, 1.75), (x0 + w * 0.35, 0.0, 0.62)))
    views.append(view(v + ', closed', (x0 + 52 * IN + w + 1.0, -1.7, 1.6), (x0 + 52 * IN + w / 2, 0.3, 0.6)))
views.append(view('CNC sheets from above', (4.27, -5.05, 6.6), (4.27, -5.0, 0.0)))
scene.saved_views.extend(views)
v0 = views[0]
scene.camera_home = {'target': list(v0.target), 'distance': v0.distance, 'yaw': v0.yaw, 'pitch': v0.pitch,
                     'fov_deg': v0.fov_deg, 'perspective': True, 'two_point': False}

# report where the swinging parts ended up (checks the hinge directions)
for top in scene.groups:
    for g, m in iter_placements(top):
        if g.name.startswith(('Half B', 'Desk leaf', 'Door, hinge', 'Pencil drawer')) and 'open' in top.name:
            xs, ys, zs = [], [], []
            for c in g.children:
                for gg, mm in iter_placements(c, m):
                    for vx in gg.mesh.vertices:
                        p = mm.map(vx.position) if mm is not None else vx.position
                        xs.append(p.x() / IN); ys.append(p.y() / IN); zs.append(p.z() / IN)
            print('%-28s %-34s x %7.1f..%7.1f  y %7.1f..%7.1f  z %5.1f..%5.1f' % (
                top.name[:28], g.name[:34], min(xs), max(xs), min(ys), max(ys), min(zs), max(zs)))
nf = sum(len(g.mesh.faces) for t in scene.groups for g, _m in iter_placements(t))
print('groups', len(scene.groups), 'faces', nf, 'labels', len(scene.text_labels), 'views', len(scene.saved_views))
save_scene(scene, out)
print('saved', out, out.stat().st_size // 1024, 'KB')
