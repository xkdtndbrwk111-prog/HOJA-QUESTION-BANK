from __future__ import annotations
import json,re,hashlib,collections,zipfile,html
from pathlib import Path

ROOT=Path('/mnt/data')
BASE=ROOT/'HOJA_YBM_영어5_6학년_10_11_12단원_183문항_통합검토_v9.html'
raw=BASE.read_text(encoding='utf-8')
match=re.search(r'const DATA_CONCISE=(\[.*?\]);\nconst DATA_ORIGINAL=',raw,re.S)
assert match,'source data not found'
questions=json.loads(match.group(1))
assert len(questions)==183 and len({q['id'] for q in questions})==183
units=collections.Counter(q['unit'] for q in questions)
assert units=={'g5u10':30,'g5u11':33,'g5u12':29,'g6u10':30,'g6u11':29,'g6u12':32}

SPEC={
 '$schema':'https://json-schema.org/draft/2020-12/schema',
 'title':'HOJA Render Tags - Question annotation v0.1 draft',
 'description':'Non-destructive annotation layer for the question bank. Tags describe meaning and relative salience; runtime decides geometry. No approval or production compatibility implied.',
 'type':'object','additionalProperties':False,
 'required':['schemaVersion','questionId','questionType','images','texts','constraints','layout','confidence','needsHumanReview','evidence'],
 'properties':{
  'schemaVersion':{'const':'0.1.0-draft'},
  'questionId':{'type':'string','minLength':1},
  'questionType':{'enum':['MCQ','OX','SHORT']},
  'images':{'type':'array','items':{'type':'object','additionalProperties':False,'required':['asset','position','kind','subtype','needsFineDetail','priority'], 'properties':{
    'asset':{'type':'string'},'position':{'enum':['question','choice']},'kind':{'enum':['general','informational','chart','geometry']},'subtype':{'enum':['scene','object','map','wayfinding','location','graph','table','timeline','shape','scientific_diagram','other']},'needsFineDetail':{'type':'boolean'},'priority':{'enum':['normal','high']}
   }}},
  'texts':{'type':'array','uniqueItems':True,'items':{'enum':['question','instruction','dialogue','reading','example_sentence','list','choices']}},
  'constraints':{'type':'object','additionalProperties':False,'required':['speakerTurnsVertical','preserveOriginalText','minimumImageDetail','elementPriority'], 'properties':{
   'speakerTurnsVertical':{'type':'boolean'},'preserveOriginalText':{'const':True},'minimumImageDetail':{'enum':['normal','high']},
   'elementPriority':{'type':'object','additionalProperties':False,'required':['question','reading','dialogue','image','choices'], 'properties':{k:{'enum':['low','medium','high']} for k in ['question','reading','dialogue','image','choices']}}
  }},
  'layout':{'type':'object','additionalProperties':False,'required':['recommendedFamily','rendererHint','selectionBasis'], 'properties':{
    'recommendedFamily':{'enum':['text_auto','text_stack','reading_stack','dialogue_stack','informational_split','dialogue_informational','picture_sentence','scene_auto','visual_choices']},
    'rendererHint':{'type':['string','null'],'enum':[None,'stack','reading-stack','dialogue-stack','map','dialogue-image','picture-stimulus','split']},
    'selectionBasis':{'type':'string'},'teacherPreference':{'type':['string','null']}
  }},
  'confidence':{'enum':['high','medium','low']},'needsHumanReview':{'type':'boolean'},'evidence':{'type':'array','items':{'type':'string'}},
  'sourceDigest':{'type':'string','description':'SHA-256 of core question JSON (not content approval)'}
 }
}

speaker_pattern=re.compile(r'(?:^|\s)(?:A|B|Kai|Gerda):\s*',re.I|re.M)
reading_cues=['다음 글','글을 읽고','다음 이야기를 읽고','이야기를 읽고','안내문을 읽고','초대장을 읽고','계절 시를 읽고','다음 시를 읽고','전기문','다음 노래','다음 두 의견','토론 주제','다음 새해 계획','다음 생일','읽고','읽은 후']

TEACHER_OVERRIDE={'g5u11:q12': 'stack', **{f'g5u12:q{x:02d}':'reading-stack' for x in range(16,22)}}

def annotate_asset(path:str, pos:str, alt:str='') -> dict:
    n=path.lower()
    if 'map_' in n:
        kind, subtype,detail='informational','map',True
    elif 'street_directions' in n:
        kind, subtype,detail='informational','wayfinding',True
    elif 'street_next_to' in n:
        kind, subtype,detail='informational','location',True
    elif 'graph' in n or 'chart' in n:
        kind, subtype,detail='chart','graph',True
    elif 'timeline' in n or 'table' in n:
        kind, subtype,detail='chart','timeline' if 'timeline' in n else 'table',True
    elif 'angle' in n or 'polygon' in n or 'geometry' in n:
        kind, subtype,detail='geometry','shape',True
    else:
        kind, subtype,detail='general','scene' if ('어린이' in alt or '학생' in alt or '장면' in alt or '활동' in alt) else 'object',False
    return {'asset':path,'position':pos,'kind':kind,'subtype':subtype,'needsFineDetail':detail,'priority':'high' if detail else 'normal'}

def classify(q):
    prompt=q['prompt']
    lines=[x.strip() for x in prompt.split('\n') if x.strip()]
    rest='\n'.join(lines[1:])
    first=lines[0] if lines else ''
    imgs=[]
    if q.get('image'):
        imgs.append(annotate_asset(q['image'],'question',q.get('imageAlt') or ''))
    for ch in q.get('choices',[]):
        if ch.get('image'):imgs.append(annotate_asset(ch['image'],'choice',ch.get('imageAlt') or ''))
    has_illustration=bool(imgs)
    image_primary=next((im for im in imgs if im['position']=='question'),None)
    has_info=bool(image_primary and image_primary['kind'] in {'informational','chart','geometry'})
    data_dialogue=bool(q.get('dialogue'))
    inline_speakers=bool(rest and len(speaker_pattern.findall(rest))>=1)
    has_dialogue=data_dialogue or inline_speakers
    is_reading=bool(rest and (
        any(cue in first for cue in reading_cues) and (len(rest)>=75 or '글을 읽고' in first or '이야기를 읽고' in first or '안내문을 읽고' in first)
    ))
    if data_dialogue and any(w in first for w in ('이야기','읽고')) and len(q.get('dialogue') or [])>=3:
        is_reading=True
    is_list=bool(rest and ('(가)' in rest or '(나)' in rest or '•' in rest or 'Plan #' in rest))
    is_sentence=bool(rest and not is_reading and not inline_speakers and not is_list)
    texts=['question']
    if any(x in first for x in ('고르세요','쓰세요','완성','배열','읽고','보고','대답','설명','알맞은')):
        texts.append('instruction')
    if has_dialogue:texts.append('dialogue')
    if is_reading:texts.append('reading')
    if is_list:texts.append('list')
    if is_sentence:texts.append('example_sentence')
    if q['type']=='MCQ':texts.append('choices')
    elif q['type']=='OX':texts.append('choices')
    if q['type']=='SHORT':texts.append('choices') # teacher judgement/reveal controls use a choice area
    texts=sorted(set(texts),key=['question','instruction','dialogue','reading','example_sentence','list','choices'].index)

    reasons=[]
    if has_dialogue:reasons.append('화자별 발화 순서가 있는 대화문으로 판별')
    if has_info:reasons.append('지도·길찾기·위치 등 세밀 판독이 필요한 자료')
    elif has_illustration:reasons.append('장면이나 물체 인식에 사용하는 일반 삽화')
    if is_reading:reasons.append('내용 이해를 위한 읽기 자료')
    if is_list:reasons.append('열거형 자료/계획/사건의 순서')
    if any(i['position']=='choice' for i in imgs):reasons.append('선택지 자체가 그림으로 구성됨')
    if inline_speakers and not data_dialogue:reasons.append('지문 내부에서 화자 표기를 탐지함 — 화면용 발화 분리 권장')

    if image_primary and has_info and has_dialogue:
        family,hint='dialogue_informational','dialogue-image'
    elif image_primary and has_info:
        family,hint='informational_split','map' if image_primary['subtype']=='map' else 'split'
    elif has_dialogue:
        family,hint='dialogue_stack','dialogue-stack'
    elif is_reading and len(lines)>1:
        family,hint='reading_stack','reading-stack' if q['type']=='MCQ' else 'stack'
    elif image_primary and is_sentence:
        family,hint='picture_sentence','picture-stimulus' if q['type']=='MCQ' else None
    elif imgs and all(x['position']=='choice' for x in imgs):
        family,hint='visual_choices',None
    elif image_primary:
        family,hint='scene_auto',None # existing renderer picks composition; do not hard-code
    elif is_sentence or is_list:
        family,hint='text_stack','stack' if q['type']=='MCQ' and len(rest)<=120 else None
    else:
        family,hint='text_auto',None

    teacher_pref=TEACHER_OVERRIDE.get(q['id'])
    if teacher_pref:
        hint=teacher_pref
        reasons.append('과거 교사 화면 검토에서 확인한 상하형 선호를 보존')
        family='reading_stack' if hint=='reading-stack' else 'text_stack'
    if family=='scene_auto':reasons.append('일반 그림의 좌우·상하 위치는 글 길이와 실제 화면 측정으로 결정')
    # Flag ambiguous metadata only, not quality defects
    needs_review=bool(inline_speakers and not data_dialogue) or bool(image_primary and image_primary['subtype'] in ('wayfinding','location'))
    if teacher_pref:needs_review=False
    confidence='medium' if needs_review else 'high'
    question_core=json.dumps(q,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()
    # sourceDigest is reference to untouched original v9 question data
    entry={
      'schemaVersion':'0.1.0-draft','questionId':q['id'],'questionType':q['type'],'images':imgs,'texts':texts,
      'constraints':{'speakerTurnsVertical':has_dialogue,'preserveOriginalText':True,
       'minimumImageDetail':'high' if has_info else 'normal','elementPriority':{
        'question':'medium','reading':'high' if is_reading else 'low',
        'dialogue':'high' if has_dialogue else 'low','image':'high' if has_info else 'medium' if has_illustration else 'low',
        'choices':'medium'}},
      'layout':{'recommendedFamily':family,'rendererHint':hint,
         'selectionBasis':'태그 의미 + 필수 제약 → 기존 A/C/D 내부 배치 힌트; 최종 배치와 용적률은 화면 실측 전까지 미확정',
         'teacherPreference':teacher_pref},
      'confidence':confidence,'needsHumanReview':needs_review,
      'evidence':reasons or ['질문 및 선택지 중심, 별도의 자료 없음'],
      'sourceDigest':hashlib.sha256(question_core).hexdigest()
    }
    return entry

tags={q['id']:classify(q) for q in questions}
assert len(tags)==183
assert sum(t['constraints']['speakerTurnsVertical'] for t in tags.values())>=15
assert sum(any(im['position']=='choice' for im in t['images']) for t in tags.values())==10
assert sum(any(im['position']=='question' for im in t['images']) for t in tags.values())==33
assert all(t['questionId']==qid for qid,t in tags.items())

# Verify schema if installed (report honestly if absent)
try:
 from jsonschema import Draft202012Validator
 validator=Draft202012Validator(SPEC)
 errors=[(id,str(e)) for id,t in tags.items() for e in validator.iter_errors(t)]
 assert not errors,errors[:8]
 schema_status='183/183 JSON Schema PASS'
except ModuleNotFoundError:
 schema_status='JSON Schema library unavailable; structural checks only'

TAG_PATH=ROOT/'HOJA_YBM_183_questions_render_tags_v0.1.json'
TAG_PATH.write_text(json.dumps({'schemaVersion':'0.1.0-draft','sourceHtml':BASE.name,
 'candidateStatus':'TEACHER_REVIEW_PENDING','tagReviewStatus':'AUTOMATIC_PROPOSAL_NOT_APPROVED','questionCount':183,
 'rendererBaseline':'v9 review-only (historical renderer preview.2 derived)','questions':tags},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
SCHEMA_PATH=ROOT/'HOJA_Render_Tags_v0.1_draft.schema.json'
SCHEMA_PATH.write_text(json.dumps(SPEC,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

counts=collections.Counter(t['layout']['recommendedFamily'] for t in tags.values())
image_kind=collections.Counter(im['kind'] for t in tags.values() for im in t['images'] if im['position']=='question')
text_c=collections.Counter(k for t in tags.values() for k in t['texts'])
review_ids=[qid for qid,t in tags.items() if t['needsHumanReview']]
map_ids=[qid for qid,t in tags.items() if any(im['subtype']=='map' for im in t['images'])]

REPORT=ROOT/'HOJA_렌더태그_v0.1_183문항_적용보고서.md'
lines=[
 '# HOJA Renderer Tags v0.1 — YBM 영어 183문항 적용 결과',
 '',
 '> 초안 / 자동 분류 제안. **교사 승인 아님.** 원본 6개 카트리지, 문제·정답·삽화, GitHub 렌더러 및 운영 게임은 변경하지 않았다.',
 '',
 '## 분류 기준',
 '',
 '- 그림: `general`(일반 삽화), `informational`(정보 삽화), `chart`(그래프·표·연표), `geometry`(수학 도형). 이 버전은 범주를 **상호 배타적인 대표 태그**로 저장한다. 세부 분류는 `subtype`.',
 '- 텍스트: `question`, `instruction`, `dialogue`, `reading`, `example_sentence`, `list`, `choices`를 **여러 개 동시에** 지정할 수 있다.',
 '- 대화는 `speakerTurnsVertical=true`. 그림과 대화가 함께 있으면 각 자료의 중요도를 별도로 유지한다.',
 '- 정밀 판독형(`needsFineDetail=true`)은 지도·길찾기·도표·도형 등. 표기 크기를 먼저 확보하고, 질문/지문/보기에 할당하는 면적은 차후 브라우저 실측으로 조절한다.',
 '- 원본과 별도 annotation JSON을 두며 `sourceDigest`로 원본과의 연결을 검증할 수 있다.',
 '- 분류가 애매한 지문 속 화자 표기 또는 위치 그림은 `needsHumanReview=true`.',
 '- `rendererHint`는 레이아웃 엔진의 기존 배치 패턴에 대한 **제안값**이며 승인된 좌표를 고정하는 값이 아니다.',
 '',
 '## 적용 요약',
 '',
 f'- 총 **{len(tags)}문항** / 6개 단원 / 본문 삽화 **33문항** / 그림 선택지 **10문항**.',
 f'- 별도 대화 배열 **{sum(bool(q.get("dialogue")) for q in questions)}문항**, 태그 기반 대화 판별 **{text_c["dialogue"]}문항**(지문 속 화자 표기 포함).',
 f'- 우선 검토 태그 **{len(review_ids)}문항**: '+(', '.join(review_ids) if review_ids else '없음'),
 f'- 스키마 검사: **{schema_status}**.',
 '',
 '### 본문 삽화 대표 종류',
 '',
 '| 이미지 종류 | 문항 수 |', '|---|---:|',
 ]
for k in ['general','informational','chart','geometry']:
 lines.append(f'| {k} | {image_kind[k]} |')
lines.extend(['', '### 추천 배치 분류', '', '| 추천 family | 문항 수 |', '|---|---:|'])
for k,v in sorted(counts.items()):lines.append(f'| `{k}` | {v} |')
lines.extend(['', '### 주요 문항별 예시', '', '| 문항 | 자동 분류 | 비고 |', '|---|---|---|'])
for qid in ['g5u11:q05','g5u11:q34','g5u10:q09','g5u12:q16','g6u10:q21','g6u11:q10','g6u12:q04','g6u12:q21']:
 t=tags[qid]
 lines.append(f'| `{qid}` | `{t["layout"]["recommendedFamily"]}` | {"; ".join(t["evidence"])} |')
lines.extend(['', '## 배치 추천과 실제 화면 품질의 구분',
 '', '- **이번에 수행:** 원본 183문항 파싱, 콘텐츠 성격별 태그 작성, 조합에 따른 배치 후보 분류, 기존 v9 검토용 HTML에 태그를 읽는 실험적 미리보기 구성.',
 '- **이번에 수행하지 않음:** 183문항 × 해상도별 유효 용적률·가독성 점수의 완전한 자동 산출, 그림 원본 여백 판독, 실제 전자칠판 검증.',
 '- 실제 브라우저 검증은 별도 테스트에서 확인한 범위만 기재하며, 추천 family는 최적 배치의 보증이 아니다.',
 '- 이전 정본에 태그를 소급 반영하지 않았다. 내용 승인과 렌더러/태그 승인은 분리한다.',
 '', '## 다음 단계',
 '', '태그 표준을 확정하기 전에 `needsHumanReview` 문항을 교사가 직접 검토하고, 정보 삽화 크기와 대화문 세로 제약의 실제 화면 검사를 강화한다.',
 ])
REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8')

# Adapt existing preview renderer to consume tags without new A/C/D top-level layout types.
js_tags=json.dumps(tags,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')
needle='function classifyLayoutHint(q){'
start=raw.find(needle);end=raw.find('\nfunction applyLayoutHints(arr)',start)
assert start>0 and end>start
repl=f'''/* HOJA Render Tags v0.1 (experimental; non-destructive data annotation). */
const HOJA_RENDER_TAGS={js_tags};
function classifyLayoutHint(q){{
 const tag=HOJA_RENDER_TAGS[q.id];
 if(!tag)return null;
 q.renderTags=tag;
 return tag.layout.rendererHint;
}}
'''
html_out=raw[:start]+repl+raw[end:]

# Render dialogue turn separators even when speakers are embedded inside a reading prompt.
# Presentation-only: do not edit the question text or candidate cartridge.
_inline_helper = r"""function hojaParseInlineTurns(value){
 const out=[];
 const lines=value.split(/\n+/).map(s=>s.trim()).filter(Boolean);
 for(const line of lines){
  const re=/(?:^|\s)(A|B|Gerda|Kai)\s*:\s*/g;
  const hits=[...line.matchAll(re)];
  if(!hits.length){out.push({speaker:'',text:line});continue;}
  const intro=line.slice(0,hits[0].index).trim();
  if(intro)out.push({speaker:'',text:intro});
  hits.forEach((m,i)=>{
    const next=hits[i+1];
    const content=line.slice(m.index+m[0].length,next?next.index:line.length).trim();
    out.push({speaker:m[1],text:content});
  });
 }
 return out;
}
"""
needle_inline="""}else if(enabled && q.prompt.includes('\\n')){"""
assert needle_inline in html_out,'inline prompt branch not found'
replacement_inline="""}else if(enabled && q.renderTags?.constraints?.speakerTurnsVertical && !q.dialogue && q.prompt.includes('\\n')){
  const lines=q.prompt.split(/\\n+/).filter(Boolean);stem=lines[0];
  const turns=hojaParseInlineTurns(lines.slice(1).join('\\n'));
  panel.className='stimulus-dialogue'+(turns.length>2?' long-dialogue':'');
  panel.setAttribute('aria-label','지문에 포함된 화자별 대화');
  for(const d of turns){
    const row=create('div','stim-dialogue-row'+(d.speaker?'':' stim-narration-row'));
    row.append(create('div','stim-speaker',d.speaker),create('div','stim-text',d.text));panel.append(row);
  }
  panel.hidden=!turns.length;
}else if(enabled && q.prompt.includes('\\n')){"""
html_out=html_out.replace(needle_inline,replacement_inline,1)
helper_anchor="""function paintQuestionAndStimulus(q){"""
assert helper_anchor in html_out
html_out=html_out.replace(helper_anchor,_inline_helper+helper_anchor,1)

# Add tag inspector and jump-to-tag group (full question list remains unchanged).
insert_after='<div class="setting"><label>문항 · 출제 유형</label><select id="questionSelect"></select></div>'
assert insert_after in html_out
inspector='''<div class="setting" id="hojaTagInspector" style="border:1px solid #6dbaa9;background:#17313b;border-radius:9px;padding:12px">
<label style="color:#b0ecdb">태그 자동 분류 실험 · v0.1</label>
<div class="note" style="line-height:1.55;margin:5px 0">기존 183문항의 내용으로 자동 추정한 태그야. 교사 승인 전이며, 렌더러 A/C/D는 그대로 유지해.</div>
<div id="hojaTagMeta" style="font-size:13px;line-height:1.6;color:#f6ead7;white-space:pre-wrap">분석 중…</div>
<label for="hojaTagFilter" style="margin-top:8px">태그별 찾아보기</label>
<select id="hojaTagFilter"><option value="all">전체 183문항</option><option value="image_general">일반 삽화가 있는 문항</option><option value="image_informational">정보 삽화가 있는 문항</option><option value="image_chart">도표 삽화</option><option value="image_geometry">도형 삽화</option><option value="image_choices">그림 선택지</option><option value="text_dialogue">대화문</option><option value="text_reading">읽기 지문</option><option value="text_example_sentence">짧은 문장 자료</option><option value="review">사람 확인이 필요한 태그</option></select>
<select id="hojaTagJumper" style="margin-top:6px"><option value="">문항 선택</option></select>
<div id="hojaTagFilterCount" class="note" style="margin-top:6px">분류 결과 불러오는 중…</div>
</div>'''
html_out=html_out.replace(insert_after,insert_after+'\n'+inspector,1)
# Replace page title and baseline description only
html_out=html_out.replace('HOJA · YBM 영어 5·6학년 검토실</h1>','HOJA · YBM 영어 5·6학년 태그 검토실</h1>',1)
html_out=html_out.replace('A/C/D 통합 화면 검토 · YBM 영어 5·6학년','태그 기반 자동 분류 실험 · YBM 영어 5·6학년',1)

last='</body></html>'
assert html_out.count(last)==1
footer='''<script>
/* Tag inspector does not modify question text, answer data or images. */
(function(){
 const tagMap=HOJA_RENDER_TAGS;
 const tagArea=document.getElementById('hojaTagMeta');
 const filter=document.getElementById('hojaTagFilter');
 const select=document.getElementById('hojaTagJumper');
 const count=document.getElementById('hojaTagFilterCount');
 const txt={general:'일반 삽화',informational:'정보 삽화',chart:'도표 삽화',geometry:'도형 삽화'};
 function match(t,key){
   if(key==='all')return true;
   if(key==='review')return t.needsHumanReview;
   if(key==='image_choices')return t.images.some(x=>x.position==='choice');
   if(key.startsWith('image_'))return t.images.some(x=>x.kind===key.slice(6));
   if(key.startsWith('text_'))return t.texts.includes(key.slice(5));
   return false;
 }
 function redrawJump(){
   const candidates=allQ().filter(q=>match(tagMap[q.id],filter.value));
   select.innerHTML='';
   if(!candidates.length){select.add(new Option('해당 문항 없음',''));select.disabled=true;}
   else {select.disabled=false;select.add(new Option('이 태그의 문항을 선택',''));for(const q of candidates){select.add(new Option(unitLabel(q.unit)+' '+q.localId.toUpperCase()+' · '+q.prompt.replace(/\\s+/g,' ').slice(0,34),q.id));}}
   count.textContent='일치: '+candidates.length+' / '+allQ().length+'문항 · 태그는 자동 추정값';
 }
 function showCurrent(){
  const t=tagMap[current().id]; if(!t){tagArea.textContent='미분류';return}
  const imageKinds=[...new Set(t.images.map(x=>txt[x.kind]||x.kind))];
  const im=imageKinds.length?imageKinds.join(', '):'없음';
  tagArea.textContent='그림: '+im+' / '+(t.constraints.minimumImageDetail==='high'?'세밀한 그림 우선':'일반 가독성')+'\\n'+
   '텍스트: '+t.texts.join(' · ')+'\\n'+
   '대화 세로: '+(t.constraints.speakerTurnsVertical?'필수':'해당 없음')+'\\n'+
   '추천 배치: '+t.layout.recommendedFamily+'\\n'+
   '렌더러 힌트: '+(t.layout.rendererHint||'자동 계산')+' / 분류 확신: '+t.confidence+'\\n'+
   (t.needsHumanReview?'※ 태그 수동 확인 권장':'')+'\\n'+
   '실제 선택된 배치: '+(state.appliedComposition||'계산 중');
 }
 filter.addEventListener('change',redrawJump);
 select.addEventListener('change',()=>{if(select.value){const q=allQ().find(q=>q.id===select.value);if(q){state.unit=q.unit;document.getElementById('unitSelect').value=q.unit;chooseQuestion(q.id);}}});
 const originalRender=renderQuestion;
 renderQuestion=function(){originalRender();requestAnimationFrame(()=>{showCurrent();requestAnimationFrame(showCurrent)})};
 redrawJump();showCurrent();
})();
</script>
'''
html_out=html_out.replace(last,footer+last)
HTML_PATH=ROOT/'HOJA_YBM_영어5_6학년_183문항_태그자동분류_v0.1_실험판.html'
HTML_PATH.write_text(html_out,encoding='utf-8')

# Summary JSON for compact use (not rewriting cartridge)
summary={'schemaVersion':'0.1.0-draft','questionCount':len(tags),'unitCounts':dict(units),
 'bodyImageQuestions':sum(any(im['position']=='question' for im in t['images']) for t in tags.values()),
 'imageChoiceQuestions':sum(any(im['position']=='choice' for im in t['images']) for t in tags.values()),
 'imageKindCounts':dict(image_kind),'textTagCounts':dict(text_c),'layoutCounts':dict(counts),
 'dialogueTagged':text_c['dialogue'],'needsReview':review_ids,'jsonSchemaValidation':schema_status,
 'dataIntegrity':'All answer/content data remains in original candidate/HTML; tags stored separately'}
SUMMARY=ROOT/'HOJA_YBM_183_tagging_summary_v0.1.json'
SUMMARY.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

BUNDLE=ROOT/'HOJA_렌더태그_v0.1_YBM183_실험패키지.zip'
with zipfile.ZipFile(BUNDLE,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for f in [SCHEMA_PATH,TAG_PATH,HTML_PATH,REPORT,SUMMARY]:
  z.write(f,f.name)

print(json.dumps(summary,ensure_ascii=False,indent=2))
for f in [SCHEMA_PATH,TAG_PATH,HTML_PATH,REPORT,SUMMARY,BUNDLE]: print('ARTIFACT',f,f.stat().st_size)
