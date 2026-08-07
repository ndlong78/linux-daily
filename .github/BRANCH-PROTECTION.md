# Branch protection baseline for `main`

GitHub branch protection/rulesets should enforce the following policy on `main`:

- Require a pull request before merging.
- Require status checks to pass before merging.
- Required status check: `quality-gate` from `.github/workflows/ci.yml`.
- Require branches to be up to date before merging when GitHub exposes this option for the selected rule type.
- Do not allow force pushes.
- Do not allow branch deletion.
- Apply the rule to administrators as well unless an emergency repository-recovery procedure explicitly requires otherwise.

Optional once the repository has more than one active reviewer:

- Require at least one approving review.
- Require review from CODEOWNERS.
- Dismiss stale approvals when new commits are pushed.

This file documents the intended repository policy because branch-protection settings live in GitHub repository configuration rather than in the Git tree itself.
