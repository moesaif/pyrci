# Security Policy for **PyCRI**

> ⚠️ **Experimental Project** — PyCRI is a learning playground, not a hardened production runtime. Expect sharp edges.

---

## 🔒 Supported Versions

| Version         | Status                       |
| --------------- | ---------------------------- |
| `main`          | Actively developed & patched |
| Tags < `v0.1.0` | *No longer maintained*       |

Because PyCRI has not yet reached 1.0, **only the `main` branch receives security fixes**.

---

## 📣 Reporting a Vulnerability

1. **Email** the maintainers at **[security@pycri.dev](mailto:mscoder12@gmail.com)** (PGP key fingerprint: `0xBEEF FEED C0DE C0DE`).
2. Do **not** open a public GitHub issue for undisclosed vulnerabilities.
3. Provide:

   * Affected commit / tag
   * Reproduction steps or PoC
   * Impact assessment (e.g., "container breakout", "DoS via unprivileged user")

We aim to:

| Phase                    | Timeline                  |
| ------------------------ | ------------------------- |
| Acknowledge receipt      | within **2 working days** |
| Initial assessment       | within **7 days**         |
| Patch & private advisory | within **30 days**        |
| Public disclosure        | coordinated with reporter |

If you need encrypted mail, import our PGP key from [keys.openpgp.org](https://keys.openpgp.org) or the SKS pool.

---

## 🔐 Security Model & Known Limitations

| Layer                    | Current status                           | Planned improvements                                          |
| ------------------------ | ---------------------------------------- | ------------------------------------------------------------- |
| **Namespaces**           | Enabled (PID, NET, MNT, UTS, IPC, USER). | Per‑container seccomp filter to block `ptrace`, `mount`, etc. |
| **Cgroups**              | Memory limit; CPU/IO WIP.                | Fine‑grained `pids.max`, IO throttling.                       |
| **Filesystem isolation** | `chroot` only, optional OverlayFS.       | Switch to `pivot_root`, readonly lowerdir by default.         |
| **Capabilities**         | All retained inside user namespace.      | Drop to minimal set (CAP\_NET\_BIND\_SERVICE, etc.).          |
| **Seccomp/AppArmor**     | *Not implemented*.                       | Seccomp baseline in `v0.2`.                                   |

**Important:** Running `pycri.py` currently requires `sudo`, meaning the parent orchestrator process has full root on the host. Use in disposable VMs only.

---

## 🔭 Scope of Supported Issues

We welcome reports of:

* Container breakout or host privilege-escalation.
* Denial‑of‑service vectors reachable by unprivileged users of PyCRI.
* Wrong cgroup limit calculations that lead to resource starvation of other host processes.

Out of scope:

* Vulnerabilities in third‑party dependencies (report upstream).
* Bugs that require already‑root access on the host.
* Theoretical side‑channel attacks (cache timing, rowhammer, etc.).

---

## 🤝 Acknowledgements

PyCRI’s security process is inspired by Kubernetes, containerd, and the OpenSSF vulnerability disclosure guidelines.
