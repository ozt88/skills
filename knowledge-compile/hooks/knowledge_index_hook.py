#!/usr/bin/env python3
"""SessionStart hook: 컴파일된 knowledge/index.md를 세션 컨텍스트에 넣는다.

작업 디렉터리에서 위로 올라가며 처음 만나는 .knowledge/knowledge/index.md를 쓴다.
상세 파일(decisions.md 등)은 넣지 않는다. index를 보고 필요할 때 모델이 Read로 연다.
index가 없으면 아무것도 출력하지 않는다.
"""
import json
import sys
from pathlib import Path

MAX_CHARS = 16000  # index가 비정상적으로 커져도 컨텍스트를 잡아먹지 않게 자른다


def find_index(start):
    for d in [start, *start.parents]:
        p = d / ".knowledge" / "knowledge" / "index.md"
        if p.is_file():
            return p
    return None


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        data = {}
    index = find_index(Path(data.get("cwd") or ".").resolve())
    if index is None:
        return
    body = index.read_text(errors="ignore")
    if len(body) > MAX_CHARS:
        body = body[:MAX_CHARS] + "\n\n(이하 생략. 전체는 파일을 직접 연다)"
    kdir = index.parent
    context = (
        f"이 프로젝트에서 지난 작업으로 쌓은 지식의 인덱스다. 경로: {kdir}/\n"
        "작업이 아래 주제나 키워드에 닿으면, 진행하기 전에 해당 파일을 Read로 열어 결정, 규칙, 함정을 확인한다.\n"
        "참고한 항목과 지금 상황이 어긋나면 그대로 따르지 말고 사용자에게 알린다.\n"
        "항목을 근거로 판단을 바꿨거나 실수를 피했다면, 작업을 마치고 raw에 기록할 때 그 항목마다\n"
        "`- 참조: <파일> › <항목 제목>` 줄을 덧붙인다. 열어 보기만 하고 판단에 쓰지 않은 항목은 적지 않는다.\n"
        "야간 컴파일이 이 줄을 세어 항목의 Referenced 횟수로 반영한다.\n\n"
        f"{body}"
    )
    json.dump({"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": context}},
              sys.stdout, ensure_ascii=False)


if __name__ == "__main__":
    main()
