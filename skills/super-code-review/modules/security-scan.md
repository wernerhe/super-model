---
name: security-scan
description: Scan the diff for common security smells - plaintext secrets, shell injection, unvalidated user input flowing to dangerous sinks, dependency vulnerabilities. Critical findings block READY-TO-MERGE verdict.
---

# security-scan

## What it does

Pattern-matches the diff for high-signal security concerns:

- **Plaintext secrets:** API keys, tokens, passwords committed in code or config. Patterns: `AKIA[0-9A-Z]{16}`, `sk_live_*`, `ghp_*`, `bearer_*`, etc.
- **Shell injection:** unescaped variable interpolation into shell commands (`os.system(f"cmd {user_input}")`, `Runtime.exec("cmd " + user)`).
- **Unvalidated user input flowing to dangerous sinks:** SQL string concatenation, eval / exec on attacker-influenced data, deserialization (`pickle.loads`, `yaml.load` without safe-loader, `eval`).
- **Dependency vulnerabilities:** check `pyproject.toml` / `package.json` against known-vulnerable version databases.

## Severity

- `critical` for any plaintext secret, eval-on-user-input, or critical CVE in a dependency.
- `important` for shell injection patterns and high CVEs.
- `minor` for moderate CVEs and stylistic risk patterns.

## Fix policy

- Plaintext secrets: `never` (auto-fix could push the leak history into git remotely; humans must rotate the secret AND scrub history).
- Other issues: `fix_with_confirm` - propose the safe variant (parameterized query, `subprocess` with list args, `yaml.safe_load`) and ask.

## Hard rule

Any `critical` finding from this module blocks a READY-TO-MERGE verdict. The verdict downgrades to NEEDS-FIXES.

## Idempotency

Read-only.
