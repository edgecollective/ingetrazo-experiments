import math
from PySide6.QtGui import QMatrix4x4
from core.saved_views import SavedView
from core.style import Style
IN = 0.0254
for g in scene.groups:
    g.hidden = False
fin = next(g for g in scene.groups if g.name.startswith('3 Finished'))
lid = next(c for c in fin.children if c.name.startswith('Lid:'))
m = QMatrix4x4(); m.translate(0.0, 40.0 * IN, 10.5 * IN); m.rotate(-45.0, 1.0, 0.0, 0.0); m.translate(0.0, -40.0 * IN, -10.5 * IN)
lid.xform = m
for lb in scene.text_labels:
    lb.layer = 'Texts'
for l in list(layers):
    if l.name == 'Labels':
        layers.remove(l)
v0 = scene.saved_views[0]
v = SavedView('restore', target=v0.target, distance=v0.distance, yaw=v0.yaw, pitch=v0.pitch, fov_deg=v0.fov_deg,
              hidden_layers=[], style=Style(name='Default').to_dict())
v.apply(scene, viewport.camera)
scene.show_axes = True
viewport.update()
print('restored; layers:', [l.name for l in layers])
