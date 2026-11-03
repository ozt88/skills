# 역할별 계약

## 공통

역할별로 model-only, prompt-only-subagent, agent 중 무엇으로 실행할지와 입력, 증거 계약은 [execution.md](execution.md)를 따른다. 판단 전용 결과는 조정자가 그대로 저장하고, 실제 도구 접근과 사용의 한계를 execution.json에 기록한다. `basis: provided-only`인 후보를 실행 확인으로 승격하지 않는다. 근거가 부족하면 evidence_requests로 반환하며 같은 공통 맥락 갱신 규칙을 적용한다.

`purpose`는 둘 중 하나다. 생략하면 `evaluation`이다.

- `evaluation`(기본): 계획, 명세, 설계, 아키텍처, 세션 결과가 사용자 목표에 얼마나 부합하는지 평가한다. [evaluation.md](evaluation.md)의 목표, 렌즈, 기대 조건, 빼 보기, 목표 달성 계약을 함께 쓴다. 실제 결함이 보이면 findings에도 낸다.
- `defect-review`: 명시된 기대에 어긋나는 결함만 찾는다. 목표 달성 계약은 쓰지 않는다.

brief에는 목표, 사용자 승인 범위, 고정 대상 경로, 제외 범위, N, 렌즈 배정, 라운드 상한, 판단 근거로 쓸 원칙 문서를 적는다. 리뷰 기준은 결과를 보기 전에 정한다. 조사 가능한 파일과 도구, 결과를 쓸 폴더를 명시한다. 비밀과 외부 발신 권한은 별도이며 리뷰 권한에서 파생되지 않는다.

manifest.json:

- `target_id`, `purpose`, `reviewers`(R1 등 유일 ID 배열), `producer`, `judge`(생산자, 리뷰어와 다른 역할 ID)
- `files` 배열: 각 항목 `original`, `snapshot`, `sha256`. snapshot은 run-directory 상대 경로이며 내용 해시를 검사한다. 원칙 문서도 판단 근거로 쓰면 여기에 넣는다. 검토 도중 소스가 변하면 고정 snapshot 판정과 새 버전 판정을 분리한다.
- `goals` 배열(evaluation에서 필수): 각 항목 `id`(G1), `text`, `source`. text는 사용자 요구 원문이나 승인된 결정을 그대로 옮긴다. 조정자가 다시 풀어 쓰지 않는다. source는 원문이 있는 곳(대화, 문서 경로, 이슈)이다.

## Reviewer

reviews/R1.json: `reviewer`, `target_id`, `status`(`complete` 또는 `failed`), `summary`, `findings` 배열. evaluation에서 complete면 `lens`, `expectations`, `assessments`도 필수다. 실패도 원인과 시도 범위를 summary에 남긴다. 결함 0개도 유효하다.

- `lens`: 배정된 렌즈 이름(architect, skeptic, minimalist 또는 brief가 정한 이름).
- `expectations`: 대상물을 읽기 **전에** 목표만 보고 적은 조건. 각 항목 `goal_id`, `condition`. 모든 목표에 하나 이상 적는다. 대상물을 읽은 뒤 고치지 않는다. 읽은 뒤 생각이 바뀌었으면 assessment의 interpretation에 적는다.
- `findings`: 각 항목 `id`(R1-001), `severity`(P0/P1/P2/P3), `claim`, `evidence`, `impact`, `suggestion`. evidence는 배열이며 문서 위치나 파일, 줄, 실제 재현과 기대, 관측을 문자열로 적는다. 추정을 실제 재현으로 쓰지 않는다. severity는 영향과 발생 조건에 근거하고 주장의 강도나 확신과 분리한다.
- `assessments`: evaluation.md 참고. `goal_ids`로 다루는 목표를 연결한다.
- `removals`(선택, minimalist 렌즈는 사실상 필수): 각 항목 `element`, `breaks_goals`(그 요소를 빼면 깨지는 목표 ID 배열), `reason`. `breaks_goals`가 비면 과설계 후보로 집계된다.

본인이 읽거나 시험한 범위와 못한 범위를 summary에 적는다.

## Judge

judge.json: `judge`, `target_id`, `issues` 배열, `summary`. evaluation이면 `assessments`와 `goal_attainment`도 필수다.

- 각 issue: `id`(J-001), `source_ids`(리뷰 finding ID 배열), `verdict`(upheld/refuted/uncertain), `severity`, `reason`, `evidence` 배열. 모든 finding은 정확히 하나의 issue로 연결한다. 중복은 여러 source_ids로 묶고, 반증된 원문도 연결을 유지한다. 서로 다른 지적을 합쳤다면 차이까지 reason에 남긴다. Judge가 새로 찾은 쟁점은 `source_ids: []`와 `origin: judge-new`로 구분한다.
- `goal_attainment`: 목표마다 정확히 한 항목. `goal_id`, `status`(met/partial/unmet/unknown), `reason`, `evidence` 배열, `source_ids`(근거가 된 리뷰어 assessment ID, 선택). 점수를 매기지 않는다. unknown은 판단할 자료가 없다는 뜻이며 무엇이 있으면 판단할 수 있는지 reason에 적는다.
- `strengths`(선택): 리뷰어가 문제를 찾지 못했고 Judge도 근거를 확인한 장점 1~3개. 채우려고 지어내지 않는다.

Judge는 리뷰어 수가 아니라 사실 근거로 판단한다. 같은 모델의 상관된 결론을 독립 재현 횟수로 부풀리지 않는다. 원인을 규명하지 못한 의심은 uncertain으로 남긴다. 합리적인 반론을 강제 합의로 지우지 않는다.

## Producer

producer.json: `producer`, `target_id`, `responses` 배열. evaluation이면 `assessment_responses`도 쓴다.

각 response: `issue_id`, `decision`(accept/partial/reject/defer), `reason`, `action`, `evidence` 배열. 모든 Judge issue에 정확히 한 번 응답한다. refuted에도 동의나 추가 이견을 짧게 남긴다. partial은 수용한 부분과 거절한 부분을 각각 적고, defer는 남은 조건과 영향을 적는다. 수정하지 않았으면 action에 미수정이라고 적는다. 거절을 수정 완료로 표시하지 않는다.

## Verification

verification.json: `verifier`(producer와 다른 역할), `target_id`, `results` 배열, `summary`. evaluation이면 `assessment_results`도 쓴다.

- 각 result: `issue_id`, `status`(resolved/open/disputed/not-run), `reason`, `evidence` 배열. 모든 issue를 확인한다. resolved는 수정이나 반증을 독립 확인한 경우이며 수용했다는 이유만으로 지정하지 않는다. Judge와 생산자의 의견이 다르면 disputed를 보존한다. 증거가 부족하면 not-run이나 open으로 남긴다. target_id는 최초 검수 패킷 ID이며 수정 후 파일과 해시는 evidence에 별도로 적는다.
- `goal_attainment`(선택): 생산자가 대상을 고쳤으면 Judge와 같은 형식으로 목표를 다시 판정한다. 넣으면 모든 목표를 다룬다. Judge의 판정은 덮어쓰지 않고 나란히 보고한다.

최종 report는 원문→Judge→생산자→검증의 연결, 목표별 달성 상태(Judge 판정과 수정 후 판정), 과설계 후보, 미해결 항목을 보여 준다. 자동 구조 검사는 거짓이거나 무관한 증거를 판별하지 않는다. 심각한 미해결 항목과 unmet 목표를 숨기지 않는다. 보고 완료를 대상의 품질 승인으로 취급하지 않는다.
