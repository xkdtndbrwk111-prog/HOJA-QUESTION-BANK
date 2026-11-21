import asyncio,json,hashlib
from pathlib import Path
from playwright.async_api import async_playwright
R=Path('/mnt/data')
files={'v04':next(R.glob('HOJA_YBM_*v0.4*')),'v05':next(R.glob('HOJA_YBM_*v0.5*'))}
JAVASCRIPT='''async()=>{
 const rq=()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));
 const badNode=e=>e&&e.scrollHeight>e.clientHeight+10;
 const issues=[],dialogue=[];let boosted=0;
 for(const q of DATA_CONCISE){
  state.unit=q.unit;state.question=q.id;state.layout=defaultLayout(q);state.composition='auto';state.removed=null;renderQuestion();await rq();
  const stim=document.getElementById('hqStimulus'),card=document.getElementById('hqCard'),rows=[...stim.querySelectorAll('.stim-dialogue-row')],choices=[...document.querySelectorAll('.hqChoice')];
  const nameOverlap=rows.some(row=>{const s=row.querySelector('.stim-speaker'),t=row.querySelector('.stim-text');if(!s||!t)return false;const a=s.getBoundingClientRect(),b=t.getBoundingClientRect();return a.right>b.left+3&&a.bottom>b.top+3&&a.top<b.bottom-3});
  const turnsOverlap=rows.some((row,i)=>i>0&&row.getBoundingClientRect().top<rows[i-1].getBoundingClientRect().bottom-3);
  const optionOverflow=choices.some(ch=>badNode(ch.querySelector('.hqChoiceLabel')));
  const quoteOverflow=[...stim.querySelectorAll('.stim-quote-text')].some(badNode);
  const questionOverflow=badNode(document.getElementById('hqQuestion'));
  const imageMissing=[...card.querySelectorAll('img')].some(img=>img.complete&&img.naturalWidth===0);
  const problems={nameOverlap,turnsOverlap,optionOverflow,quoteOverflow,questionOverflow,imageMissing};
  if(Object.values(problems).some(Boolean))issues.push({id:q.id,...problems});
  if(rows.length>=2){const p=stim.getBoundingClientRect(),first=rows[0].getBoundingClientRect(),last=rows[rows.length-1].getBoundingClientRect();dialogue.push({id:q.id,delta:Math.round(Math.abs((first.top-p.top)-(p.bottom-last.bottom))),rows:rows.length})}
  if(Number(stim.dataset.autoFontBoost)>0)boosted++;
 }
 return {count:DATA_CONCISE.length,tagCount:Object.keys(HOJA_RENDER_TAGS).length,images:Object.keys(IMAGES).length,issues,dialogue,boosted,questionsJson:JSON.stringify(DATA_CONCISE)};
}'''
async def main():
 out={}
 async with async_playwright() as p:
  browser=await p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
  for version,path in files.items():
   page=await browser.new_page(viewport={'width':1700,'height':1080});errs=[];page.on('pageerror',lambda e:errs.append(str(e)))
   await page.set_content(path.read_text(),wait_until='domcontentloaded',timeout=90000)
   out[version]={}
   for res in ['1280x720','1920x1080']:
    await page.select_option('#resolution',res)
    d=await page.evaluate(JAVASCRIPT)
    digest=hashlib.sha256(d.pop('questionsJson').encode()).hexdigest()
    d['questions_sha256']=digest;d['jsErrors']=errs[:10]
    out[version][res]=d
    print(version,res,'issues',len(d['issues']),'booster',d['boosted'],'dialogue-centering-maxDelta',max((x['delta'] for x in d['dialogue']),default=0),'JS_errors',len(errs))
   await page.close()
  await browser.close()
 for res in ['1280x720','1920x1080']:
  a={x['id']:x for x in out['v04'][res]['issues']};b={x['id']:x for x in out['v05'][res]['issues']}
  print('DIFF',res,'new',sorted(set(b)-set(a)),'resolved',sorted(set(a)-set(b)),'data_integrity',out['v04'][res]['questions_sha256']==out['v05'][res]['questions_sha256'])
 (R/'HOJA_v05_전체회귀검사.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
asyncio.run(main())
