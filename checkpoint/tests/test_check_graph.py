import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('checker', ROOT / 'skills/checkpoint/scripts/check_graph.py')
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)

DONE = '# N1 · ban\n\n## Output Contract\n- Decisions: bitset\n- Files changed: ban.go\n'
READY = '# N2 · console\n\n## Goal\nwire the console\n'


class GraphTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.graph = Path(self.temp.name)
        (self.graph / 'nodes').mkdir()
        (self.graph / 'DECISIONS.md').write_text('', encoding='utf-8')
        self.rows = [('[N1-ban](nodes/N1-ban.md)', 'Done', '—'),
                     ('[N2-console](nodes/N2-console.md)', 'Ready', 'depends_on N1')]
        self.files = {'N1-ban.md': DONE, 'N2-console.md': READY}

    def findings(self):
        table = ['## Nodes', '| Node | Status | Edges | Summary |', '|---|---|---|---|']
        table += [f'| {n} | {s} | {e} | x |' for n, s, e in self.rows]
        (self.graph / 'index.md').write_text('# G\n\n' + '\n'.join(table) + '\n', encoding='utf-8')
        for name, body in self.files.items():
            (self.graph / 'nodes' / name).write_text(body, encoding='utf-8')
        return checker.check(self.graph)

    def messages(self):
        return [f'{sev} {msg}' for sev, msg in self.findings()]

    def test_valid_graph_is_clean(self):
        self.assertEqual(self.findings(), [])

    def test_duplicate_id(self):
        self.rows.append(('[N1-ban](nodes/N1-ban.md)', 'Done', '—'))
        self.assertIn('High N1: listed more than once in index.md', self.messages())

    def test_row_without_file(self):
        self.rows.append(('N3', 'Ready', '—'))
        self.assertIn('High N3: no node file linked or found as nodes/N3-*.md', self.messages())

    def test_row_without_file_found_by_name(self):
        self.rows.append(('N3', 'Ready', '—'))
        self.files['N3-extra.md'] = READY
        self.assertEqual(self.findings(), [])

    def test_empty_output_contract(self):
        self.files['N1-ban.md'] = '# N1 · ban\n\n## Output Contract\n- Decisions:\n- Files changed:\n'
        self.assertIn('Medium N1: done with an Output Contract section left empty', self.messages())

    def test_missing_progress_snapshot(self):
        self.rows[1] = ('[N2-console](nodes/N2-console.md)', 'In Progress', 'depends_on N1')
        self.assertIn('Medium N2: in progress without a Progress Snapshot section', self.messages())

    def test_unknown_status(self):
        self.rows[0] = ('[N1-ban](nodes/N1-ban.md)', 'Finished', '—')
        self.assertIn("Medium N1: unknown status 'Finished'", self.messages())

    def test_handed_off_dependency_is_not_ready(self):
        self.rows[0] = ('[N1-ban](nodes/N1-ban.md)', 'Handed off', '—')
        self.assertIn('Medium N2: Ready but dependency N1 is handed off', self.messages())

    def test_superseded_dependency_asks_for_replacement(self):
        self.rows[0] = ('[N1-ban](nodes/N1-ban.md)', 'Superseded', '—')
        self.assertIn('Medium N2: Ready but dependency N1 is superseded; point the edge at what replaced it',
                      self.messages())

    def test_cycle(self):
        self.rows[0] = ('[N1-ban](nodes/N1-ban.md)', 'Done', 'depends_on N2')
        self.assertIn('High dependency cycle', self.messages())


if __name__ == '__main__':
    unittest.main()
