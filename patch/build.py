#!/usr/bin/env python3
"""Build ZAutoBroadcast Arclight patch from upstream ZAutoBroadcast-1.3.jar."""
from __future__ import annotations

import io
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATCH_DIR = ROOT / "patch"
WORK = PATCH_DIR / "work"
CLASS = "me/zepsizola/zautobroadcast/ZAutoBroadcast.class"
ASM_VER = "9.7"
ASM_URL = f"https://repo1.maven.org/maven2/org/ow2/asm/asm/{ASM_VER}/asm-{ASM_VER}.jar"

PLUGIN_YML = """name: ZAutoBroadcast
version: '1.3'
main: me.zepsizola.zautobroadcast.ZAutoBroadcast
api-version: '1.20'
folia-supported: true
softdepend: [PlaceholderAPI, MiniPlaceholders]
loadbefore: [PlaceholderAPI, MiniPlaceholders]
libraries:
  - net.kyori:adventure-api:4.17.0
  - net.kyori:adventure-key:4.17.0
  - net.kyori:adventure-text-minimessage:4.17.0
  - net.kyori:adventure-text-serializer-legacy:4.17.0
  - net.kyori:examination-api:1.3.0
  - net.kyori:examination-string:1.3.0
  - org.jetbrains:annotations:24.1.0

commands:
  zab:
    description: Main command for ZAutoBroadcast.
    usage: /<command> <subcommand> [arguments]
    aliases: [zautobroadcast, autobroadcast]
    subcommands:
      reload:
        description: Reloads the broadcasts.yml file.
        usage: /<command> reload
      broadcast:
        description: Broadcasts a message with the given key.
        usage: /<command> broadcast <key>
      interval:
        description: Gets or sets the broadcast interval.
        usage: /<command> interval get/set <seconds>
      custom:
        description: Sends a custom broadcast message.
        usage: /<command> custom <text>
"""


def ensure_asm() -> Path:
    jar = PATCH_DIR / f"asm-{ASM_VER}.jar"
    if not jar.exists():
        import urllib.request

        print(f"download {ASM_URL}")
        urllib.request.urlretrieve(ASM_URL, jar)
    return jar


def run(cmd: list[str], cwd: Path | None = None) -> None:
    print(">", " ".join(cmd))
    subprocess.check_call(cmd, cwd=cwd)


def patch_jar(src: Path, dst: Path) -> None:
    raw = src.read_bytes()
    with zipfile.ZipFile(io.BytesIO(raw), "r") as zin:
        old_class = zin.read(CLASS)
    if b"legacySection" in old_class:
        print("input class already contains legacySection; only refreshing plugin.yml")
        patched_class = old_class
    else:
        if b"(Lnet/kyori/adventure/text/Component;)V" not in old_class:
            raise SystemExit("unexpected ZAutoBroadcast.class — not Paper-style sendMessage(Component)")
        WORK.mkdir(parents=True, exist_ok=True)
        in_class = WORK / "ZAutoBroadcast.class"
        out_class = WORK / "ZAutoBroadcast.patched.class"
        in_class.write_bytes(old_class)
        asm = ensure_asm()
        run(["javac", "-cp", str(asm), "ZabSendPatch.java"], cwd=PATCH_DIR)
        run(
            [
                "java",
                "-cp",
                f"{PATCH_DIR}{';' if sys.platform == 'win32' else ':'}{asm}",
                "ZabSendPatch",
                str(in_class),
                str(out_class),
            ]
        )
        patched_class = out_class.read_bytes()
        if b"legacySection" not in patched_class:
            raise SystemExit("ASM patch failed")

    buf = io.BytesIO()
    with zipfile.ZipFile(io.BytesIO(raw), "r") as zin:
        with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zout:
            for info in zin.infolist():
                data = zin.read(info.filename)
                if info.filename == CLASS:
                    data = patched_class
                elif info.filename == "plugin.yml":
                    data = PLUGIN_YML.encode("utf-8")
                new = zipfile.ZipInfo(filename=info.filename, date_time=info.date_time)
                new.compress_type = zipfile.ZIP_DEFLATED
                new.external_attr = info.external_attr
                zout.writestr(new, data)
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_bytes(buf.getvalue())
    print(f"wrote {dst} ({dst.stat().st_size} bytes)")


def main() -> int:
    if len(sys.argv) < 2:
        src = ROOT / "upstream" / "ZAutoBroadcast-1.3.jar"
        if not src.exists():
            print(
                "Usage: build.py <path/to/ZAutoBroadcast-1.3.jar>\n"
                "Or place the upstream jar at upstream/ZAutoBroadcast-1.3.jar"
            )
            return 2
    else:
        src = Path(sys.argv[1])
    if not src.exists():
        raise SystemExit(f"missing {src}")
    dst = ROOT / "jar" / "ZAutoBroadcast-1.3-arclight.jar"
    patch_jar(src, dst)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
