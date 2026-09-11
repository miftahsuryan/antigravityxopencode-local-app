# API References — Quick Guide

Store your API keys, endpoints, and auth details securely.

## How It Works

1. **Save endpoint** — store base URL and auth type
2. **Store key securely** — API keys are saved in macOS Keychain (never in database)
3. **Copy with one click** — URL or key copied instantly

## API Key Security

- **Keys are stored in Keychain** — never saved as plain text
- **Key name is stored** — only the reference name in the database
- **Copy button** — use the key icon to copy the secret value
- **URL button** — use the copy icon to copy the endpoint URL

## Common API Patterns

### REST API
```
Base URL: https://api.example.com/v1
Auth: Bearer Token
Headers:
  Authorization: Bearer <token>
  Content-Type: application/json
```

### OpenAI
```
Base URL: https://api.openai.com/v1
Auth: API Key
Model: gpt-4, gpt-3.5-turbo
Docs: https://platform.openai.com/docs
```

### GitHub API
```
Base URL: https://api.github.com
Auth: Bearer Token (Personal Access Token)
Docs: https://docs.github.com/en/rest
Rate limit: 5000 requests/hour
```

### Anthropic (Claude)
```
Base URL: https://api.anthropic.com/v1
Auth: API Key
Model: claude-3-opus, claude-3-sonnet
Docs: https://docs.anthropic.com/claude/reference
```

## Tips

- **Use descriptive names** — "OpenAI Production" vs "key1"
- **Add auth type** — helps remember how to authenticate
- **Store base URL** — don't forget the version prefix (/v1, /v2)
- **Separate keys** — use different keys for dev and production
- **Rotate regularly** — update keys periodically for security
