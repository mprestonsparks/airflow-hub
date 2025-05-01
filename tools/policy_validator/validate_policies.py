#!/usr/bin/env python3

import os
import sys
import json
import frontmatter

def main():
    schema_errors = []
    policy_map = {}
    script_dir = os.path.dirname(os.path.realpath(__file__))
    docs_dir = os.path.abspath(os.path.join(script_dir, os.pardir, os.pardir, 'docs'))

    # Recursively scan all Markdown files under docs/
    for root, dirs, files in os.walk(docs_dir):
        for fname in files:
            if not fname.endswith('.md'):
                continue
            path = os.path.join(root, fname)
            try:
                post = frontmatter.load(path)
            except Exception as e:
                schema_errors.append({
                    "file": path,
                    "error": f"Failed to parse frontmatter: {e}"
                })
                continue

            metadata = post.metadata or {}
            if 'policies' not in metadata:
                continue

            policies = metadata.get('policies')
            if not isinstance(policies, list):
                schema_errors.append({
                    "file": path,
                    "error": "`policies` is not a list"
                })
                continue

            # Validate schema of each policy entry
            valid = True
            for idx, policy in enumerate(policies):
                if not isinstance(policy, dict):
                    schema_errors.append({
                        "file": path,
                        "error": f"Policy at index {idx} is not an object"
                    })
                    valid = False
                    break
                name = policy.get('name')
                rules = policy.get('rules')
                if not isinstance(name, str):
                    schema_errors.append({
                        "file": path,
                        "error": f"`name` of policy at index {idx} is not a string"
                    })
                    valid = False
                    break
                if not isinstance(rules, list) or not all(isinstance(r, str) for r in rules):
                    schema_errors.append({
                        "file": path,
                        "error": f"`rules` of policy '{name}' is not a list of strings"
                    })
                    valid = False
                    break

            if not valid:
                continue

            # Collect valid policies
            for policy in policies:
                name = policy['name']
                rules = tuple(policy['rules'])
                policy_map.setdefault(name, {}).setdefault(rules, []).append(path)

    # Detect conflicts: same policy name with differing rule lists
    conflicts = []
    for name, rules_dict in policy_map.items():
        if len(rules_dict) > 1:
            occurrences = []
            for rules, file_list in rules_dict.items():
                for fpath in file_list:
                    occurrences.append({
                        "file": fpath,
                        "rules": list(rules)
                    })
            conflicts.append({
                "policy": name,
                "occurrences": occurrences
            })

    # Section extraction and conflict detection across docs sections
    import re
    import difflib
    from collections import Counter

    section_names = {
        "Decision hierarchy": r"^##\\s*1\\s+Decision hierarchy",
        "Scope & Objectives": r"^##\\s*2\\s+Scope & Objectives",
        "Appendix A": r"^##+\\s*Appendix A"
    }
    section_texts = {name: {} for name in section_names}
    for root, dirs, files in os.walk(docs_dir):
        for fname in files:
            if not fname.endswith('.md'):
                continue
            fpath = os.path.join(root, fname)
            try:
                post = frontmatter.load(fpath)
                body = post.content
            except:
                with open(fpath, 'r', encoding='utf-8') as f:
                    content = f.read()
                body = re.sub(r'^---.*?---\\s*', '', content, flags=re.DOTALL)
            for name, pattern in section_names.items():
                regex = re.compile(pattern, flags=re.MULTILINE)
                m = regex.search(body)
                if m:
                    start = m.end()
                    if name in ["Decision hierarchy", "Scope & Objectives"]:
                        next_m = re.search(r"^##\\s+", body[start:], flags=re.MULTILINE)
                    else:
                        next_m = re.search(r"^##+", body[start:], flags=re.MULTILINE)
                    end = start + next_m.start() if next_m else len(body)
                    section = body[start:end]
                    lines = [re.sub(r'\\s+', ' ', line).strip() for line in section.splitlines()]
                    norm = "\\n".join([l for l in lines if l])
                else:
                    norm = None
                section_texts[name][fpath] = norm

    section_conflicts = []
    for name, texts in section_texts.items():
        counter = Counter(texts.values())
        if len(counter) <= 1:
            continue
        majority, _ = counter.most_common(1)[0]
        conflict_files = []
        diffs = []
        for fpath, text in texts.items():
            if text != majority:
                conflict_files.append(fpath)
                if text is None:
                    diffs.append(f"Missing section {name}")
                else:
                    diff = "\\n".join(difflib.unified_diff(
                        majority.splitlines(),
                        text.splitlines(),
                        fromfile='canonical',
                        tofile=fpath,
                        lineterm=''
                    ))
                    diffs.append(diff)
        section_conflicts.append({
            "section": name,
            "files": conflict_files,
            "diffs": diffs
        })

    # Output results
    result = {
      "schema_errors": schema_errors,
      "conflicts": conflicts,
      "section_conflicts": section_conflicts
    }
    print(json.dumps(result, indent=2))

    # Exit code: 0 if no errors or conflicts, 1 otherwise
    if schema_errors or conflicts:
        sys.exit(1)
    sys.exit(0)

if __name__ == '__main__':
    main()