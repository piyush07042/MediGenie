import os
import subprocess
from pathlib import Path

os.chdir(r'd:/medigenie/backend')
result = subprocess.run(['python', '-m', 'pytest', '-q', '--disable-warnings'], capture_output=True, text=True)
log_path = Path('pytest_capture_output.txt')
log_path.write_text(result.stdout + '\n' + result.stderr + '\nRC:' + str(result.returncode), encoding='utf-8')
print('written', log_path.resolve())
