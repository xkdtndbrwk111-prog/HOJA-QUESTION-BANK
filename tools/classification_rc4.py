"""RC4 classification contract: validates declared metadata, not source truth."""
import unicodedata,re

SUBJECTS={'국어','수학','사회','과학','영어','도덕','실과','음악','미술','체육','통합교과','바른 생활','슬기로운 생활','즐거운 생활','안전한 생활','창의적 체험활동'}
def require(ok,msg):
    if not ok: raise ValueError(msg)
def canon(s):
    return unicodedata.normalize('NFC',s).strip() if isinstance(s,str) else ''
def present(s):
    return bool(canon(s)) and canon(s).casefold() not in {'unknown','tbd','n/a','미확인','미정','불명','없음','추정'}
def check(b,unit_map=None):
    m=b['metadata']; need=['curriculum','grade','semester','subject','unitNumber','unitTitle','classificationEvidence']
    require(all(k in m for k in need),'RC4 missing metadata: '+str([k for k in need if k not in m]))
    require(isinstance(m['curriculum'],str) and re.fullmatch(r'[0-9]{4}',m['curriculum']) is not None,'RC4 curriculum year')
    require(type(m['grade']) is int and 1<=m['grade']<=6,'RC4 grade 1..6')
    require(type(m['semester']) is int and m['semester'] in (1,2),'RC4 semester 1/2')
    require(m['subject'] in SUBJECTS,'RC4 canonical subject')
    require(type(m['unitNumber']) is int and m['unitNumber']>=1,'RC4 positive unitNumber')
    require(present(m['unitTitle']),'RC4 full unitTitle')
    require(not re.match(r'^(?:Lesson\s+\d+|\d+\s*단원)\b',canon(m['unitTitle']),re.I),'RC4 unitTitle without numbering prefix')
    required=['publisher','leadAuthor','edition'] if m['subject']=='영어' else []
    for k in required:require(present(m.get(k)),'RC4 English missing '+k)
    if required:
        require(not re.search(r'외\s*\d|[()]',m['leadAuthor']),'RC4 leadAuthor must be representative name only')
        require(present(m.get('author')),'RC4 preserve full source author credit')
    e=m['classificationEvidence'];require(isinstance(e,dict),'RC4 evidence object')
    for k in ['curriculum','grade','semester','subject','unit']+required:
        require(present(e.get(k)),'RC4 missing classification evidence: '+k)
    if unit_map is not None:
        row=next((u for u in unit_map['units'] if u['id']==unit_map['currentUnit']),None)
        require(row is not None,'RC4 current unit missing')
        source=canon(row['title']); title=canon(m['unitTitle']); mat=re.match(r'^(?:Lesson\s+(\d+)\s*[.:–-]?\s*|(\d+)\s*단원\s*[.:–-]?\s*)',source,re.I)
        if mat:
            require(int(mat.group(1) or mat.group(2))==m['unitNumber'],'RC4 unit number mismatch')
            source=source[mat.end():].strip()
        require(source.casefold()==title.casefold(),'RC4 unit title mismatch against current unit-map')
        # For unit maps without a numbering prefix, require explicit integer number.
        if not mat:require(type(row.get('unitNumber')) is int and row['unitNumber']==m['unitNumber'],'RC4 unit-map needs unitNumber')
    return {'classificationRecordGate':True,'classificationSourceCertification':'NOT_CERTIFIED'}
def key(b):
    m=b['metadata'];check(b)
    return (m['curriculum'],m['grade'],m['semester'],m['subject'],canon(m.get('publisher')).casefold() if m['subject']=='영어' else '',canon(m.get('leadAuthor')).casefold() if m['subject']=='영어' else '',m['unitNumber'])
