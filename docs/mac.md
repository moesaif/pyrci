# Running **PyCRI** on macOS (Apple Silicon & Intel)

PyCRI depends on Linux kernel features (namespaces, cgroups, OverlayFS). macOS does **not** expose those APIs, so we run PyCRI **inside a lightweight Linux VM**.
The guide below uses **Colima** because it ships a turnkey Apple Silicon–optimised VM built on Apple’s `virtualization.framework`, but any ARM‑64 Linux VM (UTM, Multipass, Parallels) works.

---

## 1 · Prerequisites

| Tool                           | Install cmd                                                                                       |
| ------------------------------ | ------------------------------------------------------------------------------------------------- |
| **Homebrew**                   | `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"` |
| **Colima ≥ 0.6**               | `brew install colima`                                                                             |
| **(Optional) Rsync & GNU tar** | `brew install rsync gnu-tar` – speeds up large rootfs copies                                      |

> **Intel users**: change every `--arch aarch64` flag below to `--arch x86_64`.

---

## 2 · Spin‑up a tiny Linux VM

```bash
# Start a 4 GiB RAM, 20 GiB disk ARM64 VM via Apple’s hypervisor
colima start --arch aarch64 --memory 4 --disk 20 --vm-type vz
# Drop into a shell inside the VM
colima ssh
```

If all went well you should see a prompt like:

```text
root@colima:~#
```

> `colima ssh` connects as **root**. You can create an unprivileged `runner` user if you prefer.

---

## 3 · Get the PyCRI source inside the VM

Two common ways:

### A) Git‑clone directly (internet inside VM)

```bash
apt-get update && apt-get install -y git python3-pip curl util-linux
cd /opt
git clone https://github.com/<your‑username>/pycri.git
```

### B) Copy from macOS host

```bash
# From macOS terminal (same folder that contains the repo)
colima cp ./pycri :/opt
```

`colima cp` is a wrapper around rsync; it preserves file modes so your `scripts/` remain executable.

---

## 4 · Install Python deps

```bash
cd /opt/pycri
pip3 install -r requirements.txt  # ≈ 30 s
```

_(If `pip3` isn’t present: `apt-get install -y python3-pip`; Alpine users: `apk add python3 py3-pip`)_.

---

## 5 · Create a minimal ARM64 rootfs

```bash
./scripts/fetch_alpine_rootfs.sh   # auto‑detects arch → downloads ARM64
```

The script untars Alpine’s 3‑5 MiB mini‑rootfs into `./rootfs/` and fixes ownership.

---

## 6 · Launch your first container

```bash
sudo python3 pycri.py run ./rootfs /bin/sh --mem 256M
```

Expected output:

```text
/ #               ← BusyBox hush shell inside the container (PID 1)
```

Try a few commands:

```bash
/ # hostname
/ # ps aux
/ # ip a
```

Exit with `Ctrl‑D` or `exit`.

---

## 7 · Quality‑of‑life aliases (optional)

Add these to your macOS `~/.zshrc`:

```bash
# Jump into the VM quickly
alias pyvm='colima ssh'
# Run PyCRI from macOS shell (assumes repo mounted in /opt/pycri)
function pycri() {
  colima ssh -- sudo python3 /opt/pycri/pycri.py "$@"
}
```

Now you can do:

```bash
pycri run /opt/pycri/rootfs /bin/echo "hello from mac"
```

---

## 8 · Troubleshooting

| Symptom                                    | Cause                                                 | Fix                                                                  |
| ------------------------------------------ | ----------------------------------------------------- | -------------------------------------------------------------------- |
| `exec format error` when running BusyBox   | You downloaded x86_64 rootfs on ARM Mac or vice‑versa | Re‑run `scripts/fetch_alpine_rootfs.sh` – it auto picks correct arch |
| `Cannot open self /proc/…/exe`             | Missing execute bit on BusyBox or wrong sha           | `chmod +x rootfs/bin/busybox`                                        |
| `mount: permission denied (are you root?)` | Forgot `sudo` on `pycri run`                          | Run with `sudo` or extend uid‑map (see README)                       |
| VM out of space                            | Colima default disk is 10 GiB                         | Restart with `colima start --disk 30`                                |

---

## 9 · Alternative VM engines

| Engine                | Notes                                                              |
| --------------------- | ------------------------------------------------------------------ |
| **UTM**               | Full GUI, QEMU backend. Good for nested testing with snapshots.    |
| **Multipass**         | Canonical’s CLI wrapper; supports Apple Silicon native hypervisor. |
| **Parallels Desktop** | Commercial, best UX + continuity copy/paste.                       |

PyCRI itself is identical once inside Linux; choose whichever VM tooling fits your workflow.

---

## 10 · Next steps

- Enable **OverlayFS** in the VM kernel (`modprobe overlay`) and try PyCRI’s upcoming CoW layer.
- Forward container ports via Colima’s host‑forward feature (`colima nerdctl run -p 8080:80 …`).
- Contribute to the AI advisor – logs live‑reload happily in the VM.

Enjoy hacking containers from your Mac! 🍏🐧🤖
