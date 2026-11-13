from core.saved_views import SavedView
from core.style import Style
for g in scene.groups:
    g.hidden = False
orig = globals().get('_bt_label_layers')
for i, lb in enumerate(scene.text_labels):
    lb.layer = orig[i] if orig and i < len(orig) else None
for l in list(layers):
    if l.name == 'Labels':
        layers.remove(l)
v0 = scene.saved_views[1]
SavedView('restore', target=v0.target, distance=v0.distance, yaw=v0.yaw, pitch=v0.pitch, fov_deg=v0.fov_deg,
          hidden_layers=[], style=Style(name='Default').to_dict()).apply(scene, viewport.camera)
scene.show_axes = True
viewport.update()
globals().pop('_bt_label_layers', None)
print('restored; labels:', [lb.layer for lb in scene.text_labels], '| layers:', [l.name for l in layers])
