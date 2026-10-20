from pathlib import Path
import runpy
runpy.run_path(str(Path(__file__).with_name('render_combat_batch.py')),run_name='__main__')
