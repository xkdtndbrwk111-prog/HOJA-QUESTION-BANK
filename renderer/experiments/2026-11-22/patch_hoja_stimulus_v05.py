from pathlib import Path
P=Path('/mnt/data')
src=next(P.glob('HOJA_YBM_*v0.4*'))
out=P/'HOJA_YBM_영어5_6학년_183문항_태그자동분류_v0.5_지문확대_대화중앙정렬.html'
css='''
/* HOJA tag experiment v0.5: center the ENTIRE dialogue block, even in
 * dialogue-stack where the v0.4 generic override lost to a more specific rule.
 * Never distribute individual utterances around the panel. */
#screen #hqCard[data-composition="dialogue-stack"] #hqStimulus.stimulus-dialogue,
#screen #hqCard[data-composition="dialogue-image"] #hqStimulus.stimulus-dialogue,
#screen #hqCard[data-composition="source-split"] #hqStimulus.stimulus-dialogue,
#screen #hqStimulus.stimulus-dialogue {
  justify-content:center!important;
  align-items:stretch!important;
  align-content:center!important;
}
/* No extra tiles: compact, aligned speaker rows in one centered group. */
#screen #hqCard[data-composition="dialogue-stack"] #hqStimulus.stimulus-dialogue .stim-dialogue-row,
#screen #hqCard[data-composition="dialogue-image"] #hqStimulus.stimulus-dialogue .stim-dialogue-row {
  flex:0 0 auto!important;
  align-self:stretch!important;
}
'''
js=r'''
/* HOJA v0.5 content-aware type enlargement. Called after base fit,
 * never changes questions/answers or broadens the layout families.
 * Data tags remain descriptive; all final pixel decisions use DOM geometry. */
function hojaEnhanceStimulusTypography(){
 const panel=$('hqStimulus');
 if(!panel || panel.hidden || panel.clientHeight<30)return;
 const dialogue=panel.classList.contains('stimulus-dialogue');
 const u=Number(state.res.split('x')[1])/720;
 const initial=Number.parseFloat(panel.style.fontSize) || 27*u;
 const cap=(dialogue?49:68)*u;
 const step=Math.max(1,2*u);
 const targets=[...panel.querySelectorAll('.stim-quote-text,.stim-dialogue-row .stim-text,.stim-row .stim-text')];
 if(!targets.length)return;
 function fits(){
  const outer=panel.getBoundingClientRect();
  if(panel.scrollHeight>panel.clientHeight+3*u || panel.scrollWidth>panel.clientWidth+3*u)return false;
  const margin=3*u;
  for(const el of targets){
   const r=el.getBoundingClientRect();
   if(r.left<outer.left-margin || r.right>outer.right+margin || r.top<outer.top-margin || r.bottom>outer.bottom+margin)return false;
   if(el.scrollHeight>el.clientHeight+4*u || el.scrollWidth>el.clientWidth+4*u)return false;
   // The glyph-run can exceed the CSS line box in tightly set fonts.
   if(el.textContent?.trim()){
    const range=document.createRange(); range.selectNodeContents(el);
    for(const g of range.getClientRects()){
     if(g.left<outer.left-margin || g.right>outer.right+margin || g.top<outer.top-margin || g.bottom>outer.bottom+margin)return false;
    }
   }
  }
  return true;
 }
 let best=initial;
 for(let n=initial+step; n<=cap+0.1; n+=step){
  panel.style.fontSize=n+'px';
  if(dialogue)hojaSyncDialogueSpeakerWidth();
  if(!fits())break;
  best=n;
 }
 panel.style.fontSize=best+'px';
 if(dialogue)hojaSyncDialogueSpeakerWidth();
 panel.dataset.autoFontBoost=String(Math.round((best-initial)/u));
}
'''
s=src.read_text()
assert 'function hojaEnhanceStimulusTypography' not in s
assert '</style><!-- source CARTRIDGES' in s
s=s.replace('</style><!-- source CARTRIDGES',css+'\n</style><!-- source CARTRIDGES',1)
s=s.replace('function measureAndFit(){',js+'\nfunction measureAndFit(){',1)
needle='const imgEl=[...media.querySelectorAll(\'img\')];'
assert needle in s
s=s.replace(needle,"hojaEnhanceStimulusTypography();\nstimPx=Math.round((parseFloat(stimulus.style.fontSize)||0)/u);stimOk=fitsStimulus();\n"+needle,1)
s=s.replace('태그 자동 분류 실험 · v0.4</label>','태그 자동 분류 실험 · v0.5</label>',1)
s=s.replace('태그 검토실 · v0.4','태그 검토실 · v0.5',1)
out.write_text(s)
print(out,out.stat().st_size)
