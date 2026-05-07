#!/usr/bin/env python3
"""Env var extractor for this project.

Scans common sources (Python/JS/TS, YAML, Docker/Kubernetes configs) to find
references to environment variables and outputs a JSON inventory.
"""
import os
import re
import json
from collections import defaultdict

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

PATTERNS = {
    # Python os.environ.get and os.getenv
    'py_getenv': re.compile(r"os\.(?:getenv|environ)\(\s*['\"]?([A-Z_][A-Z0-9_]*)['\"]?"),
    'py_index': re.compile(r"os\.environ\[\s*['\"]?([A-Z_][A-Z0-9_]*)['\"]?\s*\]"),
    # Node.js process.env
    'node_env': re.compile(r"process\.env\.([A-Z_][A-Z0-9_]*)"),
    # YAML-like patterns: - VAR=value or VAR: value
    'yaml_env_dash': re.compile(r"^\s*-\s*([A-Z_][A-Z0-9_]*)=", re.M),
    'yaml_key': re.compile(r"^\s*([A-Z_][A-Z0-9_]*)\s*:\s*.*$", re.M),
}

ENV_EXTS = ('.py', '.js', '.ts', '.yaml', '.yml', '.sh', '.env', '.tf')
EXCLUDED_DIRS = {'.git', 'venv', 'node_modules', '__pycache__', '.venv'}

vars_found = defaultdict(set)

def is_text_file(path: str) -> bool:
    return path.endswith(ENV_EXTS)

for root, dirs, files in os.walk(REPO_ROOT):
    dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
    for fname in files:
        fpath = os.path.join(root, fname)
        if not is_text_file(fpath) and not fname.startswith('docker-compose'):
            continue
        try:
            with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception:
            continue

        for key, pat in PATTERNS.items():
            for m in pat.finditer(content):
                var = m.group(1)
                if var:
                    vars_found[var].add(fpath)
        # Docker-compose like env sections (explicit VAR=value)
        for m in re.finditer(r"^\s*ENV_?([A-Z_][A-Z0-9_]*)=", content, re.M):
            vars_found[m.group(1)].add(fpath)

        # Simple Kubernetes/env references in YAML: look for common refs
        for m in re.finditer(r"\bsecretKeyRef|configMapKeyRef|envFrom|env:\s*.*", content):
            pass

out = []
for var in sorted(vars_found.keys()):
    sources = sorted(list(vars_found[var]))
    # naive heuristic description
    desc_parts = []
    if var.endswith('_URL'):
        desc_parts.append('URL')
    if 'SECRET' in var or 'KEY' in var or 'TOKEN' in var:
        desc_parts.append('Secret/Key')
    if not desc_parts:
        desc_parts.append('Env var')
    out.append({
        'variable': var,
        'description': '; '.join(desc_parts),
        'sources': sources
    })

inventory_path = os.path.join(REPO_ROOT, 'docs', 'env_vars_extracted.json')
with open(inventory_path, 'w', encoding='utf-8') as jf:
    json.dump(out, jf, indent=2, ensure_ascii=False)

print(f"Env var extraction complete. {len(out)} variables found. See {inventory_path}")
