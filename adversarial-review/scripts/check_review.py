"""Read-only traceability checks. Does not judge truth, authorize edits, or launch agents."""
import argparse
import hashlib
import json
from pathlib import Path


def need(condition, message):
    if not condition:
        raise ValueError(message)


def load(path):
    result = json.loads(path.read_text(encoding='utf-8-sig'))
    need(isinstance(result, dict), f'{path.name}: object required')
    return result


def text_fields(item, fields):
    need(isinstance(item, dict), 'object required')
    for field in fields:
        need(isinstance(item.get(field), str) and item[field].strip(), f'{field}: nonempty text required')


def array(item, field):
    need(isinstance(item.get(field), list), f'{field}: array required')
    return item[field]


def evidence(item):
    values = array(item, 'evidence')
    need(bool(values) and all(isinstance(v, str) and v.strip() for v in values), 'evidence: nonempty text array required')


def unique(values, label):
    need(all(isinstance(v, str) and v for v in values), f'{label}: text IDs required')
    need(len(values) == len(set(values)), f'{label}: duplicate IDs')


def optional_array(item, field):
    if field not in item:
        return []
    return array(item, field)


def coverage(actual, expected, label):
    unique(actual, label)
    need(set(actual) == set(expected), f'{label}: coverage mismatch')


def safe(root, name):
    need(isinstance(name, str) and name.strip(), 'snapshot path required')
    path = Path(name)
    need(not path.is_absolute(), 'absolute snapshot path')
    result = (root / path).resolve()
    need(result.is_relative_to(root.resolve()), 'snapshot escapes run directory')
    return result


def check(run, phase='verification'):
    need(phase in ('reviews', 'judge', 'producer', 'verification'), 'unknown phase')
    manifest = load(run / 'manifest.json')
    text_fields(manifest, ['target_id', 'producer', 'judge'])
    seats = array(manifest, 'reviewers')
    need(bool(seats), 'at least one reviewer required')
    unique(seats + [manifest['producer'], manifest['judge']], 'roles')
    files = array(manifest, 'files')
    need(bool(files), 'snapshot files required')
    unique([item.get('snapshot') for item in files], 'snapshot files')
    for item in files:
        text_fields(item, ['original', 'snapshot', 'sha256'])
        path = safe(run, item['snapshot'])
        need(hashlib.sha256(path.read_bytes()).hexdigest() == item['sha256'], f"snapshot changed: {item['snapshot']}")
    target = manifest['target_id']
    need(manifest.get('purpose', 'defect-review') in ('defect-review', 'evaluation'), 'unknown review purpose')
    findings, failed, evaluations = [], [], []
    for seat in seats:
        # IDs are file components, never arbitrary paths.
        need(seat.isascii() and seat.replace('-', '').replace('_', '').isalnum(), 'invalid reviewer filename ID')
        review = load(run / 'reviews' / (seat + '.json'))
        need(review.get('target_id') == target and review.get('reviewer') == seat, 'review identity/target mismatch')
        text_fields(review, ['summary'])
        need(review.get('status') in ('complete', 'failed'), 'invalid review status')
        if review['status'] == 'failed':
            failed.append(seat)
        for finding in array(review, 'findings'):
            text_fields(finding, ['id', 'claim', 'impact', 'suggestion'])
            need(finding['id'].startswith(seat + '-'), 'finding ID owner mismatch')
            need(finding.get('severity') in ('P0', 'P1', 'P2', 'P3'), 'invalid severity')
            evidence(finding)
            findings.append(finding['id'])
        for assessment in optional_array(review, 'assessments'):
            text_fields(assessment, ['id', 'question', 'observation', 'interpretation', 'next_action'])
            need(assessment['id'].startswith(seat + '-'), 'assessment ID owner mismatch')
            criteria = array(assessment, 'criteria')
            need(bool(criteria) and all(isinstance(v, str) and v.strip() for v in criteria), 'assessment criteria required')
            need(all(isinstance(v, str) and v.strip() for v in array(assessment, 'unknowns')), 'invalid unknowns')
            evaluations.append(assessment['id'])
    unique(findings, 'findings')
    unique(evaluations, 'assessments')
    need(not set(evaluations) & set(findings), 'assessment/finding IDs overlap')
    if manifest.get('purpose') == 'evaluation':
        need(bool(evaluations), 'evaluation purpose requires assessment output')
    result = dict(structure_valid=True, phase=phase, reviewers=len(seats), failed_reviewers=failed, findings=len(findings))
    result['evaluations'] = len(evaluations)
    result['limitation'] = '누락·연결·snapshot 해시만 검사한다. 역할 신원·독립성·근거 진실성·합의·사용자 승인을 보증하지 않는다.'
    if phase == 'reviews':
        return result
    judge = load(run / 'judge.json')
    need(judge.get('judge') == manifest['judge'] and judge.get('target_id') == target, 'judge identity/target mismatch')
    text_fields(judge, ['summary'])
    issue_ids, covered, severities = [], [], {}
    for issue in array(judge, 'issues'):
        text_fields(issue, ['id', 'reason'])
        need(issue.get('verdict') in ('upheld', 'refuted', 'uncertain'), 'invalid verdict')
        need(issue.get('severity') in ('P0', 'P1', 'P2', 'P3'), 'invalid severity')
        evidence(issue)
        sources = array(issue, 'source_ids')
        unique(sources, 'issue sources')
        if not sources:
            need(issue.get('origin') == 'judge-new', 'new issue origin required')
        need(set(sources) <= set(findings), 'unknown finding reference')
        covered.extend(sources)
        issue_ids.append(issue['id'])
        severities[issue['id']] = issue['severity']
    unique(issue_ids, 'issues')
    unique(covered, 'finding coverage')
    need(set(covered) == set(findings), 'Judge omitted findings')
    result['issues'] = len(issue_ids)
    assessment_ids, assessment_sources = [], []
    for assessment in optional_array(judge, 'assessments'):
        text_fields(assessment, ['id', 'conclusion', 'reason', 'next_action'])
        need(assessment.get('decision_owner') in ('user', 'producer', 'none'), 'invalid decision owner')
        evidence(assessment)
        sources = array(assessment, 'source_ids')
        need(bool(sources), 'Judge assessment needs a source evaluation')
        unique(sources, 'assessment sources')
        assessment_sources.extend(sources)
        assessment_ids.append(assessment['id'])
    unique(assessment_ids, 'Judge assessments')
    coverage(assessment_sources, evaluations, 'Judge evaluation coverage')
    result['assessments'] = len(assessment_ids)
    if phase == 'judge':
        return result
    producer = load(run / 'producer.json')
    need(producer.get('producer') == manifest['producer'] and producer.get('target_id') == target, 'producer identity/target mismatch')
    answered = []
    for response in array(producer, 'responses'):
        text_fields(response, ['issue_id', 'reason', 'action'])
        need(response.get('decision') in ('accept', 'partial', 'reject', 'defer'), 'invalid decision')
        evidence(response)
        answered.append(response['issue_id'])
    unique(answered, 'responses')
    need(set(answered) == set(issue_ids), 'producer response coverage mismatch')
    assessment_answers = []
    for response in optional_array(producer, 'assessment_responses'):
        text_fields(response, ['assessment_id', 'action', 'reason'])
        evidence(response)
        assessment_answers.append(response['assessment_id'])
    coverage(assessment_answers, assessment_ids, 'producer assessment coverage')
    if phase == 'producer':
        return result
    verification = load(run / 'verification.json')
    text_fields(verification, ['verifier', 'summary'])
    need(verification['verifier'] != manifest['producer'], 'producer cannot independently verify itself')
    need(verification.get('target_id') == target, 'verification target mismatch')
    verified, unresolved = [], []
    for item in array(verification, 'results'):
        text_fields(item, ['issue_id', 'reason'])
        need(item.get('status') in ('resolved', 'open', 'disputed', 'not-run'), 'invalid verification status')
        evidence(item)
        verified.append(item['issue_id'])
        if item['status'] != 'resolved':
            unresolved.append(dict(issue_id=item['issue_id'], status=item['status'], severity=severities.get(item['issue_id'])))
    unique(verified, 'verification')
    need(set(verified) == set(issue_ids), 'verification coverage mismatch')
    assessment_checks, pending = [], []
    for item in optional_array(verification, 'assessment_results'):
        text_fields(item, ['assessment_id', 'reason'])
        need(item.get('status') in ('documented', 'open', 'decision-needed', 'not-run'), 'invalid assessment status')
        evidence(item)
        assessment_checks.append(item['assessment_id'])
        if item['status'] != 'documented':
            pending.append(dict(assessment_id=item['assessment_id'], status=item['status']))
    coverage(assessment_checks, assessment_ids, 'verification assessment coverage')
    result['pending_assessments'] = pending
    result.update(unresolved=unresolved, all_seats_complete=not failed)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run', type=Path)
    parser.add_argument('--phase', choices=['reviews', 'judge', 'producer', 'verification'], default='verification')
    args = parser.parse_args()
    try:
        print(json.dumps(check(args.run, args.phase), ensure_ascii=False, indent=2))
        return 0
    except (ValueError, OSError, KeyError, TypeError) as error:
        print(json.dumps(dict(structure_valid=False, error=str(error)), ensure_ascii=False))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
