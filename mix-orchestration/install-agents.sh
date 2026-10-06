#!/bin/sh
# Install the mixed orchestrator profile and three native specialist roles.
# Usage: sh ./install-agents.sh [codex-home]
set -eu

if [ "$#" -gt 1 ]; then
  printf 'Usage: sh %s [codex-home]\n' "$0" >&2
  exit 2
fi

package_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
config_root=${1:-${CODEX_HOME:-"$HOME/.codex"}}
case "$config_root" in
  /*) ;;
  *) config_root="$PWD/$config_root" ;;
esac
files='orchestrator-mix.config.toml
agents/dev-advisor.toml
agents/dev-debugger.toml
agents/dev-reviewer.toml'

# Check every source and destination before copying anything.
for file in $files; do
  if [ ! -f "$package_dir/$file" ]; then
    printf 'Missing configuration file: %s\n' "$package_dir/$file" >&2
    exit 1
  fi
  if [ -d "$config_root/$file" ] && [ ! -L "$config_root/$file" ]; then
    printf 'Expected a file, found a directory: %s\n' "$config_root/$file" >&2
    exit 1
  fi
done

mkdir -p "$config_root/agents"
backup_dir=
for file in $files; do
  source_file="$package_dir/$file"
  target_file="$config_root/$file"
  if [ ! -L "$target_file" ] && [ -f "$target_file" ] && cmp -s "$source_file" "$target_file"; then
    printf 'Unchanged: %s\n' "$target_file"
    continue
  fi

  if [ -e "$target_file" ] || [ -L "$target_file" ]; then
    if [ -z "$backup_dir" ]; then
      mkdir -p "$config_root/backups/orchestration-mix-agents"
      backup_dir=$(mktemp -d "$config_root/backups/orchestration-mix-agents/$(date -u +%Y%m%dT%H%M%SZ).XXXXXX")
    fi
    mv "$target_file" "$backup_dir/${file##*/}"
  fi

  cp "$source_file" "$target_file"
  chmod 644 "$target_file"
  printf 'Installed: %s\n' "$target_file"
done

if [ -n "$backup_dir" ]; then
  printf 'Previous files backed up to: %s\n' "$backup_dir"
fi
