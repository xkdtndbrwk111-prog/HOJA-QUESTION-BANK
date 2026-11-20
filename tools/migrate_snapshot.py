"""Migrate the previously exported public-only snapshot; not a live Sheets reader."""
from convert import *
from collections import Counter
import random

def verify_roundtrip(old,new):
 f=export_flat(new); back=convert_flat(f,new['title']);
 oq=[q for g in old['groups'] for q in g['questions']]; nq=back['questions']
 require(len(oq)==len(nq),'roundtrip count')
 for o,n in zip(oq,nq):
  require(o['text']==n['content'][0]['text'] and o['type']==n['type'],'text/type lost')
  if o['type']=='MCQ':
   require([c['content'][0]['text'] for c in n['choices']]==o['choices'],'choices lost');require(n['answer']['choiceId']==f'c{o["answer"]+1}','answer shifted')
  elif o['type']=='OX':require(n['answer']['value']==o['answer'],'OX changed')
  else:require(n['answer']['text']==o['answer'],'short changed')
 require(len({unit(q) for q in new['questions']})==len({unit(q) for q in back['questions']}),'units changed')
 return len(oq)
def main(snapshot,examples,out):
 cat=load(snapshot/'catalog.json');entries=[];roundtrips=0;source_hash=digest(snapshot/'catalog.json');totals=Counter();types=Counter();problems=[];seen=set()
 for e in cat['banks']:
  if e['status']!='legacy':continue
  src=snapshot/e['path'];old=load(src);b=convert_v1(old);cid=b['cartridgeId'];require(cid not in seen,'duplicate cartridge');seen.add(cid);dest=out/'cartridges'/cid;dest.mkdir(parents=True,exist_ok=True);copy_assets(b,snapshot,dest);qa=validate(b,dest);roundtrips+=verify_roundtrip(old,b);save(dest/'cartridge.json',b);save(dest/'qa.json',qa);entry={'id':cid,'title':b['title'],'path':f'cartridges/{cid}/cartridge.json','sha256':digest(dest/'cartridge.json'),'sourceSha256':digest(src),'legacySheetName':old['sourceSheet'],'legacySheetId':None,'qa':qa,'status':'held_for_review'};entries.append(entry);totals.update(cartridges=1,questions=qa['questionCount'],soloUnits=qa['soloUnits'],teamUnits=qa['teamUnits'],structuralGatePass=int(qa['structuralGate']));types.update(qa['types']);
  if not qa['structuralGate']:problems.append({'id':cid,'title':old['sourceSheet'],'soloUnits':qa['soloUnits'],'issues':qa['issues']})
 sample=[]
 for folder in sorted(examples.iterdir()):
  srcs=list(folder.glob('questions/*.json'))
  if not srcs:continue
  src=srcs[0];b=convert_v1(load(src));dest=out/'samples'/b['cartridgeId'];dest.mkdir(parents=True,exist_ok=True);copy_assets(b,folder,dest);qa=validate(b,dest);save(dest/'cartridge.json',b);save(dest/'qa.json',qa);sample.append({'id':b['cartridgeId'],'qa':qa,'sourceSha256':digest(src)})
 save(out/'catalog.draft.json',{'schemaVersion':'qb1-draft.1','publication':'NOT_APPROVED','cartridges':entries});save(out/'migration-report.json',{'scope':'prior exported public snapshot, NOT live Sheets; all entries held for review','sourceCatalogSha256':source_hash,'totals':dict(totals),'types':dict(types),'roundtripQuestions':roundtrips,'heldStructural':problems,'samples':sample});print(json.dumps(load(out/'migration-report.json'),ensure_ascii=False,indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('snapshot',type=Path);p.add_argument('examples',type=Path);p.add_argument('out',type=Path);a=p.parse_args();main(a.snapshot,a.examples,a.out)
