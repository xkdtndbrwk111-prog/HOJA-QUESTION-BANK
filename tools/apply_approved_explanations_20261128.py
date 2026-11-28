#!/usr/bin/env python3
"""Apply the teacher-approved 738 explanation replacements only. Run on a clean release branch."""
import collections, copy, hashlib, io, json, pathlib, re, subprocess, zipfile
R=pathlib.Path('.')
def read(p): return json.loads(p.read_bytes())
def jb(x): return (json.dumps(x,ensure_ascii=False,indent=2)+'\n').encode()
def compact(x): return json.dumps(x,ensure_ascii=False,separators=(',',':'))
def sha(b): return hashlib.sha256(b).hexdigest()
def blob(b): return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
def write(p,v): p.write_bytes(jb(v))
def unpack(b):
    with zipfile.ZipFile(io.BytesIO(b)) as z:
        assert z.testzip() is None and len(z.namelist())==len(set(z.namelist()))
        return {n:z.read(n) for n in z.namelist()}
def pack(d):
    out=io.BytesIO()
    with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for n,b in d.items():
            i=zipfile.ZipInfo(n,(2026,11,28,0,0,0)); i.compress_type=zipfile.ZIP_DEFLATED
            z.writestr(i,b,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
    return out.getvalue()
approval=read(R/'workflow/student-explanations-20261128-teacher-approval.json')
assert approval['teacherApproval']=='APPROVED'
approved=approval['approvedCandidateCommit']
edits={}
for p in approval['candidateFiles']:
    raw=(R/p).read_bytes()
    assert raw==subprocess.check_output(['git','show',approved+':'+p])
    for u in json.loads(raw)['units']:
        for e in u['edits']:
            assert e['questionId'] not in edits
            edits[e['questionId']]=e
assert len(edits)==738
source_seen=collections.Counter()
view_seen=collections.Counter()
def patch(qs,field,seen):
    count=0
    for q in qs:
        k=q.get('questionId',q.get('id'))
        if k not in edits: continue
        e=edits[k]
        assert q[field]==e['before'],(k,field,'old explanation differs')
        q[field]=e['after'];seen[k]+=1;count+=1
    assert count
    return qs
def html(raw):
    s=raw.decode('utf8')
    count=0
    for name,field in [('DATA_ORIGINAL','explanation'),('DATA_CONCISE','explanation'),('DATA','answerText')]:
        m=re.search(r'\bconst\s+'+name+r'\s*=\s*',s)
        if not m:continue
        q,n=json.JSONDecoder().raw_decode(s[m.end():])
        if not isinstance(q,list) or not any(x.get('questionId',x.get('id')) in edits for x in q):continue
        patch(q,field,view_seen); count+=1
        s=s[:m.end()]+compact(q).replace('</','<\\/')+s[m.end()+n:]
    assert count in (1,2)
    return s.encode()
def update_table(d,old):
    for n in ('release/file-manifest.json','release/FILES_SHA256.json','SHA256SUMS.json'):
        if n not in d:continue
        t=json.loads(d[n]); files=t.get('files',t)
        for k,v in files.items():
            assert k in d and k!=n
            prior=v if isinstance(v,str) else v['sha256']
            assert sha(old[k])==prior,(k,'old table digest')
            if isinstance(v,str):files[k]=sha(d[k])
            else:
                v['sha256']=sha(d[k])
                if 'bytes' in v:v['bytes']=len(d[k])
        d[n]=jb(t)
def mark(a):
    a['explanationRevision']={'approvedDate':'2026-11-28','scope':'explanations only','approvalRecord':'workflow/student-explanations-20261128-teacher-approval.json','priorCandidateCommit':approved}
    return a
external={}
math_hash={}
science_hash={}
for p in sorted(R.glob('approved/**/manifest.json')):
    m=read(p)
    if 'social' in p.parts:continue
    if 'approvedData' in m:
        q=p.parent/m['approvedData'];write(q,patch(read(q),'explanation',source_seen))
        h=p.parent/m['approvedPresentation'];h.write_bytes(html(h.read_bytes()))
        m['approvedDataSHA256']=sha(q.read_bytes())
        m['approvedPresentationSHA256']=sha(h.read_bytes())
        mark(m);write(p,m);continue
    if 'archive' not in m:continue
    a=p.parent/m['archive'];oldraw=a.read_bytes()
    assert sha(oldraw)==m['archiveSha256']
    old=unpack(oldraw);d=old.copy(); ap=json.loads(d['release/approval.json'])
    if 'effective/cartridge.json' in d:
        n='effective/cartridge.json'; cart=json.loads(d[n]);patch(cart['questions'],'explanation',source_seen);d[n]=jb(cart)
        v=m.get('reviewedPresentation')
        assert v
        if v.startswith('approved/'):
            h=R/v
            if h not in external:
                original=h.read_bytes();new=html(original);h.write_bytes(new);external[h]=(sha(original),sha(new))
            prev,next_=external[h]
            if m.get('reviewedPresentationSha256'):assert m['reviewedPresentationSha256']==prev
            m['reviewedPresentationSha256']=next_
        else:
            prev=sha(d[v])
            d[v]=html(d[v]);next_=sha(d[v])
            if m.get('reviewedPresentationSha256'):assert m['reviewedPresentationSha256']==prev
            m['reviewedPresentationSha256']=next_
        for key in ('reviewedPreviewSha256','reviewedPresentationSha256','htmlSHA256'):
            if ap.get(key)==prev:ap[key]=next_
        # Any existing effective version must remain valid.
        if 'effective/version.json' in d:
            v=json.loads(d['effective/version.json'])
            for k in v['files']:
                full='effective/'+k
                assert sha(old[full])==v['files'][k]
                v['files'][k]=sha(d[full])
            v['version']=sha(json.dumps(v['files'],sort_keys=True,ensure_ascii=True,separators=(',',':')).encode())
            d['effective/version.json']=jb(v)
    else:
        # Cheonjae: authoritative nested source and approved v3 display both carry explanation text.
        for u in ap['units']:
            n=next(n for n in d if n.endswith('/'+u['archive']))
            assert sha(d[n])==u['archiveSHA256']
            nz=unpack(d[n]);cart=json.loads(nz['cartridge.json']);patch(cart['questions'],'explanation',source_seen)
            v=json.loads(nz['version.json'])
            for k,h in v['files'].items():assert sha(nz[k])==h
            nz['cartridge.json']=jb(cart)
            v['files']['cartridge.json']=sha(nz['cartridge.json'])
            v['version']=sha(json.dumps(v['files'],sort_keys=True,ensure_ascii=True,separators=(',',':')).encode())
            nz['version.json']=jb(v);d[n]=pack(nz);u['archiveSHA256']=sha(d[n])
        n=ap['display'];prev=sha(d[n])
        if ap.get('htmlSHA256'):assert ap['htmlSHA256']==prev
        d[n]=html(d[n]);ap['htmlSHA256']=sha(d[n])
    d['release/approval.json']=jb(mark(ap))
    update_table(d,old)
    new=pack(d);a.write_bytes(new)
    m['archiveSha256']=sha(new);m['archiveBytes']=len(new);m['gitBlobSha']=blob(new)
    mark(m);write(p,m)
    if 'math' in p.parts:math_hash[m['id']]=m['archiveSha256']
    if 'science' in p.parts:science_hash[m['id']]=(sha(oldraw),sha(new))
    print('REBUILT',str(p),m['archiveSha256'])
assert source_seen==collections.Counter({k:1 for k in edits}),source_seen
assert all(view_seen[k]==(1 if '-ham-' in k else 2) for k in edits),view_seen
p=R/'approved/math/manifest.json';m=read(p)
for u in m['units']:u['sha256']=math_hash[u['id']]
m['reviewerSha256']=external[R/m['reviewer']][1];mark(m);write(p,m)
# Handoff checker intentionally pins exact science bytes. Update only old pins, not the check.
p=R/'tools/verify_handoff.py';s=p.read_text()
for old,new in science_hash.values():
    assert s.count(old)==1
    s=s.replace(old,new)
p.write_text(s)
# Update exact archive digest records in checkpoint only where they reference the old science bytes.
p=R/'workflow/state.json';s=p.read_text()
for old,new in science_hash.values():s=s.replace(old,new)
p.write_text(s)
print('SOURCE_AND_PRESENTATION_PASS',len(source_seen),sum(view_seen.values()))
