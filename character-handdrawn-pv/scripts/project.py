#!/usr/bin/env python3
"""Initialize or inspect a hand-drawn PV manifest; standard library only."""

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path, PurePosixPath, PureWindowsPath
import re
import sys


def is_int(value):
    return isinstance(value, int) and not isinstance(value, bool)


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def project_directory(value):
    """A scaffold directory must stay inside the requested project."""
    if not nonempty(value):
        raise ValueError("Directory must be a nonempty relative path.")
    normalized = PurePosixPath(value.replace("\\", "/"))
    if normalized.is_absolute() or PureWindowsPath(value).drive or ".." in normalized.parts:
        raise ValueError("Directory must be relative and cannot contain '..'.")
    return Path(*normalized.parts)


def validate(data, base, for_export=False, files=False):
    errors, warnings = [], []

    def issue(message, incomplete=False):
        (warnings if incomplete and not for_export else errors).append(message)

    if not isinstance(data, dict):
        return {"ok": False, "errors": ["Manifest must be an object."], "warnings": []}
    if data.get("schema_version") != 1 or isinstance(data.get("schema_version"), bool):
        issue("schema_version must be 1.")
    if not nonempty(data.get("revision")):
        issue("revision is required.", True)
    if data.get("route") not in ("original", "adaptation", "replacement"):
        issue("route must be original, adaptation or replacement.")
    directories = data.get("directories", {})
    if not isinstance(directories, dict):
        issue("directories must be an object when provided.")
    else:
        for key in ("docs", "generation"):
            if key in directories:
                try:
                    project_directory(directories[key])
                except ValueError as exc:
                    issue(f"directories.{key}: {exc}")
    policy = data.get("timeline_policy", "contiguous")
    if policy not in ("contiguous", "composited"):
        issue("timeline_policy must be contiguous or composited.")

    output = data.get("output", {})
    if not isinstance(output, dict):
        issue("output must be an object.")
        output = {}
    for key in ("width", "height", "total_frames"):
        value = output.get(key)
        if value is None:
            issue(f"output.{key} is not set.", True)
        elif not is_int(value) or value <= 0:
            issue(f"output.{key} must be a positive integer.")
    fps = output.get("fps")
    if fps is None:
        issue("output.fps is not set.", True)
    else:
        try:
            if isinstance(fps, bool) or Fraction(str(fps)) <= 0:
                raise ValueError()
        except (ValueError, ZeroDivisionError, TypeError):
            issue("output.fps must be a positive number or fraction.")
    total = output.get("total_frames")
    valid_total = is_int(total) and total > 0

    def records(key):
        items = data.get(key, [])
        if not isinstance(items, list):
            issue(f"{key} must be an array.")
            return []
        valid, ids = [], set()
        for index, item in enumerate(items):
            label = f"{key}[{index}]"
            if not isinstance(item, dict):
                issue(f"{label} must be an object.")
                continue
            ident = item.get("id")
            if not nonempty(ident):
                issue(f"{label}.id must be a nonempty string.")
            elif ident in ids:
                issue(f"Duplicate {key} id: {ident}.")
            else:
                ids.add(ident)
            valid.append(item)
        return valid

    assets, scenes, audio = (records(key) for key in ("assets", "scenes", "audio"))
    asset_map = {a["id"]: a for a in assets if nonempty(a.get("id"))}
    if not scenes:
        issue("No scenes are defined.", True)
    if not audio:
        warnings.append("No audio is listed; confirm whether this deliverable is intentionally silent.")

    def check_file(item, label):
        raw = item.get("path")
        if not nonempty(raw):
            issue(f"{label}.path is not set.", True)
            return
        digest = item.get("sha256")
        if digest is not None and (not isinstance(digest, str) or not re.fullmatch(r"[0-9a-fA-F]{64}", digest)):
            issue(f"{label}.sha256 must contain 64 hexadecimal characters.")
            digest = None
        if not files:
            return
        if "://" in raw:
            issue(f"{label}: --files only checks local files: {raw}")
            return
        target = Path(raw)
        if not target.is_absolute():
            target = base / target
        try:
            if not target.is_file():
                issue(f"{label}: file does not exist: {target}")
            elif digest:
                actual = hashlib.sha256()
                with target.open("rb") as stream:
                    for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                        actual.update(chunk)
                if actual.hexdigest().lower() != digest.lower():
                    issue(f"{label}: sha256 mismatch: {target}")
        except OSError as exc:
            issue(f"{label}: cannot read file: {exc}")

    # Optional document pointers use the manifest's directory, just like media.
    brief = data.get("brief", {})
    if not isinstance(brief, dict):
        issue("brief must be an object when provided.")
    else:
        for key in ("lyrics_file", "storyboard_file"):
            value = brief.get(key)
            if value is None:
                continue
            if not nonempty(value):
                issue(f"brief.{key} must be a nonempty path or null.")
            else:
                check_file({"path": value}, f"brief.{key}")

    orders, intervals, used = set(), [], set()
    for index, scene in enumerate(scenes):
        label = f"scene {scene.get('id', index)}"
        order = scene.get("order")
        if not is_int(order) or order < 1:
            issue(f"{label}: order must be a positive integer.")
        elif order in orders:
            issue(f"Duplicate scene order: {order}.")
        else:
            orders.add(order)
        asset = scene.get("asset_id")
        if asset is None:
            issue(f"{label}: asset_id is not set.", True)
        elif not nonempty(asset) or asset not in asset_map:
            issue(f"{label}: unknown asset_id: {asset!r}.")
        else:
            used.add(asset)
        start, end = scene.get("start_frame"), scene.get("end_frame")
        if start is None or end is None:
            issue(f"{label}: frame range is not set.", True)
        elif not is_int(start) or not is_int(end) or start < 0 or end <= start:
            issue(f"{label}: require integer 0 <= start_frame < end_frame.")
        else:
            if valid_total and end > total:
                issue(f"{label}: ends beyond output.total_frames.")
            if is_int(order):
                intervals.append((order, start, end, label))
    for ident in sorted(used):
        check_file(asset_map[ident], f"asset {ident}")
    for index, track in enumerate(audio):
        label = f"audio {track.get('id', index)}"
        check_file(track, label)
        if not is_int(track.get("offset_frames", 0)):
            issue(f"{label}: offset_frames must be an integer (negative is allowed).")

    # Half-open intervals prevent a shared boundary from becoming a missing frame.
    covered, previous_start = 0, -1
    partial_timeline = len(intervals) != len(scenes)
    for _, start, end, label in sorted(intervals):
        if start < previous_start:
            issue(f"{label}: start_frame conflicts with playback order.")
        if start > covered:
            issue(f"Timeline gap: frames [{covered}, {start}).", partial_timeline)
        elif start < covered and policy == "contiguous":
            issue(f"{label}: overlaps preceding coverage ending at {covered}.")
        covered = max(covered, end)
        previous_start = start
    if intervals and valid_total and covered < total:
        issue(f"Timeline ends at {covered}, before total_frames {total}.", partial_timeline)

    if for_export:
        auth = data.get("export_authorization")
        if not isinstance(auth, dict) or auth.get("allowed") is not True or not nonempty(auth.get("evidence")):
            issue("Export authorization is not recorded; retain preview scope unless the user has authorized export.")
        elif auth.get("revision") is not None and auth["revision"] != data.get("revision"):
            issue("Export authorization targets a different revision.")
    return {"ok": not errors, "errors": errors, "warnings": warnings}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    init = commands.add_parser("init", help="Create a project.json without overwriting.")
    init.add_argument("directory", type=Path)
    init.add_argument("--name", required=True)
    check = commands.add_parser("check", help="Read-only structural inspection.")
    check.add_argument("manifest", type=Path)
    check.add_argument("--for-export", action="store_true")
    check.add_argument("--files", action="store_true")
    args = parser.parse_args()
    try:
        if args.command == "init":
            template = Path(__file__).resolve().parents[1] / "assets" / "project-template.json"
            data = json.loads(template.read_text(encoding="utf-8-sig"))
            data["name"] = args.name
            args.directory.mkdir(parents=True, exist_ok=True)
            target = args.directory / "project.json"
            scaffold = {}
            for key, value in data.get("directories", {}).items():
                destination = args.directory / project_directory(value)
                if not destination.resolve().is_relative_to(args.directory.resolve()):
                    raise ValueError(f"Scaffold directory escapes the project: {destination}")
                if destination.exists() and not destination.is_dir():
                    raise ValueError(f"Scaffold directory is occupied by a file: {destination}")
                scaffold[key] = destination
            with target.open("x", encoding="utf-8", newline="\n") as stream:
                json.dump(data, stream, ensure_ascii=False, indent=2)
                stream.write("\n")
            for destination in scaffold.values():
                destination.mkdir(parents=True, exist_ok=True)
            if "docs" in scaffold:
                index = scaffold["docs"] / "README.md"
                body = (template.parent / "docs-index.md").read_text(encoding="utf-8")
                for key in ("docs", "generation"):
                    body = body.replace("{{" + key + "_dir}}", data["directories"].get(key, key).replace("\\", "/"))
                try:
                    with index.open("x", encoding="utf-8", newline="\n") as stream:
                        stream.write(body)
                except FileExistsError:
                    pass  # Existing project notes belong to the user.
            result = {"ok": True, "created": str(target.resolve())}
        else:
            data = json.loads(args.manifest.read_text(encoding="utf-8-sig"))
            result = validate(data, args.manifest.resolve().parent, args.for_export, args.files)
    except (OSError, ValueError) as exc:
        result = {"ok": False, "errors": [str(exc)], "warnings": []}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
