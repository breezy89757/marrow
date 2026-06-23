# AGENTS.md

> Instructions and philosophy for AI coding agents developing `marrow`.

Welcome, AI agent! You are here to help build, maintain, and optimize `marrow`. Since this is a project specifically designed to help AI agents work better in engineering teams, we expect you to follow these core guidelines when editing this codebase:

## 1. Core Principles

- **Zero design bloat**: Keep the dependencies minimal. Do not introduce large frameworks (like LangChain, LlamaIndex) unless absolutely necessary.
- **Maintain silent fallbacks**: `marrow` acts as a proxy. If a search query fails, if the database is locked, or if LLM extraction hits a rate limit, **always degrade gracefully**. The developer's primary task (communicating with the LLM) should never be blocked by `marrow`.
- **Frictionless workflow**: Changes to CLI or configuration must keep the "zero configuration, just works" experience. Use reasonable defaults.

## 2. Coding Practices

- **Write comprehensive tests**: For every new feature, API route, or database helper, write corresponding tests in the `tests/` directory using `pytest`.
- **Preserve docstrings & comments**: When modifying files, do not remove explanatory comments or docstrings that describe the architecture or gotchas.
- **SQLite sanity**: Use native SQLite operations. Ensure `FTS5` is handled with safety fallbacks (like falling back to a `LIKE` search if operational syntax fails).
- **Asynchronous boundaries**: Extraction tasks must remain async (`BackgroundTasks`) and never block the main client stream response.

## 3. Database Updates

- If you make schema changes, ensure you add them to the migration/initialization block in [database.py](file:///C:/Users/breez/source/marrow/marrow/database.py). Keep SQLite backwards compatibility in mind.

Thank you for contributing to the collective memory of engineering teams!
