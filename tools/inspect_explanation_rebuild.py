import pathlib,json,zipfile,io,collections,re
root=pathlib.Path('.')
edits={e['questionId']:e for p in root.glob('workflow/student-explanations-20261128-*.json') if p.stem.split('-')[-1] not in ('report','approval') for u in json.loads(p.read_text()).get('units',[]) for e in u['edits']}
assert len(edits)==738
def check(qs,label,k='explanation'):
    matched=[q for q in qs if q.get('questionId',q.get('id')) in edits]
    diff=[(q.get('questionId',q.get('id')),q.get(k)) for q in matched if q.get(k)!=edits[q.get('questionId',q.get('id'))]['before']]
    print(label,'count',len(matched),'different',len(diff),'examples',[(i,str(v)[:70]) for i,v in diff[:3]])
def inspect_html(s,label):
    for name,k in [('DATA_ORIGINAL','explanation'),('DATA_CONCISE','explanation'),('DATA','answerText')]:
        m=re.search(r'\bconst\s+'+name+r'\s*=\s*',s)
        if m:
            try: v=json.JSONDecoder().raw_decode(s[m.end():])[0];check(v,label+':'+name,k)
            except Exception as e: print('parse error',label,name,str(e)[:150])
for p in sorted(root.glob('approved/**/manifest.json')):
    m=json.loads(p.read_text())
    if 'social' in p.parts:continue
    if 'approvedData' in m:
        check(json.loads((p.parent/m['approvedData']).read_text()),str(p))
        inspect_html((p.parent/m['approvedPresentation']).read_text(),str(p));continue
    if 'archive' not in m:continue
    with zipfile.ZipFile(p.parent/m['archive']) as z:
        ap=json.loads(z.read('release/approval.json'))
        if 'effective/cartridge.json' in z.namelist():
            check(json.loads(z.read('effective/cartridge.json'))['questions'],str(p))
            if 'display/presentation.json' in z.namelist():print('display overlay',str(p))
            v=m.get('reviewedPresentation')
            if v: inspect_html((root/v).read_text() if v.startswith('approved/') else z.read(v).decode(),v)
        else:
            print('bundle display',ap.get('display'),'approval unit keys',list(ap['units'][0]))
            for u in ap['units']:
                n=next(n for n in z.namelist() if n.endswith('/'+u['archive']))
                with zipfile.ZipFile(io.BytesIO(z.read(n))) as q:
                    check(json.loads(q.read('cartridge.json'))['questions'],n)
                    v=json.loads(q.read('version.json'));print('version keys',list(v),'files value',list(v['files'].items())[:1])
            inspect_html(z.read(ap['display']).decode(),ap['display'])
        for name in ('release/file-manifest.json','release/FILES_SHA256.json','SHA256SUMS.json'):
            if name in z.namelist():
                t=json.loads(z.read(name));t=t.get('files',t); print('table',name,list(t.items())[:1])
