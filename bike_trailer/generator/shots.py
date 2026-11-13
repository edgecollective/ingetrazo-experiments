import subprocess, sys
XE = 80.0
SH = [
 dict(name='00_overview', keep=None, hidden=['Labels'], eye=(-5, -215, 125), tgt=(-5, -25, 6), fov=42),
 dict(name='02_assembled', keep=['3 Assembled'], hidden=['Labels'], eye=(48, 70, 34), tgt=(0, 8, 8), fov=38),
 dict(name='03_no_deck', keep=['3 Assembled'], hidden=['Labels', 'Deck'], eye=(-52, 60, 40), tgt=(0, 6, 8), fov=38),
 dict(name='04_wheel_mount', keep=['3 Assembled'], hidden=['Labels', 'Deck'], eye=(-46, -40, 30), tgt=(-9, 0, 8.6), fov=26),
 dict(name='05_exploded', keep=['4 Exploded'], hidden=['Labels'], eye=(XE + 55, -62, 58), tgt=(XE, 4, 12), fov=40),
 dict(name='06_materials', keep=['1 Materials'], hidden=['Labels'], eye=(-4, -178, 72), tgt=(-4, -84, 0), fov=40),
]
tmpl = open('shot_setup.py').read()
only = sys.argv[1:]
for s in SH:
    if only and s['name'] not in only:
        continue
    open('cur_shot.py', 'w').write(tmpl.replace('%%PARAMS%%', repr(s)))
    r = subprocess.run(['../venv/bin/python', '../scripts/mcp.py', 'run', 'cur_shot.py'], capture_output=True, text=True, timeout=120)
    if r.returncode:
        print(r.stdout, r.stderr); sys.exit(1)
    r = subprocess.run(['../venv/bin/python', '../scripts/mcp.py', 'shot', 'render/%s.png' % s['name'], '1662', '1244'],
                       capture_output=True, text=True, timeout=120)
    print(s['name'], (r.stdout or r.stderr).strip().splitlines()[0])
