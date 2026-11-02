# 역할별 계약

## 공통

역할별로 model-only/prompt-only-subagent/agent를 선택하는 기준과 입력·증거 계약은 [execution.md](execution.md)를 따른다. 판단 전용 결과는 조정자가 그대로 저장하고 실제 도구 접근/사용의 한계를 execution.json에 기록한다. `basis: provided-only`인 후보를 실행 확인으로 승격하지 않는다. 근거가 부족하면 evidence_requests로 반환하며 같은 공통 맥락 갱신 규칙을 적용한다.

모호한 기준/대안/품질을 평가하는 실행은 `purpose: evaluation`과 [evaluation.md](evaluation.md)의 기준·맥락·assessments 연결 계약을 함께 사용한다. 기존 findings는 실제 결함에만 사용하며 비결함 평가에 severity를 강제하지 않는다. purpose 생략 시 기존 결함 검수 계약과 호환된다.

brief에는 목표, 사용자 승인 범위, 고정 대상 경로, 제외 범위, N, 역할 배정, 라운드 상한을 적는다. 리뷰 기준은 결과를 보기 전에 정한다. 조사 가능 파일/도구와 결과 쓰기 폴더를 명시한다. 비밀·외부 발신 권한은 별도이며 리뷰 권한에서 파생되지 않는다.

manifest.json: `target_id`, `reviewers`(R1 등 유일 ID 배열), `producer`, `judge`(생산자/리뷰어와 다른 역할 ID), `files` 배열(`original`, `snapshot`, `sha256`). snapshot은 run-directory 상대 경로이며 내용 해시를 검사한다. 검토 도중 소스가 변하면 고정 snapshot 판정과 새 버전 판정을 분리한다.

## Reviewer

reviews/R1.json 형식: `reviewer`, `target_id`, `status`(`complete` 또는 `failed`), `summary`, `findings` 배열. 실패도 실패 원인/시도 범위를 summary에 남긴다. 결함 0개도 유효하다.

각 finding: `id`(R1-001), `severity`(P0/P1/P2/P3), `claim`, `evidence`, `impact`, `suggestion`. evidence는 배열이며 파일/줄/실제 재현과 기대·관측을 문자열로 적는다. 추정이면 실제 재현으로 쓰지 않는다. 본인이 읽거나 시험한 범위와 못한 범위를 summary에 명시한다. severity는 영향/발생 조건에 근거하고 주장 강도/확신과 분리한다.

## Judge

judge.json: `judge`, `target_id`, `issues` 배열, `summary`.
각 issue: `id`(J-001), `source_ids`(리뷰 finding ID 배열), `verdict`(upheld/refuted/uncertain), `severity`, `reason`, `evidence` 배열. 모든 finding은 정확히 하나의 issue로 연결한다. 중복은 여러 source_ids로 묶는다. 반증된 원문도 연결을 유지한다. 서로 다른 지적을 합쳤다면 차이까지 reason에 남긴다. Judge 신규 지적은 source_ids=[]과 `origin: judge-new`로 구분한다.

Judge는 리뷰어 수 대신 사실 근거로 판단한다. 동일 코드/동일 모델의 상관된 결론을 독립 재현 횟수로 부풀리지 않는다. 원인을 규명하지 못한 의심은 uncertain으로 남긴다. 의미상 합리적인 반론을 강제 합의로 지우지 않는다.

## Producer

producer.json: `producer`, `target_id`, `responses` 배열.
각 response: `issue_id`, `decision`(accept/partial/reject/defer), `reason`, `action`, `evidence` 배열. 모든 Judge issue에 정확히 한 번 응답한다. refuted에도 동의/추가 이견을 짧게 남긴다. partial은 수용/거절 부분을 각각 명시하고 defer는 남은 조건·영향을 적는다. 수정 안 했으면 action에 미수정이라고 적는다. 거절을 코드 수정 완료로 표시하지 않는다.

## Verification

verification.json: `verifier`(producer와 다른 역할), `target_id`, `results` 배열, `summary`.
각 result: `issue_id`, `status`(resolved/open/disputed/not-run), `reason`, `evidence` 배열. 모든 issue를 확인한다. resolved는 수정 또는 반증을 독립 확인한 경우이며 수용했단 이유만으로 지정하지 않는다. Judge와 생산자가 다르면 disputed를 보존한다. 불충분 증거는 not-run/open으로 남긴다. target_id는 최초 검수 패킷 ID이며 수정 후 파일/해시는 evidence에 별도 명시한다.

최종 report는 원문→Judge→생산자→검증의 연결과 전체 미해결 항목을 보여준다. 자동 구조 검사는 거짓/무관한 증거를 판별하지 않는다. high severity 미해결을 숨기지 말고 사용자에게 넘긴다. 모든 이견 해결이 보고 완료의 전제는 아니지만 보고 완료를 대상의 품질 승인으로 취급하지 않는다.
