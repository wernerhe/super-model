---
description: Run super-prepare-branch - verify the branch is ready to merge or open a PR
---

Use the super-prepare-branch skill to gate-check commit hygiene, rebase preview, and push readiness. The skill reads the `code-review-<sha>` cache marker; if present and HMAC-valid, it skips re-running review.
