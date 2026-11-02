import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('checker', ROOT / 'scripts/check_review.py')
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


class TraceabilityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.run = Path(self.temp.name)
        (self.run / 'snapshot').mkdir()
        (self.run / 'reviews').mkdir()
        (self.run / 'snapshot/code.txt').write_bytes(b'original')
        self.docs = {
            'manifest.json': dict(target_id='T', reviewers=['R1', 'R2'], producer='P', judge='J', files=[dict(original='code', snapshot='snapshot/code.txt', sha256=hashlib.sha256(b'original').hexdigest())]),
            'reviews/R1.json': dict(target_id='T', reviewer='R1', status='complete', summary='inspected', findings=[dict(id='R1-001', severity='P1', claim='bug', impact='loss', suggestion='fix', evidence=['code line 1'])]),
            'reviews/R2.json': dict(target_id='T', reviewer='R2', status='complete', summary='inspected', findings=[dict(id='R2-001', severity='P2', claim='same bug', impact='loss', suggestion='fix', evidence=['code line 1'])]),
            'judge.json': dict(target_id='T', judge='J', summary='merged', issues=[dict(id='J-001', source_ids=['R1-001', 'R2-001'], verdict='upheld', severity='P1', reason='reproduced', evidence=['reproduction'])]),
            'producer.json': dict(target_id='T', producer='P', responses=[dict(issue_id='J-001', decision='accept', reason='confirmed', action='fixed', evidence=['patch'])]),
            'verification.json': dict(target_id='T', verifier='J', summary='checked', results=[dict(issue_id='J-001', status='resolved', reason='tested fix', evidence=['run result'])])}

    def run_check(self, phase='verification'):
        for name, value in self.docs.items():
            (self.run / name).write_text(json.dumps(value), encoding='utf-8')
        return checker.check(self.run, phase)

    def test_merged_findings_trace_to_one_issue(self):
        self.assertEqual(self.run_check()['issues'], 1)

    def test_judge_cannot_drop_minority(self):
        self.docs['judge.json']['issues'][0]['source_ids'] = ['R1-001']
        with self.assertRaises(ValueError): self.run_check()

    def test_duplicate_mapping_rejected(self):
        duplicate = copy.deepcopy(self.docs['judge.json']['issues'][0])
        duplicate['id'] = 'J-002'
        self.docs['judge.json']['issues'].append(duplicate)
        with self.assertRaises(ValueError): self.run_check()

    def test_missing_producer_answer_rejected(self):
        self.docs['producer.json']['responses'] = []
        with self.assertRaises(ValueError): self.run_check()

    def test_missing_independent_verification_rejected(self):
        self.docs['verification.json']['results'] = []
        with self.assertRaises(ValueError): self.run_check()

    def test_producer_cannot_name_itself_verifier(self):
        self.docs['verification.json']['verifier'] = 'P'
        with self.assertRaises(ValueError): self.run_check()

    def test_role_overlap_rejected(self):
        self.docs['manifest.json']['judge'] = 'R1'
        with self.assertRaises(ValueError): self.run_check()

    def test_target_mismatch_rejected(self):
        self.docs['judge.json']['target_id'] = 'old-version'
        with self.assertRaises(ValueError): self.run_check()

    def test_snapshot_mutation_rejected(self):
        (self.run / 'snapshot/code.txt').write_bytes(b'changed')
        with self.assertRaises(ValueError): self.run_check()

    def test_snapshot_escape_rejected(self):
        self.docs['manifest.json']['files'][0]['snapshot'] = '../code.txt'
        with self.assertRaises(ValueError): self.run_check()

    def test_failed_reviewer_not_silently_successful(self):
        self.docs['reviews/R2.json']['status'] = 'failed'
        result = self.run_check()
        self.assertFalse(result['all_seats_complete'])
        self.assertEqual(result['failed_reviewers'], ['R2'])

    def test_rejection_does_not_erase_dispute(self):
        self.docs['producer.json']['responses'][0]['decision'] = 'reject'
        self.docs['verification.json']['results'][0]['status'] = 'disputed'
        result = self.run_check()
        self.assertTrue(result['structure_valid'])
        self.assertEqual(result['unresolved'][0]['status'], 'disputed')

    def test_zero_findings_valid(self):
        for key in ('reviews/R1.json', 'reviews/R2.json'):
            self.docs[key]['findings'] = []
        self.docs['judge.json']['issues'] = []
        self.docs['producer.json']['responses'] = []
        self.docs['verification.json']['results'] = []
        self.assertEqual(self.run_check()['issues'], 0)

    def test_unknown_finding_rejected(self):
        self.docs['judge.json']['issues'][0]['source_ids'].append('R3-999')
        with self.assertRaises(ValueError): self.run_check()

    def test_judge_new_issue_needs_origin(self):
        self.docs['judge.json']['issues'].append(dict(id='J-new-1', source_ids=[], verdict='uncertain', severity='P3', reason='new', evidence=['note']))
        with self.assertRaises(ValueError): self.run_check('judge')

    def add_evaluation(self):
        self.docs['manifest.json']['purpose'] = 'evaluation'
        self.docs['reviews/R1.json']['assessments'] = [dict(id='R1-E01', question='Which alternative?', criteria=['User: priority undecided; reviewer proposal: readability'], observation='A is dense; B uses larger text', interpretation='Depends on task', unknowns=['task priority'], next_action='Compare same data')]
        self.docs['judge.json']['assessments'] = [dict(id='A-001', source_ids=['R1-E01'], conclusion='Conditional choice', reason='No priority set', next_action='Compare tasks', decision_owner='user', evidence=['R1-E01'])]
        self.docs['producer.json']['assessment_responses'] = [dict(assessment_id='A-001', reason='Priority belongs to user', action='Prepare comparison; do not choose', evidence=['plan'])]
        self.docs['verification.json']['assessment_results'] = [dict(assessment_id='A-001', status='decision-needed', reason='Preference remains open', evidence=['comparison plan'])]

    def test_conditional_evaluation_preserves_user_choice(self):
        self.add_evaluation()
        result = self.run_check()
        self.assertEqual(result['pending_assessments'], [dict(assessment_id='A-001', status='decision-needed')])

    def test_evaluation_without_defects_is_valid(self):
        self.add_evaluation()
        for key in ('reviews/R1.json', 'reviews/R2.json'): self.docs[key]['findings'] = []
        self.docs['judge.json']['issues'] = []
        self.docs['producer.json']['responses'] = []
        self.docs['verification.json']['results'] = []
        self.assertEqual(self.run_check()['findings'], 0)

    def test_empty_evaluation_purpose_rejected(self):
        self.docs['manifest.json']['purpose'] = 'evaluation'
        with self.assertRaises(ValueError): self.run_check()

    def test_judge_cannot_drop_conditional_advice(self):
        self.add_evaluation()
        del self.docs['judge.json']['assessments']
        with self.assertRaises(ValueError): self.run_check('judge')

    def test_producer_cannot_ignore_evaluation(self):
        self.add_evaluation()
        del self.docs['producer.json']['assessment_responses']
        with self.assertRaises(ValueError): self.run_check('producer')

    def test_verification_cannot_omit_evaluation(self):
        self.add_evaluation()
        del self.docs['verification.json']['assessment_results']
        with self.assertRaises(ValueError): self.run_check()

    def test_evaluation_duplicate_mapping_rejected(self):
        self.add_evaluation()
        other = copy.deepcopy(self.docs['judge.json']['assessments'][0])
        other['id'] = 'A-002'
        self.docs['judge.json']['assessments'].append(other)
        with self.assertRaises(ValueError): self.run_check('judge')

    def test_unknown_evaluation_reference_rejected(self):
        self.add_evaluation()
        self.docs['judge.json']['assessments'][0]['source_ids'] = ['R1-missing']
        with self.assertRaises(ValueError): self.run_check('judge')


if __name__ == '__main__':
    unittest.main(verbosity=2)
