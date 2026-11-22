# HOJA 태그 분류기 · v0.1 실험 자료

**2026-11-22 기준.** 콘텐츠 **자동 태깅 후보**와 렌더링 보조용 코드. 승인 정본·운영 게임과 분리.

- [183문항 태그 JSON v0.2](ybm-kim-183-render-tags-v0.2.json): 핵심 그림이 필요한 주관식 5개 우선순위 보정. 이전 [v0.1 JSON](ybm-kim-183-render-tags-v0.1.json)도 보존.
- [183문항 태그 JSON v0.1 보존본](ybm-kim-183-render-tags-v0.1.json): YBM(김혜리) 영어 5·6학년 10~12단원 183문항에 의미 기반으로 부여한 태그. 키는 문항의 내부 ID(`g5u10:q09` 등).
- [JSON Schema](render-tags-v0.1.schema.json): 개별 문항 태그 객체의 구조 검사.
- [auto-classifier-v0.1.js](auto-classifier-v0.1.js): **신규 문항용 재사용 가능한 분류 참고 구현**. 기존 183문항의 태그와 일치한다고 보장하지 않으며, 시각 자료의 의미는 교사 검토가 필요하다.
- [YBM 실험 렌더러](../experiments/2026-11-22/ybm-183-tagged-v0.5.html): 183문항 태그 데이터가 HTML 안에 내장된 **오프라인 검토판**. 이 파일은 standalone이며 운영 게임이 아니다.

## 스키마 규칙

그림 `kind`: `general`(일반 삽화), `informational`(정보 그림·지도), `chart`(그래프·표·연표), `geometry`(수학 도형). 각각 `needsFineDetail` 보조 태그를 가짐.

텍스트 `texts`: `question`, `instruction`, `dialogue`, `reading`, `example_sentence`, `list`, `choices`. 중복 가능.

**필수 배치 제약:** 대화 발화는 위→아래, 같은 인물은 같은 색, 화자 이름 열은 해당 문항에서 가장 긴 이름에 맞춰 정렬. 정보 그림은 판독 가능한 크기 우선. 질문·지문·보기 글자 크기는 상이한 중요도. 겹침·잘림/최소 가독성 검사를 통과한 후 유효 용적률 비교.

`layout.rendererHint`는 강제 좌표가 아닌 후보 힌트. HTML에서 제공하는 A/C/D 상위 화면 유형을 변경하지 않는다.

## 새 문항 자동 태깅 예시

```js
const {classifyQuestion} = require('./auto-classifier-v0.1.js');
const tag = classifyQuestion({
  id:'example:q01', type:'MCQ',
  prompt:'다음 지도를 보고 위치를 고르세요.',
  image:'map.webp', imageAlt:'길찾기 지도',
  dialogue:[{speaker:'A',text:'Where is the bank?'}],
  choices:[{id:'c1',text:'Turn left.'}]
});
console.log(tag.layout.recommendedFamily); // dialogue_informational
```

**검수 절차:** 제작 시 태그 생성 → 스키마 검사 → 의미상 잘못 분류된 그림/대화 교정 → 렌더러 후보 화면 비교 → 가독성·겹침·용적률 검사 → 교사 최종 승인. 자동 태깅만으로 승인 상태를 바꾸지 않는다.

내용·정답은 원본 카트리지에, 의미 태그는 별도 annotations에 저장. 승인 ZIP을 직접 수정하지 않는다.

## 제작 소스 보존

- [build_hoja_tag_trial_original.py](build_hoja_tag_trial_original.py): 이번 YBM 태그 실험에 사용된 **원본 Python 분류·실험판 빌더 소스**. 과거 작업 환경의 절대 경로와 별도의 후보 ZIP을 전제로 하며, 해당 ZIP은 이 저장소에 포함되어 있지 않다.
- [auto-classifier-v0.1.js](auto-classifier-v0.1.js): 이후 신규 문항에 사용하기 위한 일반화 참고 구현. 두 코드가 같은 결과를 내는지 검증했다고 간주하지 않는다.

## v0.6 우선순위 보정
원문·정답·이미지의 SHA는 변경하지 않으며, SHORT+핵심 그림 5개 문항에 한해 `image.priority=high`, `constraints.elementPriority.image=high` 태그만 적용합니다. 그림의 `kind=general`과 `needsFineDetail=false`는 그대로입니다. 렌더러는 해당 태그와 주관식·C 유형을 확인하여 기존 내부 배치 중 하나를 선택합니다.

## 승인 YBM 및 후속 태그
- 승인 태그: approved/english/ybm-kim/grade5-6-u10-12/r1/tags.approved.json (183개, 핵심 그림 5개 우선순위 보정).
- 새로운 미태그 문항은 문제의 질과 정답·교육적 오류를 먼저 확인한 후, 그림 중요도 및 배치를 검수합니다.


## 2026-11-22 · 수학 문항 태그 실험과 스키마 주의
- `auto-classifier-v0.2.js`도 저장소에 존재하며 `VERSION.json`의 `tagClassifier`가 해당 파일을 가리킨다. v0.1은 이전 참고 구현으로 보존한다.
- 수학 187문항은 태그 규격이 생기기 전에 제작되었으므로, **내용·정답 검수 → 문항별 의미 태그 → 기존 A/C/D 렌더러 → 실측 브라우저 시험 → 교사 승인** 절차가 필요하다.
- [수학 187문항 태그 실험 JSON](../experiments/2026-11-22/math-187-meaning-render-tags-review.3.json) 및 [태그 연결 HTML](../experiments/2026-11-22/math-187-legacy-tagged-review-v0.2.0-review.3.html)은 구형 렌더러 연동 **실험안**이며 정본 아님. 원본 승인 데이터를 바꾸지 않는다.
- 현재 `render-tags-v0.1.schema.json`은 수학 전용 `mathSemantics`, `preferredLayout` 및 수학 전용 enum을 허용하지 않는다. **실험 JSON은 현재 공통 스키마를 통과한다고 주장할 수 없다.** 형식 통일·스키마 버전업/정규화·자동 분류기 검증이 후속 필수 작업이다.
- `rendererHint`는 최종 좌표 지정이 아니라 보조 힌트다. 전개도·숫자선·막대그래프·회전판·입체도형 비교처럼 도형 내부 글자가 정답 판정에 필요한 자료에는 가독성 우선순위를 부여하고 실제 브라우저 실측으로 레이아웃을 최종 판단한다.

## 2026-11-22 · 공통 태그 스키마 v0.2 (수학 review.4)
- [후방 호환 공통 JSON Schema v0.2](render-tags-v0.2.schema.json)는 v0.1 영어 태그 구조를 유지하면서 수학의 `preferredLayout=A/C/D`, `mathSemantics`, 전개도·수직선·회전판 등 세부 그림 태그를 허용한다. 기존 v0.1 스키마는 삭제하지 않는다.
- [수학 187문항 v0.2 태그](../experiments/2026-11-22/math-187-meaning-render-tags-review.4.json)는 187/187개 속성/필수필드/enum 정적 검사 통과. 자동분류기 `auto-classifier-v0.2.js`와 **동등성 검증은 하지 않았으며**, 교사 재확인 권고 68문항이 남아 있다.
- [기존 A/C/D 렌더러 연결 review.4](../experiments/2026-11-22/math-187-legacy-tagged-review-v0.2.0-review.4.html) 및 [QA 보고서](../experiments/2026-11-22/MATH_187_LEGACY_TAGGING_REVIEW4.md). 실제 브라우저 시각 전수 검사는 미실시, 교사 승인·운영 배포 아님.
