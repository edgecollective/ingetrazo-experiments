"""Cheap lean-to roofs for the site row: container | workshop | shed | kitchen.
Suntuf polycarbonate on 2x4 trusses.  Each lean-to's support side is tied to
its neighbour (container: non-penetrating straps; shed: screws into its
framing), which takes the sideways wind and holds that side down; the open
side's posts stand on ballast bases.  Pure Python.  Inches, Z up; the row runs
along +x, every building 240 in long in y."""
import math

SL = 1.5 / 12.0                              # Suntuf minimum slope
TCD = 3.5 * math.sqrt(1 + SL * SL)
OSB = 0.4375
ZBC, ZBCT = 84.0, 87.5                       # 7 ft clear under the trusses
DRAW_BALLAST = False                         # user: show simple pads only for now

COL = {'container': (0.42, 0.50, 0.56, 1.0), 'concrete': (0.72, 0.71, 0.68, 1.0), 'spf': (0.90, 0.78, 0.57, 1.0),
       'spf2': (0.84, 0.71, 0.50, 1.0), 'osb': (0.80, 0.66, 0.42, 1.0), 'panel': (0.86, 0.94, 1.0, 1.0),
       'strap': (0.95, 0.55, 0.10, 1.0), 'dark': (0.18, 0.20, 0.22, 1.0), 'shed': (0.48, 0.33, 0.22, 1.0), 'door': (0.12, 0.27, 0.17, 1.0),
       'shedroof': (0.30, 0.30, 0.31, 1.0), 'ply': (0.88, 0.77, 0.56, 1.0)}

CONTAINER = dict(x0=0.0, x1=96.0, h=105.0)
SHED = dict(x0=266.0, x1=386.0, hk=96.0, hw=96.0, over=12.0, blocks=8.0, pitch=6.0 / 12.0, gable_over=4.0,
            door_w=34.0, door_h=78.0, door_x=18.0, door_sill=14.0, step_h=7.0, step_d=12.0)   # gable roof; one-person door, left of centre, hinged on the left


class Lean:
    """One lean-to.  xs: outer face of the support-side posts; xs + span: outer
    face of the open-side posts.  side = +1 when the open side is toward +x."""

    def __init__(self, key, title, xs, span, ycs, anchor, high_over, eave_over, ballast_h):
        self.key, self.title, self.xs, self.span, self.ycs = key, title, xs, span, ycs
        self.anchor, self.high_over, self.eave_over, self.ballast_h = anchor, high_over, eave_over, ballast_h
        self.xl = xs + span
        self.items = []

    # -- helpers
    def add(self, sys_, name, color, kind, data, lumber=None, opacity=None):
        self.items.append(dict(sys=sys_, name=name, color=color, kind=kind, data=data, lumber=lumber, opacity=opacity))

    def B(self, sys_, name, color, b, lumber=None, opacity=None):
        x0, x1, y0, y1, z0, z1 = b
        assert x1 > x0 and y1 > y0 and z1 > z0, (name, b)
        self.add(sys_, name, color, 'box', tuple(float(c) for c in b), lumber, opacity)

    def xzp(self, sys_, name, color, prof, y0, y1, lumber=None):
        self.add(sys_, name, color, 'prism', ([(x, y0, z) for x, z in prof], (0.0, y1 - y0, 0.0), []), lumber)

    def yzp(self, sys_, name, color, prof, x0, x1, lumber=None):
        self.add(sys_, name, color, 'prism', ([(x0, y, z) for y, z in prof], (x1 - x0, 0.0, 0.0), []), lumber)

    def zb(self, x):
        return ZBC + 7.0 + (self.xl - x) * SL

    def zt(self, x):
        return self.zb(x) + TCD

    # -- one frame
    def bent(self, yc, outer=0):
        T, P = 'Trusses', 'Posts and bracing'
        y0, y1 = yc - 0.75, yc + 0.75
        xs, xl = self.xs, self.xl
        hb = self.ballast_h
        # support side stands on a paver, open side on a ballast base
        self.B('Bases', 'Bearing pad: 16 x 16 in paver or flat stone', 'concrete',
               (xs - 4.0 if self.anchor == 'container' else xs - 6.25, xs + 12.0 if self.anchor == 'container' else xs + 9.75,
                yc - 8.0, yc + 8.0, 0.0, 2.0))
        if DRAW_BALLAST:
            self.B('Bases', 'Ballast base 24 x 24 x %d in (about %d lb): cast, or a 2x4 crib of stones' % (hb, 576 * hb // 12),
                   'concrete', (xl - 13.75, xl + 10.25, yc - 12.0, yc + 12.0, 0.0, hb))
        else:
            hb = 2.0
            self.B('Bases', 'Pad: 16 x 16 in paver or flat stone (needs ballast for wind, not drawn)', 'concrete',
                   (xl - 9.75, xl + 6.25, yc - 8.0, yc + 8.0, 0.0, 2.0))
        for xa, xb, z0 in ((xs, xs + 3.5, 2.0), (xl - 3.5, xl, hb)):
            for ya, yb in ((yc - 1.5, yc), (yc, yc + 1.5)):
                self.B(P, 'Post ply 2x4 (doubled post)', 'spf', (xa, xb, ya, yb, z0, ZBC), lumber=[ZBC - z0])
        split = xs + 96.0
        for a, b in ((xs, split), (split, xl)):
            self.B(T, 'Bottom chord 2x4', 'spf', (a, b, y0, y1, ZBC, ZBCT), lumber=[b - a])
        tx0, tx1 = xs - self.high_over, xl + self.eave_over
        mid = (tx0 + tx1) / 2
        for a, b in ((tx0, mid), (mid, tx1)):
            self.xzp(T, 'Top chord 2x4', 'spf', [(a, self.zb(a)), (b, self.zb(b)), (b, self.zt(b)), (a, self.zt(a))], y0, y1,
                     lumber=[(b - a) * math.sqrt(1 + SL * SL)])
        npan = int(math.ceil(self.span / 32.0))
        cs = [xs + 1.75 + (self.span - 3.5) * k / npan for k in range(npan + 1)]
        for c in cs:
            a, b = c - 1.75, c + 1.75
            self.xzp(T, 'Web 2x4 (vertical)', 'spf2', [(a, ZBCT), (b, ZBCT), (b, self.zb(b)), (a, self.zb(a))], y0, y1,
                     lumber=[self.zb(a) - ZBCT])
        for k in range(npan - 1):                    # last (shallow heel) panel gets an OSB web instead
            L, R = cs[k] + 1.75, cs[k + 1] - 1.75
            h = self.zb((L + R) / 2) - ZBCT
            wh = 3.5 * math.hypot(h, R - L) / h
            if L + wh > R - wh:
                continue
            if k < (npan - 1) / 2:
                prof = [(R - wh, ZBCT), (R, ZBCT), (L + wh, self.zb(L + wh)), (L, self.zb(L))]
            else:
                prof = [(L, ZBCT), (L + wh, ZBCT), (R, self.zb(R)), (R - wh, self.zb(R - wh))]
            self.xzp(T, 'Web 2x4 (diagonal)', 'spf2', prof, y0, y1, lumber=[math.hypot(h, R - L) + 4])
        plates = [(xs, xs + 8.75)] + [(c - 7.0, c + 7.0) for c in cs[1:-2]] + [(cs[-2] - 6.0, xl)]
        for a, b in plates:
            nm = 'OSB heel web plate 7/16 in' if b == xl else 'OSB gusset 7/16 in'
            for side, (ga, gb) in ((1, (y1, y1 + OSB)), (-1, (y0 - OSB, y0))):
                if side == outer:                       # the end skin does this face's job
                    continue
                self.xzp(T, nm, 'osb', [(a, ZBC), (b, ZBC), (b, self.zt(b)), (a, self.zt(a))], ga, gb)
        if outer:                                       # end truss: solid plywood skin on the outside face
            ga, gb = (y1, y1 + 0.5) if outer > 0 else (y0 - 0.5, y0)
            self.xzp(T, 'End-truss skin, 1/2 in exterior plywood', 'ply',
                     [(xs, ZBC), (xl, ZBC), (xl, self.zt(xl)), (xs, self.zt(xs))], ga, gb)
        d = 3.5 * math.sqrt(2)
        for xf, s in ((xs + 3.5, 1), (xl - 3.5, -1)):
            prof = [(xf, ZBC - 24.0), (xf, ZBC - 24.0 + d), (xf + s * (24.0 - d), ZBC), (xf + s * 24.0, ZBC)]
            self.xzp(P, 'Knee brace 2x4', 'spf2', prof, y0, y1, lumber=[24.0 * math.sqrt(2)])

    def strap(self, name, p1, p2, w=2.0, t=0.08):
        d = [p2[i] - p1[i] for i in range(3)]
        L = math.sqrt(sum(c * c for c in d)); u = [c / L for c in d]
        ref = (0.0, 1.0, 0.0) if abs(u[1]) < 0.9 else (1.0, 0.0, 0.0)
        a = [u[1] * ref[2] - u[2] * ref[1], u[2] * ref[0] - u[0] * ref[2], u[0] * ref[1] - u[1] * ref[0]]
        la = math.sqrt(sum(c * c for c in a)); a = [c / la for c in a]
        b = [u[1] * a[2] - u[2] * a[1], u[2] * a[0] - u[0] * a[2], u[0] * a[1] - u[1] * a[0]]
        loop = [tuple(p1[i] + a[i] * sa * t / 2 + b[i] * sb * w / 2 for i in range(3))
                for sa, sb in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
        self.add('Tie-downs to the ' + self.anchor, name, 'strap', 'prism', (loop, tuple(d), []))

    def build(self):
        del self.items[:]
        for i, yc in enumerate(self.ycs):
            self.bent(yc, -1 if i == 0 else 1 if i == len(self.ycs) - 1 else 0)
        xs, xl, ycs = self.xs, self.xl, self.ycs
        tie = 'Tie-downs to the ' + self.anchor
        if self.anchor == 'container':
            for yc in ycs:
                ya = 3.5 if yc < 10 else 236.5 if yc > 230 else (79.65 if yc < 120 else 160.35)
                self.strap('Ratchet strap: post down to ' + ('bottom corner casting' if yc < 10 or yc > 230 else 'forklift pocket'),
                           (xs - 0.1, yc, 46.0), (CONTAINER['x1'] + 0.1, ya, 3.0))
                self.B(tie, 'Bearing block 2x4 against the container wall', 'spf2',
                       (CONTAINER['x1'] + 0.05, xs, yc - 1.75, yc + 1.75, ZBC, ZBCT), lumber=[6.0])
            for i in range(len(ycs) - 1):           # container side: one diagonal per bay on the outside face
                ya, yb = ycs[i] + 1.5, ycs[i + 1] - 1.5
                p1, p2 = ((ya, 16.0), (yb, 82.0)) if i % 2 == 0 else ((yb, 16.0), (ya, 82.0))
                self.yzp('Posts and bracing', 'Diagonal brace 2x4', 'spf2', band(p1, p2, 3.5), xs - 1.5, xs,
                         lumber=[96.0])
        else:                                       # shed: two 2x4 arms per frame, screwed into its framing
            sx = SHED['x1']
            for z0 in (14.0, 77.0):
                for a, b in ((0.0, 96.0), (96.0, 192.0), (192.0, 240.0)):
                    self.B(tie, '2x4 nailer screwed flat to the shed wall', 'spf2', (sx, sx + 1.5, a, b, z0 - 1.0, z0 + 4.5),
                           lumber=[b - a])
                for yc in ycs:
                    self.B(tie, '2x4 arm: post to shed wall', 'spf2', (sx + 1.5, xs, yc - 0.75, yc + 0.75, z0, z0 + 3.5),
                           lumber=[xs - sx - 1.5])
        # open side: eave strut on the post faces and lengthwise knee braces
        P = 'Posts and bracing'
        for a, b in ((0.0, 96.0), (96.0, 192.0), (192.0, 240.0)):
            self.B(P, 'Eave strut 2x4', 'spf2', (xl, xl + 1.5, a, b, ZBC - 3.5, ZBC), lumber=[b - a])
        d = 3.5 * math.sqrt(2)
        for i, yc in enumerate(ycs):
            for s in ((1,) if i == 0 else (-1,) if i == len(ycs) - 1 else (1, -1)):
                yf = yc + s * 1.5
                z1 = ZBC - 3.5
                prof = [(yf, z1 - 24.0), (yf, z1 - 24.0 + d), (yf + s * (24.0 - d), z1), (yf + s * 24.0, z1)]
                self.yzp(P, 'Knee brace 2x4 (lengthwise)', 'spf2', prof, xl, xl + 1.5, lumber=[24.0 * math.sqrt(2)])
        # roof: purlins blocked in between trusses, Suntuf on top
        tx0, tx1 = xs - self.high_over, xl + self.eave_over
        slope_len = (tx1 - tx0) * math.sqrt(1 + SL * SL)
        lap = slope_len > 144.0
        top_piece = slope_len - 144.0 + 6.0 if lap else 0.0
        k = math.sqrt(1 + SL * SL)
        p0, p1 = (tx0 + 1.5) * 1.0, tx1 - 1.5           # first and last purlin centres (x)
        if lap:                                     # second purlin under the end lap
            lap_mid = tx0 + (top_piece - 3.0) / k
            rest = [lap_mid + (p1 - lap_mid) * j / math.ceil((p1 - lap_mid) * k / 23.5)
                    for j in range(int(math.ceil((p1 - lap_mid) * k / 23.5)) + 1)]
            xsP = [p0] + rest
        else:
            n = int(math.ceil((p1 - p0) * k / 23.5))
            xsP = [p0 + (p1 - p0) * j / n for j in range(n + 1)]
        self.purlin_lines = len(xsP)
        for x in xsP:
            top = self.zt(x - 0.75)
            for i in range(len(ycs) - 1):
                self.B('Purlins', 'Purlin 2x4 on edge', 'spf', (x - 0.75, x + 0.75, ycs[i] + 1.25, ycs[i + 1] - 1.25,
                                                                 top - 3.5, top), lumber=[ycs[i + 1] - ycs[i] - 2.5])
        run = slope_len / k
        za = self.zt(tx0)
        pieces = [(tx0 + (top_piece - 6.0) / k, 144.0, 0.0)] if lap else [(tx0 + (run - 144.0 / k) / 2, 144.0, 0.0)]
        if lap:
            pieces.append((tx0, top_piece, 0.7))      # top piece laps over the 12 ft panel
        self.panels = []
        for i in range(11):
            y0 = -1.0 + 23.0 * i
            w = min(26.0, 241.0 - y0)
            dz = 0.06 * (i % 2)
            for xa, Ls, lift in pieces:
                rl = Ls / k
                zz = self.zt(xa) + dz + lift
                prof = [(y0, zz), (y0 + w, zz), (y0 + w, zz + 0.63), (y0, zz + 0.63)]
                nm = 'Suntuf 26 in x 12 ft clear' if Ls == 144.0 else 'Suntuf top piece %.0f in (cut from 8 ft)' % Ls
                self.add('Suntuf roof panels', nm + (' (ripped)' if w < 26.0 else ''), 'panel', 'prism',
                         ([(xa, yy, zv) for yy, zv in prof], (rl, 0.0, -rl * SL), []), None, 0.33)
            self.panels.append(w)
        self.top_piece = top_piece
        return self.items


def band(p1, p2, w):
    dx, dy = p2[0] - p1[0], p2[1] - p1[1]
    L = math.hypot(dx, dy); nx, ny = -dy / L * w / 2, dx / L * w / 2
    return [(p1[0] - nx, p1[1] - ny), (p2[0] - nx, p2[1] - ny), (p2[0] + nx, p2[1] + ny), (p1[0] + nx, p1[1] + ny)]


def context_items(with_container=True, with_shed=True):
    out = []

    def B(name, color, b):
        out.append(dict(sys='Context', name=name, color=color, kind='box', data=tuple(float(c) for c in b),
                        lumber=None, opacity=None))
    if with_container:
        B('Shipping container 8 x 20 ft (existing)', 'container', (0.0, 96.0, 0.0, 240.0, 0.0, 105.0))
        for y0, y1 in ((-0.1, 7.0), (233.0, 240.1)):
            for z0, z1 in ((0.0, 4.5), (100.5, 105.1)):
                B('Corner casting', 'dark', (89.0, 96.1, y0, y1, z0, z1))
        for yc in (79.65, 160.35):
            B('Forklift pocket (check yours has them)', 'dark', (95.9, 96.05, yc - 7.0, yc + 7.0, 0.8, 5.8))
    if with_shed:
        s = SHED
        for x in (s['x0'] + 4.0, s['x1'] - 12.0):
            for y in (4.0, 116.0, 228.0):
                B('Shed block (existing)', 'concrete', (x, x + 8.0, y, y + 8.0, 0.0, s['blocks']))
        xc = (s['x0'] + s['x1']) / 2
        ridge = s['hk'] + (xc - s['x0']) * s['pitch']
        out.append(dict(sys='Context', name='Shed 10 x 20 ft, gable roof (existing; placeholder, check heights)', color='shed',
                        kind='prism', lumber=None, opacity=None,
                        data=([(s['x0'], 0.0, s['blocks']), (s['x1'], 0.0, s['blocks']), (s['x1'], 0.0, s['hk']),
                               (xc, 0.0, ridge), (s['x0'], 0.0, s['hk'])], (0.0, 240.0, 0.0), [])))
        th = 6.0 * math.sqrt(1 + s['pitch'] ** 2)
        go = s['gable_over']
        for xe in (s['x0'] - s['over'], s['x1'] + s['over']):
            ze = s['hk'] - s['over'] * s['pitch']
            out.append(dict(sys='Context', name='Shed roof (gable)', color='shedroof', kind='prism', lumber=None,
                            opacity=None, data=([(xc, -go, ridge), (xe, -go, ze), (xe, -go, ze + th), (xc, -go, ridge + th)],
                                                (0.0, 240.0 + 2 * go, 0.0), [])))
        dw, dh = s['door_w'], s['door_h']
        dl = s['x0'] + s['door_x']                    # door's left edge, seen from the front (left = toward the workshop)
        zb0 = s['door_sill'] + 0.5                   # door sits up at floor level, one step below
        B('Step (one, about %d in)' % s['step_h'], 'shed', (dl - 4.0, dl + dw + 4.0, -s['step_d'], -0.8, 0.0, s['step_h']))
        B('Shed door (one-person, hinged on the left)', 'door', (dl, dl + dw, -0.6, 0.0, zb0, zb0 + dh))
        B('Door handle (right side)', 'dark', (dl + dw - 3.5, dl + dw - 2.0, -1.6, -0.6, zb0 + 36.0, zb0 + 42.0))
        for zz in (zb0 + 8.0, zb0 + dh - 12.0):
            B('Door hinge (left side)', 'dark', (dl - 0.5, dl + 5.0, -0.9, -0.6, zz, zz + 1.25))
        for xa, xb, za, zb2 in ((dl - 3.5, dl, s['door_sill'], zb0 + dh + 3.5), (dl + dw, dl + dw + 3.5, s['door_sill'], zb0 + dh + 3.5),
                                (dl - 3.5, dl + dw + 3.5, zb0 + dh, zb0 + dh + 3.5)):
            B('Door trim', 'shed', (xa, xb, -0.75, 0.0, za, zb2))
    return out


def workshop():
    return Lean('workshop', 'Workshop lean-to: Suntuf on 2x4 trusses, strapped to the container', 102.0, 128.0,
                [1.5, 80.0, 160.0, 238.5], 'container', 8.0, 6.0, 10)


def kitchen():
    return Lean('kitchen', 'Kitchen lean-to: Suntuf on 2x4 trusses, screwed to the shed', SHED['x1'] + 18.0, 150.0,
                [1.5, 60.75, 120.0, 179.25, 238.5], 'shed', 2.0, 6.0, 12)


def check(items):
    bx = [(i['sys'] + ':' + i['name'], i['data']) for i in items if i['kind'] == 'box']
    bad = []
    for i in range(len(bx)):
        for j in range(i + 1, len(bx)):
            a, b = bx[i][1], bx[j][1]
            if all(min(a[2 * k + 1], b[2 * k + 1]) - max(a[2 * k], b[2 * k]) > 0.05 for k in range(3)):
                bad.append((bx[i][0], bx[j][0]))
    return bad


def boards(items, stock=96.0, kerf=0.25):
    L = sorted((l for i in items for l in (i['lumber'] or [])), reverse=True)
    bs = []
    for p in L:
        for b in bs:
            if b[0] >= p + kerf:
                b[0] -= p + kerf
                break
        else:
            bs.append([stock - p - kerf])
    return len(bs)
