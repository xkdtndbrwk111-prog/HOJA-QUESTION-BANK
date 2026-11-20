"""RC3 record coverage and consistency checks, not semantic certification."""
import math
from pathlib import Path
from verify_repository import cartridge_version, checked, read
STATES={'PASS','HOLD','NOT_RUN'}
CHECKS={'answerUniqueness','evidenceSufficiency','shortcutResistance','objectiveAlignment'}

def require(ok, msg):
    if not ok: raise ValueError('RC3: '+msg)
def indexed(rows,key):
    require(isinstance(rows,list),'expected list '+key)
    out={}
    for r in rows:
        require(isinstance(r,dict) and isinstance(r.get(key),str) and bool(r[key].strip()) and r[key] not in out,'invalid/duplicate '+key)
        out[r[key]]=r
    return out

def audit(root,b,refs,base=None):
    root=Path(root); r=read(checked(root,'rc3-review.json')); version=cartridge_version(root)
    require(r.get('version')==version['version'],'stale version or wrong review')
    require(isinstance(r.get('reviewer'),str) and bool(r['reviewer'].strip()),'reviewer missing')
    statuses=[]
    def check(row,loc):
        require(isinstance(row,dict) and row.get('status') in STATES and isinstance(row.get('evidence'),str) and bool(row['evidence'].strip()),'invalid evidence/status '+loc)
        statuses.append(row['status'])
    rows=indexed(r['questions'],'questionId'); questions={q['questionId']:q for q in b['questions']}
    require(rows.keys()==questions.keys(),'question review inventory')
    subset_count=0
    for id,q in questions.items():
        x=rows[id]; checks=x['checks'];require(isinstance(checks,dict) and checks.keys()==CHECKS,'missing/unknown checks '+id)
        for k in CHECKS:check(checks[k],id+' '+k)
        choices=indexed(x['choices'],'choiceId'); subsets=indexed(x['subsets'],'omittedChoiceId')
        expected={c['id'] for c in q.get('choices',[])} if q['type']=='MCQ' else set()
        omitted=expected-{q['answer'].get('choiceId')}
        require(choices.keys()==expected and subsets.keys()==omitted,'incomplete choices/subsets '+id)
        for k,v in choices.items():check(v,id+' choice '+k)
        for k,v in subsets.items():check(v,id+' omitted '+k);subset_count+=1
    units=indexed(r['units'],'unitId'); bp=indexed(read(checked(root,'question-blueprint.json')),'unitId')
    require(units.keys()==bp.keys(),'unit review inventory')
    for k,v in units.items():check(v,k)
    media=indexed(r['media'],'src');plan=indexed(read(checked(root,'media-plan.json')),'src')
    require(media.keys()==refs.keys(),'media review inventory')
    clocks=0; composites=0
    for k,v in media.items():
        check(v,k); method=v.get('method'); require(method in ('generated','coded','authorized-source','composite'),'unknown media method '+k)
        require(plan[k]['origin']==('coded' if method=='composite' else method),'media origin mismatch '+k)
        require('precision' in v,'precision classification missing '+k); p=v['precision']
        if method=='composite':composites+=1;require(p is not None,'composite missing precision '+k)
        if p is not None:
            require(method in ('coded','composite'),'precision requires code-based output '+k);check(p,k+' precision');require(p.get('kind') in ('clock','other'),'invalid precision kind '+k)
            if p['kind']=='clock':
                clocks+=1;h=p.get('hour');m=p.get('minute');require(type(h) is int and 1<=h<=12 and type(m) is int and 0<=m<=59,'clock time range '+k)
                for key,val in [('hourAngle',(h%12)*30+m*.5),('minuteAngle',m*6)]:
                    a=p.get(key);require(type(a) in (int,float) and math.isfinite(a) and 0<=a<360 and abs(a-val)<=1e-6,'clock angle mismatch '+k+' '+key)
    if base is not None:
        base=Path(base); prev=cartridge_version(base)['files']; curr=version['files']; mapping=read(checked(root,'remaster-map.json'))
        for x in mapping['oldQuestions']:
            if x['action']!='KEEP':continue
            q=questions[x['oldQuestionId']]
            for block in q['content']+[b for c in q.get('choices',[]) for b in c['content']]:
                if block['kind']=='image':
                    path=block['src'];require(prev.get(path)==curr.get(path),'KEEP references mutated asset '+q['questionId']+' '+path)
    return {'rc3RecordGate':all(s=='PASS' for s in statuses),'rc3ReviewedQuestions':len(rows),'rc3SubsetRecords':subset_count,'rc3ReviewedUnits':len(units),'rc3ReviewedMedia':len(media),'rc3CompositeRecords':composites,'rc3ClockParameterRecords':clocks,'rc3SemanticCertification':'NOT_CERTIFIED'}
