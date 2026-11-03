# Adversarial Review

계획, 명세, 설계, 시스템 아키텍처, 세션 결과가 사용자가 원한 것을 얼마나 달성하는지 다른 세션이 판정하게 하는 스킬입니다. Codex와 Claude Code에서 씁니다. 작업한 세션은 자기 결과를 잘 판정하지 못한다는 데서 출발합니다.

독립 리뷰어 N명 → 별도 Judge → 생산자의 수용, 반박, 수정 → 독립 확인 → 사용자 보고 순서로 진행합니다.

- 리뷰어마다 렌즈(architect, skeptic, minimalist)를 하나씩 맡깁니다. 렌즈 수는 대상의 규모로 정합니다.
- 리뷰어는 대상을 읽기 전에 목표만 보고 기대 조건을 먼저 적습니다. 대상은 작성자를 감춘 "제출된 안"으로 받습니다. 같은 모델이 자기 글을 알아보고 후하게 평가하는 편향을 줄이려는 장치입니다.
- Judge는 목표마다 met, partial, unmet, unknown으로 판정합니다. minimalist의 빼 보기에서 어느 목표에도 닿지 않은 요소는 과설계 후보로 보고합니다.
- 프로젝트의 원칙 문서(`.knowledge/knowledge/` 등)를 판단 근거로 넣을 수 있습니다.
- 코드 결함만 찾는 `defect-review`도 지원합니다.

## Codex에 설치

Codex에서 다음처럼 요청합니다.

```text
$skill-installer https://github.com/ozt88/skills/tree/main/adversarial-review 를 설치해줘.
```

설치 대상은 기본적으로 `~/.codex/skills/adversarial-review`입니다. 설치 후 다음 턴부터 사용할 수 있습니다. 특정 버전이 필요하면 URL의 `main` 대신 commit SHA를 지정합니다. 이미 설치된 경우 기존 변경을 확인한 뒤 업데이트해야 합니다.

## Claude Code에 설치

```bash
bash scripts/install-claude.sh
```

`SKILL.md`, `references/`, `scripts/check_review.py`를 `~/.claude/skills/adversarial-review`로 복사합니다. README와 테스트는 복사하지 않습니다.

Claude Code에서는 판단 전용 좌석을 도구가 하나도 없는 `claude -p`로 띄웁니다. `--tools ""`만으로는 MCP 도구가 남으므로 `--strict-mcp-config`를 함께 씁니다. 자세한 명령은 [execution.md](references/execution.md)의 "런타임별 실행"에 있습니다.

## 사용

Codex에서는 `$adversarial-review`, Claude Code에서는 `/adversarial-review`로 부릅니다.

```text
$adversarial-review 이 아키텍처 문서가 내가 처음 요청한 목표를 얼마나 달성하는지
다른 세션들로 평가하고, 목표별 판정과 과설계 후보까지 보고해줘.
```

```text
$adversarial-review 이 작업의 완료 기준이 적절한지 평가해줘.
사용자 요구와 제안 기준을 구분하고, 조건부 결론과 다음 관찰도 보존해줘.
```

검토 대상과 허용 수정 범위를 지정합니다. 검토만 요청한 경우 실제 수정 권한이 생기지 않습니다. 작은 일상 수정마다 다중 리뷰를 자동 강제하지 않습니다. 동시 슬롯이 부족하면 리뷰어를 배치로 실행할 수 있습니다.

## 구성

- [SKILL.md](SKILL.md): 시작점과 역할 흐름.
- [contracts.md](references/contracts.md): 원문 지적부터 생산자 응답, 검증까지의 연결 계약.
- [evaluation.md](references/evaluation.md): 기준 출처, 충분성, 비결함 평가, 공통 맥락 처리.
- [execution.md](references/execution.md): 판단 전용 호출과 조사, 재현, 수정 에이전트 선택.
- [prompts.md](references/prompts.md): 역할/실행 방식별 입력 템플릿.
- [sources.md](references/sources.md): 참고한 공개 선례와 적용 차이.
- `scripts/check_review.py`: 누락, ID 연결, snapshot 해시 검사. 에이전트를 자동 호출하지 않습니다.

## 검사

Python 표준 라이브러리만 사용합니다. 아래는 이 폴더에서 실행합니다.

```text
python -B -X utf8 tests/test_check_review.py
python -B -X utf8 scripts/check_review.py <run-directory>
```

부분 단계는 `--phase reviews`, `--phase judge`, `--phase producer`로 확인합니다. 기본값은 verification입니다. 실행 자료 형식은 contracts.md와 evaluation.md를 따릅니다.

## 한계

순수 모델 호출은 도구를 제공하지 않는 인터페이스가 실제로 있을 때만 `model-only`로 기록합니다. Claude Code에는 그 인터페이스가 있습니다. Codex에서 그런 인터페이스가 없으면 도구 사용 금지를 지시한 `prompt-only-subagent`로 대체했다고 밝힙니다. 지시가 물리적 도구 차단을 보장하지는 않습니다. 실행, 수정, 현실 관찰은 에이전트와 실제 도구가 담당합니다.

구조 검사 성공은 근거의 진실성, 판단 품질, 사용자 승인, 생산성 향상을 보증하지 않습니다. 별도 모델 API 키나 예약 실행은 설치하지 않습니다. 합성 시험 및 프로젝트별 실행 보고는 이 배포 패키지에 포함하지 않습니다.
