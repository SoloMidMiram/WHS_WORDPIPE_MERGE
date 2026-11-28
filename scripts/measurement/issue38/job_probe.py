"""Three synthetic Windows probes. Run from the repository root."""
import _winapi
import ctypes as ct
import json
import os
from pathlib import Path
import sys
import time
import uuid

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from wordpipe import _execution_windows as native

CHILD = """
from time import perf_counter
b=bytearray(int(__import__('sys').argv[1])*1048576)
for n in range(0,len(b),4096): b[n]=1
deadline=perf_counter()+.06
while perf_counter()<deadline: pass
"""


def probe(children, mib):
    code = ("import subprocess,sys;"
            f"[subprocess.run([sys.executable,'-S','-c',{CHILD!r},'{mib}'],check=True) for _ in range({children})]")
    process = native.Process([sys.executable, "-S", "-c", code], os.environ.copy(), False,
                             "Local\\WordPipe-EXEC01-probe-" + uuid.uuid4().hex)
    try:
        if _winapi.WaitForSingleObject(process.process, 10000) != _winapi.WAIT_OBJECT_0:
            raise RuntimeError("probe exceeded its wait budget")
        start = time.perf_counter()
        account, limits = native._Accounting(), native._ExtendedLimits()
        for kind, struct in ((1, account), (9, limits)):
            native._checked(native.query_job(process.job, kind, ct.byref(struct), ct.sizeof(struct), None))
        overhead = time.perf_counter() - start
        if process.code() or account.active or account.total != children + 1:
            raise RuntimeError("probe did not finish with expected job membership")
        return {"expected_descendants": children, "child_mib": mib, "total_processes": account.total,
                "active_processes": account.active, "lifetime_cpu_seconds": sum(account.times[:2]) / 1e7,
                "peak_job_committed_bytes": limits.memory[3], "sampled_tree_rss_bytes": None,
                "query_wall_seconds": overhead}
    finally:
        process.close(False)


def main():
    results = []
    start = time.monotonic()
    for children, mib in ((0, 0), (1, 16), (2, 32)):
        if time.monotonic() - start >= 1800:
            break
        try:
            results.append(probe(children, mib))
        except (OSError, RuntimeError) as exc:
            results.append({"expected_descendants": children, "child_mib": mib,
                            "error_type": type(exc).__name__, "winerror": getattr(exc, "winerror", None)})
            break
    print(json.dumps({"platform":sys.platform, "python":sys.version.split()[0],
                      "windows_build":sys.getwindowsversion().build, "probes":results}, indent=2))


if __name__ == "__main__":
    main()
