# QB10 — RC4 분류 및 비공개 정본 등록

2026-11-20. 기존 QB2 baseline 174개 해시와 기존 76개 초안 카트리지를 유지. 새 `catalog.json`은 승인 콘텐츠 및 보류 기존 목록을 구분하는 **비공개 관리용**이다. `catalog.draft.json`, `versions.draft.json`은 기존 고정 스냅샷. 게임용 공급 카탈로그가 아니다. `publication: NOT_APPROVED`, `deliveryStatus: HOLD` 유지.

- 분류는 `cartridge.json.metadata`: curriculum, grade, semester, subject, unitNumber, unitTitle. 영어는 publisher, leadAuthor, author, edition 추가. classificationEvidence 기록. 실제 폴더와 ID는 안정적으로 유지. 교육과정·학년·학기·교과·영어 출판사/대표저자·단원 번호의 중복 등록 차단. 기존 legacy 자료는 미확인 필드를 null로 표시하고 재분류 전 보류한다. 동일 단원 기존 legacy 링크는 삭제나 랭킹 이전이 아니다.
- RC4 작성 단계: `python scripts/build_candidate.py WORK OUTPUT.zip --rc4` (REMASTER 시 `--base ORIGINAL`). --rc4는 RC3 심화 검수도 포함. 모든 새 후보는 교사 승인을 자동 부여하지 않는다.
- 새로운 승인 후보 등록: `python -m pip install Pillow jsonschema`; `python tools/register_cartridge.py register CANDIDATE.zip APPROVAL.json [--base ORIGINAL]`. 실제 승인 기록의 ID/revision/version/teacherApproval=APPROVED/deliveryStatus=HOLD/evidence 필요. 기존 ID 덮어쓰기 거부; 향후 개정 등록은 검토된 별도 마이그레이션 절차로 수행. 재빌드 일치 확인 후 등록, catalog 자동 생성. `python tools/register_cartridge.py catalog --verify`로 일치 검사. 쓰기 작업은 동시에 수행하지 않는다.
- 최초 등록 `eng5-ham-u10` rev.4: 사용자 승인 rev.3의 전체 문항 36개와 14개 이미지 bytes 동일. 분류 정보만 수정하여 revision/hash 변경. 30 solo units. `approval.json`으로 교사 승인 연결, `history/rev3`의 이전 데이터 및 version lock 보존. RC3 교육 검사 소급 인증 없음. 학기 2는 사용자와 합의한 분류값이며 교과서 원본은 미검증. 원본 파일의 판본/출처 보존. 실게임 배포, GAS, Firebase, 랭킹 수정 없음.
