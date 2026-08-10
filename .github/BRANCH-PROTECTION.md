# Branch protection baseline for `main`

GitHub branch protection/rulesets should enforce the following policy on `main`:

- Require a pull request before merging.
- Require status checks to pass before merging.
- Required status check: `quality-gate` from `.github/workflows/ci.yml`.
- Require branches to be up to date before merging when GitHub exposes this option for the selected rule type.
- Do not allow direct pushes to `main`.
- Do not allow force pushes.
- Do not allow branch deletion.
- Apply the rule to administrators as well unless an emergency repository-recovery procedure explicitly requires otherwise.

## Merge method baseline

Normal Linux Daily PRs should use **Squash and merge** so experimental/fixup commits on a feature branch do not pollute `main` history.

Repository merge settings should therefore be:

- Squash merging: **enabled**.
- Merge commits: **disabled** for normal development.
- Rebase merging: **disabled** for normal development.
- Auto-merge: optional only when it still respects required checks and explicit user approval; automation must not enable or perform it by itself.

The final squash subject must be descriptive. For daily content use:

```text
Linux Daily #<NNN>: <tên chủ đề>
```

For maintenance/features use a descriptive subject such as:

```text
Simplify Git and CI workflow hygiene
```

Subjects such as `x`, `tmp`, `test`, `wip`, `placeholder`, `fix`, `update` or `changes` are rejected by PR hygiene.

Optional once the repository has more than one active reviewer:

- Require at least one approving review.
- Require review from CODEOWNERS.
- Dismiss stale approvals when new commits are pushed.

This file documents the intended repository policy because branch-protection and merge-method settings live in GitHub repository configuration rather than in the Git tree itself. `tools/pr_hygiene.py` and `tools/workflow_safety.py` enforce the parts that can be verified from a PR checkout.
