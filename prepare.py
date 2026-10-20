import sys
from pathlib import Path

script = Path(sys.argv[1])
text = script.read_text()
anchor = '\tgit clone --depth=1 --single-branch --branch $PKG_BRANCH "https://github.com/$PKG_REPO.git" $REPO_PATH'
if anchor not in text:
    raise SystemExit('Upstream package clone command changed; review required')
record = '\n\tprintf "%s\\t%s\\t%s\\n" "$PKG_REPO" "$PKG_BRANCH" "$(git -C "$REPO_PATH" rev-parse HEAD)" >> "$GITHUB_WORKSPACE/build-output/third-party-sources.txt"'
script.write_text(text.replace(anchor, anchor + record))
