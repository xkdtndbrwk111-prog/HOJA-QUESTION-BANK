# HOJA 과학 5학년 2학기 3·4단원 교사 승인 정본 복구 체크포인트

> 확인일: 2026-11-22 (KST)  
> **상태: 원본 정본 ZIP 2개 재확보·검증 완료, GitHub 정본 바이너리 업로드 미완료.**  
> 이 문서의 존재를 `approved/` 정본 등록 완료로 간주하지 말 것.

## 확보한 교사 승인 원본 (2026-11-21 r1)

| 단원 | 카트리지 ID | 정본 파일명 | 원본 ZIP SHA-256 | 바이트 |
|---|---|---|---|---:|
| 3. 열과 우리 생활 | `sci5-s2-heat-common` | `HOJA_SCI5_S2_HEAT_COMMON_APPROVED_20261121_r1.zip` | `a503459e875d4565e888ce40878d279e9b3513c76e95711ff6f806a610186947` | 586647 |
| 4. 자원과 에너지 | `sci5-s2-u4-common` | `HOJA_SCI5_S2_U4_COMMON_APPROVED_20261121_r1.zip` | `7b711e6d2d29e77152b49958b9bfe22690e1b297a45edd3828cb56270b8b7fae` | 665332 |

두 ZIP은 사용자가 **2026-11-22 대화에 다시 첨부**하였다. 각 ZIP에 있는 `release/approval.json`의 `teacherApproval=APPROVED`, 승인일 `2026-11-21`, source revision 3 및 `gameDeployment=NOT_DEPLOYED` 확인. ZIP CRC 정상; `release/file-manifest.json`에 기록된 9개 파일/각 ZIP의 SHA-256·바이트 불일치 **0**. `source-candidate/` 내 rev3 ZIP 해시와 `release/approval.json` 참조값 일치. `effective/cartridge.json`은 source-candidate 원본과 같음(원본 데이터 보존), 두 ZIP의 동일한 64문항 HTML SHA-256은 `55d4ff85f3f7a2d47aa0f44c52c330e51153541877a8faaf39dad1b99c1435df`.

## 문항·콘텐츠

- 각 단원 32문항(객관식 22 / OX 6 / 주관식 4), 합계 64문항; 각 단원 삽화 5개, OX O3/X3.
- 3단원 Q04 승인 HTML에는 `layoutHint=split` 적용. 기존 공통 A/C/D 화면 사용.
- `effective/cartridge.json`의 `reviewStatus=pending`과 내부 rev3 후보의 `qa.json.teacherApproval=PENDING`은 **원본 후보의 역사적 상태**. 최종 승인 증빙은 ZIP 외피의 `release/approval.json`이다. 이 값들을 근거 없이 고치지 말 것.
- 실제 호자게임 배포 및 전자칠판 실기기 시험은 이 ZIP에서 `NOT_DEPLOYED` / `NOT_RUN`으로 표기.

## GitHub 누락 복구 절차 (실행 전 확인)

1. **첨부된 두 ZIP 원본 그대로** SHA-256 확인 후 다음 경로에 바이너리 업로드:
   - `approved/science/grade5/semester2/sci5-s2-heat-common/HOJA_SCI5_S2_HEAT_COMMON_APPROVED_20261121_r1.zip`
   - `approved/science/grade5/semester2/sci5-s2-u4-common/HOJA_SCI5_S2_U4_COMMON_APPROVED_20261121_r1.zip`
2. 사회 정본과 동일하게 단원별 `README.md` 및 `manifest.json` (각 ZIP의 실제 SHA와 크기, sourceRevision3, APPROVED, NOT_DEPLOYED) 등록.
3. ZIP의 원본 SHA/크기가 원격에서 일치하는지 확인한 뒤 `approved/catalog.json`, `approved/README.md`를 갱신: 기존 15단원 481문항 + 과학 2단원 64문항 = **17단원 545문항**. 영어 출판사별, 비영어 출판사 공통 정책 유지.
4. 실제 `approved/science/` ZIP이 원격에서 확인되기 전에는 catalog 요약을 545로 올리거나 등록 완료를 주장하지 않는다. 게임 배포·승인 렌더러 current는 변경하지 않는다.

## 작업 중단 복구 주의

본 문서가 남아 있어도 바이너리 파일의 GitHub 등록이 보장되는 것은 아니다. 다음 대화에서는 먼저 `approved/science/`의 **실제 ZIP 원격 존재와 SHA**를 확인해야 한다.
