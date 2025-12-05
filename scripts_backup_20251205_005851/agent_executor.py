#!/usr/bin/env python3
import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime

TASK_FILE = Path("agent_tasks/commands.json")


def run_shell(cmd: str) -> dict:
    print(f"[agent_executor] RUN:", cmd, flush=True)
    proc = subprocess.run(cmd, shell=True, text=True,
                          stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE)
    return {
        "command": cmd,
        "returncode": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
    }


def main():
    if not TASK_FILE.exists():
        print(f"[agent_executor] No {TASK_FILE} found. Create it with a list of shell commands.")
        print('Example:\n{"commands": ["ls -la", "supabase db push"]}')
        sys.exit(0)

    data = json.loads(TASK_FILE.read_text())
    commands = data.get("commands", [])
    results = []

    for cmd in commands:
        if not isinstance(cmd, str):
            continue
        results.append(run_shell(cmd))

    out_file = Path("agent_tasks/commands_result.json")
    out = {
        "ran_at": datetime.utcnow().isoformat(),
        "results": results,
    }
    out_file.write_text(json.dumps(out, indent=2))
    print(f"[agent_executor] Done. Results written to {out_file}")


if __name__ == "__main__":
    main()
