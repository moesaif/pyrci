# PyCRI – AI‑Powered Container Runtime Interface in Pure Python 🐍🧠

> **A weekend‑size project that grows into an experiment ground for adding machine‑learning brains to low‑level container runtimes.**

![Status](https://img.shields.io/badge/status-experimental-orange) ![License](https://img.shields.io/github/license/your-name/pycri)

---

## ✨ Why does this exist?

1. **Pedagogy first** – understand what Docker/containerd _actually_ do by rebuilding the essentials in \~150 LOC of Python.
2. **AI second** – explore how lightweight ML models can:

   - predict resource usage and recommend cgroup limits ➡️ fewer OOM‑kills.
   - detect anomalous syscalls or network patterns ➡️ early compromise alerts.
   - auto‑label workload types that K8s‑scheduler hints can use.

Think of PyCRI as a playground where systems enthusiasts and ML folks meet.

---

## 🚀 Features (current)

| Area              | What we have                                                                                                    |
| ----------------- | --------------------------------------------------------------------------------------------------------------- |
| **Namespaces**    | PID, UTS, IPC, NET, MNT, USER via `unshare --map-root-user`.                                                    |
| **Filesystem**    | `chroot` into any minimal **rootfs** (BusyBox, Alpine, Debian…).                                                |
| **Cgroups v1/v2** | Memory limit; hooks ready for CPU/IO/`pids.max`.                                                                |
| **CLI**           | `pycri run <rootfs> <cmd>` with `--mem` flag.                                                                   |
| **AI advisor v0** | Simple linear‑regression model that watches `/sys/fs/cgroup/<cid>/memory.current` and suggests +/‑ adjustments. |

---

## 🏁 Quick Start

```bash
# 1. clone & install deps
$ git clone https://github.com/your-name/pycri.git && cd pycri
$ pip install -r requirements.txt     # only argparse + scikit‑learn

# 2. prepare a tiny ARM64 or x86_64 linux rootfs (example: Alpine)
$ ./scripts/fetch_alpine_rootfs.sh    # puts it under ./rootfs

# 3. run a shell inside a namespaced container
$ sudo python3 pycri.py run ./rootfs /bin/sh --mem 256M
/ # hostname
/ # exit
```

> **macOS/Apple Silicon?** Use `colima start --arch aarch64` and `colima ssh` – see [docs/mac.md](docs/mac.md).

---

## 🧩 Repository Layout

```
pycri/
├── pycri.py           # main script
├── advisor.py         # ML resource advisor (WIP)
├── requirements.txt   # pip deps (tiny)
├── rootfs/            # example BusyBox root filesystem
└── scripts/
    └── fetch_alpine_rootfs.sh
```

---

## 📝 Architecture Overview

```
(pycri CLI)        (kernel)                 (optional)
   │                clone() + ns           +--------------+
   │   unshare ───▶ pid/net/... namespaces │  cgroup v2   │
   │                ↳ child PID            │  resource    │
   │   chroot  ───▶ new rootfs             │  limits      │
   │   exec    ───▶ /bin/sh                +--------------+
   │
   └─► advisor thread  ⇄  cgroup stats  ⇄  scikit‑learn model
```

---

## 🤖 AI Roadmap

| Phase  | ML capability                                           | Notes       |
| ------ | ------------------------------------------------------- | ----------- |
| **v0** | Linear trend on RSS; suggest `memory.max` update.       | Done ✅     |
| **v1** | LSTM forecasting of CPU & RSS; autoscale hint.          | ETA Q3 2025 |
| **v2** | Online clustering of syscall sequences; flag anomalies. | Researching |
| **v3** | Reinforcement‑learning scheduler shim for K8s.          | Moon‑shot   |

---

## 🔜 General Roadmap

- [ ] OverlayFS copy‑on‑write layer
- [ ] veth + bridge network isolation
- [ ] OCI image pull/unpack
- [ ] Minimal CRI shim (gRPC) so kubelet can launch pods via PyCRI
- [ ] Seccomp + reduced capability set

---

## 🤝 Contributing

1. **Fork** the repo and create a feature branch.
2. Follow `pre-commit` hooks (`ruff`, `black`, `isort`).
3. Add unit tests under `tests/` (`pytest`).
4. Open a PR – describe _why_ not just _what_.

We love learning‑oriented PRs: even comments, doc fixes, or failing tests are welcome.

---

## 🛡️ License

Apache‑2.0. See [LICENSE](LICENSE) for full text.

---

## 🙏 Acknowledgements

Inspired by Liz Rice’s “Containers From Scratch”, Julia Evans’ `containers‑from‑scratch`, and the runc & containerd communities. Special thanks to everyone experimenting with AI for infra.

---

> _Made with \:coffee: & \:sparkles: by Saif and contributors._
