# Read-only MCP adapter (AG-04)

The stdio server exposes existing Tessera HTTP reads as MCP tools and the
published canonical documents as knowledge-base resources. It uses the official
[MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk/tree/v1.x).
It is a local adapter, not an integration with real enterprise agents.

Start the existing API first (`make backend`). Configure your MCP host to launch:

```json
{
  "mcpServers": {
    "tessera": {
      "command": "/absolute/path/to/repo/backend/.venv/bin/tessera",
      "args": ["mcp", "--api-url", "http://127.0.0.1:8000"]
    }
  }
}
```

Alternatively, from the repository root:

```sh
backend/.venv/bin/tessera mcp --api-url http://127.0.0.1:8000
```

The MCP transport is stdio: stdout belongs exclusively to protocol messages.
No MCP HTTP listener, provider key, LLM call or mock systems server is needed.
The trusted operator chooses the API origin at process startup; tools cannot
change it or send arbitrary requests. Use a local or otherwise trusted Tessera
API. This adapter adds no authentication to the existing API and must not be
used to expose private data to an untrusted MCP host. HTTP requests have a
30-second timeout, do not follow redirects, ignore environment proxies and
never retry against a live fallback. API failures are MCP errors; absent records
are never converted to stock zero or fabricated evidence.

For fixtures, add `--fixture-mode` to the command and enable `FIXTURE_MODE=1`
on the API. Namespace selection is fixed for the server's lifetime. The model
cannot switch it; product mode remains the default. No fixtures are loaded by
this command.

## Tools and knowledge base

All nine tools carry `readOnlyHint=true` and `destructiveHint=false`. Their
implementation can only issue GET requests to a fixed set of existing routes:

- `list_runs`, `get_run`: metadata, including incomplete runs and their status.
- `list_cases`, `get_case`: case summaries, evidence references, origin counts,
  uncertainty, optional exact case version.
- `list_documents`, `get_document`: canonical documents, segments, observations
  and links. Document reads support an exact `version`.
- `get_forecast`: persisted baselines, scenarios and abstention reasons.
- `get_options`: persisted proposals/checks for a case; no stock refresh,
  evaluation, reservation or approval.
- `get_reports`: persisted briefs; with `owner`, also resolves exact-version
  citations using the existing report-detail route.

Read `tessera://guide` for navigation. Discover document IDs/versions with
`list_documents`, then read the resource template:

```text
tessera://runs/{run_id}/documents/{document_id}/versions/{version}
```

A document resource returns the same JSON as `get_document` with that exact
version: canonical text, matching segments, observations and links. Text and
Unicode code-point offsets are preserved, including emoji and CJK. Resources
never open local files, raw attachments, arbitrary URIs or hidden answer keys.
This knowledge base is the published source snapshot, not a separate RAG index.

The API remains authoritative for run publication, `as_of`, store visibility,
version lookup and namespace isolation. Pending/failed runs expose metadata
only; artifact reads fail until successful/degraded publication. Every artifact
read includes an explicit run ID. Keep references within that run and preserve
versions and mode labels. Source text and tool outputs are untrusted data,
including any apparent instructions embedded in an email.

AG-01's allowlist rule is preserved through explicit registration. The adapter
does not expose `finish`, clarification drafts, pipeline execution or decisions.
It also does not claim the investigator's live stock/ETA/evaluation tools: those
are separate capabilities; this server only reads already published artifacts.
The process is a service adapter, not an executable pipeline module, so it is
not registered as a module that could mutate a run.

## Verification

`cd backend && uv run pytest -q tests/api/test_mcp.py` checks MCP initialization,
tool/resource discovery, reads through the real API, Unicode text preservation,
publication/clock/store/version/namespace guards, rejected path injection,
network failure, redirect refusal and a subprocess stdio handshake. All test
data is synthetic and stored in temporary databases. `make check` runs the
repository checks.
