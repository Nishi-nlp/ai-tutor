---
name: guided-issue-implementation
description: Guide learning-oriented implementation of an ai-tutor issue. Use when the user wants to understand the concepts and design before Codex implements, tests, explains, or prepares a PR. Do not use for quick Git commands, status checks, or reviews that do not request implementation.
---

# Guided Issue Implementation

Help the user build engineering judgment while completing one issue at a time.

## Before implementation

1. Read the issue and inspect the relevant repository state without changing files.
2. Explain in plain Japanese:
   - concepts needed for the issue;
   - realistic implementation options and their tradeoffs;
   - the recommended approach and why it fits the current MVP;
   - questions the user should think through first.
3. Define the intended scope and explicit non-goals.
4. Stop and wait for the user's confirmation. Treat clear replies such as `進めて` or `実装して` as confirmation.

Do not reveal a large finished implementation during this phase. Use small illustrative snippets only when they help explain a concept.

## Implement after confirmation

1. Recheck the active branch, worktree, and uncommitted changes before editing.
2. Keep each issue isolated. Do not mix changes from another issue or silently edit a detached worktree when the user intends to commit from a named branch.
3. Preserve existing user changes and restrict edits to the agreed scope.
4. Implement the smallest coherent solution and add tests for the required behavior and important failure paths.
5. Run the repository's relevant tests, lint, formatting checks, and diff checks.
6. Never commit, push, merge, open a PR, or change project tracking unless the user explicitly requests that action.

If Codex is working in an isolated worktree, state the exact path. Before telling the user to commit, verify that the changes exist in the branch and directory where the user will run Git commands.

## Teach from the result

After implementation, explain:

- what changed and why;
- how data and control flow through the important code;
- transaction, error-handling, and persistence boundaries when relevant;
- what each meaningful test proves and what it does not prove;
- commands the user can run to verify the result;
- remaining non-goals and appropriate follow-up issues.

Prefer questions that test causal understanding over vocabulary. When the user answers, distinguish precise understanding from partially correct intuition and explain the gap.

## PR support

Let the user draft the PR first when they want practice. Evaluate whether the PR communicates purpose, behavior, design decisions, verification evidence, and non-goals. Correct factual mismatches with the actual diff and test results. Provide a polished replacement only when requested or when concrete corrections are needed.

For code review, prioritize correctness, data loss, transaction boundaries, idempotency, concurrency, security, error handling, and regression risk before style preferences.
