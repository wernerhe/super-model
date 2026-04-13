---
name: performance-hotspots
description: Catch obvious performance smells in the diff - O(n^2) loops over collections, N+1 query patterns, repeated regex compilation in hot paths, unintentional sync calls in async contexts.
---

# performance-hotspots

## What it does

Pattern-matches the diff for common performance smells:

- **Nested loops over collections:** an inner loop iterates over the same collection the outer loop scans. Linear scan inside a linear scan = quadratic.
- **N+1 queries:** a loop body queries the database per iteration instead of batch-fetching.
- **Repeated compilation:** `re.compile(...)` or template parsing called inside a hot path instead of cached at module level.
- **Sync calls in async contexts:** `time.sleep` in `async def`, blocking IO inside an event loop, etc.

## Severity

- `important` if the hotspot is in a hot path (request handler, render loop).
- `minor` for hotspots in cold paths (setup code, init).

## Fix policy

`fix_with_risk_report` - propose the fix (move regex compile out of the loop, batch the query, use `asyncio.sleep`) with a risk annotation. The user accepts or asks for more analysis.

## What it does NOT catch

- Algorithmic problems (wrong data structure for the operation).
- Memory leaks.
- These need profiling, not static review.

## Idempotency

Read-only.
