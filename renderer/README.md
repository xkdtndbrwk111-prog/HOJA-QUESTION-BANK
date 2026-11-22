# HOJA 문제 검토 렌더러 · 독립 보관 구역

> **현재 기준:** `v0.2.0-review.1` (2026-11-22) · **검토용** · 운영 게임 미배포

## 현재 기준을 확인하는 법

1. **무조건 이 폴더의 [`VERSION.json`](VERSION.json)을 먼저 읽는다.** `rendererVersion`과 `currentRelease`를 기준으로 한다.
2. 실행 시 [`releases/v0.2.0-review.1/review-renderer-183.html`](releases/v0.1.0-preview.2/review-renderer-demo.html)을 열어 승인된 YBM 183문항과 검수도구를 확인한다.
3. 실제 사회 5학년 3-1·3-2 **64문항 검토 화면은** [`fixtures/social-5-u3-1-rev4-u3-2-rev5-q13-datefree-64q.html`](fixtures/social-5-u3-1-rev4-u3-2-rev5-q13-datefree-64q.html)에 **보존본**으로 둔다. 보존본의 콘텐츠는 **2026-11-21 교사 승인**되었으나, 렌더러 자체와 운영 게임은 미배포 상태다. 정본 ZIP은 [`approved/README.md`](../approved/README.md)를 따른다.

## 역할 분리

- **렌더러 버전:** 이 폴더의 `rendererVersion` — 화면 구성, 교사용 검토 조작, 자동 배치, 그림 확대 등
- **스킬 버전:** HOJA Question Bank `v0.3.0-rc9.1` 등 — 문제 생성·콘텐츠 검수, 렌더링과 독립
- **문제 카트리지 revision:** 각 교과/단원의 수정 차수 (예: 사회 3-1 rev4) — 렌더러 버전과 독립
- **교사 승인 상태:** `approved/`의 승인 문서가 정본 기준; 이 폴더의 모든 HTML이 정본이라는 뜻은 아님

## 기준 화면의 필수 기능

- A/C/D 화면 전환, 이미지·자료가 있을 때 좌우/상하 자동 판단, 화면 크기별 미리보기
- 그림 확대, 객관식 4보기 중 오답 1개 제외한 3지선다, O/X
- **주관식: 학생 답변 → 큰 정답 공개 → 교사의 정답/오답 수동 판정 → 중복 판정 차단 → 다음 문항**
- 검토용 클릭은 **실제 게임 점수, 랭킹, 운영 서버를 변경하지 않음**

## 절대 혼동하지 말 것

- `approved/english/...` ZIP 안에 들어 있는 과거 HTML을 **이 폴더의 current 렌더러로 간주하지 않는다.**
- 사회 33문항 구버전, v3 검토판을 **최신 렌더러로 사용하지 않는다.**
- `fixtures/` 아래는 *콘텐츠와 렌더링이 결합된 시험 보존본*이며, 범용 API/운영 게임 렌더러가 아니다.
- `review-renderer-demo.html`은 **렌더러 동작을 확인하기 위한 가상 데이터 포함 단일 HTML**이고 실제 카트리지 로더, 점수 처리, 데이터 동적 주입 API가 아직 완성된 것은 아니다.

## 변경 절차

수정 시 기존 릴리스 HTML을 덮어쓰지 않는다. 새 `releases/vX/`에 파일 생성 → 샘플/실제 보존본 회귀 검사 → `CHANGELOG.md` 추가 → 마지막에 `VERSION.json`의 `currentRelease` 갱신. 이 과정을 끝내기 전에는 새 버전을 current라 부르지 않는다.

### 시각 자료 개선 기록

- `v0.1.0-preview.2`는 도표 내부의 큰 글자, 칸 안쪽 여백, 균일한 정렬을 추가하고 이미지 있는 문항에서 `layoutHint=split`을 허용한다. 학생 문항, 선택지, 정답은 변경하지 않는다.
- 이전 `v0.1.0-preview.1` HTML과 기존 사회 `rev4-64q.html` 파일은 참고용으로 그대로 남긴다.


## 실험 트랙과 대화 중단 시 복구 (2026-11-22)

- [WORKFLOW_HANDOFF.md](WORKFLOW_HANDOFF.md): 버전 표·실행법·내용/화면 책임 분리·회귀 경고·향후 변경 시 필수 동기화 목록. **새 작업을 이어갈 때 가장 먼저 확인할 문서**.
- [experiments/2026-11-22/README.md](experiments/2026-11-22/README.md): YBM 5·6학년 183문항 태그 렌더링 실험 v0.5, 지문 글자 확대·대화 묶음 세로 중앙 정렬 및 검사 결과.
- [tags/README.md](tags/README.md): 그림/텍스트 의미 태그, 초기 183문항 주석, 자동 분류 참고 스크립트, JSON Schema.

v0.6 실험 HTML은 보존본이고, 승인 검수판 v0.2.0-review.1이 current입니다. 변경 코드를 올릴 때에는 **보존용 HTML + 태그/스키마(변경 시) + CHANGELOG + 인수인계 문서 + 검사 결과**를 함께 갱신한다.

### v0.2.0-review.1
YBM 183문항·31개 원본 그림 내장. 문항별 상태·메모 및 검수 JSON 가져오기/내보내기 지원. 주관식 정오 판정 뒤 다음 버튼의 겹침 개선. 단, 범용 카트리지 동적 로더/API 및 운영 게임 연결은 아직 구현하지 않았습니다.
