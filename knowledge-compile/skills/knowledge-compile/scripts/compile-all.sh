#!/usr/bin/env bash
# 새 raw 기록이 있는 프로젝트마다 knowledge-compile 스킬을 헤드리스로 돌린다. 스케줄러가 매시간 불러도 된다.
# 업무 시간을 피해 밤(기본 20시~다음 날 8시)에만, 밤마다 한 번 돈다. 그 밤에 PC가 꺼져 있었으면 다음 날 밤에 몰아서 한다.
#
# 사용법:
#   compile-all.sh          # 시간 창과 하루 한 번 조건을 지킨다
#   compile-all.sh --now    # 조건을 무시하고 지금 돈다
#
# 환경 변수:
#   KNOWLEDGE_ROOTS   훑을 .knowledge 디렉터리(공백 구분 glob). 기본: ~/.knowledge ~/.claude/.knowledge ~/*/.knowledge
#   KC_NIGHT_START    밤 시작 시각(기본 20)
#   KC_NIGHT_END      밤 끝 시각(기본 8)
set -uo pipefail
M="$(cd "$(dirname "$0")" && pwd)/manifest.py"
STATE="${XDG_STATE_HOME:-$HOME/.local/state}/knowledge-compile"
DONE="$STATE/last"
START="${KC_NIGHT_START:-20}"
END="${KC_NIGHT_END:-8}"
mkdir -p "$STATE"

if [ "${1:-}" != "--now" ]; then
    hour=$(date +%-H)
    if [ "$hour" -ge "$START" ]; then
        target=$(date +%F)
    elif [ "$hour" -lt "$END" ]; then
        target=$(date -d yesterday +%F)
    else
        echo "knowledge-compile: 업무 시간(${hour}시), 건너뜀"
        exit 0
    fi
    last=$(cat "$DONE" 2>/dev/null || echo 0000-00-00)
    if [[ ! "$last" < "$target" ]]; then
        echo "knowledge-compile: $last 몫까지 끝남, 건너뜀"
        exit 0
    fi
fi

# 스킬은 장부 명령을 ~ 경로로 적는다. 모델이 펼친 경로로 써도 통과하도록 둘 다 허용한다.
SKILL_M="~/.claude/skills/knowledge-compile/scripts/manifest.py"
failed=0
# shellcheck disable=SC2086
for kn in ${KNOWLEDGE_ROOTS:-$HOME/.knowledge $HOME/.claude/.knowledge $HOME/*/.knowledge}; do
    [ -d "$kn/raw" ] || continue
    proj=$(dirname "$kn")
    mapfile -t files < <(python3 "$M" pending "$proj")
    [ "${#files[@]}" -gt 0 ] || continue
    echo "knowledge-compile: $proj (raw ${#files[@]}개)"
    # 쓰기는 knowledge/ 아래로, 셸은 장부 도구로만 묶는다. 허용 밖 호출은 묻지 않고 거부된다.
    (cd "$proj" && timeout 30m claude -p "/knowledge-compile" \
        --tools Skill,Read,Write,Edit,Glob,Bash \
        --allowedTools Skill Read Glob \
            "Write(/$kn/knowledge/**)" "Edit(/$kn/knowledge/**)" \
            "Bash(python3 $SKILL_M *)" "Bash(python3 $M *)" \
        --permission-mode dontAsk --strict-mcp-config --no-session-persistence) \
        || { echo "knowledge-compile: $proj 실패 (exit $?)"; failed=1; continue; }
    # 스킬도 장부를 갱신하지만, 셸 호출이 거부돼도 같은 raw를 다시 컴파일하지 않도록 여기서 한 번 더 적는다.
    python3 "$M" mark "$proj" "${files[@]}"
done

if [ "$failed" -eq 0 ] && [ "${1:-}" != "--now" ]; then
    echo "$target" >"$DONE"
fi
exit "$failed"
