# 사회 6학년 2학기 3-1·3-2 · rev2 HOJA 렌더링 검수 체크리스트

2026-11-22 · 교사 **최종 승인 전** rev2 후보 · 게임 미배포 · 렌더러 current 미변경

## 렌더러/콘텐츠 경계
- 렌더러: 기존 [수학 UI3 실험판](../renderer/experiments/2026-11-22/math-187-reviewfix1-ui.3.html)에서 A/C/D 표시·자동 배치·교사 판정·문항 메모/JSON 기능을 **재사용**, 6학년 사회 카트리지로 데이터/이미지/태그만 교체.
- source inputs: `soc6-s2-u3-1-common-rev2-candidate-v0.3.0-rc9.1.zip`, `soc6-s2-u3-2-common-rev2-candidate-v0.3.0-rc9.1.zip` (각 revision 2). 데이터 변경 아님.
- 총 64문항: MCQ 44·OX 12·SHORT 8, 그림 5종/9회 사용, rev2에서 수정한 24문항 필터.
- 추천 레이아웃 A 55/C 9, D는 교사 수동 전환 가능. 원본 4보기 중 오답 1개 제외한 3지선다 예시.
- [HTML](../renderer/experiments/2026-11-22/social6-64-rev2-hoja-review-ui1.html)은 1개 파일로 독립 실행 가능. 기존 VERSION.json의 current와 approved/ 아래 정본은 그대로 보존.

## 브라우저 자동 점검
- [x] Chromium DOM 실제 실행: 2개 단원, 64개 자료 로드.
- [x] HD(1280×720) 64문항 + FHD(1920×1080) 64문항 = **128화면 상태** 검사.
- [x] 발문 글리프 경계·보기 라벨과 버튼 경계·5개 이미지 로딩·정답 포함 3지선다 → 검사 경고 0.
- [x] JavaScript 런타임 오류 0.
- [x] rev2 수정 24문항 필터 24/64 표시.
- [x] 단원 전환, 주관식 정답 공개·교사 정오판정, 코멘트 입력/문항 이동, 검수 상태 변경·JSON 기능 구조 확인.
- [ ] 독립적인 macOS/Windows 파일 URL에서 localStorage 재실행 보존은 미검증. 자동 검사는 `page.set_content`을 이용했으므로 저장 기능의 영속성까지 PASS로 표시하지 않음.
- [ ] QHD·4K·4:3·모바일 전수 및 85인치 Windows 전자칠판 실기기 검수.
- [ ] 사회 교과서 3종 원문과 rev2 수정 문항의 교육적 교정 내용 직접 대조.
- [ ] 실제 HOJA 게임 로더/주관식 별칭/운영 점수 연동 및 게임 배포.

## 승인 및 보존
**status: REVIEW_CANDIDATE_ONLY**. 사회 6학년 64문항은 승인 색인과 승인 전체 집계에 포함하지 않는다. `approved/`, `renderer/VERSION.json`, 운영 게임은 이 커밋에서 변경하지 않는다.
