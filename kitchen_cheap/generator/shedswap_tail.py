
# ---- swap the shed placeholder in this tab (container, workshop and kitchen untouched)
IN = 0.0254
w = viewport.window()
if str(w._current_path) != '/home/dwblair/gitwork/ingetrazo-experiments/kitchen_cheap/site_row_cheap_v3.igz':
    raise RuntimeError('unexpected tab: %s' % w._current_path)
old = [g for g in scene.groups if g.name.startswith('Shed 10 x 20 ft')]
if len(old) != 1:
    raise RuntimeError('expected one shed group, found %d' % len(old))


def q(p):
    return QVector3D(p[0] * IN, p[1] * IN, p[2] * IN)


def make(it):
    if it['kind'] == 'box':
        x0, x1, y0, y1, z0, z1 = it['data']
        g = box((x0 * IN, y0 * IN, z0 * IN), ((x1 - x0) * IN, (y1 - y0) * IN, (z1 - z0) * IN), name=it['name'],
                color=COL[it['color']])
    else:
        loop, vec, holes = it['data']
        g = prism([q(p) for p in loop], q(vec), name=it['name'], color=COL[it['color']])
    scene.groups.remove(g)
    g.layer = 'Context (container, shed)'
    return g


kids = [make(i) for i in context_items(with_container=False, with_shed=True)]
g = Group(Mesh(), name='Shed 10 x 20 ft, gable roof, one-person door front left, up one step (existing; placeholder, check heights)')
g.adopt(kids); g.component = False; g.layer = 'Context (container, shed)'
scene.groups[scene.groups.index(old[0])] = g
viewport.update()
print('shed swapped:', len(kids), 'parts')
