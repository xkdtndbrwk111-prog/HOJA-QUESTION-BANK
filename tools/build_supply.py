"""Build local-only trial catalog from exact QB2 bank, never publish draft data."""
import argparse, base64, hashlib, json, re, shutil, xml.etree.ElementTree as ET
from pathlib import Path
from PIL import Image
from convert import validate, asset, unit
from verify_repository import cartridge_version, checked, verify
ROOT=Path(__file__).resolve().parents[1]
IDS=['eng6-ham-u10-gen','math5-fractions-demo','legacy-c1403d6ac0502c']
MAX_ASSET=131072
NS='{http://www.w3.org/2000/svg}'
def require(condition,msg):
 if not condition: raise ValueError(msg)
def digest(data): return hashlib.sha256(data).hexdigest()
def read(p): return json.loads(p.read_text(encoding='utf-8'))
def dump(p,x): p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
# Intentionally narrow SVG profile: static primitive fills/strokes only. No references, CSS, links, text or embedded images.
TAGS={'svg':{'width','height','viewBox'}, 'g':set(), 'rect':{'x','y','width','height','rx','ry'},'circle':{'cx','cy','r'},'ellipse':{'cx','cy','rx','ry'},'line':{'x1','y1','x2','y2'},'polygon':{'points'},'polyline':{'points'},'path':{'d'}}
COMMON={'fill','stroke','stroke-width','stroke-linecap','stroke-linejoin','opacity','fill-opacity','stroke-opacity'}
NUM=re.compile(r'-?(?:\d+(?:\.\d+)?|\.\d+)')
def svg_check(data):
 text=data.decode('utf-8',errors='strict');require(not re.search(r'<!|<\?',text),'SVG markup declaration disabled')
 root=ET.fromstring(text);require(root.tag==NS+'svg','SVG root');require(len(list(root.iter()))<=256,'SVG node limit')
 for i,e in enumerate(root.iter()):
  require(e.tag.startswith(NS),'SVG namespace');tag=e.tag[len(NS):];require(tag in TAGS and (tag!='svg' or i==0),'SVG tag '+tag)
  require(not (e.text or '').strip() and not (e.tail or '').strip(),'SVG text disabled')
  for k,v in e.attrib.items():
   require(k in TAGS[tag]|COMMON and len(v)<=8192,'SVG attribute '+k)
   if k in ('fill','stroke'):require(re.fullmatch(r'#[0-9a-fA-F]{3,8}|none|black|white',v),'SVG paint')
   elif k in ('stroke-linecap','stroke-linejoin'):require(v in ('butt','round','square','miter','bevel'),'SVG stroke style')
   elif k=='d':require(re.fullmatch(r'[MmZzLlHhVvCcSsQqTtAa0-9.,\s+\-]+',v),'SVG path')
   elif k in ('viewBox','points'):require(re.fullmatch(r'[-+0-9.,\s]+',v),'SVG number list')
   else:require(NUM.fullmatch(v) and abs(float(v))<=4096,'SVG numeric attribute')
 for k in ['width','height']:require(k in root.attrib and 1<=float(root.attrib[k])<=2048,'SVG dimensions')
 return True
def image_check(p):
 data=p.read_bytes();require(0<len(data)<=MAX_ASSET,'asset byte limit')
 if p.suffix=='.svg':svg_check(data)
 elif p.suffix=='.webp':
  require(data[:4]==b'RIFF' and data[8:12]==b'WEBP','WebP signature')
  with Image.open(p) as im:
   require(im.format=='WEBP' and not getattr(im,'is_animated',False) and 1<=im.width<=2048 and 1<=im.height<=2048,'WebP format/dimensions');im.load()
 else:raise ValueError('unsupported image')
def check_tokens(text):
 m=re.sub(r'\[\[(?:frac:\d+/([1-9]\d*)|mixed:\d+:\d+/([1-9]\d*))\]\]','',text)
 require(not re.search(r'\[\[(?:frac|mixed):',m),'invalid fraction token')
def validate_content(q):
 blocks=q['content']+[b for c in q.get('choices',[]) for b in c['content']]
 require(len(blocks)<=64,'too many blocks')
 for b in blocks:
  if b['kind']=='text':require(len(b['text'])<=4000,'text limit');check_tokens(b['text'])
  if b['kind']=='frequency':require(1<=len(b['labels'])<=31 and len(b['marks'])==len(b['labels']),'frequency limit')
  if b['kind']=='dialogue':
   require(len(b['lines'])<=20,'dialogue limit')
   for l in b['lines']:require(len(l['speaker'])<=100 and len(l['text'])<=2000,'dialogue length');check_tokens(l['text'])
 if q['type']=='SHORT':check_tokens(q['answer']['text'])
def build(bank,out):
 verify(bank);lock=read(bank/'versions.draft.json');byid={x['id']:x for x in lock['cartridges']+lock['samples']};entries=[];total=set();assets=set();count=0
 for cid in IDS:
  v=byid[cid];require(v['status'] in ('test_only','held_for_review'),'unexpected publication');p=checked(bank,v['path']);folder=p.parent;require(cartridge_version(folder)=={k:v[k] for k in ('id','version','files')},'version mismatch');q=read(p);qa=validate(q,folder);require(not qa['issues'],'source QA issues');require(len(q['questions'])<=3000,'row limit')
  for r in q['questions']:
   validate_content(r)
   if r['type']!='SHORT':total.add((cid,*unit(r)))
  count+=len(q['questions']);entries.append({'id':cid,'version':v['version'],'status':v['status'],'files':v['files'],'path':'bank/'+cid+'/'})
  for rel in v['files']:
   src=checked(folder,rel)
   if rel!='cartridge.json': image_check(src);assets.add(v['files'][rel])
   dest=out/'bank'/cid/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dest)
 require(len(total)>=25,'trial selection under 25 eligible units')
 manifest={'format':'qb5-local-test.1','publication':'TEST_ONLY','name':'6-기타-QB5 통합 시험 (공개 금지)','id':'qb5-local-trial','sources':entries,'soloUnits':len(total),'questionCount':count}
 dump(out/'trial-catalog.json',manifest); print('PASS supply pack',count,'questions',len(total),'eligible units',len(assets),'unique assets');return digest((out/'trial-catalog.json').read_bytes())
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('bank',type=Path);p.add_argument('out',type=Path);a=p.parse_args();print('CATALOG_SHA256='+build(a.bank,a.out))
