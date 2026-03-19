# Relaytic ChatGPT Connector

Relaytic exposes a host-neutral MCP surface. For ChatGPT, expose that surface as a public HTTPS MCP endpoint.

This is not auto-discovered from the repository. You must register the connector explicitly in ChatGPT once you have a reachable HTTPS `/mcp` URL.

## Local server command

```bash
relaytic interoperability serve-mcp --transport streamable-http --host 127.0.0.1 --port 8000 --mount-path /mcp
```

## Public connector requirement

ChatGPT connectors expect a public HTTPS MCP endpoint. A typical production shape is:

1. Run the Relaytic MCP server locally or in your deployment environment.
2. Put it behind trusted TLS/auth infrastructure.
3. Expose the final endpoint at `/mcp`.
4. Register that public HTTPS URL inside ChatGPT.

Example public MCP URL:

```text
https://example.com/mcp
```

## Safety notes

- Do not commit tokens, headers, or private URLs.
- Relaytic binds to `127.0.0.1` by default; only widen exposure deliberately.
- Keep the remote boundary thin: MCP transport outside, Relaytic artifacts inside.
