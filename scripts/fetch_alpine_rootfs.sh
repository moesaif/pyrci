#!/usr/bin/env bash
# -----------------------------------------------------------------------------
# fetch_alpine_rootfs.sh – download & unpack the latest Alpine mini‑rootfs
# -----------------------------------------------------------------------------
# Usage: ./scripts/fetch_alpine_rootfs.sh [version] [dest]
#        version – optional, default: latest‑stable metadata from dl‑cdn
#        dest    – directory to untar into (default: ./rootfs)
#
# Notes:
#   * Requires: curl, tar, sudo (for chown/untar with preserved UIDs)
#   * Works on x86_64 and aarch64 hosts (auto‑detects uname ‑m)
# -----------------------------------------------------------------------------
set -euo pipefail

ARCH=$(uname -m)
case "$ARCH" in
  x86_64) ARCH="x86_64" ;;
  arm64|aarch64) ARCH="aarch64" ;;
  *) echo "✖ Unsupported arch: $ARCH" >&2 ; exit 1 ;;
esac

VERSION="${1:-latest-stable}"
DEST="${2:-rootfs}"

BASE_URL="https://dl-cdn.alpinelinux.org/alpine/${VERSION}/releases/${ARCH}"

# If VERSION was explicit (e.g. 3.20.0) use that; else figure out the
# exact file name via curl -L -I trick.
FILENAME=$(curl -sSL "${BASE_URL}/" | \
          grep -o "alpine-minirootfs-[0-9.]*-${ARCH}\.tar\.gz" | \
          sort -V | tail -n1)

URL="${BASE_URL}/${FILENAME}"

mkdir -p "$DEST"
TMP=$(mktemp /tmp/alpine-rootfs.XXXXXX.tar.gz)

printf "📥 Downloading %s…\n" "$URL"
curl -L "$URL" -o "$TMP"

printf "📦 Extracting into %s (needs sudo to preserve UIDs) …\n" "$DEST"
sudo tar -xpf "$TMP" -C "$DEST"
rm "$TMP"

printf "✅ Done. A minimal Alpine rootfs is now in %s\n" "$DEST"
