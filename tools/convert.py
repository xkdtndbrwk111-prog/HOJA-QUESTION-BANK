"""QB1 candidate: offline, no network or publication side effects."""
import json, hashlib, re, shutil, argparse
from pathlib import Path, PurePosixPath
from collections import Counter
from copy import deepcopy
from fractions import Fraction
import jsonschema
ROOT=Path(__file__).resolve().parents[1]
SCHEMA=json.loads((ROOT/'schemas/cartridge.schema.json').read_text())
def load(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def save(p,obj):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def require(v,msg):
 if not v:raise ValueError(msg)
def asset(src):
 require(isinstance(src,str) and re.fullmatch(r'assets/[A-Za-z0-9_./-]+\.(?:webp|svg)',src) and all(x not in ('.','..','') for x in src.split('/')),f'unsafe asset: {src}')
 return src
def blocks(text=None,media=None,stimulus=None):
 out=[]
 if text is not None:out.append({'kind':'text','text':text})
 for m in media or []:
  require(m.get('kind')=='image','unsupported media');out.append({'kind':'image','src':asset(m['src']),'alt':m['alt']})
 if stimulus:
  k=stimulus['kind']
  if k=='combined':
   for b in stimulus['blocks']:out.extend(blocks(stimulus=b))
  elif k in ('frequency','dialogue'):out.append(deepcopy(stimulus))
  else:raise ValueError('unsupported stimulus '+k)
 return out
def choice_blocks(c):return blocks(c) if isinstance(c,str) else blocks(c.get('text'),c.get('media'))
def convert_v1(b):
 require(b.get('schemaVersion')==1,'not skill v1')
 allowed={'id','type','text','answer','choices','explanation','source','sourceRow','media','stimulus','acceptedAnswers','layout','fractionMode','answerForm'}
 out={'schemaVersion':'qb1-draft.1','cartridgeId':b['id'],'revision':1,'title':b['title'],'metadata':{k:deepcopy(v) for k,v in b.items() if k not in ('schemaVersion','id','title','groups')},'reviewStatus':'pending','questions':[]}
 for g in b['groups']:
  for q in g['questions']:
   require(not(set(q)-allowed),'unhandled fields '+str(set(q)-allowed))
   t=q['type'];n={'questionId':q['id'],'type':t,'content':blocks(q['text'],q.get('media'),q.get('stimulus')),'provenance':{'inputFormat':'skill-v1','originalGroupId':g['id']}}
   if len(g['questions'])>1:n['groupId']=g['id']
   if 'sourceBundleId' in g:n['provenance']['sourceBundleId']=g['sourceBundleId']
   for k in ('source','sourceRow'): 
    if k in q:n['provenance'][k]=q[k]
   for k in ('fractionMode','answerForm','explanation','acceptedAnswers'):
    if k in q:n[k]=deepcopy(q[k])
   if t=='MCQ':
    i=q['answer'];require(type(i)==int and 0<=i<len(q['choices']),'bad 0-based index');n['choices']=[{'id':f'c{j+1}','content':choice_blocks(c)} for j,c in enumerate(q['choices'])];n['answer']={'choiceId':n['choices'][i]['id']}
   elif t=='OX':require(type(q['answer'])==bool,'bad OX');n['answer']={'value':q['answer']}
   elif t=='SHORT':n['answer']={'text':q['answer']}
   else:raise ValueError('unknown type '+t)
   out['questions'].append(n)
 return out
def convert_flat(b,title):
 require(b.get('questionSchemaVersion')==2,'not GAS/develop v2');groups={};cid=str(b['cartridgeId'])
 for q in b['questions']:
  require(not q.get('isNull'),'null row');require(q['type'] in ('MULTIPLE','OX','SUBJECTIVE'),'unknown type')
  fam=str(q['familyId']);gid=cid+':'+fam;typ={'MULTIPLE':'MCQ','OX':'OX','SUBJECTIVE':'SHORT'}[q['type']];a=q['answer'];n={'id':cid+':'+str(q['sourceNum']),'type':typ,'text':q['question']}
  if typ=='MCQ':require(isinstance(a,str) and a in ('1','2','3','4'),'bad 1-based index');n.update(choices=q['options'],answer=int(a)-1)
  elif typ=='OX':require(a in ('O','X'),'bad OX');n['answer']=a=='O'
  else:n['answer']=a
  groups.setdefault(gid,{'id':gid,'sourceBundleId':fam,'questions':[]})['questions'].append(n)
 out=convert_v1({'schemaVersion':1,'id':cid,'title':title,'sourceSheetVersion':b.get('sourceSheetVersion'),'groups':list(groups.values())})
 for q,old in zip(out['questions'], [q for g in groups.values() for q in g['questions']]):q['provenance']['inputFormat']='gas-v2'
 return out
def unit(q):return ('group',q['groupId']) if 'groupId' in q else ('question',q['questionId'])
def number(c):
 if len(c)!=1 or c[0]['kind']!='text':return None
 s=c[0]['text'].strip();m=re.fullmatch(r'\[\[mixed:(-?\d+):(\d+)/(\d+)\]\]',s)
 try:
  if m:
   w,n,d=map(int,m.groups());return Fraction(w)+(1 if w>=0 else -1)*Fraction(n,d)
  s=re.sub(r'^\[\[frac:([^\]]+)\]\]$',r'\1',s)
  if re.fullmatch(r'[+-]?\d+(?:/\d+|\.\d+)?',s):return Fraction(s)
 except (ValueError,ZeroDivisionError):return None
 return None
def validate(b,base=None):
 jsonschema.validate(b,SCHEMA);ids=set();issues=[];bad=set();files=set();counts=Counter()
 def issue(q,code):issues.append({'questionId':q['questionId'],'code':code});bad.add(q['questionId'])
 def scan(q,bs):
  for x in bs:
   if x['kind']=='image':
    p=asset(x['src']);files.add(p)
    if base is not None and (not (base/p).is_file() or not (base/p).resolve().is_relative_to(base.resolve())):issue(q,'missing_or_unsafe_asset')
   if x['kind']=='frequency' and len(x['marks'])!=len(x['labels']):issue(q,'frequency_length')
   if x['kind']=='text':
    for token in re.findall(r'\[\[(?:frac|mixed):[^\]]*\]\]',x['text']):
     if number([{'kind':'text','text':token}]) is None:issue(q,'invalid_fraction')
 for q in b['questions']:
  require(q['questionId'] not in ids,'duplicate questionId');ids.add(q['questionId']);counts[q['type']]+=1;scan(q,q['content'])
  if q['type']=='MCQ':
   cs=q['choices'];require(len({c['id'] for c in cs})==len(cs),'duplicate choice ID');require(q['answer']['choiceId'] in {c['id'] for c in cs},'unknown correct ID')
   signatures=[json.dumps([{k:v for k,v in x.items() if k!='alt'} for x in c['content']],sort_keys=True,ensure_ascii=False) for c in cs]
   if len(set(signatures))!=len(cs):issue(q,'duplicate_choice')
   if b['metadata'].get('subject')=='수학' and q.get('answerForm')!='representation':
    ns=[number(c['content']) for c in cs];ns=[n for n in ns if n is not None]
    if len(ns)!=len(set(ns)):issue(q,'equivalent_numeric_choice')
   for c in cs:scan(q,c['content'])
 valid=[q for q in b['questions'] if q['questionId'] not in bad];solo=len({unit(q) for q in valid if q['type'] in ('OX','MCQ')});team=len({unit(q) for q in valid});return {'questionCount':len(ids),'types':dict(counts),'soloUnits':solo,'teamUnits':team,'issues':issues,'minimum25':solo>=25,'assets':sorted(files),'structuralGate':solo>=25 and not issues,'publication':'NOT_APPROVED'}
def export_flat(b):
 """Strict legacy projection; never silently drop media or semantic stimulus."""
 out=[];order={}
 def plain(bs):require(len(bs)==1 and bs[0]['kind']=='text','rich content needs new game adapter');return bs[0]['text']
 for i,q in enumerate(b['questions'],1):
  u=unit(q);order.setdefault(u,len(order)+1);typ={'MCQ':'MULTIPLE','OX':'OX','SHORT':'SUBJECTIVE'}[q['type']];opts=[]
  if typ=='MULTIPLE':opts=[plain(c['content']) for c in q['choices']];a=str(next(i for i,c in enumerate(q['choices'],1) if c['id']==q['answer']['choiceId']))
  elif typ=='OX':opts=['O','X'];a='O' if q['answer']['value'] else 'X'
  else:a=q['answer']['text']
  out.append({'num':i,'sourceNum':i,'familyId':u[1],'familyOrder':order[u],'variantType':{'MCQ':'multiple','OX':'ox','SHORT':'subjective'}[q['type']],'type':typ,'question':plain(q['content']),'answer':a,'options':opts,'isNull':False})
 return {'questionSchemaVersion':2,'sourceSheetVersion':2,'cartridgeId':b['cartridgeId'],'questions':out}
def copy_assets(b,src,dst):
 for q in b['questions']:
  for block in q['content']+[x for c in q.get('choices',[]) for x in c['content']]:
   if block['kind']=='image':
    a=asset(block['src']);p=src/a;require(p.is_file() and p.resolve().is_relative_to(src.resolve()),'invalid source asset');d=dst/a;d.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,d)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('input',type=Path);p.add_argument('output',type=Path);p.add_argument('--format',choices=['skill','gas'],default='skill');p.add_argument('--title');p.add_argument('--asset-root',type=Path);a=p.parse_args();b=load(a.input);n=convert_v1(b) if a.format=='skill' else convert_flat(b,a.title or b['cartridgeId']);a.output.mkdir(parents=True,exist_ok=True);copy_assets(n,a.asset_root or a.input.parent.parent,a.output);r=validate(n,a.output);save(a.output/'cartridge.json',n);save(a.output/'qa.json',r);print(json.dumps(r,ensure_ascii=False))
