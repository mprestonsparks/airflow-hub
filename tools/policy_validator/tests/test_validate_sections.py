import os
import json
import subprocess

def run_validate():
    script = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'validate_policies.py'))
    result = subprocess.run(['python', script], capture_output=True, text=True)
    return json.loads(result.stdout)

def test_decision_hierarchy_conflict():
    data = run_validate()
    sections = data.get('section_conflicts', [])
    dh = [s for s in sections if s['section'] == 'Decision hierarchy']
    assert dh, "Missing Decision hierarchy conflict"
    assert len(dh[0]['files']) == 2
    assert dh[0]['diffs']

def test_appendix_a_missing_conflict():
    data = run_validate()
    ap = [s for s in data.get('section_conflicts', []) if s['section'] == 'Appendix A']
    assert ap, "Missing Appendix A conflict"
    assert any('Missing section Appendix A' in diff for diff in ap[0]['diffs'])

def test_scope_objectives_no_conflict():
    data = run_validate()
    sc = [s for s in data.get('section_conflicts', []) if s['section'] == 'Scope & Objectives']
