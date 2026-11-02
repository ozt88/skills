# 조사와 채택

확인: 2026-11-02. 아래는 공식 저장소/운영자의 1차 문서에서 확인한 유사 절차다. 동일한 표준 이름이 있는 단일 기법이나 효과 입증으로 주장하지 않는다. 구현/문장을 복제한 패키지가 아니라 절차를 참고한 자체 적용본이다.

- [Review Council](https://github.com/deployhq/review-council): 여러 독립 리뷰와 별도 Judge, 중복·반증·이견을 남기는 구조가 직접적인 선례다. Claude Code와 여러 provider를 연결하는 플러그인이므로 이 환경에 그대로 설치하지 않고 역할/추적 방식을 참고한다. 서로 다른 모델 계열 검증이나 원문이 주장하는 효과는 이번 실행의 사실로 가져오지 않는다.
- [CodePanel — Several agents, one PR](https://codepanel.ai/guides/several-agents-one-pull-request): 한 생산자, 여러 리뷰어, 통합자 역할 및 수정/근거 있는 반박, 라운드 한계가 사용자 설명과 가깝다. PR 게시·계정·서비스 연결을 요구하는 부분은 채용하지 않는다.
- [ICML 2026 Peer Review FAQ](https://icml.cc/Conferences/2026/PeerReviewFAQ): 리뷰/저자 응답과 area chair의 판단 구조가 학술 동료심사 선례다. 논문 채택 절차를 게임 설계 승인으로 옮기지 않는다.
- [Anthropic — Building effective agents](https://www.anthropic.com/research/building-effective-agents): evaluator-optimizer는 생성과 평가 반복의 일반 구성요소다. 단일 평가 루프만으로 N리뷰어/Judge/생산자 구조 전체를 제공한다고 보지 않는다.

이번 선택: 기존 현재 협업 도구 위에 독립 N리뷰어→Judge→생산자 응답→변경/반박 검증→사용자 보고를 구성한다. 외부 계정/유료 provider/플러그인을 새로 연결하지 않는다. 원문 기법보다 낫다는 결론은 없으며 운영비·실제 결함 발견·오탐을 작업별로 관찰한다.
