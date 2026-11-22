# HOJA Math 187 — reviewfix1 / A·C·D 교사 검토판 체크포인트

확인일: 2026-11-22 KST. **미승인 수학 후보이며 운영 게임 미배포.**

## 산출물
- [새 검토 렌더러 HTML](renderer/experiments/2026-11-22/math-187-reviewfix1-ui.1.html) — 이전 YBM 승인 렌더러의 **A/C/D 핵심 화면 엔진(v0.2.0-review.1)**을 재사용하고, 기존 수학 review.4의 문항별 A/C/D 선호 분류(A120/C48/D19)와 Gemini rev2 문항/그림 36개를 연결함.
- [ChatGPT에서 바로 열어볼 검토 페이지](https://chatgpt.com/space/page_ee435eceba948191a0390e71aabd2b58) — HTML 시각화 임베드 완료.
- HTML SHA-256: `7f7f8a60bf1906c9a2b7ef4dbf16fbf886288d091dba408155d50a519940cddd` · 991,708 bytes · GitHub blob SHA `d51a2cae7e61e11f595622020d92aed98fa6b564`.
- **수정후보 6개 ZIP 묶음**: 사용자 대화 산출물 `HOJA_MATH_187_REVIEWFIX1_20261122.zip`, SHA-256 `102d859ed6352db96eab23b131c2a81b3f49e13dbbf5718683e1d7ba394938ae`, 522,170 bytes. **현재 GitHub ZIP 바이너리는 미등록**이므로, 새 대화에서 반드시 대화 산출물/Library를 조회하거나 첨부받아야 함. 원본 Gemini rev2 ZIP 6개는 사용자의 Library에서 확인 가능하며, 개별 이미지 원본을 모두 보존. GitHub `approved/`에는 등록 금지.

## 직접 교정한 네 곳 (Gemini rev2 → reviewfix1)
1. `math6-s2-u5:q08` c3: 원의 넓이 정답이 중복되는 진술 제거 → 이전 정답 유일성 보장 오답 `144 cm²보다 넓고 200 cm²보다 좁다.` 복원. 정답 c4 고정.
2. `math5-s2-u6:q08` c3: 평균이 양끝값과 같을 수 있음을 명확히 → `최솟값 이상, 최댓값 이하` 복원. 정답 c4 고정.
3. `math6-s2-u6:q11` c1: 구의 중심 정의를 모호한 `가장 안쪽` 대신 겉면까지 같은 거리라는 표현으로 복원. 정답 c3 고정.
4. `math6-s2-u6:q19`: 캔의 최대 개수 48에 필요한 **같은 방향/상자 모서리 정렬 조건**을 발문에 복구. 정답 c3 및 설명 보존.

다른 문항 183개, 187개 questionId/정답/그룹, 그리고 **rev2 그림 36개는 수정하지 않음**. ZIP별 cartridge/version SHA-256 재검사, CRC, 187문항 집계 통과.

## 기존 렌더러 기능 유지 + 검수실 사용성 개선
왼쪽 상단 순서: **이전·다음 → 단원 선택 → 코멘트(자동 저장) → 검수 JSON 내보내기 → 나머지 기능**.
- 코멘트는 `input` 즉시 기존 `localStorage` 키 `hoja:math:187:chatfix1:qa-v1`에 저장. 이전/다음·단원 이동, 브라우저 페이지 이탈 및 JSON 내보내기에서도 동기화. 기존 `hoja-qa-v1`·`sourceRelease=math-grade5-6-s2-u4-6-chatfix1-20261122` 유지.
- 5학년 소수곱셈 Q13의 ㄱ~ㄹ과 수치를 2열 그리드로 표현. Q21 등 계산식은 별도 색상으로 강조. 분수 마커는 가독성 있는 분수 표기.
- 기존 수학 review.4의 선호 A/C/D 분포 **120/48/19** 유지, 의미 태그 인간 검토 권고 68문항 유지. 정식 렌더러 VERSION/current/타과목 승인 원본 변경 안 함.

## 실제 수행 검사
- Chromium에서 `page.set_content`으로 187문항 순회, 각 문항의 객관식 3개/ OX 2개/주관식 1개 버튼 구성 확인. Javascript 페이지 오류 0.
- WebP 이미지 표시는 실제 렌더링되는 모든 문항에서 유효한 naturalWidth(960) 확인. Q08 원/사각형 이미지 확인.
- 메모 입력 → 이전·다음 → 복귀 후 동일 텍스트 확인; JSON 출력 재수입; 과거 `HOJA_MATH_187_검수기록.json` 11건 가져오기 및 Q01/Q05 메모 표시 확인.
- Q13 보기 2열 표시, Q21 수식 강조 확인; 가상 FHD 화면 스크린샷 캡처.
- 해당 브라우저는 네트워크·파일 URI 직접 이동이 차단돼 있으므로 HTML `set_content` 기반 검사에서 브라우저 localStorage를 *메모리 방식으로 모사*하여 자동 저장 로직을 확인함. 실제 사용자 브라우저 간 데이터 동기화는 제공하지 않으며, JSON 백업 필요.

## 미실시 / 다음
- **전수 육안/해상도별 레이아웃 QA**(HD/FHD/QHD/4:3/모바일)는 완료했다고 주장하지 않음. 각 화면의 클릭 동작/DOM 무결성 테스트만 완료.
- 교사 신규 화면 확인 및 추가 지적 → 별도 후보 수정 → 교사 최종 콘텐츠 승인. 이 시점까지 게임 배포 없음.
- 대화가 끝날 때 `CURRENT_WORK.md`, `workflow/state.json` 동시 업데이트 및 원격 커밋.
