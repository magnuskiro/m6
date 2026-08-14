# Workspace Guidelines & Git Protocol

## Git Workflow Rules for `magnuskiro/m6`
1. **Pull Before Edit**:
   - Before starting any changes, ALWAYS run `git pull origin main` to ensure local `main` is completely up to date with the remote repository.
2. **Commit and Push After Edit**:
   - Immediately after completing any file edit or feature, stage the changes (`git add .`), write a descriptive commit message (`git commit -m "..."`), and push to remote (`git push origin main`).
3. **Multi-Computer Safety**:
   - The user works directly on `main` across multiple devices. Keeping local changes synchronized immediately prevents merge conflicts and branch drift.

## Privacy & Security Boundaries
- All operations, reads, and writes must remain strictly within `C:\Users\magkir\projects\hus` (or local repo subdirectories).
- Never read, reference, or leak external business/corporate directories.
