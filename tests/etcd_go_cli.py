import os
import shlex
import sys
from subprocess import Popen, PIPE

from .envs import ETCD_ENDPOINT


# https://gist.github.com/4368898
# Public domain code by anatoly techtonik <techtonik@gmail.com>
# AKA Linux `which` and Windows `where`
def find_executable(executable, path=None):
    """Find if 'executable' can be run. Looks for it in 'path'
    (string that lists directories separated by 'os.pathsep';
    defaults to os.environ['PATH']). Checks for all executable
    extensions. Returns full path or None if no command is found.
    """
    if path is None:
        path = os.environ['PATH']
    paths = path.split(os.pathsep)
    extlist = ['']
    if os.name == 'os2':
        (base, ext) = os.path.splitext(executable)
        # executable files on OS/2 can have an arbitrary extension, but
        # .exe is automatically appended if no dot is present in the name
        if not ext:
            executable = executable + ".exe"
    elif sys.platform == 'win32':
        pathext = os.environ['PATHEXT'].lower().split(os.pathsep)
        (base, ext) = os.path.splitext(executable)
        if ext.lower() not in pathext:
            extlist = pathext
    for ext in extlist:
        execname = executable + ext
        if os.path.isfile(execname):
            return execname
        else:
            for p in paths:
                f = os.path.join(p, execname)
                if os.path.isfile(f):
                    return f
    else:
        return None


etcdctl_path = find_executable('etcdctl')


def etcdctl(*args, **kwargs):
    if len(args) == 1:
        args = shlex.split(args[0])
    json = kwargs.get('json', True)
    endpoint = kwargs.get('endpoint', ETCD_ENDPOINT)
    version = kwargs.get('version', 3)

    envs = {}
    cmd = [etcdctl_path, '--endpoints', endpoint]
    if json:
        cmd.extend(['-w', 'json'])
    if version == 3:
        envs['ETCDCTL_API'] = '3'
    cmd.extend(args)
    p = Popen(cmd, stdout=PIPE, env=envs)
    return p.communicate()[0]


if __name__ == '__main__':
    print(etcdctl('get foo'))
