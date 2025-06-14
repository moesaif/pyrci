#!/usr/bin/env python3
"""
pyCRI – a *tiny* Container Runtime Interface clone
Usage:
  sudo ./pycri.py run ./rootfs /bin/sh
"""
import argparse
import os
import subprocess
import sys
import textwrap
from pathlib import Path

CGROUP_ROOT = Path("/sys/fs/cgroup")
CG_NAME     = "pycri"

def ensure_root():
    if os.geteuid() != 0:
        sys.exit("❌  Must run as root (namespaces need CAP_SYS_ADMIN)")

# ---------- cgroup helpers ----------
def create_cgroup(pid: int, mem_limit: str | None):
    """
    Creates /sys/fs/cgroup/pycri, moves PID there,
    and optionally sets memory limit (cgroups v1).
    """
    cg_dir = CGROUP_ROOT / CG_NAME
    cg_dir.mkdir(exist_ok=True)

    (cg_dir / "cgroup.procs").write_text(str(pid))

    if mem_limit:
        try:
            (cg_dir / "memory.max"      ).write_text(mem_limit)
            (cg_dir / "memory.limit_in_bytes").write_text(mem_limit)
        except FileNotFoundError:
            print("⚠️  Memory controller not found – skipping limit")

def run_container(rootfs: Path, command: list[str], mem: str | None):
    rootfs = rootfs.resolve()
    if not rootfs.is_dir():
        sys.exit(f"Rootfs {rootfs} not found")

    unshare_cmd = [
        "unshare",
        "--fork",
        "--pid", "--mount", "--uts", "--ipc", "--net",
        "--mount-proc",
        "--user",
        "--map-root-user",
        "chroot", str(rootfs),
        *command
    ]

    child = subprocess.Popen(unshare_cmd)

    if mem:
        create_cgroup(child.pid, mem)

    child.wait()

def main():
    parser = argparse.ArgumentParser(
        description="pyCRI – super-light educational container runtime")
    sub = parser.add_subparsers(dest="action", required=True)

    run_p = sub.add_parser("run", help="Run command inside new container")
    run_p.add_argument("rootfs", help="Path to minimal root filesystem")
    run_p.add_argument("cmd",    nargs=argparse.REMAINDER,
                       help="Command to execute (default: /bin/sh)")
    run_p.add_argument("--mem",  help="Memory limit (e.g. 256M)", default=None)

    args = parser.parse_args()
    ensure_root()

    if args.action == "run":
        cmd = args.cmd or ["/bin/sh"]
        run_container(Path(args.rootfs), cmd, args.mem)

if __name__ == "__main__":
    main()
