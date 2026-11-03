"""Install the three local Codex ports and their SessionStart hooks."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import tomllib

ROOT = Path(__file__).resolve().parents[1]
HOME_DIR = Path(os.environ.get("CODEX_HOME") or Path.home() / ".codex").resolve()
SKILLS = HOME_DIR / "skills"
NAMES = ("digest", "knowledge-compile", "inbox")
BEGIN = "# BEGIN digest-knowledge-inbox Codex hooks"
END = "# END digest-knowledge-inbox Codex hooks"


def main():
    node = shutil.which("node")
    if not node or int(subprocess.check_output([node, "-p", "process.versions.node.split('.')[0]"])) < 24:
        sys.exit("Node 24+ required for inbox")
    SKILLS.mkdir(parents=True, exist_ok=True)
    config = HOME_DIR / "config.toml"
    old = config.read_bytes() if config.exists() else b""
    text = old.decode("utf-8")
    if BEGIN in text:
        start = text.index(BEGIN)
        stop = text.index(END, start) + len(END)
        text = text[:start] + text[stop:]
    commands = [
        f'"{sys.executable}" -X utf8 "{SKILLS / "knowledge-compile/scripts/knowledge_index_hook.py"}"',
        f'"{node}" "{SKILLS / "inbox/scripts/inbox.mjs"}" session-start',
    ]
    block = [BEGIN]
    for command in commands:
        block.extend(["[[hooks.SessionStart]]", 'matcher = "startup|resume|clear|compact"',
                      "[[hooks.SessionStart.hooks]]", 'type = "command"',
                      "command = " + json.dumps(command, ensure_ascii=False), "timeout = 10", ""])
    updated = text.rstrip() + "\n\n" + "\n".join(block + [END, ""])
    tomllib.loads(updated)
    backups = HOME_DIR / "skill-updates"
    backups.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(dir=HOME_DIR) as stage:
        stage = Path(stage)
        for name in NAMES:
            shutil.copytree(ROOT / name / "skills" / name, stage / name,
                            ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "compile-all.sh"))
        shutil.copy2(ROOT / "inbox/mod/hooks/todo.ts", stage / "inbox/scripts/todo.mts")
        shutil.copy2(ROOT / "knowledge-compile/hooks/knowledge_index_hook.py", stage / "knowledge-compile/scripts")
        # The Claude tool allowlist is not a Codex permission policy.
        entry = stage / "knowledge-compile/SKILL.md"
        body = entry.read_text(encoding="utf-8")
        start = body.index("allowed-tools:")
        entry.write_text(body[:start] + body[body.index("\n---", start)+1:], encoding="utf-8")
        backup = Path(tempfile.mkdtemp(prefix="codex-ports-", dir=backups))
        installed = []
        if config.exists():
            shutil.copy2(config, backup / config.name)
        try:
            for name in NAMES:
                target = SKILLS / name
                if target.exists():
                    target.rename(backup / name)
                installed.append(name)
                (stage / name).rename(target)
            if (config.read_bytes() if config.exists() else b"") != old:
                raise RuntimeError("Codex config changed during installation")
            temp_config = stage / config.name
            temp_config.write_bytes(updated.encode("utf-8"))
            temp_config.replace(config)
        except Exception:
            for name in reversed(installed):
                target = SKILLS / name
                if target.exists():
                    target.rename(stage / name)
                if (backup / name).exists():
                    (backup / name).rename(target)
            raise
    print(f"Installed {', '.join(NAMES)} in {SKILLS}. Backup: {backup}")


if __name__ == "__main__":
    main()
