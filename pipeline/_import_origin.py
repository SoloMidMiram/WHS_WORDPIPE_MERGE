"""CI-01 qualification checks for the repository's real Python launch paths."""

from __future__ import annotations

import importlib.metadata
import json
import os
import sys
import sysconfig
from pathlib import Path


CONTEXT_ENV = "WORDPIPE_ORIGIN_QUALIFICATION"


class OriginError(ValueError):
    """A qualification launch cannot establish its declared origins."""


def _resolved(value):
    try:
        return Path(value).resolve(strict=True)
    except (OSError, RuntimeError, TypeError, ValueError) as exc:
        raise OriginError(f"invalid path: expected an existing filesystem path, actual {value!r}") from exc


def _spec(name, search_path):
    if name in sys.modules:
        loaded = sys.modules[name]
        return getattr(loaded, "__spec__", None), loaded
    # Follow the same finder order and parent search path as the real import,
    # without executing any package initializers in order to inspect a child.
    for finder in sys.meta_path:
        spec = finder.find_spec(name, search_path, None)
        if spec is not None:
            return spec, None
    return None, None


def _wheel_records(prefix):
    if _resolved(sys.prefix) != prefix or _resolved(sys.base_prefix) == prefix:
        raise OriginError(f"invalid wheel interpreter: expected a virtualenv at {prefix}, actual {sys.prefix}")
    libs = {_resolved(sysconfig.get_path(key)) for key in ("purelib", "platlib")}
    if not all(lib.is_relative_to(prefix) for lib in libs):
        raise OriginError(f"foreign installation libraries: expected under {prefix}, actual {sorted(libs)}")
    try:
        dist = importlib.metadata.distribution("wordpipe")
    except importlib.metadata.PackageNotFoundError as exc:
        raise OriginError(f"missing wordpipe distribution metadata: expected under {prefix}") from exc
    files = dist.files or ()
    metadata = [
        dist.locate_file(file) for file in files
        if file.name == "METADATA" and file.parent.name.endswith(".dist-info")
    ]
    if len(metadata) != 1 or _resolved(metadata[0]).parent.parent not in libs:
        raise OriginError(f"invalid distribution metadata: expected under {sorted(libs)}, actual {metadata}")
    direct_url = json.loads(dist.read_text("direct_url.json") or "{}")
    if direct_url.get("dir_info", {}).get("editable") is True:
        raise OriginError(f"invalid wheel distribution: editable metadata at {metadata[0]}")
    origins = {
        Path(dist.locate_file(file)).resolve()
        for file in files if file.parts and file.parts[0] == "wordpipe"
    }
    return {lib / "wordpipe" for lib in libs}, origins, str(metadata[0])


def verify(mode, checkout, prefix=None, *, modules=(), driver=None):
    """Validate real import specifications and separately report wheel metadata."""
    checkout = _resolved(checkout)
    if not checkout.is_dir():
        raise OriginError(f"invalid intended checkout: {checkout}")
    if driver is not None and not _resolved(driver).is_relative_to(checkout):
        raise OriginError(f"foreign driver: expected under {checkout}, actual {driver}")
    if mode == "source" and prefix is None:
        package = _resolved(checkout / "wordpipe")
        if not package.is_dir() or not package.is_relative_to(checkout):
            raise OriginError(f"invalid intended package: expected a directory under {checkout}, actual {package}")
        roots, records, metadata = {package}, None, None
    elif mode == "wheel" and prefix is not None:
        roots, records, metadata = _wheel_records(_resolved(prefix))
        if _resolved(prefix).is_relative_to(checkout):
            raise OriginError(f"invalid wheel installation: expected outside drivers {checkout}, actual {prefix}")
    else:
        raise OriginError(f"invalid qualification mode or installation prefix: {mode!r}, {prefix!r}")

    specs = {}

    def check(name):
        if name in specs:
            return specs[name][1]
        parent, _, _ = name.rpartition(".")
        search_path = check(parent) if parent else None
        if parent and search_path is None:
            raise OriginError(f"invalid package parent: {parent}")
        spec, loaded = _spec(name, search_path)
        if spec is None:
            kind = "invalid" if name in sys.modules else "missing"
            raise OriginError(f"{kind} origin for {name}: expected under {sorted(roots)}, actual unavailable")
        locations = getattr(loaded, "__path__", spec.submodule_search_locations)
        if not spec.has_location or not spec.origin or (name == "wordpipe" and locations is None):
            raise OriginError(f"invalid origin for {name}: expected under {sorted(roots)}, actual {spec.origin!r}")
        origin = _resolved(spec.origin)
        if not origin.is_file():
            raise OriginError(f"invalid origin for {name}: expected a file, actual {origin}")
        paths = [origin]
        if loaded is not None:
            filename = getattr(loaded, "__file__", None)
            if not filename:
                raise OriginError(f"invalid loaded file for {name}: expected {origin}, actual {filename!r}")
            paths.append(_resolved(filename))
        if locations is not None:
            paths.extend(_resolved(path) for path in locations)
        if spec.submodule_search_locations is not None:
            paths.extend(_resolved(path) for path in spec.submodule_search_locations)
        if locations is not None and (not locations or not all(_resolved(path).is_dir() for path in locations)):
            raise OriginError(f"invalid package search path for {name}: actual {locations}")
        valid = [any(path.is_relative_to(root) for root in roots) for path in paths]
        if not all(valid):
            kind = "mixed" if any(valid) or parent else "foreign"
            raise OriginError(f"{kind} origin for {name}: expected under {sorted(roots)}, actual {paths}")
        if len(paths) > 1 and loaded is not None and paths[1] != origin:
            raise OriginError(f"mixed origin for {name}: expected {origin}, actual {paths[1]}")
        if records is not None and (origin not in records or origin.is_relative_to(checkout)):
            raise OriginError(f"invalid wheel origin for {name}: expected a file from {metadata}, actual {origin}")
        specs[name] = (str(origin), locations)
        return locations

    check("wordpipe")
    for name in (*modules, *(n for n in list(sys.modules) if n.startswith("wordpipe."))):
        check(name)
    return {
        "mode": mode,
        "interpreter": sys.executable,
        "checkout": str(checkout),
        "distribution_metadata": metadata,
        "origins": {name: origin for name, (origin, _) in specs.items()},
    }


def require_driver(driver, *modules):
    """Run in the original child process before the driver imports WordPipe."""
    if CONTEXT_ENV not in os.environ:
        return
    try:
        context = json.loads(os.environ[CONTEXT_ENV])
        verify(**context, modules=modules, driver=driver)
    except (OSError, TypeError, ValueError, AttributeError) as exc:
        raise SystemExit(f"CI-01: {exc}") from None
