"""Offline draft repository integrity and cartridge version verification.
Does not authorize publication. Never reads network or writes game data.
"""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def read(path):
    return json.loads(path.read_text(encoding='utf-8'))

def checked(root, rel):
    parts = rel.split('/')
    if not parts or any(p in ('', '.', '..') for p in parts) or '\\' in rel:
        raise ValueError('unsafe relative path: ' + rel)
    p = root.joinpath(*parts)
    if not p.is_file() or not p.resolve().is_relative_to(root.resolve()) or any(x.is_symlink() for x in [p, *p.parents] if x != root and x.is_relative_to(root)):
        raise ValueError('missing or unsafe file: ' + rel)
    return p

def cartridge_version(folder):
    """Full SHA-256 of exact JSON bytes + all referenced asset bytes by relative path."""
    q = read(checked(folder, 'cartridge.json'))
    assets = set()
    for question in q['questions']:
        for block in question['content'] + [b for c in question.get('choices', []) for b in c['content']]:
            if block['kind'] == 'image':
                rel = block['src']
                if not rel.startswith('assets/') or Path(rel).suffix not in ('.webp', '.svg'):
                    raise ValueError('unsupported asset path: ' + rel)
                assets.add(rel)
    hashes = {p: sha(checked(folder, p)) for p in sorted(assets | {'cartridge.json'})}
    canonical = json.dumps(hashes, sort_keys=True, ensure_ascii=True, separators=(',', ':')).encode('utf-8')
    return {'id': q['cartridgeId'], 'version': hashlib.sha256(canonical).hexdigest(), 'files': hashes}

def inventory(root):
    catalog = read(root/'catalog.draft.json')
    if catalog['publication'] != 'NOT_APPROVED':
        raise ValueError('draft catalog must not be published')
    ids = set(); entries = []
    for x in catalog['cartridges']:
        rel = x['path']; p = checked(root, rel)
        if x['status'] != 'held_for_review' or x['qa']['publication'] != 'NOT_APPROVED':
            raise ValueError('unexpected publication status')
        if sha(p) != x['sha256']:
            raise ValueError('catalog JSON hash mismatch: ' + rel)
        v = cartridge_version(p.parent)
        if v['id'] != x['id'] or v['id'] in ids:
            raise ValueError('catalog ID mismatch/duplicate: ' + rel)
        ids.add(v['id'])
        entries.append({'path': rel, 'status': 'held_for_review', **v})
    samples = []
    for p in sorted((root/'samples').glob('*/cartridge.json')):
        v = cartridge_version(p.parent)
        if v['id'] in ids:
            raise ValueError('duplicate sample ID')
        ids.add(v['id'])
        samples.append({'path': p.relative_to(root).as_posix(), 'status': 'test_only', **v})
    return {'algorithm': 'sha256-canonical-json-file-hashes-v1', 'publication': 'NOT_APPROVED', 'cartridges': entries, 'samples': samples}

def verify(root):
    manifest = read(root/'manifest.sha256.json')
    for rel, expected in manifest.items():
        if sha(checked(root, rel)) != expected:
            raise ValueError('QB1 baseline mismatch: ' + rel)
    got = inventory(root)
    if got != read(root/'versions.draft.json'):
        raise ValueError('version manifest mismatch')
    print(f"PASS: baseline {len(manifest)}/{len(manifest)}, draft cartridges {len(got['cartridges'])}, test-only {len(got['samples'])}")
    print('PUBLICATION: NOT_APPROVED; no deploy')

if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--init-version-lock', action='store_true', help='Create draft version lock once; refuses overwrite')
    args = ap.parse_args()
    if args.init_version_lock:
        with (ROOT/'versions.draft.json').open('x', encoding='utf-8') as f:
            json.dump(inventory(ROOT), f, ensure_ascii=False, indent=2); f.write('\n')
    verify(ROOT)
