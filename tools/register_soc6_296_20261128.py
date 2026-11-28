#!/usr/bin/env python3
"""Reconstruct canonical effective archives from the teacher-reviewed data and exact image bytes.
The original candidate ZIP digests are recorded; source-only audit files are not reconstructed."""
import base64,collections,copy,hashlib,io,json,pathlib,re,zipfile
R=pathlib.Path('.')
def sha(b):return hashlib.sha256(b).hexdigest()
def jb(x):return (json.dumps(x,ensure_ascii=False,indent=2)+'\n').encode()
def compact(x):return json.dumps(x,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')
def read(p):return json.loads(p.read_bytes())
def write(p,x):p.write_bytes(jb(x))
def blob(b):return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
def pack(d):
    out=io.BytesIO()
    with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for n,b in sorted(d.items()):
            i=zipfile.ZipInfo(n,(2026,11,28,0,0,0));i.compress_type=zipfile.ZIP_DEFLATED
            z.writestr(i,b,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
    return out.getvalue()
data={}
inputs={
 'landforms':'d56af7b81e1eeb179369fe55f36faa431db10f6939b35277912bd34cec0ae957',
 'climate':'e0c29b4ca99c313d677b1add3dc18873ef839ea65e257db6335fb87bac54b1ac',
 'economics':'512764252099f10e392f3061a6aa40b1a19766265c37c7bb30fdef72417a6c22'
}
specs=[
 ('landforms','soc6-2-common-u1-1-landforms','1-1','세계의 다양한 지형',65,2,21,11,'b79110469e3e10f718b18e390cf30d7a399156a02f559a9f6dbcbc6c179bcdf8'),
 ('climate','soc6-2-common-u1-2-climate','1-2','세계의 다양한 기후',72,2,18,13,'32851ddbc213a428942820796f377857b316d0b3da5591dc25c7fe4ffd79bb2d'),
 ('economics','soc6-2-common-u2-1-market','2-1','가계와 기업의 역할',47,6,7,4,'b06555fadf50c99e3fa7b74f2575a25c58a3989edc1ba442454a49c94830aa1b'),
 ('economics','soc6-2-common-u2-2-growth','2-2','우리나라의 경제 성장',59,6,10,6,'0fc303520d870af7f9e97986b1f621f93a99be5c27f7143e11237e305742b5a3'),
 ('economics','soc6-2-common-u2-3-trade','2-3','세계의 무역',53,6,15,6,'877b6c33f3245838ef16d4653354e38ce486cf1c05167ba19817d25a773df600')
]
for key,digest in inputs.items():
    p=R/'workflow/soc6-296-input'/f'{key}-review-data.js'
    b=p.read_bytes().rstrip(b'\r\n')
    assert sha(b)==digest,(key,sha(b),digest)
    s=b.decode()
    def extract(name):
        m=re.search(r'\bconst\s+'+name+r'\s*=\s*',s);assert m,name
        return json.JSONDecoder().raw_decode(s[m.end():])[0]
    data[key]=(extract('DATA_CONCISE'),extract('IMAGES'),extract('HOJA_RENDER_TAGS'))
assert sum(len(v[0]) for v in data.values())==296
reports=[]
for key,old,number,title,count,rev,iq,assets,original_sha in specs:
    cid=f'soc6-s2-u{number}-common';uid='s6u'+number.replace('-','')
    qs,images,tags=data[key]
    src=[q for q in qs if q['questionId'].startswith(old+':')]
    assert len(src)==count and len({q['questionId'] for q in src})==count
    out=[];effective=[];newtags={};used={};imgfiles={};fixed={}
    for o in src:
        q=copy.deepcopy(o);local=q['localId'];assert q['questionId']==old+':'+local
        q['id']=uid+':'+local;q['questionId']=cid+':'+local;q['unit']=uid
        group=q.get('group')
        if group:
            assert group.startswith(old+':')
            q['group']=cid+group[len(old):]
        assert not q.get('dialogue') and not any(c.get('image') for c in q['choices'])
        t=copy.deepcopy(tags[o['questionId']]);t['questionId']=q['id']
        t['layout']['preferredLayout']='C' if q.get('image') else 'A'
        if q.get('image'):
            srcpath=q['image']
            assert srcpath.startswith('assets/') and srcpath in images
            uri=images[srcpath];assert uri.startswith('data:image/webp;base64,')
            raw=base64.b64decode(uri.split(',',1)[1],validate=True)
            assert raw[:4]==b'RIFF' and raw[8:12]==b'WEBP'
            imgfiles['effective/'+srcpath]=raw
            q['image']=cid+'/'+srcpath;used[q['image']]=uri
            t['layout']['rendererHint']='split'
            t['layout']['teacherLayoutLock']=True
            t['layout']['teacherPreference']='C'
            fixed[q['questionId']]={'family':'C','rendererHint':'split'}
            for im in t.get('images',[]):
                if im.get('asset')==srcpath:im['asset']=q['image']
            q['layoutHint']='C'
        else:
            t['layout']['rendererHint']=None
            q['layoutHint']=None
        q['renderTags']=t
        newtags[q['id']]=t
        c={'questionId':q['questionId'],'type':q['type'],'content':[{'kind':'text','text':q['prompt']}],
           'answer':q['answer'],'explanation':q['explanation'],
           'provenance':{'inputFormat':'assessment-rebuild-v0.1.2','commonBasis':q.get('source',''),'reviewDataId':o['questionId'],'sourceCandidateSha256':original_sha}}
        if q.get('image'):c['content'].append({'kind':'image','src':srcpath,'alt':q['imageAlt']})
        if q['type']=='MCQ':
            assert len(q['choices'])==4 and q['answer']['choiceId'] in [x['id'] for x in q['choices']]
            c['choices']=[{'id':x['id'],'content':[{'kind':'text','text':x['text']}]} for x in q['choices']]
        elif q['type']=='OX':assert type(q['answer']['value']) is bool and not q['choices']
        elif q['type']=='SHORT':
            assert q['answer']['text'] and not q['choices']
            c['acceptedAnswers']=q['accepted']
        else:raise ValueError(q['type'])
        if group:c['groupId']=q['group']
        assert c['explanation']==o['explanation'] and c['answer']==o['answer'] and c['content'][0]['text']==o['prompt']
        effective.append(c);out.append(q)
    assert len(fixed)==iq and len(imgfiles)==assets,(cid,len(fixed),len(imgfiles))
    # Only ID namespace and explicit image layout change. No prompt, answer, option, explanation, source or image content changes.
    fulltitle=f'초등 사회 6-2 {number}. {title} (2종 공통)'
    release=cid+'-teacher-20261128-r1'
    cart={'schemaVersion':'qb1-draft.1','cartridgeId':cid,'revision':rev+1,'title':fulltitle,
          'metadata':{'grade':6,'semester':2,'subject':'사회','publisher':'공통(천재 김정인·비상 설규주 형성평가 재구성)','unit':number,'unitNumber':int(number[0]),'unitTitle':title,'status':'approved'},
          'reviewStatus':'teacher_approved','questions':effective}
    meta={uid:{'label':'6학년 '+number,'title':title,'count':count}}
    html=('<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>'+fulltitle+'</title></head><body><script>\n'+
          '\n'.join('const '+k+'='+compact(v)+';' for k,v in [('DATA_ORIGINAL',out),('DATA_CONCISE',out),('IMAGES',used),('HOJA_RENDER_TAGS',newtags),('UNIT_META',meta)])+'\n</script></body></html>\n').encode()
    rights='NOT_INDEPENDENTLY_AUDITED_GENERATED_OR_REDRAWN_MEDIA'
    approval={'teacherApproval':'APPROVED','approvalDate':'2026-11-28','cartridgeId':cid,'title':fulltitle,'releaseId':release,
              'scope':'teacher-approved review text, answer, choices, group, images and left-right layout','gameDeployment':'NOT_DEPLOYED',
              'sourceCandidateSha256':original_sha,'sourceReviewDataSha256':inputs[key],'publicMediaRights':rights,
              'note':'Reconstructed from exact approved reviewer data. Original candidate ZIP was independently compared locally (all question/answer/choice/explanation/group/accepted/image/alt fields equal); source-only candidate audit records were not transferred. No independent rights clearance or live game test claimed.'}
    d={'effective/cartridge.json':jb(cart),'presentation/renderer-data.html':html,'presentation/layout-preferences.json':jb({'schemaVersion':'hoja-layout-preferences-v1','fixed':fixed}),
       'release/approval.json':jb(approval),**imgfiles}
    d['release/file-manifest.json']=jb({'files':{n:{'sha256':sha(b),'bytes':len(b)} for n,b in d.items()}})
    z=pack(d)
    with zipfile.ZipFile(io.BytesIO(z)) as f:
        assert f.testzip() is None
        assert all(f.read(n)==b for n,b in d.items())
    path=R/'approved/social/grade6/semester2'/cid;path.mkdir(parents=True,exist_ok=False)
    archive=cid+'-teacher-approved-20261128-r1.zip';(path/archive).write_bytes(z)
    types=dict(collections.Counter(x['type'] for x in effective))
    unit={'id':cid,'releaseId':release,'teacherApproval':'APPROVED','approvalDate':'2026-11-28','gameDeployment':'NOT_DEPLOYED','sourceRevision':rev,'effectiveRevision':rev+1,'questions':count,'types':types,'assets':assets,
          'archive':archive,'archiveBytes':len(z),'archiveSha256':sha(z),'gitBlobSha':blob(z),'sourceCandidateSha256':original_sha,'sourceReviewDataSha256':inputs[key],
          'effectiveCartridge':'effective/cartridge.json','effectiveAssets':'effective/assets/','reviewedPresentation':'presentation/renderer-data.html','reviewedPresentationSha256':sha(html),'approvedLayout':'presentation/layout-preferences.json','publicMediaRights':rights,'liveGameTest':'NOT_RUN'}
    write(path/'manifest.json',unit)
    solo=len({q.get('group') or q['id'] for q in out if q['type']!='SHORT'})
    team=len({q.get('group') or q['id'] for q in out})
    assert solo>=25 and team>=solo
    reports.append({'id':cid,'title':title,'questions':count,'types':types,'assets':assets,'imageQuestionsSplit':iq,'soloEffective':solo,'teamEffective':team,'archiveSha256':sha(z),'sourceCandidateSha256':original_sha})
    print('APPROVED',cid,count,solo,team,iq,sha(z))
p=R/'approved/catalog.json';cat=read(p);assert cat['summary']['approvedUnits']==29 and cat['summary']['approvedQuestions']==899
cat['updatedAt']='2026-11-28';cat['summary']['approvedUnits']=34;cat['summary']['approvedQuestions']=1195;cat['summary']['social']=457
social=cat['subjects']['social'];social['units']=10;social['questions']=457
social['paths'] += ['social/grade6/semester2/'+x['id']+'/' for x in reports];write(p,cat)
p=R/'workflow/state.json';state=read(p);state['registeredApproved']={'units':34,'questions':1195}
rp='workflow/soc6-296-approval-report.json'
state['workstreams'].append({'id':'social-grade6-296','name':'사회 6-2 1-1~2-3 296문항','status':'APPROVED_GITHUB_REGISTERED','entry':rp,'evidence':[rp]+['approved/social/grade6/semester2/'+r['id']+'/manifest.json' for r in reports],'facts':['교사 승인 5단원 296문항; 검수 데이터와 원래 ZIP의 학생용 문항 데이터 전수 일치','이미지 40종, 그림 문제 71개 C 좌우 고정'], 'next':['정본 런타임 재생성 및 독립 렌더링 시험','권리 상태 보존, 활성 카탈로그 발행']})
write(p,state)
report={'status':'APPROVED_SOURCE_RECONSTRUCTED','teacherApproval':'APPROVED','approvalDate':'2026-11-28','sourceReviewDataSha256':inputs,'originalCandidateStudentFieldComparison':'296/296 matched locally','sourceAuditFiles':'not transferred; candidate ZIP digests retained','units':reports,'questions':296,'assets':40,'imageQuestionsSplit':71,'actualBrowser':'NOT_RUN','publicMediaRights':'HOLD pending independent audit','runtime':'NOT_YET_BUILT'}
write(R/rp,report)
assert sum(x['questions'] for x in reports)==296 and sum(x['assets'] for x in reports)==40 and sum(x['imageQuestionsSplit'] for x in reports)==71
print('SOC6_CANONICAL_PASS 296 40 71')
