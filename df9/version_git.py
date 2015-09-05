import subprocess

version = subprocess.check_output(['git', 'rev-parse', 'HEAD'])
