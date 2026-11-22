# 수학 187문항 · HOJA 기존 렌더러 태그 연결 검토

- 기준: renderer/releases/v0.2.0-review.1/review-renderer-183.html 의 기존 A/C/D 렌더링과 화면 실측 선택 로직
- 콘텐츠: math5-s2-u4..u6, math6-s2-u4..u6의 교정 후보 187문항
- **기존 원본·승인 정본·운영 게임을 수정하지 않음.** 이 실험판은 교사 승인 대기 상태
- 36개 실제 삽화 파일을 육안 대조하고, 67개의 문항 그림 참조를 문항 내용과 연결

## 문항별 분석
- A 텍스트 중심: 120; C 단일 그림/수직선/전개도: 48; D 여러 도형·선택 비교: 19
- 자동 힌트 분포: split 22, null 145, stack 1, map 19
- 의미 계열: math_geometry_reference 40, math_stimulus_text 1, math_formula_notation 12, math_text 61, math_informational_reference 2, math_statement_ox 36, math_short_answer 10, math_multifigure_comparison 21, math_chart_or_graph 4
- 이미지 세밀도, 수식 토큰, 긴 선택지, 문항 내 지문 여부, 보기 최대 글자 수를 별도 태그에 기록
- 교사 재확인 권고: 68문항 (주로 그림이 있거나 긴 보기·긴 자료인 문항)

## 호환 원칙
1. A/C/D 배치 CSS, 측정 함수, 보기 3개 선택·정답 처리, 짧은 답 교사 판정, 과목별 검수 기록은 기존 코드 그대로 유지.
2. 문항별 태그만 보강하고, 기존 자동 실측이 실제 좌우/상하 구성을 결정하게 함.
3. math `[[frac:a/b]]` 토큰을 원본 JSON은 변경하지 않고 브라우저 출력 시 분자·분모로 표시하는 독립 어댑터를 추가.
4. 기존 영어 승인 문항과 key `hoja:ybm:183:r1:qa-v1`는 그대로 유지. 수학 QA key도 기존 실험판과 동일.

## 아직 필요한 검증
- 187문항 × 여러 해상도의 실제 브라우저 스크린샷 및 잘림 전수 시험은 **아직 수행하지 않음**.
- 그림을 포함한 문항과 수식이 긴 문항은 교사 육안 재확인이 필요.
- 파일이 만들어졌다는 사실을 출시/승인으로 간주하면 안 됨.
