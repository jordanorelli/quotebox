import subprocess

def get_quote():
    return subprocess.check_output("fortune", shell=True)
