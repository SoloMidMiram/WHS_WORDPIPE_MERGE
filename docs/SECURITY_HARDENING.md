# Security Hardening

## Purpose
Define the repo policy for secret handling, logging hygiene, and response steps when sensitive material appears in tracked content.

## Secret Handling Policy
- Never commit live credentials, tokens, or private keys.
- Load runtime credentials from environment variables (for example `OPENAI_API_KEY`).
- Keep local secrets in `.env` or equivalent local secret stores; `.env` is git-ignored.
- Use `.env.example` for placeholders only.

## Required Environment Variables
- `OPENAI_API_KEY`
- `OPENAI_MODEL` (optional, defaultable in code)
- `OPENAI_BASE_URL` (optional)
- `OPENAI_ORG` (optional)
- `AI_TOKEN_BUDGET` (optional)
- `OPENAI_PRICE_IN` (optional)
- `OPENAI_PRICE_OUT` (optional)

## Log Safety
- `tools/tool_common.py` redacts secret-like values before appending log lines.
- Redaction is defense-in-depth and does not replace source control hygiene.
- Never rely on logs for secret storage.

## Scanning
Run high-confidence secret scans before commit:

```powershell
python tools/security_scan.py --root . --fail-on-findings
```

Optional targeted grep:

```powershell
rg -n -S "sk-[A-Za-z0-9]{20,}|ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|AKIA[0-9A-Z]{16}" -g "*.py" -g "*.md" -g "*.json" -g "*.log"
```

## Incident Response
If any live secret is discovered in tracked content:
1. Revoke and rotate the credential immediately.
2. Redact the working tree and commit the fix.
3. Purge repository history containing leaked values (`git filter-repo` or BFG).
4. Force-push rewritten history with team coordination.
5. Require downstream consumers to reclone or hard-reset.

## Notes
- Snapshot/canonical immutability is secondary to active secret exposure. Active credentials must be sanitized.
- Keep scan outputs under `_SECURITY/scan_reports/` (git-ignored).
