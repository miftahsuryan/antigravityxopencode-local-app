# Prompt Guide — Best Practices

Writing effective prompts is key to getting the best results from AI models. This guide helps you create, organize, and reuse prompts in DevCodex.

## Why Use Prompts?

- **Consistency** — get the same quality output every time
- **Speed** — no need to rewrite similar instructions
- **Organization** — keep your best prompts in one place
- **Sharing** — share proven prompts with your team

## Anatomy of a Good Prompt

```
[Role]     — Who should the AI be?
[Task]     — What should it do?
[Context]  — What background info does it need?
[Format]   — How should the output look?
[Examples] — Show what you want (optional)
```

### Example: Code Review Prompt

```markdown
## Role
You are a senior software engineer reviewing code.

## Task
Review the following code for:
- Bugs or logical errors
- Performance issues
- Security vulnerabilities
- Code style and best practices

## Context
This is a Python REST API using FastAPI and SQLAlchemy.

## Output Format
For each issue found:
1. Line number
2. Issue type (Bug/Performance/Security/Style)
3. Explanation
4. Suggested fix
```

## Prompt Templates by Category

### Code Generation
```
Write a [language] function that [description].
Requirements:
- [requirement 1]
- [requirement 2]
Include error handling and type hints.
```

### Code Explanation
```
Explain this code like I'm a junior developer:
[paste code here]
Focus on:
1. What it does
2. How it works
3. Why this approach was chosen
```

### Debugging
```
I'm getting this error: [error message]
Here's my code: [code]
I've tried: [what you've tried]
What might be causing this and how do I fix it?
```

### API Design
```
Design a REST API for [feature].
Include:
- Endpoint paths
- HTTP methods
- Request/response formats
- Authentication requirements
- Error responses
```

## Tips for Better Prompts

1. **Be specific** — "Write a Python function" is better than "Write code"
2. **Provide context** — tell the AI what project/framework you're using
3. **Use examples** — show the AI what you want, not just describe it
4. **Set constraints** — "Keep it under 50 lines" helps focus output
5. **Iterate** — refine your prompt based on results
6. **Use Markdown** — structure your prompts with headers and lists
7. **Tag properly** — use labels to organize by project or category

## Organizing Prompts in DevCodex

1. **Create Labels** — group by project, tool, or use case
2. **Use Favorites** — mark your most-used prompts with ⭐
3. **Add Tool/Model** — specify which AI model the prompt is for
4. **Copy with One Click** — use the copy button to paste into any AI chat

## Common Mistakes

| Bad Prompt | Better Prompt |
|---|---|
| "Fix my code" | "Find and fix the bug in this Python function that calculates total price with tax" |
| "Write a README" | "Write a README.md for a Python CLI tool that converts CSV to JSON, include install and usage sections" |
| "Make it faster" | "Optimize this SQL query to handle 1M+ rows, explain your approach" |

## Keyboard Shortcuts

| Shortcut | Action |
|---|---|
| `Cmd + N` | Add new prompt |
| `Cmd + F` | Focus search |
