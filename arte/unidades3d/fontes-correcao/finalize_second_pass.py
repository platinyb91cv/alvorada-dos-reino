from pathlib import Path
import subprocess,sys,shutil,json,hashlib
O=Path(__file__).resolve().parent.parent;P=O.parent/'correcao-aldeao-guerreiro/segunda-volta';R=O.parent/'alvorada-dos-reino';S=O/'source'
def run(script,*args):subprocess.run([sys.executable,str(S/script),*args],check=True)
for name in ['aldeao','guerreiro']:
 report=json.loads((O/name/'render-report.json').read_text());assert report['sourceModelSha256']==hashlib.sha256((O/name/(name+'-jogo.glb')).read_bytes()).hexdigest()
 run('pack_units.py','--unit',name)
run('verify_atlas_correction.py','--baseline',str(P/'antes'))
shutil.copyfile(P.parent/'atlas-alignment-verification.json',P/'atlas-alignment-verification.json')
run('integrate_correction.py')
run('compare_correction.py','--baseline',str(P/'antes'),'--output',str(P))
for f in S.iterdir():
 if f.name in ['second_tools.py','import_work_clips.py','calibrate_work_tools.py','verify_second_pass.py','verify_models.py','verify_correction.py','render_units.py','pack_units.py','verify_atlas_correction.py','integrate_correction.py','compare_correction.py','package_second_pass.py','finalize_second_pass.py']:
  shutil.copyfile(f,R/'arte/unidades3d/fontes-correcao'/f.name)
run('package_second_pass.py')
for test in ['check_unit3d.cjs','check_king_atlas.cjs','check_king_memory.cjs','check_unit3d_correction.cjs','check_unit3d_second_pass.cjs']:
 subprocess.run(['node','tests/'+test],cwd=R,check=True)
print('SECOND_PASS_ALL_CHECKS_PASSED',flush=True)
