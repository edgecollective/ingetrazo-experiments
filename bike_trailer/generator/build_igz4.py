"""Build bike_trailer_v4.igz headlessly with IngeTrazo's own engine.
Run inside the Flatpak:
  flatpak run --command=sh com.ingetrazo.IngeTrazo -c \
    'export PYTHONPATH=/app/lib/python3.13/site-packages; python3 build_igz.py OUT.igz'"""
import os
import sys
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, '/app/ingetrazo')
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
from PySide6.QtGui import QGuiApplication, QVector3D  # noqa: E402
app = QGuiApplication(sys.argv[:1])
from core.ai import _recipe_helpers  # noqa: E402
from core.group import Group  # noqa: E402
from core.layers import Layer  # noqa: E402
from core.mesh import Mesh  # noqa: E402
from core.scene import Scene  # noqa: E402
from formats.igz import save_scene  # noqa: E402

out = Path(sys.argv[1])
if out.exists():
    sys.exit('%s exists; not overwriting' % out)
scene = Scene()
ns = dict(scene=scene, layers=scene.layers, Group=Group, Mesh=Mesh, Layer=Layer, QVector3D=QVector3D, __name__='__ai__')
ns.update(_recipe_helpers(scene))
src = open(os.path.join(HERE, 'bt_geom.py'), encoding='utf-8').read() + open(os.path.join(HERE, 'bt4_geom.py'), encoding='utf-8').read() + open(os.path.join(HERE, 'bt4_app.py'), encoding='utf-8').read()
exec(compile(src, 'bike_trailer_v4', 'exec'), ns)
save_scene(scene, out)
print('saved', out, out.stat().st_size // 1024, 'KB; groups', [g.name for g in scene.groups])
