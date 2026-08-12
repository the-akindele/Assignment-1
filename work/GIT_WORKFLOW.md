# Git Workflow — quick reference

Your working copy is a real clone of `the-akindele/Assignment-1`. Do all assignment work inside
this folder, then commit and push.

## Everyday loop

```bash
git status                 # what changed
git add <files>            # stage only what you intend (e.g. work/notebooks/w01...ipynb)
git commit -m "short message"
git push                   # sync to GitHub
```

Never `git add .` blindly — it can stage junk. Stage specific files.

## Before each assignment

```bash
git pull                   # get any template changes pushed to your repo
```

## On this machine

- Git is at `C:\Program Files\Git\cmd` and was added to your user PATH (open a new terminal to pick it up).
- Identity is set: `the-akindele` / `114057261+the-akindele@users.noreply.github.com`.
- Pushes use your saved GitHub credential — no re-login needed.
- Don't commit secrets: never `git add .env` or any token-bearing file. The repo CI also blocks dataset CSVs.

## Good commit messages

- `Add week 1 research question`  → what, not how
- `Fix leakage in w03 feature check`
- `Regenerate outputs after model change`

## Undo / fix

```bash
git status                        # see what's staged/unstaged
git restore <file>                # discard uncommitted changes to a file
git reset                          # unstage everything (keeps your edits)
```
