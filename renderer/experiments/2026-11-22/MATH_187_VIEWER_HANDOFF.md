# 수학 187문항 · 기존 review.4 렌더러 수학 전용 화면
작성: 2026-11-22

- [GitHub 원본 통합판](math-187-legacy-tagged-review-v0.2.0-review.4.html): 수학 187 + YBM 영어 183
- [이번 수학 전용 HTML](math-187-review4-math-only.html): **기존 CSS/JS 엔진을 그대로 사용하고 영어 데이터·영어 태그·영어 이미지 테이블만 제외**한 검토 화면. 수학 187문항, 수학 WebP 36개, 기존 A/C/D·자동 구성·주관식 판정·검수 메모·JSON 내보내기 사용.
- [대화에서 열어 보는 페이지](https://chatgpt.com/space/page_d0ff5f4f867c8191b6049f714f5886c1): 실제 HTML 시각화가 첨부된 ChatGPT 개인 페이지.
- 입력 GitHub blob SHA: `a81dc04aff2aebe70f3c38b975b6507e9169b530`
- 수학 전용 HTML의 시각화 저장본 SHA-256: `6fa4559caa0c6dfc65d677c663fe90534cd15041e28cfd86374cc34fb23b3277`, UTF-8 1,033,938 bytes.
- 변경 범위: `DATA_CONCISE=[]`, `DATA_ORIGINAL=[]`, `IMAGES={}` 뒤 원래 `Object.assign(IMAGES, {math images})`는 유지, 영어 `HOJA_RENDER_TAGS={}` 뒤 수학 태그 삽입은 유지. 초기 상태 `math/m5u4:q01`, 영어 선택 옵션 제거, 설명문 수정. **원본 수학 질문·답·이미지·기존 CSS·렌더러 함수는 변경하지 않음.**
- 확인 완료: GitHub blob에서 출처 읽기, Math 187 엔트리와 36개 WebP data URI 보존, A/C/D UI·검수 메모·내보내기 코드 존재, ChatGPT Page의 업로드된 HTML을 재조회해 1,033,938 byte 및 SHA 확인.
- **미실시**: 실제 화면 브라우저 HD/FHD/4:3/모바일 187문항 전수 검증, 교사 육안 평가, 운영 게임 적용. HTML/정적 검사 통과가 화면 전수 PASS나 교사 승인 상태를 의미하지 않음.
- 기존 `renderer/VERSION.json` current와 `approved/`는 그대로 둔다. 수학은 여전히 후보.
