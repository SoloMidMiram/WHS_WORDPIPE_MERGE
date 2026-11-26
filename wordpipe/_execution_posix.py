"""Linux process ownership with a pinned, unreaped session leader."""

import os
import signal
import subprocess
from pathlib import Path


def _stat(pid):
    fields = Path(f"/proc/{pid}/stat").read_text().rsplit(")", 1)[1].split()
    return fields[0], int(fields[1]), int(fields[2]), int(fields[3])


def verify_inherited(owner_pid, token):
    group = os.getpgrp()
    if token != "linux-session" or group == os.getpid() or os.getsid(0) != group:
        raise ValueError("invalid inherited Linux session")
    if _stat(group)[1:] != (owner_pid, group, group):
        raise ValueError("inherited Linux session does not have the declared owner")
    return group


class Process:
    def __init__(self, argv, env, inherited, token):
        self.inherited = inherited
        self.child = subprocess.Popen(
            argv, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            start_new_session=not inherited,
        )
        self.streams = (self.child.stdout, self.child.stderr)
        for stream in self.streams:
            os.set_blocking(stream.fileno(), False)

    def read(self, stream, size):
        try:
            return os.read(stream.fileno(), size)
        except BlockingIOError:
            return None

    def code(self):
        if self.inherited:
            return self.child.poll()
        # Do not free the leader PID while the group may still be signalled.
        status = os.waitid(os.P_PID, self.child.pid, os.WEXITED | os.WNOHANG | os.WNOWAIT)
        if status is None:
            return None
        return status.si_status if status.si_code == os.CLD_EXITED else -status.si_status

    def remaining(self):
        if self.inherited:
            return (0, 0) if self.code() is not None else (1, 0)
        if self.code() is None:
            return 1, 0
        live = exited = 0
        for path in Path("/proc").iterdir():
            if not path.name.isdecimal() or int(path.name) == self.child.pid:
                continue
            try:
                state, _, group, session = _stat(path.name)
            except (FileNotFoundError, ProcessLookupError):
                continue
            if group == session == self.child.pid:
                if state in ("Z", "X"):
                    exited += 1
                else:
                    live += 1
        return live, exited

    def stop(self, force):
        if not self.inherited:
            try:
                os.killpg(self.child.pid, signal.SIGKILL if force else signal.SIGTERM)
            except ProcessLookupError:
                pass

    def close(self, exited):
        for stream in self.streams:
            stream.close()
        if exited:
            self.child.wait()
