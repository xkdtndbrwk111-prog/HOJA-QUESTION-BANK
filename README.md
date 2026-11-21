# HOJA QB1 — 공용 문제은행 데이터 규격 (검토 후보)

2026-11-20. 앱스크립트 기반 호자게임 1.0 개선 및 향후 Firebase 기반 2.0 계승을 위한 **오프라인 초안**. 운영 배포 파일이 아니다. 원본 시트/저장소/스킬 V0.2.2 변경 없음.

## 정본과 어댑터
- `schemas/cartridge.schema.json`: `qb1-draft.1` (게임의 `questionSchemaVersion:2`, 스킬의 `schemaVersion:1`과 별개). 카트리지 ID 및 문항 ID는 배포 이후 고정. 기존 스냅샷의 ID는 유지하되 라이브 Google Sheet ID 및 명칭 매핑 확정 전 임시 식별자다. 보기 ID는 최초 변환 때 부여하고 이후 재정렬해도 유지. 정답은 ID로 지정. 같은 문항에서 보기의 정체성 변경 시 새 ID 부여 또는 검수.
- `groupId`는 선택 사항. 독립 문항의 출제 단위는 questionId, 변형 묶음은 groupId. 같은 카트리지 안에서 유형 필터 후 그룹당 한 문항. 객관식/OX로 출제 가능한 유효 단위 25개 이상, 주관식은 팀전에서만 지원하는 현행 규칙 유지. 문항 수 고정 없음. 데이터는 4보기 유지, 실제 게임이 정답과 오답 2개를 선택.
- `content` / `choices[].content`는 순서가 있는 의미 블록(text, image, frequency, dialogue). 분수/대분수는 기존 `[[frac:2/3]]` / `[[mixed:1:2/3]]` 토큰 유지. 폰트/버튼/레이아웃 필드 배제. 새 종류는 계약 검토 후 추가. 일반 텍스트와 평문 슬래시는 보존; 해석은 게임 규칙에 따름.
- `answer`: MCQ `{choiceId}`, OX `{value: boolean}`, SHORT `{text}`. 설명, acceptedAnswers, answerForm, fractionMode, 원본 출처/행 등 유지. 정답의 교육적 옳음은 별도 검수. 이미지 alt는 교사용/접근성 데이터이며 정답을 직접 노출하지 않도록 이후 검수 필요.
- `tools/convert.py`: 스킬 v1 및 GAS flat v2 입력 변환, 텍스트 전용 flat 호환 내보내기. 미디어가 있는 문항을 기존 flat 형식으로 내보내려 하면 실패시켜 데이터 손실 방지. flat 변환은 문제 내용/보기/정답/그룹 단위 보존용이며 기존 정렬, 런타임 ID, 랭킹/통계 연동, 해설·추가 판정 규칙 등 전체 원본 복원용 아님. 1.0은 새로운 미디어 지원 어댑터가 필요하다.
- `tools/migrate_snapshot.py`: 이전 공개용 JSON 변환본에 대한 재변환 및 왕복 확인. 현재 Google Sheets의 공개 카탈로그를 직접 검증한 것이 아님. `catalog.draft.json`은 정식 공개 목록이 아님. 원본 시트명 보존, 실제 sheetId 미확인(null), 전 항목 held_for_review. `samples/`는 영어·수학 시험 문항으로 일반 카탈로그에서 제외.

## 검사 및 경계
- 검증은 JSON Schema, 문항/보기 ID, 보기 중복, 수학 동치수, 일부 분수 토큰, 로컬 미디어 경로·참조, 빈도 배열 길이, 출제 단위 수. 구조 검사에 실패한 기존 문항도 원본 보존 목적의 보류 데이터에는 저장한다. `structuralGate`는 기계적 조건일 뿐 출판 승인 아님. 기존 76개 중 73개 구조 조건 통과, 3개 보류 사유 있음. 전체 76개 공개/내용 검수 대기.
- SVG 내부의 능동 콘텐츠 허용 목록 검증, WebP 디코드/실제 MIME/크기, 전체 토큰 문법, 데이터 크기 제한, 복수 정답 의미 검수, 접근 제어, 캐시/네트워크, 브라우저·GAS·실기기, 과거 rank/usage 호환은 미구현 또는 미시험. 이 패키지를 웹 공개하거나 게임에 직접 연결하지 말 것.
- `manifest.sha256.json`은 생성물의 개별 파일 해시. 향후 카트리지 버전은 JSON과 참조 미디어 모두 포함하여 산출, QR/버전 계약 별도 확정. 해시는 진위나 출판 승인 보증 아님.

## 실행
Python 3.10+ 및 jsonschema:
```
python -m pip install -r requirements.txt
python tests/test_contract.py
python tools/convert.py <skill-package>/questions/unit.json <output-folder> --asset-root <skill-package>
python tools/convert.py <gas-v2.json> <output-folder> --format gas --title "단원 이름"
python tools/migrate_snapshot.py <prior-json-bank> <skill-examples-dir> <output-dir>
```
`migration-report.json`, `test-results.txt` 참조. 출처 스냅샷과 스킬 샘플은 사용자 제공 작업 파일이며 별도 원본 ZIP/엑셀은 여기 포함하지 않았다.

## 다음 단계
QB2 저장소/버전 관리, 매핑 확정(라이브 공개 검증 포함), 실제 1.0 공통 로더/렌더러 및 테스트 경로 구축. 2.0 develop은 변경하지 않는다. 스킬 최종 개정은 1.0 게임 계약 통합 시험 뒤.

## 교사 승인 콘텐츠 (2026-11-21)

- [영어 5·6학년 천재(함순애) 10·11·12단원 · 201문항 정본 r1](approved/english/cheonjae-ham/grade5-6-u10-12/README.md): 질문·자료·그림·대화·교사 수동 판정 화면을 통합 HTML로 승인. **게임 배포 미실시**, 5학년 10단원 q21 미디어 교체는 HTML 오버레이로 관리.

- [사회 5학년 2학기 공통 · 새로운 사회를 향한 움직임 · r2](approved/social/grade5/semester2/soc5-s2-u2-2-common/README.md): 33문항 / UQ 27, q07 실지도·q21 연표 최종 수정 반영. **콘텐츠 교사 승인, 게임 공개 배포 미실시**. q07 고지도 교과서 사진 재배포 권리 확인 필요.
- 승인 ZIP·무결성·레이아웃은 위 폴더의 `manifest.json`과 `release/approval.json`(ZIP 내부)을 참조.

> 이 섹션은 아래 기존 QB1 설계 초안과 구별되는 신규 교사 승인 콘텐츠 목록이며, QB1 스키마·운영 게임 배포 상태를 자동 변경하지 않습니다.


## 교사 승인 정본 색인 (2026-11-21)

[approved/README.md](approved/README.md)에서 **총 9개 단원, 298문항**의 교사 승인 결과를 확인합니다. 새로 승인된 사회 5-2 3-1(rev4)·3-2(rev5)는 최종 큰 글씨 도표를 포함하며, 3-2 q13의 선택지 날짜 제거까지 반영했습니다. **승인 = 게임 배포가 아닙니다.**


## 렌더러·태그 자동 분류·재개 안내 (2026-11-22)

- [렌더러 현행 버전/재개 절차](renderer/WORKFLOW_HANDOFF.md) — 새 채팅/담당자가 먼저 읽는 인수인계 문서
- [태그 분류기·스키마·YBM 183문항 주석](renderer/tags/README.md)
- [YBM 183문항 실험판 v0.5](renderer/experiments/2026-11-22/README.md) — 지문 자동 확대 및 대화 묶음 중앙 정렬

**반드시 구분:** `renderer/VERSION.json`의 current는 여전히 `v0.1.0-preview.2`이다. 위 v0.5는 교사 승인 전 콘텐츠를 사용한 실험 트랙이다. 승인 정본·운영 게임 배포 상태를 변경하지 않는다.
