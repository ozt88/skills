---
name: adversarial-review
description: Have separate sessions judge how well a plan, spec, design, system architecture, or a session's results achieve what the user asked for, because the session that produced the work cannot reliably judge it. Runs lens-assigned independent reviewers who write their expectations from the goals before reading the work, a separate Judge that rules on each goal (met, partial, unmet, unknown), the producer's accept/reject responses, and an independent verification, then reports goal attainment, overdesign candidates, and what is still disputed. Can also run a plain defect review. Use only when the user asks for independent reviewers, a Judge, or an adversarial or fit-for-purpose review; never attach it automatically to small everyday changes.
---

# 독립 리뷰 → Judge → 생산자 응답

작업한 세션은 자기 결과를 잘 판정하지 못한다. 그래서 다른 세션이 "사용자가 원한 것을 얼마나 달성했는가"를 판정하게 한다.
같은 모델은 자기 글을 알아보고 더 높게 평가하므로, 맥락을 끊는 데 더해 작성자를 감추고 기대 조건을 먼저 쓰게 한다. 근거는 [references/evaluation.md](references/evaluation.md)에 있다.

적대적 검토는 반례와 실패 조건을 찾는 일이다. 결함 할당량이나 부정적인 결론을 강제하지 않는다.
기준은 사용자 목표다. 리뷰어 수나 Judge의 말이 권한이나 사실을 정하지 않는다.

## 시작 전에 정할 것

- **실행 방식**: 단계마다 [references/execution.md](references/execution.md)로 고른다. 완결된 자료를 판단만 하는 단계는 model-only, 조사, 재현, 수정은 agent가 기본이다.
  도구 없는 추론 호출이 없으면 prompt-only-subagent로 대체했다고 밝힌다. 역할(Reviewer, Judge, 생산자)과 도구 사용 여부는 따로 정한다.
- **런타임**: Codex와 Claude Code를 모두 지원한다. 각 방식을 어떤 도구로 띄우는지는 execution.md의 "런타임별 실행" 표를 따른다.
- **검토 목적**: 기본은 `purpose: evaluation`(목적 부합 평가)이다. 계획, 명세, 설계, 아키텍처, 세션 결과가 대상이며 [references/evaluation.md](references/evaluation.md)를 읽는다. 실제 결함이 보이면 findings로 함께 낸다.
  명시된 기대에 어긋나는 결함만 찾는 검수면 `purpose: defect-review`를 적는다.
  평가를 마쳤다고 사용자가 선택을 확정했거나 품질을 승인한 것은 아니다.

## 절차

1. **대상과 기준 고정**: 사용자 목표, 리뷰 대상, 제외 범위, 허용된 수정, 검수 기준을 `brief.md`에 적는다.
   대상 파일을 `snapshot/`에 복사하고 원본 경로와 SHA256을 manifest에 남긴다. 기획에서 아직 정하지 않은 것과 코드에서 관찰한 것을 나눠 적는다.
   - 사용자 목표를 G1, G2처럼 나눠 manifest `goals`에 원문 그대로, 출처와 함께 적는다. 생산자가 요약한 의도로 대신하지 않는다.
   - 판단 근거가 될 원칙 문서(프로젝트의 `.knowledge/knowledge/decisions.md`, `guardrails.md`, 설계 원칙 문서)가 있으면 snapshot에 함께 넣는다.
   - 모호한 기준을 승인된 합격선처럼 고정하지 않는다. 사용자 요구 원문, 승인된 결정과 이유, 리뷰어가 제안한 기준, 미결정을 출처와 함께 나눈다.
   - 리뷰어는 기준이 목적을 충분히 다루는지도 점검한다. 기준을 바꾸자고 제안할 때는 이유와 영향을 적는다. 결과를 본 뒤 기준을 몰래 바꾸지 않는다.
2. **N과 렌즈**: 리뷰어마다 렌즈(architect, skeptic, minimalist) 하나를 배정한다. N은 대상의 규모와 되돌리기 어려운 정도로 정한다.
   결정 하나면 1명(architect), 여러 결정이 얽힌 명세면 2명(architect, skeptic), 아키텍처나 되돌리기 어려운 결정이면 3명이다. 렌즈의 질문과 기준은 evaluation.md에 있다.
   사용자가 N을 정했으면 그것을 따른다. N은 전체 리뷰어 수이고 동시 실행 수와 다르다. 슬롯이 부족하면 여러 배치로 나눠 실행한다.
   이번 실행의 상한을 적는다. 기본값은 첫 리뷰 1회와 변경, 쟁점 재검증 1회다. 이 상한은 이번 실행에만 적용한다.
3. **입력 만들기**: 역할별 입력과 출력은 [references/contracts.md](references/contracts.md)를, 프롬프트는 [references/prompts.md](references/prompts.md)를 채워 쓴다.
   - 리뷰어에게는 공통 brief와 원본, 서로 다른 렌즈만 준다. 이전 대화 전체, 생산자의 방어 논리, 다른 리뷰 결과는 넘기지 않는다.
   - 대상은 "제출된 안"으로 주고 작성자를 밝히지 않는다. 리뷰어는 대상을 읽기 전에 목표만 보고 기대 조건(`expectations`)을 먼저 적는다. 입력을 두 번에 나눠 주는 방법은 prompts.md에 있다.
   - 설계 이유와 제약은 방어 논리가 아니다. 출처가 있는 공통 사실과 필요한 의존 자료는 준다. 생산자의 자기평가는 주장으로 표시한다.
   - 판단 전용 호출에는 경로가 아니라 실제 내용을 넣는다. 자료가 부족할 때 추가 맥락을 모든 좌석에 같게 전하는 방법은 evaluation.md의 맥락 절차를 따른다.
   - 새 좌석은 이전 대화를 물려받지 않게 띄운다(런타임별 방법은 execution.md). 모델은 환경과 사용자가 허용한 설정을 따른다. 같은 모델을 별도 맥락으로 돌린 것은 여러 모델 계열로 검증한 것과 다르다.
4. **리뷰어 N명 → 별도 Judge 1명 → 생산자** 순서를 지킨다.
   - 별도 채팅이나 세션 창은 사용자가 만들라고 했을 때만 만든다. 그 밖에는 추론 호출이나 현재 작업의 subagent를 쓴다.
   - 판단 전용 호출은 응답만 돌려주고, 조정자가 원문 그대로 저장한다. 결과 폴더에 직접 쓰는 것은 조사 에이전트뿐이다.
   - 리뷰어와 Judge는 대상을 고치지 않는다. 공유 파일시스템은 격리가 아니므로 소스 해시도 확인한다.
5. **Judge**: 모든 리뷰어 결과를 그대로 Judge에게 준다. 실패한 좌석은 실패로 남기고 재시도, 교체, 부분 검수 중 무엇을 했는지 적는다.
   Judge는 원본에 비춰 중복을 묶고 반증, 보류, 상충 의견을 남긴다. 다수결이나 의견이 하나뿐이라는 이유로 지적을 채택하거나 지우지 않는다.
   Judge가 새로 찾은 쟁점은 `source_ids: []`와 `origin: judge-new`로 구분하고 근거를 단다.
   evaluation이면 목표마다 `goal_attainment`(met, partial, unmet, unknown)를 근거와 함께 판정한다. 점수는 매기지 않는다.
6. **생산자 응답**: 생산자는 Judge 결과를 받은 뒤 모든 쟁점에 수용, 부분 수용, 거절, 보류 중 하나와 근거를 적는다.
   수용과 수정 완료는 다르다. 승인된 범위의 수정은 진행하고 코드와 검증 증거를 연결한다. 수정 승인이 없는 검토면 제안으로 남긴다.
   거절에는 반증, 비용, 범위 중 무엇이 근거인지 적고 Judge의 결론을 덮어쓰지 않는다.
7. **검증**: 같은 Judge나 독립 검수자가 바뀐 대상과 생산자 응답을 확인한다. 수정은 증거로, 거절은 반증이 타당한지로 판단한다.
   리뷰 규칙 자체를 고쳤다면 처음 고정한 기준으로 판단하고, 기준이 바뀌었다는 사실은 따로 밝힌다.
8. **보고**: 목표별 달성 상태(Judge 판정과 수정 후 판정), 과설계 후보, 채택하고 고친 것, 거절한 것, 보류한 것, 남은 이견, 실행한 검증을 사용자에게 보고한다.
   해결되지 않은 중대 문제, 이견, 실행하지 못한 검증, 범위 밖 문제를 감추지 않는다. 상한에 닿아도 합의를 꾸미거나 완료로 판정하지 않는다.
   새 근거 없이 전체 검토를 되풀이하지 않는다. 기록은 기존 checkpoint에 연결하고, 앞으로 할 일을 따로 관리하지 않는다.

## 저장과 확인

실행 폴더 하나에 다음을 둔다.

| 파일 | 쓰는 쪽 | 비고 |
|---|---|---|
| `brief.md`, `manifest.json`, `snapshot/` | 조정자 | manifest에 사용한 계약 문서의 버전이나 해시를 적는다. 계약을 실행마다 복사하지 않는다 |
| `reviews/R1.json` ... `RN.json` | 리뷰어(판단 전용이면 조정자가 저장) | |
| `judge.json`, `producer.json`, `verification.json` | 각 역할 | |
| `execution.json` | 조정자 | 단계별 계획한 방식과 실제 방식. execution.md 참고 |
| `context-updates.md` | 조정자 | 추가 맥락을 전한 경우만. evaluation.md 참고 |
| `report.md` | 조정자 | 사용자 보고 |

파일마다 누가 썼는지 적되, 도구가 역할 신원을 인증한다고 주장하지 않는다.

`scripts/check_review.py <run-directory>`는 리뷰 ID가 모두 Judge 쟁점에 연결됐는지, 모든 목표에 리뷰어 기대 조건과 Judge 판정이 있는지, 모든 쟁점에 생산자 응답과 검증 기록이 있는지, snapshot 해시가 그대로인지만 검사한다.
기대 조건을 정말 대상보다 먼저 썼는지는 검사하지 못한다. 그 순서는 조정자가 입력을 나눠 주는 것으로 지킨다.
지적이 맞는지, 증거가 참인지는 사람이나 에이전트가 판단한다. 이 도구는 에이전트를 부르거나 대상을 실행, 수정하지 않는다. 구조 검사 통과를 품질 승인이나 합의 완료로 쓰지 않는다.

참고한 외부 선례와 다른 점: [references/sources.md](references/sources.md). 외부 플러그인이나 API 서비스를 설치하지 않고 현재 협업 도구로 수행한다.
