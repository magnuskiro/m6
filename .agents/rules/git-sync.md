# Git Synchronization Rule for Multi-Machine Development

Always enforce the following Git workflow on `main` branch:
1. **Start of Task / Session**: Run `git pull origin main` before making any code modifications or analysis.
2. **End of Task / Session**: After making edits or completing a task, stage all changes, create a clear commit message, and push directly to `origin main`:
   ```bash
   git add .
   git commit -m "Auto-sync: <brief description of changes>"
   git push origin main
   ```
