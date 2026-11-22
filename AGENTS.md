# HOJA Question Bank — 모든 AI 작업자 공통 규칙

이 저장소의 작업을 재개할 때에는 **대화의 기억이나 이전 GPT의 완료 보고보다 GitHub의 실제 파일과 원격 커밋을 우선**한다.

1. 가장 먼저 [CURRENT_WORK.md](CURRENT_WORK.md) → [workflow/state.json](workflow/state.json) → [docs/CHAT_RESUME_PROTOCOL.md](docs/CHAT_RESUME_PROTOCOL.md)를 읽는다.
2. `main` 최신 SHA, `renderer/VERSION.json`, `approved/catalog.json`, 활성 작업의 실제 파일 경로를 확인한다.
3. `python3 tools/verify_handoff.py`를 실행할 수 있으면 실행한다. 이 검사는 **기록의 일관성**을 확인할 뿐 브라우저 QA·교육적 정답 인증은 하지 않는다.
4. 상태를 **교사 승인 / GitHub 원격 등록 / 렌더러 정본 / 실제 운영 배포 / QA 실행**으로 분리한다. 파일 생성 보고만으로 GitHub 등록·배포 완료라고 적지 않는다.
5. 수정 시 문항 데이터·그림·배치 태그·렌더러·검수 기록을 구별하고 승인 정본과 `renderer/VERSION.json`을 교사 승인 없이 변경하지 않는다. 수학은 기존 A/C/D 기반으로 처리하며 새로운 고정형 독자 규격을 만들지 않는다.
6. **작업 세션의 종료 또는 사용자에게 완료 답변을 하기 직전에는 체크포인트 커밋을 필수 종료 단계로 수행**한다. 결과와 **마지막 정상 파일·미완료·다음 행동**을 `workflow/state.json`, `CURRENT_WORK.md`에 함께 갱신하여 같은 커밋에 포함한다. 중간에 큰 단계가 끝날 때도 저장한다. 새 채팅 자동 생성/백그라운드 갱신, 예기치 않은 대화 한도 종료의 사전 감지는 설정되어 있지 않다.
7. 여러 AI가 동시에 수정한다면 최신 main 재조회 후 충돌을 확인하고 비파괴적인 새 실험 파일을 만든다. 경합하는 상태 파일 커밋을 무조건 덮어쓰지 않는다.

다른 프로젝트(호자게임 2.0, Teacher Tools, 미니게임)의 실행 상태를 이 저장소 문서 하나로 확정하지 않는다. 각 저장소의 체크포인트를 따로 확인한다.
