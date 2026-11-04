import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('collect', ROOT / 'skills/worklog/scripts/collect.py')
collect = importlib.util.module_from_spec(spec)
spec.loader.exec_module(collect)

# 2026-11-03 KST = 2026-11-02T15:00Z ~ 2026-11-03T15:00Z
IN_DAY = '2026-11-03T01:00:00.000Z'
LATER = '2026-11-03T02:00:00.000Z'
NEXT_DAY = '2026-11-03T16:00:00.000Z'


def user(text, ts=IN_DAY, **extra):
    return {'type': 'user', 'timestamp': ts, 'message': {'content': text}, **extra}


def assistant(text, ts=LATER, **extra):
    return {'type': 'assistant', 'timestamp': ts,
            'message': {'content': [{'type': 'text', 'text': text}, {'type': 'tool_use', 'name': 'Bash'}]}, **extra}


class CollectTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        base = Path(self.temp.name)
        self.home = base / 'home/me'
        self.win = base / 'win/projects'

    def write(self, root, folder, sid, rows, cwd=None):
        d = root / folder
        d.mkdir(parents=True, exist_ok=True)
        lines = [json.dumps({**r, 'cwd': cwd} if cwd else r) for r in rows]
        (d / f'{sid}.jsonl').write_text('\n'.join(lines) + '\nnot json\n', encoding='utf-8')

    def sessions(self):
        return collect.collect_sessions('2026-11-03', str(self.home), str(self.win))

    def test_prompts_in_period_and_last_reply(self):
        self.write(self.home / '.claude/projects', '-home-me-repo', 'a' * 8, [
            user('어제 일', ts='2026-11-02T10:00:00.000Z'),
            user('낙원 시뮬레이션 문서 고쳐줘'),
            assistant('중간 응답'),
            assistant('하위 문서를 고쳤습니다.', ts='2026-11-03T03:00:00.000Z'),
            user('내일 일', ts=NEXT_DAY),
        ], cwd=str(self.home / 'repo'))
        [s] = self.sessions()
        self.assertEqual(s['label'], '~/repo')
        self.assertEqual([t for _, t in s['prompts']], ['낙원 시뮬레이션 문서 고쳐줘'])
        self.assertEqual(s['reply'], '하위 문서를 고쳤습니다.')

    def test_noise_is_dropped(self):
        self.write(self.home / '.claude/projects', 'p', 'b' * 8, [
            user('<command-name>/clear</command-name>'),
            user('<cross-session-message from="x">hi</cross-session-message>'),
            user('[Request interrupted by user]'),
            user('메타', isMeta=True),
            user('서브에이전트 지시', isSidechain=True),
            user('<command-name>/review</command-name>'),
            user([{'type': 'text', 'text': '목록  형태\n프롬프트'}]),
        ])
        [s] = self.sessions()
        self.assertEqual([t for _, t in s['prompts']], ['/review', '목록 형태 프롬프트'])
        self.assertIsNone(s['reply'])

    def test_session_without_prompts_is_skipped(self):
        self.write(self.home / '.claude/projects', 'p', 'c' * 8, [assistant('혼자 말함')])
        self.assertEqual(self.sessions(), [])

    def test_windows_sessions_are_added_with_wsl_label(self):
        unc = '\\\\wsl.localhost\\ubuntu' + str(self.home).replace('/', '\\') + '\\skills'
        self.write(self.win, '--wsl-localhost-ubuntu-home-me-skills', 'd' * 8, [user('inbox 고쳐줘')], cwd=unc)
        self.write(self.win, 'C--Users-me', 'e' * 8, [user('윈도우 작업')], cwd='C:\\Users\\me')
        labels = {s['label'] for s in self.sessions()}
        self.assertEqual(labels, {'~/skills', 'C:\\Users\\me'})

    def test_remote_and_duplicate_windows_sessions_are_not_counted_twice(self):
        self.write(self.home / '.claude/projects', '-home-me', 'f' * 8, [user('WSL 쪽')], cwd=str(self.home))
        self.write(self.win, 'ssh-' + 'f' * 8, 'f' * 8, [user('원격 사본')])
        self.write(self.win, 'other', 'f' * 8, [user('같은 id 사본')])
        self.write(self.win, 'ssh-' + '1' * 8, '1' * 8, [user('원격 전용')])
        [s] = self.sessions()
        self.assertEqual([t for _, t in s['prompts']], ['WSL 쪽'])

    def test_missing_windows_folder_reads_wsl_only(self):
        self.write(self.home / '.claude/projects', 'p', '2' * 8, [user('WSL만')])
        self.assertEqual(len(self.sessions()), 1)

    def test_knowledge_heads_and_render(self):
        raw = self.home / 'repo/.knowledge/raw'
        raw.mkdir(parents=True)
        (raw / '2026-11-03.md').write_text('### 10:00 — 보류 규칙 추가\n- 내용\n', encoding='utf-8')
        (raw / '2026-11-04.md').write_text('### 다른 날\n', encoding='utf-8')
        self.write(self.home / '.claude/projects', 'p', '3' * 8, [user('작업'), assistant('끝냈습니다')],
                   cwd=str(self.home / 'repo'))
        data = collect.collect('2026-11-03', prs=False, home=str(self.home), win_projects=str(self.win))
        self.assertEqual(data['knowledge'], [{'file': '~/repo/.knowledge/raw/2026-11-03.md',
                                              'heads': ['10:00 — 보류 규칙 추가']}])
        text = collect.render(data)
        self.assertIn('## ~/repo 33333333 11-03~11-03 (1 prompts)', text)
        self.assertIn('- 11-03 10:00 작업', text)
        self.assertIn('- 마지막 응답: 끝냈습니다', text)
        self.assertNotIn('# PR', text)

    def test_month_period(self):
        self.assertEqual(collect.period_range_utc('2026-10'), ('2026-09-30T15:00', '2026-10-31T15:00'))
        self.assertEqual(collect.period_range_utc('2026-11-03'), ('2026-11-02T15:00', '2026-11-03T15:00'))


if __name__ == '__main__':
    unittest.main()
