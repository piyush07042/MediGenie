import os
import subprocess
from pathlib import Path

os.chdir(r'd:/medigenie/backend')

result = subprocess.run(
    [
        'python',
        '-m',
        'coverage',
        'run',
        '-m',
        'pytest',
        '-q',
        '--disable-warnings',
    ],
    capture_output=True,
    text=True,
)
report = subprocess.run(
    [
        'python',
        '-m',
        'coverage',
        'report',
        '-m',
    ],
    capture_output=True,
    text=True,
)
output = []
output.append('RUN_RETURNCODE:' + str(result.returncode))
output.append('RUN_STDOUT:')
output.append(result.stdout)
output.append('RUN_STDERR:')
output.append(result.stderr)
output.append('REPORT_RETURNCODE:' + str(report.returncode))
output.append('REPORT_STDOUT:')
output.append(report.stdout)
output.append('REPORT_STDERR:')
output.append(report.stderr)
Path('coverage_runner_output.txt').write_text('\n'.join(output), encoding='utf-8')
print('written', Path('coverage_runner_output.txt').resolve())
