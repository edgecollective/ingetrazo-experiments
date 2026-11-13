import math
from core.saved_views import SavedView
from core.style import Style
from core.insert import is_scale_figure
IN = 0.0254
P = %%PARAMS%%
if not str(viewport.window()._current_path).endswith('/bike_trailer/bike_trailer_v4.igz'):
    raise RuntimeError('unexpected tab: %s' % viewport.window()._current_path)
g_ = globals()
if '_bt4_label_layers' not in g_:
    g_['_bt4_label_layers'] = [lb.layer for lb in scene.text_labels]
if not any(l.name == 'Labels' for l in layers):
    layers.append(Layer('Labels'))
for lb in scene.text_labels:
    lb.layer = 'Labels'
keep = P['keep']
for g in scene.groups:
    g.hidden = is_scale_figure(g) or (bool(keep) and not g.name.startswith(tuple(keep)))
st = Style(name='Print', face_mode='hidden_line', background=(1.0, 1.0, 1.0), sky=False, edge_color=(0.0, 0.0, 0.0),
           back_edges=P.get('back', False))
e = [c * IN for c in P['eye']]; t = [c * IN for c in P['tgt']]
o = [e[i] - t[i] for i in range(3)]; d = math.sqrt(sum(c * c for c in o))
v = SavedView('print', target=tuple(t), distance=d, yaw=math.atan2(o[1], o[0]), pitch=math.asin(o[2] / d),
              fov_deg=P['fov'], hidden_layers=P['hidden'] + ['Labels'], style=st.to_dict())
v.apply(scene, viewport.camera)
scene.show_axes = False
viewport.update()
print('set', P['name'])
