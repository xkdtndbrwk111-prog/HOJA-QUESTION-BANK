# QB2 — 독립 문제은행 저장소 준비 (2026-11-20)

상태: PRIVATE 검토용 / NOT_APPROVED / 원격 등록 대기. 운영판 연결 금지.

- 최초 커밋은 QB1 ZIP을 그대로 보존한다. `manifest.sha256.json`은 이 기준판의 174개 파일을 잠근다. 원본 수정·덮어쓰기 금지. 추후 규격 확정 시 별도 버전 태그와 manifest를 설계한다.
- `versions.draft.json`: 76개 레거시 카트리지 및 시험 카트리지 2개의 전체 파일 버전. 카트리지 JSON과 참조된 SVG/WebP의 상대 경로별 SHA-256을 정렬한 compact JSON의 SHA-256. **현재 버전은 검토용**이며 2.0 QR 버전 계약은 건드리지 않았다.
- `catalog.draft.json`: 76개 모두 held_for_review; 시험 2개는 일반 목록에서 제외. 73개 구조 검사 통과는 공개 승인이나 정답 검수가 아니다.
- 기존 Apps Script main / Firebase develop / 운영 Sheets는 변경 금지. 새 저장소에서 문제 자산과 도구만 관리하고, 게임에서 직접 렌더링한다.
- 공개/비공개 접근 제어와 원본 시트 ID 매핑, 랭킹·통계, 미디어 보안(특히 SVG), 교사 검수는 통합 전 별도 게이트. 파일 해시만으로 신뢰 가능한 콘텐츠임을 보장하지 않는다. 기초 비밀 패턴 검사만 했으며 완전한 개인정보 검사나 저작권 검수가 아니다.
- Windows/macOS/Linux 공통: Python 3.10+, `python -m pip install -r requirements.txt`, `python tools/verify_repository.py`, `python tests/test_contract.py`, `python tests/test_repository.py`. `.gitattributes`로 줄바꿈 자동 변환 방지.

## 원격 등록

현재 GitHub 연결에서는 새 저장소 생성 기능이 제공되지 않는다. GitHub에서 소유자 `xkdtndbrwk111-prog`, 이름 `HOJA-QUESTION-BANK`, **Private**, README/.gitignore/license 없이 빈 저장소를 만든 후 GitHub 인증 및 접근 권한을 준비한다. 제공된 bundle은 로컬 Git 초기 커밋까지 포함한다. 기존 게임 저장소로 push하지 말 것.

```sh
git clone -b main HOJA-QUESTION-BANK-QB2.bundle HOJA-QUESTION-BANK
cd HOJA-QUESTION-BANK
git remote set-url origin https://github.com/xkdtndbrwk111-prog/HOJA-QUESTION-BANK.git
git push -u origin main
```

저장소가 비어 있지 않으면 중지하고 확인. 강제 push 금지. 저장소 공개 전환·Pages·Firebase 배포 금지. 실제 원격 커밋 및 visibility 확인 후 QB2 원격 완료로 판정한다.
