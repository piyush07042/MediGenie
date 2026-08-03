import subprocess

result = subprocess.run(
    ["py", "-m", "pytest", "tests/agents/test_report_generation.py", "-q"],
    capture_output=True,
    text=True,
)
print('RETURN_CODE:', result.returncode)
print('STDOUT:')
print(result.stdout)
print('STDERR:')
print(result.stderr)
