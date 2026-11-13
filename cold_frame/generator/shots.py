import json, subprocess, sys
SH = [
 dict(name='00_overview', keep=None, hidden=['Labels'], back=False, closed=False, eye=(-22, -238, 112), tgt=(-22, 20, 8), fov=40),
 dict(name='01_pallet', keep=['1 Source'], hidden=['Labels'], back=False, closed=False, eye=(-120, -48, 45), tgt=(-166, 20, 2), fov=38),
 dict(name='02_upside_down', keep=['2 Box built'], hidden=['Labels'], back=False, closed=False, eye=(-45, -50, 40), tgt=(-80, 20, 3), fov=38),
 dict(name='03_finished_open', keep=['3 Finished', 'Soil bed'], hidden=['Labels'], back=False, closed=False, eye=(80, -52, 48), tgt=(20, 18, 8), fov=38),
 dict(name='04_finished_closed', keep=['3 Finished', 'Soil bed'], hidden=['Labels'], back=False, closed=True, eye=(76, -55, 40), tgt=(20, 20, 6), fov=38),
 dict(name='05_box_design', keep=['3 Finished'], hidden=['Lid', 'Plastic', 'Labels'], back=True, closed=False, eye=(70, -45, 60), tgt=(20, 20, 3), fov=38),
 dict(name='06_lid_design', keep=['4 Cold frame, exploded'], hidden=['Box', 'Posts', 'Labels'], back=False, closed=False, eye=(162, -45, 70), tgt=(112, 20, 24), fov=38),
 dict(name='07_exploded', keep=['4 Cold frame, exploded'], hidden=['Labels'], back=False, closed=False, eye=(175, -85, 72), tgt=(112, 18, 12), fov=40),
]
tmpl = open('shot_setup.py').read()
only = sys.argv[1:]
for s in SH:
    if only and s['name'] not in only:
        continue
    open('cur_shot.py', 'w').write(tmpl.replace('%%PARAMS%%', repr(s)))
    r = subprocess.run(['../venv/bin/python', '../scripts/mcp.py', 'run', 'cur_shot.py'], capture_output=True, text=True, timeout=120)
    if r.returncode: print(r.stdout, r.stderr); sys.exit(1)
    r = subprocess.run(['../venv/bin/python', '../scripts/mcp.py', 'shot', 'print/%s.png' % s['name'], '2552', '1146'],
                       capture_output=True, text=True, timeout=120)
    print(s['name'], r.stdout.strip().splitlines()[0] if r.stdout else r.stderr[-200:])
