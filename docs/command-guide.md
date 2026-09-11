# Command Snippets — Quick Reference

Store your most-used terminal commands here for quick access.

## How It Works

1. **Save** — store commands with a clear title and description
2. **Label** — organize by project or category (docker, git, npm, etc.)
3. **Copy** — one-click copy to clipboard, paste in terminal

## Common Commands

### Git
```bash
git add . && git commit -m "message"
git push origin main
git pull --rebase origin main
git log --oneline -10
git status
git diff --staged
git stash && git stash pop
```

### Docker
```bash
docker ps -a
docker compose up -d
docker compose down
docker logs -f <container>
docker exec -it <container> sh
docker system prune -a
```

### NPM / Node
```bash
npm install
npm run dev
npm run build
npm test
npx prisma generate
npx prisma migrate dev
```

### Python
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m pytest tests/ -v
python -m ruff check src/
python -m mypy src/
```

### System
```bash
# Find port usage
lsof -i :3000

# Kill process on port
kill -9 $(lsof -t -i:3000)

# Disk usage
du -sh *

# Quick HTTP server
python -m http.server 8000
```

## Tips

- **Add descriptions** — explain what the command does and when to use it
- **Use labels** — tag by project (backend, frontend) or tool (docker, git)
- **Copy safety** — always review before pasting into production terminals
