# HOJA 문제은행 — 현재 작업 체크포인트

> **새 대화 시작점**: 먼저 [AGENTS.md](AGENTS.md)와 [workflow/state.json](workflow/state.json), [복구 절차](docs/CHAT_RESUME_PROTOCOL.md)를 읽고 GitHub main의 최신 커밋을 확인한다. 아래는 **2026-11-22 확인 시점**이고 실제 원격 파일이 우선이다.

**활성 작업:** 수학 187문항 시각 검수 준비 · **정식 승인이 아닌 실험 단계**

| 영역 | 교사 승인 | GitHub 등록 | 화면/QA | 운영 게임 |
|---|---|---|---|---|
| 영어·사회 15단원 481문항 | 완료 | 정본 등록 확인 | 별도 검토·미해결 경고 있음 | 미배포 |
| 과학 2단원 64문항 | 2026-11-21 승인 | **ZIP 바이너리 미등록** | 최종 승인 화면 확보 | 미배포 |
| 수학 6단원 187문항 | **미승인** | review.4 실험판 등록 | 태그 정적 검사 기록, **브라우저 전수 QA 미실시** | 미배포 |
| 렌더러 엔진 | 별도 승격 필요 | VERSION current 확인 | `v0.2.0-review.1` | 미배포 |

## 다음 작업 — 수학 187
- **시작 파일:** [수학 review.4 HTML](renderer/experiments/2026-11-22/math-187-legacy-tagged-review-v0.2.0-review.4.html) · [태그](renderer/experiments/2026-11-22/math-187-meaning-render-tags-review.4.json) · [검사 보고](renderer/experiments/2026-11-22/MATH_187_LEGACY_TAGGING_REVIEW4.md)
- **유지:** 기존 A/C/D(현재 분류 A120·C48·D19), 기존 렌더러/검수기, 원본 객관식 4보기/게임 3지선다, 각 단원 OX 균형.
- **확인:** 68개 `needsHumanReview` 문항 우선, 전체 187문항을 HD/FHD/4:3/모바일 실제 브라우저에서 수식·전개도·이미지·보기·주관식 정오판정·잘림 점검.
- **금지:** 그림 유무만으로 A/C 일괄 배정, 독립 규격 렌더러 신설, 미검증 화면을 PASS로 표시, 수학 정본 승인·운영 배포를 임의 완료 처리.

## 남은 별도 복구 — 과학 정본
교사 승인 원본 ZIP 2개는 재확보되었으나 GitHub에는 아직 등록되지 않았다. [과학 ZIP SHA와 원격 등록 체크리스트](docs/SCIENCE_APPROVED_R1_RECOVERY_20261122.md). **원격 파일 SHA 확인 전 승인 색인을 545문항으로 올리지 않는다.**

## 재개/검증
```bash
python3 tools/verify_handoff.py
```

내용을 수정했다면 `workflow/state.json`과 이 문서를 **동일 커밋**으로 갱신한다. 이 문서는 백그라운드 자동 저장이 아니다. 정확한 실행 절차: [CHAT_RESUME_PROTOCOL](docs/CHAT_RESUME_PROTOCOL.md).
