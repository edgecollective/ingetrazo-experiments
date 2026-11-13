import math
from PySide6.QtGui import QMatrix4x4
from core.saved_views import SavedView
from core.style import Style
from core.insert import is_scale_figure
IN = 0.0254
P = %%PARAMS%%
if str(viewport.window()._current_path) != '/home/dwblair/gitwork/ingetrazo-experiments/cold_frame/cold_frame.igz':
    raise RuntimeError('unexpected tab')
if not any(l.name == 'Labels' for l in layers):
    layers.append(Layer('Labels'))
for lb in scene.text_labels:
    lb.layer = 'Labels'
keep = P['keep']
for g in scene.groups:
    g.hidden = is_scale_figure(g) or (bool(keep) and not g.name.startswith(tuple(keep)))
fin = next(g for g in scene.groups if g.name.startswith('3 Finished'))
lid = next(c for c in fin.children if c.name.startswith('Lid:'))
m = QMatrix4x4()
if not P['closed']:
    m.translate(0.0, 40.0 * IN, 10.5 * IN); m.rotate(-45.0, 1.0, 0.0, 0.0); m.translate(0.0, -40.0 * IN, -10.5 * IN)
lid.xform = m
st = Style(name='Print', face_mode='hidden_line', background=(1.0, 1.0, 1.0), sky=False, edge_color=(0.0, 0.0, 0.0),
           back_edges=P['back'])
e = [c * IN for c in P['eye']]; t = [c * IN for c in P['tgt']]
o = [e[i] - t[i] for i in range(3)]; d = math.sqrt(sum(c * c for c in o))
v = SavedView('print', target=tuple(t), distance=d, yaw=math.atan2(o[1], o[0]), pitch=math.asin(o[2] / d),
              fov_deg=P['fov'], hidden_layers=P['hidden'], style=st.to_dict())
v.apply(scene, viewport.camera)
scene.show_axes = False
viewport.update()
print('set', P['name'])
