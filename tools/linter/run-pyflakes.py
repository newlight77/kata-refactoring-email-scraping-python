import subprocess
import sys
import configparser
from utils import collect_sources


configParser = configparser.RawConfigParser()
configFilePath = r'setup.cfg'
configParser.read(configFilePath)


def ignore(path):
    ignores = configParser.get('pyflakes', 'ignores')
    if path in ignores:
        return True
    return False


def run_pyflakes():
    paths = configParser.get('pyflakes', 'paths').split(",")
    cmd = ["pyflakes"]
    cmd.extend(collect_sources(dirs=paths, extensions=".py", ignore_func=ignore))
    return subprocess.call(cmd)


if __name__ == "__main__":
    rc = run_pyflakes()
    sys.exit(rc)
