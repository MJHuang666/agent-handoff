#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$repo_root"

fail() {
  printf 'validation error: %s\n' "$*" >&2
  exit 1
}

for required_file in \
  LICENSE README.md README.zh-CN.md CHANGELOG.md CONTRIBUTING.md SECURITY.md \
  shared/.agents/skills/project-role-workflow/SKILL.md \
  shared/.agents/skills/project-role-workflow/references/state-helper.md \
  shared/.agents/skills/project-role-workflow/scripts/workflow_state.py \
  shared/.agents/skills/project-role-workflow/assets/project-template/shared/.agents/skills/project-role-workflow/SKILL.md \
  shared/.agents/skills/project-role-workflow/assets/project-template/shared/.agents/skills/project-role-workflow/scripts/workflow_state.py \
  shared/.agents/skills/project-role-workflow/assets/project-template/locales/zh-CN/docs/agent/protocol.md \
  shared/docs/agent/tasks/_template/STATE.md \
  codex/prompts/replace-agent.md \
  cursor/.cursor/commands/replace-agent.md \
  tests/test_workflow_state.py; do
  test -f "$required_file" || fail "missing required file: $required_file"
done

cmp -s \
  shared/.agents/skills/project-role-workflow/scripts/workflow_state.py \
  shared/.agents/skills/project-role-workflow/assets/project-template/shared/.agents/skills/project-role-workflow/scripts/workflow_state.py \
  || fail "workflow_state.py bootstrap copy differs from source"
test -x shared/.agents/skills/project-role-workflow/scripts/workflow_state.py \
  || fail "workflow_state.py must be executable"

python3 -m unittest discover -v tests

for skill_file in \
  shared/.agents/skills/project-role-workflow/SKILL.md \
  shared/.agents/skills/project-role-workflow/assets/project-template/shared/.agents/skills/project-role-workflow/SKILL.md; do
  test "$(sed -n '1p' "$skill_file")" = '---' || fail "missing frontmatter start: $skill_file"
  sed -n '2,40p' "$skill_file" | grep -Eq '^name: [a-z0-9-]+$' || fail "invalid name field: $skill_file"
  sed -n '2,40p' "$skill_file" | grep -Eq '^description: .+' || fail "missing description field: $skill_file"
done

cmp -s \
  shared/.agents/skills/project-role-workflow/SKILL.md \
  shared/.agents/skills/project-role-workflow/assets/project-template/shared/.agents/skills/project-role-workflow/SKILL.md \
  || fail "bootstrap Skill differs from source"

for tool_id in deepseek-harness opencode; do
  for tool_file in \
    shared/.agents/skills/project-role-workflow/references/initialization.md \
    shared/.agents/skills/project-role-workflow/assets/project-template/shared/.agents/skills/project-role-workflow/references/initialization.md \
    shared/docs/agent/profiles/_templates/participant.md \
    shared/.agents/skills/project-role-workflow/assets/project-template/shared/docs/agent/profiles/_templates/participant.md \
    shared/.agents/skills/project-role-workflow/assets/project-template/locales/zh-CN/docs/agent/profiles/_templates/participant.md \
    shared/.agents/skills/project-role-workflow/assets/project-template/locales/en-US/docs/agent/profiles/_templates/participant.md; do
    grep -Fq "$tool_id" "$tool_file" || fail "missing $tool_id in $tool_file"
  done
done

for integration_file in \
  shared/docs/agent/integrations.md \
  shared/.agents/skills/project-role-workflow/assets/project-template/shared/docs/agent/integrations.md \
  shared/.agents/skills/project-role-workflow/assets/project-template/locales/zh-CN/docs/agent/integrations.md \
  shared/.agents/skills/project-role-workflow/assets/project-template/locales/en-US/docs/agent/integrations.md; do
  grep -Fq 'DeepSeek Harness' "$integration_file" || fail "missing DeepSeek Harness in $integration_file"
  grep -Fq 'OpenCode' "$integration_file" || fail "missing OpenCode in $integration_file"
done

test ! -d shared/.agents/skills/project-role-workflow/assets/project-template/adapters/dsh \
  || fail "DeepSeek Harness must reuse the shared entry, not a duplicate adapter"
test ! -d shared/.agents/skills/project-role-workflow/assets/project-template/adapters/opencode \
  || fail "OpenCode must reuse the shared entry, not a duplicate adapter"

python3 - <<'PY'
from pathlib import Path
import re
import sys

root = Path.cwd()
errors = []
link_re = re.compile(r'(?<!!)\[[^]]*\]\(([^)]+)\)')

for path in list(root.rglob('*.md')) + list(root.rglob('*.mdc')):
    if path.name.startswith('._') or any(part in {'.git', 'dist', '.learnings'} for part in path.parts):
        continue
    text = path.read_text(encoding='utf-8')
    if 'locales/en-US/docs/agent' in str(path):
        if any('\u4e00' <= char <= '\u9fff' for char in text):
            errors.append(f'Chinese text found in English overlay: {path.relative_to(root)}')
    for target in link_re.findall(text):
        target = target.strip().strip('<>').split('#', 1)[0].split('?', 1)[0]
        if not target or target.startswith(('/', '#', 'http:', 'https:', 'mailto:')):
            continue
        if not (path.parent / target).exists():
            errors.append(f'broken local link in {path.relative_to(root)}: {target}')

if errors:
    print('\n'.join(errors), file=sys.stderr)
    sys.exit(1)
PY

metadata_files="$(find . \( -path './.git' -o -path './._.git' -o -path './dist' -o -path './.learnings' \) -prune -o -type f \( -name '._*' -o -name '.DS_Store' \) -print)"
test -z "$metadata_files" || fail "metadata files must not be tracked source: $metadata_files"

bootstrap_example='shared/.agents/skills/project-role-workflow/assets/project-template/shared/docs/agent/tasks/TASK-EXAMPLE-001'
test ! -e "$bootstrap_example" || fail "bootstrap assets must not include TASK-EXAMPLE-001"

build_dir="$(mktemp -d "${TMPDIR:-/tmp}/project-role-workflow-validate.XXXXXX")"
trap 'rm -rf -- "$build_dir"' EXIT
package_root="$build_dir/project-role-workflow-skill-pack"
version="$(tr -d '[:space:]' < distribution/VERSION)"
archive="$build_dir/project-role-workflow-skill-pack-v${version}.zip"
checksum="$archive.sha256"

mkdir -p "$package_root"
cp -R shared "$package_root/shared"
cp -R codex "$package_root/codex"
cp -R cursor "$package_root/cursor"
cp distribution/INSTALL.md distribution/INSTALL_PROMPT.md distribution/VERSION "$package_root/"

(
  cd "$build_dir"
  zip -qr "$archive" project-role-workflow-skill-pack
)
unzip -tqq "$archive"

if command -v sha256sum >/dev/null 2>&1; then
  archive_hash="$(sha256sum "$archive" | awk '{print $1}')"
else
  archive_hash="$(shasum -a 256 "$archive" | awk '{print $1}')"
fi
printf '%s  %s\n' "$archive_hash" "$(basename "$archive")" > "$checksum"
test -s "$checksum" || fail "checksum was not generated"

if unzip -Z1 "$archive" | grep -Eq '(^|/)(\._|\.DS_Store)'; then
  fail "archive contains macOS metadata"
fi
if unzip -Z1 "$archive" | grep -Fq 'assets/project-template/shared/docs/agent/tasks/TASK-EXAMPLE-001'; then
  fail "archive bootstrap assets include TASK-EXAMPLE-001"
fi

printf 'validated source and generated release archive: %s\n' "$archive_hash"
