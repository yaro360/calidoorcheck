#!/usr/bin/env bash
# Push the source branch and publish site/ to the gh-pages branch, then enable GitHub Pages.
# Nightly job: ./publish_next.sh (which calls this after committing one new page).
# Manual: python3 build.py && ./deploy.sh
set -euo pipefail
cd "$(dirname "$0")"

REPO_SLUG="${CALIDOORCHECK_GITHUB_REPO:-yaro360/calidoorcheck}"
REMOTE="${CALIDOORCHECK_GIT_REMOTE:-origin}"
PAGES_BRANCH="gh-pages"

site_url=$(python3 -c 'import json; print(json.load(open("config.json"))["site_url"])')
site_host=$(python3 -c 'import json; from urllib.parse import urlparse; print(urlparse(json.load(open("config.json"))["site_url"]).hostname or "")')
if [[ "$site_url" == *example* ]]; then
  echo "deploy: site_url is still the placeholder. Set it in config.json first." >&2
  exit 1
fi

if [[ ! -f site/index.html ]]; then
  echo "deploy: site/index.html is missing. Run python3 build.py first." >&2
  exit 1
fi
touch site/.nojekyll
if [[ -n "$site_host" && "$site_host" != *.github.io ]]; then
  printf '%s\n' "$site_host" > site/CNAME
fi

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
        --description "CaliDoorCheck: licensed garage door repair directory for Los Angeles and SoCal" \
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
git -C "$work" commit -q -m "Deploy CaliDoorCheck $(date +%Y-%m-%dT%H:%M:%S%z)"
git -C "$work" remote add origin "$(git remote get-url "$REMOTE")"
echo "deploy: force-pushing $PAGES_BRANCH"
git -C "$work" push -f origin "$PAGES_BRANCH"

if [[ "$gh_ok" -eq 1 ]]; then
  if [[ -n "$site_host" && "$site_host" != *.github.io ]]; then
    pages_payload=$(PAGES_BRANCH="$PAGES_BRANCH" SITE_HOST="$site_host" python3 -c 'import json,os; print(json.dumps({"build_type":"legacy","cname":os.environ["SITE_HOST"],"source":{"branch":os.environ["PAGES_BRANCH"],"path":"/"}}))')
  else
    pages_payload=$(PAGES_BRANCH="$PAGES_BRANCH" python3 -c 'import json,os; print(json.dumps({"build_type":"legacy","source":{"branch":os.environ["PAGES_BRANCH"],"path":"/"}}))')
  fi
  if gh api "repos/${REPO_SLUG}/pages" >/dev/null 2>&1; then
    # Make sure Pages is serving from gh-pages root, with custom domain when set.
    printf '%s' "$pages_payload" | gh api --method PUT "repos/${REPO_SLUG}/pages" --input - >/dev/null
  else
    echo "deploy: enabling GitHub Pages from ${PAGES_BRANCH} /"
    # Pushing a CNAME can enable Pages automatically, so POST may 409; fall back to PUT.
    post_err=$(mktemp)
    if ! printf '%s' "$pages_payload" | gh api --method POST "repos/${REPO_SLUG}/pages" --input - >/dev/null 2> "$post_err"; then
      if grep -q 'already enabled' "$post_err"; then
        printf '%s' "$pages_payload" | gh api --method PUT "repos/${REPO_SLUG}/pages" --input - >/dev/null
      else
        cat "$post_err" >&2
        rm -f "$post_err"
        exit 1
      fi
    fi
    rm -f "$post_err"
  fi
  echo "deploy: Pages source is ${PAGES_BRANCH} /"
  if [[ -n "$site_host" && "$site_host" != *.github.io ]]; then
    echo "deploy: custom domain set to $site_host"
    if gh api --method PUT "repos/${REPO_SLUG}/pages" -F https_enforced=true >/dev/null 2>&1; then
      echo "deploy: HTTPS enforcement enabled"
    else
      echo "deploy: HTTPS enforcement not ready yet (certificate may not exist until DNS points at GitHub). Continuing."
    fi
  fi
else
  echo "deploy: pushed ${PAGES_BRANCH}, but gh is not authenticated so Pages could not be enabled via API. Enable it in the repo settings (gh-pages branch, /)." >&2
fi


# Submit the published URLs to IndexNow (Bing, Yandex, and others).
# Do not fail the deploy if the ping errors; the site is already pushed.
if [[ -x ./indexnow.sh ]]; then
  if ./indexnow.sh; then
    echo "deploy: IndexNow ping succeeded"
  else
    echo "deploy: IndexNow ping failed (site was still deployed)." >&2
  fi
fi

echo "deploy: live URL should be ${site_url}/"
