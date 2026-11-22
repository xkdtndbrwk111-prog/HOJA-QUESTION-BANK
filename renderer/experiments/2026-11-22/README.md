# YBM 183문항 태그 렌더링 실험 · 2026-11-22

**검토 후보, 정본/게임 배포 아님.** 최신 파일: [ybm-183-tagged-v0.6.html](ybm-183-tagged-v0.6.html). v0.5는 보존본입니다.

## v0.6 변경 사항 · 핵심 그림 주관식 자동 공간 배분
- v0.5 오프라인 검토판을 보존하고 새 HTML `ybm-183-tagged-v0.6.html`을 추가. 승인 콘텐츠/운영 게임에는 영향 없음.
- `g5u10:q29`, `g5u12:q29`, `g6u10:q29`, `g6u11:q29`, `g6u12:q29` 총 **5개 SHORT+그림**에서 별도 태그의 `image.priority=high`를 사용해 기존 내부 배치로 자동 전환. 문장 포함은 `picture-stimulus`, 그림만 있는 문항은 `split`. 수동 상하 선택 시 예외.
- 그 외 **178문항의 자동 배치 선택은 v0.5와 동일**. DATA_CONCISE/DATA_ORIGINAL/IMAGES 원본 문자열 그대로.
- 회귀: **183문항×HD·FHD** 비교. v0.5→v0.6 경고 수 HD 24→24, FHD 63→63. 신규 경고 0, JS 오류 0. 신규 변경된 문항 5개. 기존 경고는 해결되지 않음.
- Q29(5학년 12단원) 그림 패널 표시 높이: 720p 환산 **137→273px**. 주관식 답 공개·정오판정 1회 제한·다음 문항 전환 통과.
- QHD/4K는 대표 7문항 표본 검사만 실시. 변경된 5문항 정상, g5u11:q34는 기존 '재검토 필요' 판정 유지. **전체 4K 전수 통과라고 주장하지 않음**.
- 태그 보존: 기존 `ybm-kim-183-render-tags-v0.1.json` 유지, 5개 우선순위만 보정한 `v0.2.json` 추가. 전체 스키마는 여전히 `0.1.0-draft`.

## v0.5 변경 사항
- v0.4 단일 대화 패널·화자별 색상·최장 화자명 공통 열 그대로 유지.
- 특정 `dialogue-stack` 레이아웃에서 위로 붙던 대화 묶음 전체를 **세로 중앙 정렬** (CSS 우선순위 충돌 해결).
- 남는 지문 공간에서는 실제 렌더된 글자의 경계를 검사하며 **최대 허용 글자 크기로 확대**. 너무 길거나 화면을 넘으면 이전 크기로 복귀. 질문·보기·정답 자체는 수정하지 않음.
- 기존 렌더러 A/C/D 상위 유형과 의미 태그 구조는 유지.

## 복구·검사 소스

- [v0.4→v0.5 패치 코드](patch_hoja_stimulus_v05.py) — 과거 절대 경로를 포함하므로 현재 환경에 맞춰 수정
- [183문항 HD/FHD 회귀 검사](qa_hoja_v05_full.py) — Playwright/Chromium 필요
- [183문항 태그 파일](../../tags/ybm-kim-183-render-tags-v0.1.json)
- [태그 규칙·참고 자동 분류기](../../tags/README.md)
- [최상위 인수인계](../../WORKFLOW_HANDOFF.md)

## 2026-11-22 테스트

| 검사항목 | v0.4 | v0.5 |
|---|---:|---:|
| HD 자동 경고 문항 수 | 24 | 24 |
| FHD 자동 경고 문항 수 | 63 | 63 |
| 새로 발생한 경고 | — | 0 |
| 자바스크립트 오류 | 0 | 0 |
| 원본 문항 데이터 변경 | — | 없음 |
| 대화 블록 세로 여백 불균형 | 일부 | 검사한 다중 발화에서 0 |

Q08 FHD 지문 글자 약 53→101px, Q09 위·아래 여백 차이 약 81→0px. 빈 공간 활용 개선과 별개로 기존 경고 24/63은 아직 분석/해결되지 않았다.

**다음 단계:** 기존 경고의 실제 시각적 잘림 구분, 183문항 전수 교사 검토, 지도·도표/대화·그림 중요도 조합 평가, 자동 용적률/겹침 검사 구현, 교육적 적절성 검수, 이후 정본 적용 여부 결정.

## 정본 승인 이관
YBM 183문항은 2026-11-22 approved/english/ybm-kim/grade5-6-u10-12/r1/에 교사 승인 정본으로 등록했습니다. v0.5/v0.6은 실험 보존본입니다. 현재 검수 도구는 renderer/releases/v0.2.0-review.1/review-renderer-183.html입니다.

## 2026-11-22 · 수학 187문항 공통 렌더러 연결 실험 (승인·배포 아님)

- 기존 `renderer/releases/v0.2.0-review.1/review-renderer-183.html`의 A/C/D 레이아웃·교사 판정·검수 기록 UI를 재사용해 **수학 187문항 + 영어 183문항** 통합 실험판을 별도 저장함.
- 통합 실험 HTML: [`math-187-integrated-review-v0.2.0-review.2.html`](math-187-integrated-review-v0.2.0-review.2.html).
- 구현/검사/미완료: [`MATH_187_UNIFIED_REVIEW_HANDOFF.md`](MATH_187_UNIFIED_REVIEW_HANDOFF.md).
- 수학 5·6학년 2학기 4~6단원 187문항, 삽화 36개, 문항 태그 187개를 인라인 포함. 영어 183문항 원본 보존.
- 과목별 검수 localStorage와 JSON sourceRelease를 분리. 수학 OX 각 단원 O 3/X 3 유지.
- GitHub 재조회·자바스크립트 구문·문항/이미지/정답 참조 검사는 통과. **통합판의 실제 브라우저 시각 회귀와 전체 해상도 검사는 미수행**.
- 저장소 비공개: GitHub 로그인 후 HTML 원본을 다운로드해 로컬 브라우저로 실행. 외부 htmlpreview에서는 비공개 저장소 접근 불가.
- 교사 승인을 받기 전까지 `renderer/VERSION.json` current, `approved/`, 운영 게임 배포 상태 변경 금지.


## 2026-11-22 · 수학 의미 태깅 및 기존 엔진 보존 실험 review.3
- [수학 187문항 의미·배치 태그 초안](math-187-meaning-render-tags-review.3.json)
- [수학+영어 검수 HTML (기존 A/C/D 배치 보존 실험)](math-187-legacy-tagged-review-v0.2.0-review.3.html)
- [실험 분석·한계·재검수 안내](MATH_187_LEGACY_TAGGING_REVIEW3.md)
- 현재 **수학 태그 초안은 v0.1 공통 JSON Schema 미호환**, 브라우저 전수 검수 미실시, 교사 승인 전. 이전 독립형 수학 좌우 고정 화면은 HOJA 표준 렌더러가 아니며 승인/배포하면 안 됨.
- 영어 v6/v7 개별 배치 수정은 과거 대화에 보고되었지만 이 폴더에서 해당 이름의 HTML은 확인되지 않음. 요구 사항만 [인수인계 문서](../../WORKFLOW_HANDOFF.md)에 남겼으며 GitHub에 완제품이 있다고 간주하지 않음.

## 2026-11-22 · 수학 review.4 — 공통 v0.2 태그 규격 확인, 기존 A/C/D 유지
- [수학 187문항 실험 HTML (review.4)](math-187-legacy-tagged-review-v0.2.0-review.4.html)
- [수학 의미 태그 187개 (review.4)](math-187-meaning-render-tags-review.4.json), [스키마 v0.2](../../tags/render-tags-v0.2.schema.json), [QA 기록](MATH_187_LEGACY_TAGGING_REVIEW4.md).
- 187/187 태그 공통 확장 스키마 정적 검사 통과. 67 그림 참조/36 고유 WebP 검증, MCQ 정답 참조·OX/SHORT 타입 검증. **실제 브라우저 전수 화면 검증은 미완료**.
- 구형 A/C/D 배치 엔진 및 영어 승인 콘텐츠 불변. 원본 수학 문항·답·삽화 불변, 분수 접근성 레이블 수정. 교사 승인·운영 배포 금지.
