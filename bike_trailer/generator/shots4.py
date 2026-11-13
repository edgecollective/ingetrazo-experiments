"""Hidden-line renders of bike_trailer_v4.igz for the print set, through the
IngeTrazo bridge (the file must be open in the front tab).
Usage: python shots4.py MCP_CLIENT OUT_DIR WIDTH HEIGHT [name ...]
Then run restore4.py through the same client to put the labels and style back."""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MCP, OUT, W, H = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
only = sys.argv[5:]
XB, XE = -80.0, 90.0
A = ['3 Assembled']
SH = [
    dict(name='00_overview', keep=None, hidden=['Notes'], eye=(47, -222, 123), tgt=(12, -42, 8), fov=40),
    dict(name='02_assembled', keep=A, hidden=['Notes'], eye=(49, 63, 44), tgt=(0, 2, 11), fov=32),
    dict(name='03_no_deck', keep=A, hidden=['Notes', 'Deck'], eye=(-50, 62, 45), tgt=(0, 2, 11), fov=32),
    dict(name='04_wheel_mount', keep=A, hidden=['Notes', 'Deck'], eye=(-36, -34, 26), tgt=(-6, 0, 12), fov=40),
    dict(name='05_exploded', keep=['4 Exploded'], hidden=['Notes'], eye=(XE + 70, -74, 74), tgt=(XE, 0, 21), fov=38),
    dict(name='06_materials', keep=['1 Materials'], hidden=['Notes'], eye=(0, -190, 70), tgt=(0, -88, 0), fov=30),
    dict(name='07_bent', keep=['2 Main frame'], hidden=['Notes'], eye=(XB + 38, -50, 40), tgt=(XB, 0, 0), fov=34),
]
os.makedirs(OUT, exist_ok=True)
tmpl = open(os.path.join(HERE, 'shot_setup4.py'), encoding='utf-8').read()
cur = os.path.join(OUT, '_cur_shot.py')
for s in SH:
    if only and s['name'] not in only:
        continue
    open(cur, 'w').write(tmpl.replace('%%PARAMS%%', repr(s)))
    r = subprocess.run([sys.executable, MCP, 'run', cur], capture_output=True, text=True, timeout=120)
    if r.returncode:
        print(r.stdout, r.stderr); sys.exit(1)
    r = subprocess.run([sys.executable, MCP, 'shot', os.path.join(OUT, s['name'] + '.png'), W, H],
                       capture_output=True, text=True, timeout=180)
    print(s['name'], (r.stdout or r.stderr).strip().splitlines()[0])
os.remove(cur)
