# 조사와 채택

확인: 2026-11-02. 아래는 공식 저장소/운영자의 1차 문서에서 확인한 유사 절차다. 동일한 표준 이름이 있는 단일 기법이나 효과 입증으로 주장하지 않는다. 구현/문장을 복제한 패키지가 아니라 절차를 참고한 자체 적용본이다.

- [Review Council](https://github.com/deployhq/review-council): 여러 독립 리뷰와 별도 Judge, 중복, 반증, 이견을 남기는 구조가 직접적인 선례다. Claude Code와 여러 provider를 연결하는 플러그인이므로 이 환경에 그대로 설치하지 않고 역할/추적 방식을 참고한다. 서로 다른 모델 계열 검증이나 원문이 주장하는 효과는 이번 실행의 사실로 가져오지 않는다.
- [CodePanel — Several agents, one PR](https://codepanel.ai/guides/several-agents-one-pull-request): 한 생산자, 여러 리뷰어, 통합자 역할 및 수정/근거 있는 반박, 라운드 한계가 사용자 설명과 가깝다. PR 게시, 계정, 서비스 연결을 요구하는 부분은 채용하지 않는다.
- [ICML 2026 Peer Review FAQ](https://icml.cc/Conferences/2026/PeerReviewFAQ): 리뷰/저자 응답과 area chair의 판단 구조가 학술 동료심사 선례다. 논문 채택 절차를 설계 승인으로 옮기지 않는다.
- [Anthropic — Building effective agents](https://www.anthropic.com/research/building-effective-agents): evaluator-optimizer는 생성과 평가 반복의 일반 구성요소다. 단일 평가 루프만으로 N리뷰어/Judge/생산자 구조 전체를 제공한다고 보지 않는다.

확인: 2026-11-03. 목적 부합 평가를 기본으로 바꾸며 참고한 근거와 선례다.

- [Large Language Models Cannot Self-Correct Reasoning Yet](https://arxiv.org/abs/2310.01798) (Huang et al., ICLR 2024): 외부 피드백 없이 모델이 스스로 고치면 정확도가 오르지 않고, 맞던 답을 틀리게 바꾸기도 한다. 원인은 자기 답의 정오 판정이 약하다는 것이다. 이 스킬의 출발점이다.
- [LLM Evaluators Recognize and Favor Their Own Generations](https://papers.nips.cc/paper_files/paper/2024/hash/7f1f0218e45f5414c79c0679633e47bc-Abstract-Conference.html) (Panickssery et al., NeurIPS 2024): 모델은 자기 글을 알아보고 더 높게 평가하며, 알아보는 능력과 편향의 크기가 선형으로 함께 커진다. 맥락을 나눈 같은 모델 세션에도 남는 문제라서 작성자 감추기와 기대 조건 선기록을 넣었다. 이 장치가 편향을 얼마나 줄이는지는 측정하지 않았다.
- [poteto/noodle adversarial-review](https://github.com/poteto/noodle/blob/main/.agents/skills/adversarial-review/SKILL.md): 의도를 명시하고 "의도가 옳은가"가 아니라 "의도를 얼마나 잘 달성하는가"를 판정하는 틀, architect, skeptic, minimalist 렌즈, 원칙 문서 근거, 규모에 따른 리뷰어 수, 잘된 점 기록을 가져왔다. 리뷰어를 다른 모델로만 띄우는 강제 조건과, 리뷰를 띄운 세션이 최종 판정하는 Lead Judgment는 가져오지 않았다.
- [alirezarezvani/claude-skills adversarial-reviewer](https://github.com/alirezarezvani/claude-skills/blob/main/engineering-team/skills/adversarial-reviewer/SKILL.md): 본문을 읽기 전에 계약을 먼저 적는 기법과 "이 변경을 지우면 무엇이 깨지는가"를 묻는 시험을 기대 조건과 빼 보기로 옮겼다. 같은 세션의 페르소나 전환, 페르소나별 최소 지적 할당량, 여러 페르소나가 잡은 지적의 심각도 상향은 이 스킬의 독립성 원칙과 맞지 않아 가져오지 않았다.
- [dlowd/claude-skill-critique](https://github.com/dlowd/claude-skill-critique): 새 맥락의 비평가가 계획과 설계 문서를 리뷰하고 잘된 점도 남기는 선례다. 목표별 판정과 생산자 응답은 없다.

이번 선택: 현재 협업 도구 위에 독립 N리뷰어→Judge→생산자 응답→변경/반박 검증→사용자 보고를 구성한다. 외부 계정, 유료 provider, 플러그인을 새로 연결하지 않는다. 원문 기법보다 낫다는 결론은 없으며 검토 비용, 실제 결함 발견, 오탐을 작업별로 관찰한다.
