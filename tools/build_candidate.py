"""Offline QB1/QB5 candidate builder. Never uploads, publishes, or certifies semantics."""
import argparse, json, re, zipfile, hashlib, unicodedata
from collections import Counter
from pathlib import Path
from convert import validate, unit, load
from verify_repository import checked, cartridge_version
from build_supply import image_check, validate_content, check_tokens


def need(x, msg):
    if not x: raise ValueError(msg)
def read(root, name): return load(checked(root, name))
def nonempty(x): return isinstance(x,str) and bool(x.strip())
def index(items, key):
    need(isinstance(items,list),key+' list required')
    out={}
    for item in items:
        k=item[key]; need(nonempty(k) and k not in out,'duplicate/empty '+key); out[k]=item
    return out
def distinct_list(xs): return isinstance(xs,list) and len(xs)==len(set(xs))
def norm(s): return unicodedata.normalize('NFC',s).strip().casefold()
def sem_blocks(bs):
    return json.dumps([{k:(norm(v) if isinstance(v,str) and k=='text' else v) for k,v in b.items() if k!='alt'} for b in bs],sort_keys=True,ensure_ascii=False)

def technical(root):
    b=read(root,'cartridge.json'); report=validate(b,root); need(not report['issues'],str(report['issues'])); need(len(b['questions'])<=3000,'row limit')
    qids=index(b['questions'],'questionId'); seen={}; refs={}; sizes={}
    for q in qids.values():
        validate_content(q)
        if 'explanation' in q: check_tokens(q['explanation'])
        if q['type']=='SHORT':
            need(nonempty(q['answer']['text']) and all('[[' not in a and nonempty(a) for a in [q['answer']['text'],*q.get('acceptedAnswers',[])]),'SHORT plain answer')
        if q['type']=='MCQ':
            need(len({sem_blocks(c['content']) for c in q['choices']})==4,'normalized duplicate choice '+q['questionId'])
        # Exact prompts of same type in distinct units require review; avoid obvious padding.
        sig=(q['type'],sem_blocks(q['content']))
        need(sig not in seen or seen[sig]==unit(q),'identical prompt split across units: '+q['questionId']); seen[sig]=unit(q)
        for block in q['content']+[x for c in q.get('choices',[]) for x in c['content']]:
            if block['kind']=='image': refs.setdefault(block['src'],set()).add(q['questionId'])
    for path in refs:
        p=checked(root,path); image_check(p); sizes[path]=p.stat().st_size
    report.update(assetBytes=sizes,averageAssetBytes=(sum(sizes.values())/len(sizes) if sizes else 0),imageBudgetWarnings=[p for p,n in sizes.items() if n>20000],independentUnits=sum(n==1 for n in Counter(unit(q) for q in b['questions']).values()),variantUnits=sum(n>1 for n in Counter(unit(q) for q in b['questions']).values()))
    return b,qids,refs,report

def plan(root,qids,refs,report):
    um=read(root,'unit-map.json'); units=index(um['units'],'id'); need(um['currentUnit'] in units,'current unit missing'); need(nonempty(um['source']['id']),'source ID'); need(nonempty(units[um['currentUnit']]['title']),'unit title')
    cs=index(read(root,'candidates.json'),'id'); intents=index(read(root,'learning-intents.json'),'id'); bp=index(read(root,'question-blueprint.json'),'unitId')
    covered=set(); active=set()
    for c in cs.values(): need(all(nonempty(c.get(k)) for k in ('focus','evidence','locator')),'candidate evidence')
    for i in intents.values():
        need(i['status'] in ('KEEP','MERGED','REVIEW','DROP'),'intent status'); need(nonempty(i.get('focus')) and nonempty(i.get('reason')),'intent reason')
        ids=i['candidateIds']; need(distinct_list(ids) and ids and set(ids)<=cs.keys(),'invalid candidate link'); covered.update(ids)
        if i['status'] in ('KEEP','MERGED'):active.add(i['id'])
    need(covered==cs.keys(),'candidate silently lost'); seen_q=set(); seen_u=set(); used=set()
    for p in bp.values():
        ids=p['questionIds']; ii=p['intentIds']; need(distinct_list(ids) and ids and set(ids)<=qids.keys(),'invalid blueprint question link'); need(distinct_list(ii) and ii and set(ii)<=active,'unapproved intent or missing link'); need(not seen_q.intersection(ids),'question repeated in blueprint'); seen_q.update(ids); used.update(ii)
        us={unit(qids[x]) for x in ids}; need(len(us)==1,'blueprint splits actual unit'); u=next(iter(us)); need(u not in seen_u,'unit repeated in blueprint'); seen_u.add(u)
        need(all(nonempty(p.get(k)) for k in ('assessment','scenario','distinctReason')) and p['scenarioKind'] in ('SOURCE_FACT','CREATED_SCENARIO'),'blueprint information')
    need(seen_q==qids.keys(),'question omitted from blueprint'); need(used==active,'active intent omitted')
    media=index(read(root,'media-plan.json'),'src'); need(media.keys()==refs.keys(),'missing/unused media plan')
    for path,m in media.items():
        need(set(m['questionIds'])==refs[path] and distinct_list(m['questionIds']),'incorrect media linkage');need(m['origin'] in ('generated','coded','authorized-source') and nonempty(m.get('role')) and nonempty(m.get('evidence')),'media provenance');need(m['visualCheck'] in ('PASS','HOLD','NOT_RUN'),'visual status')
        if report['assetBytes'][path]>25000:need(nonempty(m.get('budgetException')),'large image needs budgetException')
    er=read(root,'educational-review.json'); qr=index(er['questions'],'questionId'); need(qr.keys()==qids.keys(),'incomplete item review');need(er['teacherApproval']=='PENDING','teacher approval cannot be auto-set');need(nonempty(er['reviewer']),'reviewer missing');
    states={'PASS','HOLD','NOT_RUN'}
    need(er['sourceCheck'] in states and er['independenceCheck'] in states and er['gameCheck'] in states,'invalid review state')
    for item in qr.values():need(item['status'] in states and nonempty(item.get('evidence')),'item review evidence missing')
    passed=er['sourceCheck']=='PASS' and er['independenceCheck']=='PASS' and all(x['status']=='PASS' for x in qr.values()) and all(x['visualCheck']=='PASS' for x in media.values()) and all(i['status']!='REVIEW' for i in intents.values())
    return {'candidateCount':len(cs),'intentCount':len(intents),'activeIntents':len(active),'blueprintUnits':len(bp),'educationalRecordGate':passed,'reviewStatusCounts':dict(Counter(x['status'] for x in qr.values())),'gameCheckReported':er['gameCheck'],'teacherApproval':'PENDING'}

def remaster(root,b,qids,base):
    mp=read(root,'remaster-map.json'); old=read(base,'cartridge.json'); ver=cartridge_version(base)
    need(mp['baseCartridgeId']==b['cartridgeId']==old['cartridgeId'] and mp['baseRevision']==old['revision'] and b['revision']>old['revision'] and mp['baseVersion']==ver['version'],'base identity/version mismatch')
    prev=index(old['questions'],'questionId'); rows=index(mp['oldQuestions'],'oldQuestionId'); need(prev.keys()==rows.keys(),'old question inventory missing'); used=set()
    for id,e in rows.items():
        n=e['newQuestionIds']; action=e['action'];need(distinct_list(n) and set(n)<=qids.keys() and nonempty(e.get('reason')),'remaster map row');need(action in ('KEEP','IMPROVE','REBUILD','REMOVE'),'unknown action');need(bool(n)==(action!='REMOVE'),'bad removal');need(not used.intersection(n),'duplicate remaster target');used.update(n)
        if action=='KEEP':need(n==[id] and prev[id]==qids[id],'KEEP changed content')
        if action=='IMPROVE':need(n==[id],'IMPROVE must retain ID; changed intent must REBUILD')
        if action=='REBUILD':need(not set(n).intersection(prev),'REBUILD reused old ID')
    new=mp['newQuestionIds'];need(distinct_list(new) and not set(new).intersection(prev) and not set(new).intersection(used) and used|set(new)==qids.keys(),'incorrect new ID coverage')

def build(root,out,demo=False,base=None,rc3_review=False,rc4=False):
    root=Path(root);out=Path(out);need(out.suffix=='.zip' and not out.exists(),'new ZIP destination required');b,qids,refs,qa=technical(root);qa.update(plan(root,qids,refs,qa))
    need(b['reviewStatus']=='pending','publication state');need(demo or qa['minimum25'],'minimum 25 MCQ/OX units');need(demo or qa['educationalRecordGate'],'education/visual review HOLD')
    if rc4:
        from classification_rc4 import check
        qa.update(check(b,read(root,'unit-map.json')))
        rc3_review=True
    files=['unit-map.json','candidates.json','learning-intents.json','question-blueprint.json','media-plan.json','educational-review.json']
    if (root/'remaster-map.json').exists() or base is not None:
        need(base is not None,'REMASTER requires --base');remaster(root,b,qids,Path(base));files.append('remaster-map.json')
    if rc3_review:
        from review_rc3 import audit
        qa.update(audit(root,b,refs,base))
        need(demo or qa['rc3RecordGate'],'RC3 review HOLD')
        files.append('rc3-review.json')
    qa.update(publication='NOT_APPROVED',packageKind='DEMO_ONLY' if demo else 'CANDIDATE_ONLY',gameCompatibility='NOT_CERTIFIED',structuralGate=qa['minimum25'] and not qa['issues'])
    ver=cartridge_version(root);dump=lambda x:json.dumps(x,ensure_ascii=False,indent=2)+'\n'
    with zipfile.ZipFile(out,'x',zipfile.ZIP_DEFLATED) as z:
        for p in ver['files']:z.write(checked(root,p),p)
        for p in files:z.write(checked(root,p),'review/'+p)
        z.writestr('qa.json',dump(qa));z.writestr('version.json',dump(ver))
    with zipfile.ZipFile(out) as z:need(z.testzip() is None,'ZIP corruption')
    print(dump(qa));return qa

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('work');p.add_argument('output');p.add_argument('--demo',action='store_true');p.add_argument('--base',help='immutable original canonical directory for remaster')
    p.add_argument('--rc3-review',action='store_true',help='RC3 required review record gate; omit only for legacy regression')
    p.add_argument('--rc4',action='store_true',help='RC4 classification and RC3 review required');a=p.parse_args();build(a.work,a.output,a.demo,a.base,a.rc3_review,a.rc4)
