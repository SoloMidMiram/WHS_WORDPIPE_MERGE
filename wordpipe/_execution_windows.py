"""Windows suspended launch and Job Object ownership for native stages."""

import ctypes as ct
import msvcrt
import os
import subprocess
import _winapi
from ctypes import wintypes as wt
from contextlib import ExitStack


kernel = ct.WinDLL("kernel32", use_last_error=True)


def _api(name, restype, *argtypes):
    function = getattr(kernel, name)
    function.restype = restype
    function.argtypes = argtypes
    return function


class _BasicLimits(ct.Structure):
    _fields_ = [
        ("process_time", ct.c_longlong), ("job_time", ct.c_longlong),
        ("flags", wt.DWORD), ("min_working_set", ct.c_size_t),
        ("max_working_set", ct.c_size_t), ("active_limit", wt.DWORD),
        ("affinity", ct.c_size_t), ("priority", wt.DWORD), ("scheduling", wt.DWORD),
    ]


class _ExtendedLimits(ct.Structure):
    _fields_ = [
        ("basic", _BasicLimits), ("io", ct.c_ulonglong * 6),
        ("memory", ct.c_size_t * 4),
    ]


class _Accounting(ct.Structure):
    _fields_ = [
        ("times", ct.c_longlong * 4), ("page_faults", wt.DWORD),
        ("total", wt.DWORD), ("active", wt.DWORD), ("terminated", wt.DWORD),
    ]


create_job = _api("CreateJobObjectW", wt.HANDLE, wt.LPVOID, wt.LPCWSTR)
open_job = _api("OpenJobObjectW", wt.HANDLE, wt.DWORD, wt.BOOL, wt.LPCWSTR)
set_job = _api("SetInformationJobObject", wt.BOOL, wt.HANDLE, ct.c_int, wt.LPVOID, wt.DWORD)
query_job = _api("QueryInformationJobObject", wt.BOOL, wt.HANDLE, ct.c_int, wt.LPVOID, wt.DWORD, wt.LPVOID)
assign_job = _api("AssignProcessToJobObject", wt.BOOL, wt.HANDLE, wt.HANDLE)
in_job = _api("IsProcessInJob", wt.BOOL, wt.HANDLE, wt.HANDLE, ct.POINTER(wt.BOOL))
terminate_job = _api("TerminateJobObject", wt.BOOL, wt.HANDLE, wt.UINT)
resume = _api("ResumeThread", wt.DWORD, wt.HANDLE)
peek = _api("PeekNamedPipe", wt.BOOL, wt.HANDLE, wt.LPVOID, wt.DWORD, wt.LPVOID,
            ct.POINTER(wt.DWORD), wt.LPVOID)
console_break = _api("GenerateConsoleCtrlEvent", wt.BOOL, wt.DWORD, wt.DWORD)


def _checked(value):
    if not value:
        raise ct.WinError(ct.get_last_error())
    return value


def _verify_member(process, job):
    inside = wt.BOOL()
    _checked(in_job(process, job, ct.byref(inside)))
    if not inside.value:
        raise ValueError("process does not belong to the declared Windows job")


def verify_inherited(owner_pid, token):
    if not token.startswith("Local\\WordPipe-EXEC01-"):
        raise ValueError("invalid inherited Windows job")
    handle = _checked(open_job(0x0004, False, token))  # JOB_OBJECT_QUERY
    try:
        _verify_member(_winapi.GetCurrentProcess(), handle)
    finally:
        _winapi.CloseHandle(handle)
    return token


def _pipe(stack, write_ends):
    reader, writer = os.pipe()
    write_ends.callback(os.close, writer)
    stream = os.fdopen(reader, "rb", buffering=0)
    stack.enter_context(stream)
    handle = msvcrt.get_osfhandle(writer)
    os.set_handle_inheritable(handle, True)
    return stream, handle


class Process:
    def __init__(self, argv, env, inherited, token):
        self.resources = ExitStack()
        self.inherited = inherited
        with ExitStack() as stack, ExitStack() as write_ends:
            self.job = None
            if not inherited:
                self.job = _checked(create_job(None, token))
                stack.callback(_winapi.CloseHandle, self.job)
                limits = _ExtendedLimits()
                limits.basic.flags = 0x2000  # JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
                _checked(set_job(self.job, 9, ct.byref(limits), ct.sizeof(limits)))
            stdout, out_handle = _pipe(stack, write_ends)
            stderr, err_handle = _pipe(stack, write_ends)
            self.streams = (stdout, stderr)
            std_in = _winapi.GetStdHandle(_winapi.STD_INPUT_HANDLE)
            if std_in in (None, 0, -1):
                stream = write_ends.enter_context(open(os.devnull, "rb"))
                std_in = msvcrt.get_osfhandle(stream.fileno())
            current = _winapi.GetCurrentProcess()
            input_handle = _winapi.DuplicateHandle(current, std_in, current, 0, True, 2)
            write_ends.callback(_winapi.CloseHandle, input_handle)
            startup = subprocess.STARTUPINFO(
                dwFlags=subprocess.STARTF_USESTDHANDLES, hStdInput=input_handle,
                hStdOutput=out_handle, hStdError=err_handle,
                lpAttributeList={"handle_list": [input_handle, out_handle, err_handle]},
            )
            process, thread, self.pid, _ = _winapi.CreateProcess(
                None, subprocess.list2cmdline(argv), None, None, True,
                0x00000004 | (0 if inherited else subprocess.CREATE_NEW_PROCESS_GROUP),
                env, None, startup,
            )
            self.process = process
            stack.callback(_winapi.CloseHandle, process)
            try:
                if self.job is not None:
                    _checked(assign_job(self.job, process))
                    _verify_member(process, self.job)
                else:
                    containing_job = _checked(open_job(0x0004, False, token))
                    try:
                        _verify_member(process, containing_job)
                    finally:
                        _winapi.CloseHandle(containing_job)
                if resume(thread) == 0xFFFFFFFF:
                    raise ct.WinError(ct.get_last_error())
            except (OSError, ValueError):
                try:
                    _winapi.TerminateProcess(process, 125)
                    if _winapi.WaitForSingleObject(process, 250) != _winapi.WAIT_OBJECT_0:
                        raise RuntimeError("suspended process termination could not be verified")
                except OSError as exc:
                    if _winapi.WaitForSingleObject(process, 0) != _winapi.WAIT_OBJECT_0:
                        raise RuntimeError("suspended process termination failed") from exc
                raise
            finally:
                _winapi.CloseHandle(thread)
            self.resources = stack.pop_all()

    def read(self, stream, size):
        available = wt.DWORD()
        if not peek(msvcrt.get_osfhandle(stream.fileno()), None, 0, None, ct.byref(available), None):
            error = ct.get_last_error()
            if error in (109, 232):  # broken/no-data pipe
                return b""
            raise ct.WinError(error)
        return os.read(stream.fileno(), min(size, available.value)) if available.value else None

    def code(self):
        if _winapi.WaitForSingleObject(self.process, 0) != _winapi.WAIT_OBJECT_0:
            return None
        return _winapi.GetExitCodeProcess(self.process)

    def remaining(self):
        if self.job is None:
            return (0, 0) if self.code() is not None else (1, 0)
        accounting = _Accounting()
        _checked(query_job(self.job, 1, ct.byref(accounting), ct.sizeof(accounting), None))
        return accounting.active, 0

    def stop(self, force):
        if self.job is not None:
            if force:
                _checked(terminate_job(self.job, 125))
            else:
                # Headless hosts may reject a console signal. The same
                # absolute cleanup budget still governs job termination.
                console_break(1, self.pid)

    def close(self, exited):
        self.resources.close()
