import subprocess

version = NotImplementedError('Unidentifieable version')

try:
    version = subprocess.check_output(['git', 'rev-parse', 'HEAD'])
except OSError:
    pass
