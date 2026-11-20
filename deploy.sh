#!/usr/bin/env bash
# Push the source branch and publish site/ to the gh-pages branch, then enable GitHub Pages.
# Nightly job: ./publish_next.sh (which calls this after committing one new page).
# Manual: python3 build.py && ./deploy.sh
set -euo pipefail
cd "$(dirname "$0")"

REPO_SLUG="${FAIRDOORLA_GITHUB_REPO:-yaro360/fairdoorla}"
REMOTE="${FAIRDOORLA_GIT_REMOTE:-origin}"
PAGES_BRANCH="gh-pages"

site_url=$(python3 -c 'import json; print(json.load(open("config.json"))["site_url"])')
if [[ "$site_url" == *fairdoorla.example* ]]; then
  echo "deploy: site_url is still the placeholder. Set it in config.json first." >&2
  exit 1
fi

if [[ ! -f site/index.html ]]; then
  echo "deploy: site/index.html is missing. Run python3 build.py first." >&2
  exit 1
fi
touch site/.nojekyll

# Ensure gh can talk to GitHub when we need to create the repo or enable Pages.
gh_ok=0
if command -v gh >/dev/null 2>&1 && gh auth status >/dev/null 2>&1; then
  gh_ok=1
  gh auth setup-git >/dev/null 2>&1 || true
fi

if ! git remote get-url "$REMOTE" >/dev/null 2>&1; then
  if [[ "$gh_ok" -eq 1 ]]; then
    if ! gh repo view "$REPO_SLUG" >/dev/null 2>&1; then
      echo "deploy: creating public repo $REPO_SLUG"
      # --source/--remote only when creating from this checkout; add remote ourselves for clarity.
      gh repo create "$REPO_SLUG" --public \
        --description "FairDoorLA: licensed garage door repair directory for Los Angeles and SoCal" \
        --disable-wiki
    fi
    git remote add "$REMOTE" "https://github.com/${REPO_SLUG}.git"
  else
    echo "deploy: no '$REMOTE' remote, and gh is not authenticated, so the GitHub repo cannot be created or pushed to." >&2
    exit 1
  fi
fi

source_branch=$(git rev-parse --abbrev-ref HEAD)
echo "deploy: pushing $source_branch to $REMOTE"
git push -u "$REMOTE" "$source_branch"

# Publish only site/ contents to gh-pages (orphan commit, force-push).
work=$(mktemp -d)
cleanup() { rm -rf "$work"; }
trap cleanup EXIT
cp -a site/. "$work/"
# Ensure we don't carry over a nested .git if one ever appears under site/
rm -rf "$work/.git"
git -C "$work" init -q
git -C "$work" checkout -q -b "$PAGES_BRANCH"
name=$(git config user.name || true)
email=$(git config user.email || true)
if [[ -z "${name}" ]]; then name=$(git log -1 --format='%an'); fi
if [[ -z "${email}" ]]; then email=$(git log -1 --format='%ae'); fi
git -C "$work" config user.name "$name"
git -C "$work" config user.email "$email"
# Avoid signing issues in this throwaway repo
git -C "$work" config commit.gpgsign false
git -C "$work" add -A
if git -C "$work" diff --cached --quiet; then
  echo "deploy: site/ is empty, aborting." >&2
  exit 1
fi
git -C "$work" commit -q -m "Deploy FairDoorLA $(date +%Y-%m-%dT%H:%M:%S%z)"
git -C "$work" remote add origin "$(git remote get-url "$REMOTE")"
echo "deploy: force-pushing $PAGES_BRANCH"
git -C "$work" push -f origin "$PAGES_BRANCH"

if [[ "$gh_ok" -eq 1 ]]; then
  if gh api "repos/${REPO_SLUG}/pages" >/dev/null 2>&1; then
    # Make sure Pages is serving from gh-pages root.
    gh api --method PUT "repos/${REPO_SLUG}/pages" \
      --input - >/dev/null <<JSON
{"build_type":"legacy","source":{"branch":"${PAGES_BRANCH}","path":"/"}}
JSON
  else
    echo "deploy: enabling GitHub Pages from ${PAGES_BRANCH} /"
    gh api --method POST "repos/${REPO_SLUG}/pages" \
      --input - >/dev/null <<JSON
{"build_type":"legacy","source":{"branch":"${PAGES_BRANCH}","path":"/"}}
JSON
  fi
  echo "deploy: Pages source is ${PAGES_BRANCH} /"
else
  echo "deploy: pushed ${PAGES_BRANCH}, but gh is not authenticated so Pages could not be enabled via API. Enable it in the repo settings (gh-pages branch, /)." >&2
fi

echo "deploy: live URL should be ${site_url}/"
