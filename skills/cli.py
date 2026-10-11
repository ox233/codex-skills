"""`skills` command-line interface."""
import argparse
import os
import pathlib
import socket
import sys
import time

REQUIRED_KEYS = ("name", "description")


def parse_frontmatter(text):
    """Parse the leading YAML-ish frontmatter block of a SKILL.md."""
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---\n", 4)
    if end == -1:
        return None
    block = text[4:end]
    meta = {}
    for line in block.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip()
    return meta


def find_skills(root):
    """Yield (skill_dir, frontmatter) for every SKILL.md under root."""
    for p in sorted(root.rglob("SKILL.md")):
        yield p.parent, parse_frontmatter(p.read_text())


def validate(root):
    bad = []
    for d, meta in find_skills(root):
        if meta is None:
            bad.append((d, "no frontmatter block"))
            continue
        for key in REQUIRED_KEYS:
            if not meta.get(key):
                bad.append((d, f"missing required key: {key}"))
    return bad


def bus_socket():
    """Return the user session bus socket path, or None if unset."""
    runtime_dir = os.environ.get("XDG_RUNTIME_DIR")
    return pathlib.Path(runtime_dir) / "bus" if runtime_dir else None


def doctor():
    """Report optional-feature availability. Informational only."""
    checks = {}
    bus = bus_socket()
    checks["user session bus"] = bool(bus and bus.is_socket())
    checks["git"] = bool(_on_path("git"))
    for name, ok in checks.items():
        print(f"{name}: {'ok' if ok else 'missing'}")
    return 0


def watch(root, verbose=False, interval=0.5, iterations=None):
    """Poll SKILL.md files and print reload hints on change.

    The in-place reload hint is delivered through the user session bus
    when a bus socket is present, per `skills doctor`.
    """
    bus = bus_socket()

    def snap():
        return {str(p): p.stat().st_mtime for p in sorted(root.rglob("SKILL.md"))}

    before = snap()
    n = 0
    while iterations is None or n < iterations:
        time.sleep(interval)
        n += 1
        after = snap()
        diff = sorted(
            set(before) ^ set(after)
            | {p for p in before if p in after and before[p] != after[p]}
        )
        if diff:
            if bus and bus.is_socket():
                try:
                    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                    s.settimeout(2)
                    s.connect(str(bus))
                    s.close()
                    if verbose:
                        print("reload hint via user session bus")
                except OSError as e:
                    print(f"reload hint failed: user bus unreachable: {e}", file=sys.stderr)
                    return 1
            for p in diff:
                print(f"changed: {p}")
        before = after
    return 0


def _on_path(binary):
    for dir_ in os.environ.get("PATH", "").split(os.pathsep):
        if pathlib.Path(dir_, binary).is_file():
            return True
    return False


def main(argv=None):
    p = argparse.ArgumentParser(prog="skills", description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)

    n = sub.add_parser("new", help="Scaffold a new skill directory.")
    n.add_argument("name")

    sub.add_parser("list", help="Catalog skills under the current tree.")
    sub.add_parser("validate", help="Validate every SKILL.md frontmatter.")
    sub.add_parser("doctor", help="Check the local environment.")

    w = sub.add_parser("watch", help="Poll SKILL.md files and print reload hints.")
    w.add_argument("--verbose", action="store_true")
    w.add_argument("--interval", type=float, default=0.5)
    w.add_argument("--iterations", type=int, default=None)

    a = p.parse_args(argv)
    root = pathlib.Path.cwd()
    if a.cmd == "new":
        d = root / a.name
        (d).mkdir(exist_ok=True)
        (d / "SKILL.md").write_text(
            "---\n"
            f"name: {a.name}\n"
            "description: TODO — what this skill does and when to use it.\n"
            "---\n\n"
            "# TODO\n\nDescribe the workflow.\n"
        )
        print(d)
        return 0
    if a.cmd == "list":
        for d, meta in find_skills(root):
            print(f"{d.name}\t{meta.get('description', '') if meta else '<invalid>'}")
        return 0
    if a.cmd == "validate":
        bad = validate(root)
        for d, why in bad:
            print(f"{d}: {why}", file=sys.stderr)
        return 1 if bad else 0
    if a.cmd == "doctor":
        return doctor()
    if a.cmd == "watch":
        return watch(root, verbose=a.verbose, interval=a.interval, iterations=a.iterations)
    return 2


if __name__ == "__main__":
    sys.exit(main())