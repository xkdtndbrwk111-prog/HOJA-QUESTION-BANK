#!/usr/bin/env python3
"""Independent read-only gate for a catalog publication PR. No secret, no writes.
The private publisher owns teacher approval gates. This checks integrity,
ancestry, monotonic pointer, no extra files, and exact runtime pins.
"""
import hashlib
import json
import re
import subprocess
import sys

DIR = 'game-runtime/active/v1/'
PKG = 'game-runtime/approved-packages/v1/'
REPO = 'xkdtndbrwk111-prog/HOJA-QUESTION-BANK'
HEX40 = re.compile(r'[0-9a-f]{40}')
HEX64 = re.compile(r'[0-9a-f]{64}')
ID = re.compile(r'[a-z0-9][a-z0-9-]{2,63}')
def require(value, message):
    if not value:
        raise ValueError(message)
def git(*args):
    return subprocess.check_output(['git', *args])
def blob(commit, path):
    return git('show', commit + ':' + path)
def sha(raw):
    return hashlib.sha256(raw).hexdigest()
def pointer(raw):
    p = json.loads(raw)
    require(p.get('schemaVersion') == 'hoja-active-catalog-pointer-v1', 'POINTER_SCHEMA')
    require(type(p.get('generation')) is int and 0 < p['generation'] < 2**53, 'POINTER_GENERATION')
    require(HEX40.fullmatch(p.get('catalogCommit', '')) and HEX64.fullmatch(p.get('catalogSha256', '')), 'POINTER_PIN')
    return p
def ancestor(a, b):
    git('merge-base', '--is-ancestor', a, b)
def main(base, head):
    require(HEX40.fullmatch(base) and HEX40.fullmatch(head), 'IMMUTABLE_REF')
    ancestor(base, head)
    changed = set(git('diff', '--name-only', base, head).decode().splitlines())
    require(changed in ({DIR+'catalog.json', DIR+'current.json'}, {DIR+'current.json'}), 'PUBLICATION_ONLY_METADATA')
    p = pointer(blob(head, DIR+'current.json'))
    previous_path = git('ls-tree', '--name-only', base, '--', DIR+'current.json').strip()
    if previous_path:
        prev = pointer(blob(base, DIR+'current.json'))
        ancestor(prev['catalogCommit'], base)
        require(sha(blob(prev['catalogCommit'], DIR+'catalog.json')) == prev['catalogSha256'], 'PREVIOUS_DIGEST')
        require(p['generation'] == prev['generation']+1, 'GENERATION_NOT_NEXT')
        require(p['catalogSha256'] != prev['catalogSha256'] or p['catalogCommit'] != prev['catalogCommit'], 'NO_CHANGE')
    else:
        require(p['generation'] == 1, 'BOOTSTRAP_GENERATION')
    ancestor(base, p['catalogCommit'])
    ancestor(p['catalogCommit'], head)
    raw = blob(p['catalogCommit'], DIR+'catalog.json')
    require(len(raw) <= 350000 and sha(raw) == p['catalogSha256'], 'CATALOG_DIGEST')
    require(raw == blob(head, DIR+'catalog.json'), 'CATALOG_POINTER_MISMATCH')
    cat = json.loads(raw)
    require(cat.get('schemaVersion') == 'hoja-active-cartridge-catalog-v1' and cat.get('buildType') == 'RELEASE', 'RELEASE_REQUIRED')
    require(cat.get('sourceRepo') == REPO and HEX40.fullmatch(cat.get('sourceCommit','')), 'SOURCE_PIN')
    src = cat.get('contentSource') or {}
    require(src.get('kind') == 'GITHUB_RAW_PINNED_V1' and src.get('repo') == REPO and HEX40.fullmatch(src.get('commit','')), 'CONTENT_PIN')
    ancestor(cat['sourceCommit'], src['commit'])
    ancestor(src['commit'], base)
    git('diff', '--exit-code', cat['sourceCommit'], base, '--', 'approved')
    git('diff', '--exit-code', src['commit'], base, '--', PKG)
    idx = json.loads(blob(src['commit'], PKG+'INDEX.json'))
    require(idx.get('schemaVersion') == 'hoja-game-runtime-packages-v1' and idx.get('sourceCommit') == cat['sourceCommit'], 'INDEX_PIN')
    packages = {x['cartridgeId']:x for x in idx['packages']}
    require(len(packages) == len(idx['packages']), 'DUPLICATE_PACKAGE')
    entries = cat.get('entries')
    require(isinstance(entries, list) and 0 < len(entries) <= 1000, 'ENTRY_COUNT')
    seen = set()
    total = 0
    for e in entries:
        cid = e.get('cartridgeId','')
        require(ID.fullmatch(cid) and not cid.isdigit() and cid not in seen, 'ENTRY_ID')
        seen.add(cid)
        require(e.get('deploymentStatus') == 'DEPLOYED' and HEX64.fullmatch(e.get('effectiveSha256','')), 'ENTRY_STATUS')
        path = PKG+cid+'.json'
        pin = packages.get(cid) or {}
        require(e.get('contentPath') == path and pin.get('path') == path and HEX64.fullmatch(e.get('packageSha256','')) and e['packageSha256'] == pin.get('sha256'), 'PACKAGE_PIN')
        raw = blob(src['commit'], path)
        require(sha(raw) == e['packageSha256'] and len(raw) == pin.get('bytes'), 'PACKAGE_DIGEST')
        d = json.loads(raw)
        require(d.get('cartridgeId') == cid and d.get('questionSchemaVersion') == 2 and isinstance(d.get('questions'),list) and type(e.get('questionCount')) is int and e['questionCount'] > 0 and len(d['questions']) == e['questionCount'], 'PACKAGE_QUESTION_COUNT')
        total += e['questionCount']
    print(f'ACTIVE_CATALOG_PUBLICATION_PASS generation={p["generation"]} units={len(entries)} questions={total}')
if __name__ == '__main__':
    main(*sys.argv[1:])
