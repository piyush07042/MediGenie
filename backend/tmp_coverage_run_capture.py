import os
import subprocess
from pathlib import Path

os.chdir(r'd:/medigenie/backend')
cmd = ['python', '-m', 'coverage', 'run', '-m', 'pytest', '-q', '--disable-warnings']
proc = subprocess.run(cmd, capture_output=True, text=True)
output = []
output.append('RUN_RETURNCODE:' + str(proc.returncode))
output.append('STDOUT:')
output.append(proc.stdout)
output.append('STDERR:')
output.append(proc.stderr)
Path('coverage_run_capture.txt').write_text('\n'.join(output), encoding='utf-8')
print('written', Path('coverage_run_capture.txt').resolve())
