"""Private repository catalog/registration. No network, no runtime publication.
Usage: python tools/register_cartridge.py catalog [--verify]
       python tools/register_cartridge.py register CANDIDATE.zip APPROVAL.json [--base DIR]
Approval is a human-maintained record, not automatically granted by this program.
New entries only; revisions require explicit reviewed migration, never silent overwrite.
"""
import argparse,hashlib,json,re,shutil,tempfile,zipfile,os
from pathlib import Path
from classification_rc4 import check,key,require
from verify_repository import cartridge_version,checked,sha,verify as verify_baseline,read
from build_candidate import build,technical
ROOT=Path(__file__).resolve().parents[1]
def dump(p,x):
    p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def fields(b):
    return {k:b['metadata'].get(k) for k in ('curriculum','grade','semester','subject','publisher','leadAuthor','edition','unitNumber','unitTitle')}
def entry(root,p):
    require(not p.is_symlink(),'symlink directory');b,_,refs,qa=technical(p);v=cartridge_version(p)
    require(p.name==b['cartridgeId'] and re.fullmatch('[a-z0-9][a-z0-9-]{1,79}',p.name),'invalid cartridge folder ID')
    require(v==read(p/'version.json'),'version lock mismatch');check(b,read(p/'review/unit-map.json'))
    a=read(p/'approval.json');q=read(p/'qa.json')
    require(a['cartridgeId']==v['id'] and a['version']==v['version'] and a['revision']==b['revision'],'approval version mismatch')
    require(a['teacherApproval']=='APPROVED' and a['deliveryStatus']=='HOLD' and isinstance(a.get('evidence'),str) and bool(a['evidence'].strip()),'approval/hold evidence required')
    require(q['publication']=='NOT_APPROVED' and q['gameCompatibility']=='NOT_CERTIFIED' and q['structuralGate'] and q['minimum25'] and not q['issues'] and qa['minimum25'],'invalid candidate status')
    require(all(q[k]==qa[k] for k in ('questionCount','soloUnits','teamUnits','types','assets','assetBytes')),'QA counts mismatch')
    if a.get('approvedContentRevision') is not None:
        # Historical approval carried only when all content and media bytes match previously approved version.
        olddir=p/'history'/('rev'+str(a['approvedContentRevision']));old=read(checked(p,olddir.relative_to(p).as_posix()+'/cartridge.json'));ov=read(checked(p,olddir.relative_to(p).as_posix()+'/version.json'))
        require(old['questions']==b['questions'] and old['cartridgeId']==b['cartridgeId'] and old['revision']==a['approvedContentRevision']<b['revision'],'approved content changed')
        require(sha(olddir/'cartridge.json')==ov['files']['cartridge.json'],'historical cartridge hash mismatch')
        require(ov['version']==a['approvedContentVersion']==hashlib.sha256(json.dumps(ov['files'],sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest(),'historical version hash mismatch')
        require({k:h for k,h in ov['files'].items() if k!='cartridge.json'}=={k:h for k,h in v['files'].items() if k!='cartridge.json'},'approved media changed')
    else:
        require(q.get('classificationRecordGate') is True and q.get('rc3RecordGate') is True,'RC4 gate required')
    return {'id':v['id'],'path':(p/'cartridge.json').relative_to(root).as_posix(),'version':v['version'],'revision':b['revision'],'title':b['title'],'classification':fields(b),'classificationStatus':'declared_verified_structure','teacherApproval':'APPROVED','deliveryStatus':'HOLD','questionCount':qa['questionCount'],'soloUnits':qa['soloUnits'],'supersedesLegacyId':a.get('supersedesLegacyId')},key(b)
def catalog(root):
    old=read(root/'catalog.draft.json');held=[];ids=set();keys=set();approved=[]
    for x in old['cartridges']:
        p=checked(root,x['path']);require(sha(p)==x['sha256'],'legacy changed');b=read(p);require(b['cartridgeId']==x['id'] and x['id'] not in ids,'legacy ID mismatch');ids.add(x['id'])
        held.append({'id':x['id'],'title':x['title'],'path':x['path'],'classification':fields(b),'sourceSheet':x.get('legacySheetName'),'classificationStatus':'legacy_needs_review','teacherApproval':'PENDING','deliveryStatus':'HOLD','questionCount':x['qa']['questionCount'],'soloUnits':x['qa']['soloUnits']})
    legacy_ids=set(ids);linked=set()
    for p in sorted((root/'cartridges').iterdir()):
        if p.name in legacy_ids:continue
        require(p.is_dir(),'unexpected cartridge entry');item,k=entry(root,p);require(item['id'] not in ids and k not in keys,'duplicate ID or classification key');ids.add(item['id']);keys.add(k)
        oldid=item['supersedesLegacyId']
        if oldid is not None:
            require(oldid in legacy_ids and oldid not in linked,'invalid legacy replacement link');linked.add(oldid)
        approved.append(item)
    for h in held:
        if h['id'] in linked:h['supersededBy']=next(x['id'] for x in approved if x['supersedesLegacyId']==h['id'])
    approved.sort(key=lambda x:(x['classification']['grade'],x['classification']['semester'],x['classification']['subject'],x['classification']['publisher'] or '',x['classification']['leadAuthor'] or '',x['classification']['unitNumber'],x['classification']['curriculum']))
    return {'schemaVersion':'hoja-catalog.1','publication':'NOT_APPROVED','deliveryStatus':'HOLD','approvedCount':len(approved),'legacyHeldCount':len(held),'cartridges':approved,'legacyHeld':held}
def write_catalog(root):
    got=catalog(root);p=root/'catalog.json';tmp=root/'catalog.json.tmp';dump(tmp,got);os.replace(tmp,p);return got

def unpack(zpath,d):
    with zipfile.ZipFile(zpath) as z:
        infos=z.infolist();names=[i.filename for i in infos]
        require(len(names)==len(set(names)) and len(names)<=500 and sum(i.file_size for i in infos)<=32*1024*1024,'ZIP size or duplicates')
        require(z.testzip() is None,'bad ZIP');v=json.loads(z.read('version.json'));expected=set(v['files'])|{'qa.json','version.json'}
        for i in infos:
            n=i.filename;require(not i.is_dir() and ((i.external_attr>>16)&0o170000)!=0o120000 and not '\\' in n and all(t not in ('','.','..') for t in n.split('/')),'unsafe ZIP entry')
            require(n in expected or re.fullmatch(r'review/(?:unit-map|candidates|learning-intents|question-blueprint|media-plan|educational-review|remaster-map|rc3-review)\.json',n),'unexpected ZIP entry')
            out=d/n;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(z.read(i))
        require(expected<=set(names),'missing ZIP entries')
    require(cartridge_version(d)==v,'candidate hash mismatch')
def register(root,zpath,approval,base=None):
    verify_baseline(root)
    with tempfile.TemporaryDirectory(dir=root) as t:
        tmp=Path(t);p=tmp/'candidate';p.mkdir();unpack(zpath,p);b=read(p/'cartridge.json');v=read(p/'version.json');cid=b['cartridgeId'];require(re.fullmatch('[a-z0-9][a-z0-9-]{1,79}',cid),'bad ID')
        dest=root/'cartridges'/cid;require(not dest.exists(),'ID already exists; do not overwrite')
        work=tmp/'work';shutil.copytree(p,work)
        for f in (work/'review').glob('*.json'):shutil.copy2(f,work/f.name)
        out=tmp/'rebuilt.zip';build(work,out,base=base,rc4=True)
        with zipfile.ZipFile(out) as a,zipfile.ZipFile(zpath) as z:
            require(set(a.namelist())==set(z.namelist()) and all(a.read(n)==z.read(n) for n in a.namelist()),'independent RC4 rebuild differs')
        require(approval.is_file(),'approval needed');a=read(approval);require('approvedContentRevision' not in a,'historical approval migration uses separate audited workflow');dump(p/'approval.json',a)
        # validate staged directory under correct name before touching repository
        staged=tmp/cid;p.rename(staged);new,k=entry(tmp,staged)
        current=catalog(root);require(not any(key(read(root/x['path']))==k for x in current['cartridges']),'duplicate classification key')
        shutil.move(staged,dest)
        try:write_catalog(root)
        except Exception:shutil.rmtree(dest);raise
    print('REGISTERED locally; delivery HOLD',cid,v['version'])
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);s=p.add_subparsers(dest='cmd',required=True);c=s.add_parser('catalog');c.add_argument('--verify',action='store_true');r=s.add_parser('register');r.add_argument('candidate',type=Path);r.add_argument('approval',type=Path);r.add_argument('--base',type=Path);a=p.parse_args()
    if a.cmd=='catalog':
        verify_baseline(ROOT);got=catalog(ROOT)
        if a.verify:require(got==read(ROOT/'catalog.json'),'catalog not current')
        else:write_catalog(ROOT)
        print('PASS: approved',got['approvedCount'],'legacy held',got['legacyHeldCount'],'delivery HOLD')
    else:register(ROOT,a.candidate,a.approval,a.base)
