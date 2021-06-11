import os


def collect_sources(dirs, extensions, ignore_func):
    for basedir in dirs:
        for base, dirs, files in os.walk(basedir):
            for filename in files:
                (basename, ext) = os.path.splitext(filename)
                if ext in (extensions):
                    full_path = os.path.join(base, filename)
                    if not ignore_func(full_path):
                        yield full_path
