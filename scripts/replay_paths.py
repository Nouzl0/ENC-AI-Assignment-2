"""Explicit read-time path relocation. Never rewrite signed CSV/JSON bytes."""

import glob
import json
import os
from pathlib import Path

_PREFIXES = []


def configure_path_map(path=None, repo_root=None):
    """Replay only: disjoint absolute prefixes, one target is the current repo."""
    global _PREFIXES
    _PREFIXES = []
    if path is None:
        return
    # Delay the import: common's file readers depend on this module.
    from common import unique_json_object

    with open(path, encoding="utf-8") as f:
        value = json.load(f, object_pairs_hook=unique_json_object)
    if (
        not isinstance(value, dict)
        or value.get("schema_version") != 1
        or not isinstance(value.get("prefixes"), list)
    ):
        raise ValueError("path map requires schema_version=1 and prefixes")
    prefixes = []
    for item in value["prefixes"]:
        if not isinstance(item, dict) or set(item) != {"from", "to"}:
            raise ValueError("each path mapping requires only from/to")
        source, target = item["from"], item["to"]
        if (
            not isinstance(source, str)
            or not isinstance(target, str)
            or not os.path.isabs(source)
            or not os.path.isabs(target)
            or os.path.normpath(source) != source
            or os.path.normpath(target) != target
            or source == os.path.sep
            or target == os.path.sep
        ):
            raise ValueError(
                "mapping prefixes must be canonical absolute non-root paths"
            )
        target = str(Path(target).resolve())
        if not Path(target).is_dir():
            raise ValueError("mapping target must be an existing directory")
        for old_source, old_target in prefixes:
            if any(
                _within(a, b) or _within(b, a)
                for a, b in ((source, old_source), (target, old_target))
            ):
                raise ValueError("mapping prefixes/targets must not overlap")
        prefixes.append((source, target))
    for i, (source, _) in enumerate(prefixes):
        for j, (_, target) in enumerate(prefixes):
            if i == j and source == target:
                continue  # Keeping one directory at its original location is safe.
            if _within(source, target) or _within(target, source):
                raise ValueError(
                    "source/target cross-overlap would remap an already mapped path"
                )
    if (
        len(prefixes) < 2
        or sum(target == str(Path(repo_root).resolve()) for _, target in prefixes) != 1
    ):
        raise ValueError(
            "map the original repo and private directory to distinct targets, including the current repo"
        )
    _PREFIXES = prefixes


def _within(path, prefix):
    return path == prefix or path.startswith(prefix + os.path.sep)


def resolve_input(path):
    """Map I/O only; retain the original logical path inside all loaded records."""
    value = os.fspath(path)
    if not _PREFIXES:
        return value
    value = os.path.abspath(value)
    for source, target in _PREFIXES:
        if _within(value, source):
            value = target + value[len(source) :]
            resolved = str(Path(value).resolve())
            if not _within(resolved, target):
                raise ValueError("mapped path escapes target (including symlinks)")
            return resolved
    for _, target in _PREFIXES:
        if _within(value, target) and not _within(str(Path(value).resolve()), target):
            raise ValueError("input path escapes mapped target through a symlink")
    return value


def input_glob(pattern):
    return sorted(glob.glob(resolve_input(pattern)))
