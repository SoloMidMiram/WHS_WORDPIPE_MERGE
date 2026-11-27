"""Linux process ownership with a pinned, unreaped session leader."""

import ctypes
import os
import signal
import subprocess
from pathlib import Path


def _stat(pid):
    fields = Path(f"/proc/{pid}/stat").read_text().rsplit(")", 1)[1].split()
    return fields[0], int(fields[1]), int(fields[2]), int(fields[3])


def verify_inherited(owner_pid, token):
    group = os.getpgrp()
    if token != "linux-session" or os.getsid(0) != group:
        raise ValueError("invalid inherited Linux session")
    if _stat(group)[1:] != (owner_pid, group, group):
        raise ValueError("inherited Linux session does not have the declared owner")
    return group


def _set_subreaper(enabled):
    # Linux reparents an exiting process's children to its nearest subreaper.
    prctl = ctypes.CDLL(None, use_errno=True).prctl
    prctl.argtypes = (ctypes.c_int,) + (ctypes.c_ulong,) * 4
    if prctl(36, enabled, 0, 0, 0) != 0:  # PR_SET_CHILD_SUBREAPER
        error = ctypes.get_errno()
        raise OSError(error, os.strerror(error))


class Process:
    def __init__(self, argv, env, inherited, token):
        self.inherited = inherited
        self.exited_descendants = 0
        if inherited:
            # The bridge is a dedicated process with a single stage. Reaping
            # adopted descendants does not give it authority to signal them.
            try:
                os.waitid(os.P_ALL, 0, os.WEXITED | os.WNOHANG | os.WNOWAIT)
            except ChildProcessError:
                _set_subreaper(True)
            else:
                raise ValueError("inherited Linux stage requires a dedicated bridge without other children")
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
            # After the leader is reaped, any live branch still has a child
            # at its root. The kernel completes reparenting before wait returns.
            try:
                pid, _ = os.waitpid(-1, os.WNOHANG)
            except ChildProcessError:
                return 0, self.exited_descendants
            if pid:
                self.exited_descendants += 1
            return 1, self.exited_descendants
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
            if session == self.child.pid:
                if state in ("Z", "X"):
                    exited += 1
                elif group != self.child.pid:
                    raise ValueError("live descendant left the owned Linux process group")
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
