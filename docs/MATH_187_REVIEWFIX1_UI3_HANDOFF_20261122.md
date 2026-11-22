# HOJA 수학 187문항 검수 기록 반영 · reviewfix1-ui.3
2026-11-22 · 교사 승인/운영 배포 **아님**

## 원본
- [교사 검수 JSON 20건](../renderer/experiments/2026-11-22/teacher-review-math-187-20261122-1418.json) — 원본 `HOJA_MATH_187_검수기록 (1).json`, export `2026-11-22T05:18:49.134Z`, sourceRelease `math-grade5-6-s2-u4-6-chatfix1-20261122`; 검수 상태는 모두 `pending`.
- [GitHub reviewfix1-ui.2](../renderer/experiments/2026-11-22/math-187-reviewfix1-ui.2.html)에서 **표시 규칙만** 수정했다. 문항 187개, 답안·보기·36개 WebP와 교사 메모·JSON 형식은 변경하지 않았다.

## 적용 사항
1. **교사 C형 요청 19개**: 기존 19개 모두 D형 및 삽화 포함인 것을 확인하고 각 문항의 **표시 시점 선호 레이아웃만 C형**으로 오버라이드. 기존 A/C/D 엔진 구조는 유지하고 D형 버튼 수동 선택은 유지. 표준 기본 분포 A120/C67/D0.
2. **`m6u6:q08`** 원뿔의 ㉠/㉡/㉢/㉣ 보기: 기호와 명칭을 개별 묶음으로 만들어, 묶음 **사이**에서만 줄바꿈하는 flex 배치. 4지선다 원본 및 게임 3지선다 표시 유지. 선별된 실제 3개 보기 모두 4개 그룹 유지. 기존 `m5u4:q13` 보기 2열 처리도 유지.
3. 기존 코멘트 즉시 자동 저장, 문항/단원 전환, JSON 가져오기/내보내기와 UI2의 선택지 분수 색 중립화 유지.

### C형 대상 ID (19)
- `m5u5:q01`
- `m5u5:q10`
- `m5u5:q13`
- `m5u6:q09`
- `m5u6:q10`
- `m5u6:q13`
- `m5u6:q14`
- `m5u6:q17`
- `m5u6:q19`
- `m6u4:q09`
- `m6u4:q17`
- `m6u6:q01`
- `m6u6:q02`
- `m6u6:q04`
- `m6u6:q12`
- `m6u6:q13`
- `m6u6:q14`
- `m6u6:q15`
- `m6u6:q20`

## 실제 확인한 검사
- 원본 UI2와 신규 UI3 내 `DATA_CONCISE`, `DATA_ORIGINAL`, `IMAGES`, `HOJA_RENDER_TAGS` 정적 데이터 동등성 비교 PASS.
- Chromium DOM: **19/19** 문항 기본 C형, **19/19** 이미지 표시 PASS; JavaScript 오류 0.
- Q08: FHD 1920×1080, HD 1280×720에서 자동/좌우/상하 각 조합 **6개** 점검, ㉠~㉣ 묶음 내부 가로 overflow 및 보기 박스 overflow 0.
- 교사 검수 JSON **20건 불러오기** → 코멘트 변경 → **20건 내보내기** 및 수정 메모 보존 PASS.
- source SHA-256: `440ff086673f3dfac2b6c85721ba3dace4bcb2608cd6ff94dbc961431c7d3b33` / 994,404 UTF-8 bytes / Git blob `943d38259b8f095f3afecaf935936aa2108a4272`.
- 교사 검토 페이지: [UI3 열기](https://chatgpt.com/space/page_5b35706854dc819192878d63c6999ecc). 오프라인 `file://`의 Chromium 자동 테스트는 관리자 정책으로 차단돼, DOM 테스트는 `page.set_content()`로 시행. 교사의 브라우저에서 실제 파일 열기/저장 확인은 별도 필요.

## 한계/다음
- 187문항 모든 해상도 전수 육안 검수, 수학 콘텐츠 최종 승인, 게임 배포는 미실시.
- 검수 JSON 파일은 새 페이지 브라우저에 자동 반영되지 않으므로 **'검수 JSON 불러오기'**로 가져와야 한다.
- **원본 정본/카트리지 ZIP/공통 렌더러 VERSION.json 미변경**. UI3는 검수용 후속 버전이다.
