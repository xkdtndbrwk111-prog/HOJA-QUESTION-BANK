# HOJA Render Tags v0.1 — 표준 태그 설계 초안

**상태:** 실험 초안. 승인된 문제은행 형식이나 운영 렌더러에 아직 적용하지 않는다.

## 설계 의도

콘텐츠를 제작할 때 `그림/텍스트가 무엇인지` 분류하고, **배치 자체는 렌더러가 판단**한다. 태그는 CSS 좌표·화면 크기·용적률 점수를 저장하지 않는다. 문제은행 원문·정답은 그대로 두고 별도 annotation으로 보관한다.

## 1. 그림 태그 (이미지마다 하나)

| `kind` | 의미 | 기본 처리 |
|---|---|---|
| `general` | 일반 삽화(표정·행동·상황) | 의미를 식별할 크기를 확보하고 나머지와 균형 |
| `informational` | 정보 삽화(길찾기 지도·위치 관계·설명 그림) | **세부 글자·표식이 읽힐 크기 최우선** |
| `chart` | 도표 삽화(그래프·표·연표) | 축·눈금·칸 안의 글자를 우선 확대 |
| `geometry` | 도형(수학 도형·전개도·각도) | 수치·꼭짓점·기호·선 관계 판독 우선 |

각 이미지에는 `subtype`, `needsFineDetail`, `priority`를 보조 기록한다. 하나의 문항에 여러 그림이 있을 수 있으므로 `images` 배열을 사용한다. 그림 선택지는 `position="choice"`다.

## 2. 텍스트 태그 (중복 가능)

- `question`: 평가할 질문 본문
- `instruction`: 무엇을 하라는 지시문(예: 알맞은 것을 고르세요)
- `dialogue`: 화자별 발화(배열에 있거나 지문 속에 등장할 수 있음)
- `reading`: 내용 이해가 필요한 읽기 지문
- `example_sentence`: 짧은 문장·빈칸 문장
- `list`: (가)/(나), 계획 목록 등 구조화된 자료
- `choices`: 학생이 고르는 보기 또는 주관식 교사용 판정 영역

텍스트 태그는 겹칠 수 있다. 예를 들어 질문 안에 영어 대화가 포함된 경우 `question+dialogue+choices`가 모두 붙는다.

## 3. 필수 안전 규칙

1. **대화문 발화는 무조건 위→아래 순서.** 그림과 대화문의 상호 배치(좌우 또는 상하)는 별도로 선택 가능
2. 정보 삽화·도표·도형은 `minimumImageDetail=high`로 지정하고 실제 그림 내용 판독 크기를 먼저 확보
3. `question`은 상대적으로 작은 공간, `reading`·`dialogue`·핵심 그림은 더 높은 공간 비중
4. `choices`도 교실 뒤에서 읽히는 최소 글자 크기와 터치 높이는 확보
5. **겹침·잘림·가독성 검사 통과 후** 유효 용적률을 비교한다. 공간 점수가 높아도 글자가 잘리면 탈락
6. 특정 문항 배치를 좌표로 고정하는 속성은 태그에 두지 않는다. 교사가 확정한 선호는 `teacherPreference`로 별도 추적

## 4. 데이터와 렌더러의 역할 분리

- 문제은행 제작기(Gemini/GPT): 그림의 의미, 텍스트의 역할, 정밀 판독 필요성을 분류해 annotation 작성
- 렌더러: 태그 조합을 읽어 기존 A/C/D 안에서 배치 후보를 선택하고 **실제 화면을 측정**
- QA 검사기(차후): 겹침·잘림·최소 글자 크기·내용 용적률 점수와 후보 비교
- 교사: 경계 사례와 정본 최종 화면 승인

## 5. 실제 적용 예 — 5학년 11단원 Q34

```json
{
  "questionId": "g5u11:q34",
  "images": [
    {
      "asset": "g5u11/assets/u11_street_directions.webp",
      "position": "question",
      "kind": "informational",
      "subtype": "wayfinding",
      "needsFineDetail": true,
      "priority": "high"
    }
  ],
  "texts": [
    "question",
    "instruction",
    "dialogue",
    "choices"
  ],
  "constraints": {
    "speakerTurnsVertical": true,
    "preserveOriginalText": true,
    "minimumImageDetail": "high",
    "elementPriority": {
      "question": "medium",
      "reading": "low",
      "dialogue": "high",
      "image": "high",
      "choices": "medium"
    }
  },
  "layout": {
    "recommendedFamily": "dialogue_informational",
    "rendererHint": "dialogue-image",
    "selectionBasis": "태그 의미 + 필수 제약 → 기존 A/C/D 내부 배치 힌트; 최종 배치와 용적률은 화면 실측 전까지 미확정",
    "teacherPreference": null
  },
  "confidence": "medium",
  "needsHumanReview": true
}
```

화자별 대화는 세로로 유지하면서 은행과 꽃집을 구분해야 하는 그림은 크게 다루는 조합이다. `rendererHint`는 이 HTML에 이미 존재하는 배치 패턴 이름일 뿐, 새 상위 유형을 늘린다는 뜻은 아니다.

## 6. YBM 183문항 적용 현황

- 5학년 92문항, 6학년 91문항 **전수 자동 태깅 완료**
- 본문 그림 **33문항**: 일반 삽화 **25**, 정보 삽화 **8**, 도표 **0**, 도형 **0**
- 그림 선택지 **10문항**(별도 이미지 태그 보존)
- 대화 태그 **18문항**: 별도 대화 데이터 15 + 지문 안의 화자 표기 3
- 읽기 지문 태그 **38문항**(대화와 중복 가능)
- **사람 확인 권장 5문항**: `g5u11:q33`, `g5u11:q34`, `g6u10:q15`, `g6u10:q17`, `g6u12:q21`

## 7. 브라우저 회귀 점검 결과와 한계

HD(1280×720) 및 FHD(1920×1080)에서 **각 183문항의 표시 DOM을 순회**했다. 화자·대사의 실제 사각형 충돌, 발화 순서의 역전, 이미지 로딩 실패는 검사 신호에서 나타나지 않았다.

다만 범용 scrollHeight 기반 검사기는 기존 렌더러와 동일하게 FHD **63문항**, HD **24문항**에 텍스트 경계 관련 *의심 경고*를 표시했다. 이 수치는 **실제 잘림 확정 건수도, 새로운 태그가 만든 오류 건수도 아니다.** 동일한 검사를 태그 이전 v9와 비교했을 때 두 해상도에서 경고 문항과 경고 유형은 같았다. 후속 QA에서는 글리프 단위 및 스크린샷 검증으로 오탐을 줄여야 한다.

**이번 범위에 포함되지 않음:** 전수 4K 검사, 전체 화면 실측 용적률 점수화, 전자칠판 현장 검증, 태그 교사 승인, GitHub/운영 게임 반영.