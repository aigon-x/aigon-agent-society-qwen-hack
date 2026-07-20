#!/usr/bin/env python3
"""
Auto-sync project snapshots to PROD PostgreSQL with versioning.

Usage:
  python3 sync-snapshot-db.py <project_name> <snapshot_path> [tenant]
  python3 sync-snapshot-db.py qwen-hack /opt/aigon-x-new/products/qwen-hack/docs/PROJECT-SNAPSHOT.md szamani

Runs from cron every N minutes to auto-save project state.
Each save is versioned — full history preserved.
"""

import json, os, subprocess, sys, re
from datetime import datetime, timezone

DB = "postgresql://aigon:changeme@100.99.59.100:5437/aigoncode"
TABLE = "project_snapshots"

def ensure_schema():
    """Create table + index if not exist."""
    cmds = [
        f"""CREATE TABLE IF NOT EXISTS {TABLE} (
            id SERIAL PRIMARY KEY,
            project_name TEXT NOT NULL,
            tenant TEXT NOT NULL DEFAULT 'default',
            version INT NOT NULL DEFAULT 1,
            data JSONB NOT NULL,
            file_hash TEXT,
            created_at TIMESTAMPTZ DEFAULT NOW()
        )""",
        f"""CREATE INDEX IF NOT EXISTS idx_{TABLE}_project_tenant
            ON {TABLE} (project_name, tenant)""",
    ]
    for c in cmds:
        subprocess.run(["psql", DB, "-c", c], capture_output=True)

def file_hash(path):
    import hashlib
    with open(path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()[:16]

def sync(project, path, tenant="default"):
    if not os.path.isfile(path):
        print(f"❌ No file: {path}")
        return False

    with open(path) as f:
        content = f.read()

    fh = file_hash(path)
    mtime = os.path.getmtime(path)
    mtime_str = datetime.fromtimestamp(mtime, tz=timezone.utc).isoformat()

    # Check if same content already saved (dedup)
    r = subprocess.run([
        "psql", DB, "-t", "-A", "-c",
        f"SELECT file_hash FROM {TABLE} WHERE project_name='{project}' AND tenant='{tenant}' ORDER BY version DESC LIMIT 1"
    ], capture_output=True, text=True)
    last_hash = r.stdout.strip()
    if last_hash == fh:
        print(f"⏭️  {project}/{tenant}: unchanged (hash {fh})")
        return True

    # Next version number
    r = subprocess.run([
        "psql", DB, "-t", "-A", "-c",
        f"SELECT COALESCE(MAX(version), 0) + 1 FROM {TABLE} WHERE project_name='{project}' AND tenant='{tenant}'"
    ], capture_output=True, text=True)
    ver = int(r.stdout.strip() or 1)

    data = json.dumps({
        "markdown": content,
        "file_path": path,
        "size_bytes": len(content),
        "mtime": mtime_str,
    })

    cmd = f"""INSERT INTO {TABLE} (project_name, tenant, version, data, file_hash)
VALUES ('{project}', '{tenant}', {ver}, '{data}'::jsonb, '{fh}')"""
    r = subprocess.run(["psql", DB, "-c", cmd], capture_output=True, text=True)
    if r.returncode == 0:
        print(f"✅ {project}/{tenant}: v{ver} saved ({len(content)} chars, hash={fh})")
        return True
    else:
        print(f"❌ {project}/{tenant}: {r.stderr.strip()}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: sync-snapshot-db.py <project> <snapshot_path> [tenant]")
        sys.exit(1)
    ensure_schema()
    ok = sync(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "default")
    sys.exit(0 if ok else 1)
