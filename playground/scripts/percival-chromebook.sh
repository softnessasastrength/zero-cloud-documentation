#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="${PERCIVAL_CHROMEBOOK_DIR:-$HOME/.local/share/percival-chromebook}"
METRO="$ROOT/metro"
PERCIVAL="$ROOT/percival"
NODE_VERSION=22.23.5
NODE="$ROOT/node-v$NODE_VERSION"
API_PID=
WEB_PID=
OLLAMA_PID=

cleanup() {
  local pid
  for pid in "$WEB_PID" "$API_PID" "$OLLAMA_PID"; do
    if [[ -n "$pid" ]]; then
      kill "$pid" 2>/dev/null || true
      wait "$pid" 2>/dev/null || true
    fi
  done
  API_PID= WEB_PID= OLLAMA_PID=
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

packages() {
  [[ "${PERCIVAL_SKIP_PACKAGES:-}" == 1 ]] && return
  local package missing=()
  for package in "$@"; do
    if ! dpkg-query -W -f='${Status}' "$package" 2>/dev/null | grep -qx 'install ok installed'; then
      missing+=("$package")
    fi
  done
  if (("${#missing[@]}")); then
    sudo apt-get update
    sudo apt-get install -y "${missing[@]}"
  fi
}

checkout() {
  local repo=$1 branch=$2 commit=$3 dest=$4
  local remote="https://github.com/softnessasastrength/$repo.git"
  if [[ ! -e "$dest" ]]; then
    git clone --branch "$branch" "$remote" "$dest"
    git -C "$dest" switch --detach "$commit"
  fi
  if [[ "$(git -C "$dest" remote get-url origin 2>/dev/null)" != "$remote" ||
        "$(git -C "$dest" rev-parse HEAD 2>/dev/null)" != "$commit" ||
        -n "$(git -C "$dest" status --porcelain --untracked-files=no 2>/dev/null)" ]]; then
    printf 'Existing checkout differs from the pinned version. Preserved %s\n' "$dest" >&2
    exit 1
  fi
}

install_node() {
  if [[ "${PERCIVAL_USE_SYSTEM_NODE:-}" == 1 ]]; then
    node -e 'if(Number(process.versions.node.split(".")[0])<22)process.exit(1)' || return 1
    NODE=$(dirname "$(dirname "$(command -v node)")")
    return
  fi
  [[ -x "$NODE/bin/node" && -x "$NODE/bin/npm" ]] && return
  local arch
  case "$(uname -m)" in
    x86_64) arch=x64 ;;
    aarch64) arch=arm64 ;;
    *) printf 'Unsupported Linux architecture.\n' >&2; exit 1 ;;
  esac
  (
    temp=$(mktemp -d "$ROOT/node-download.XXXXXXXX")
    trap 'rm -rf -- "$temp"' EXIT
    cd "$temp"
    archive="node-v$NODE_VERSION-linux-$arch.tar.xz"
    curl -fsSLO "https://nodejs.org/dist/v$NODE_VERSION/$archive"
    curl -fsSLO "https://nodejs.org/dist/v$NODE_VERSION/SHASUMS256.txt"
    awk -v file="$archive" '$2 == file' SHASUMS256.txt | sha256sum --check
    mkdir extracted
    tar -xJf "$archive" --strip-components=1 -C extracted
    mv -T extracted "$NODE"
  )
}

await_http() {
  local url=$1 pid=$2
  for ((attempt=0; attempt<40; attempt++)); do
    kill -0 "$pid" 2>/dev/null || break
    if curl -fsS --max-time 1 "$url" >/dev/null 2>&1; then
      return
    fi
    sleep 0.25
  done
  printf 'Could not start %s. Check the server output above.\n' "$url" >&2
  exit 1
}

metro() {
  local mode=$1 port=$2 vite_args=()
  packages git curl ca-certificates xz-utils
  checkout zero-cloud-documentation feat/metro-resort-ui e5c301cb2fd0dbc0c6f2acf6195260455bef2d50 "$METRO"
  install_node
  local PATH="$NODE/bin:$PATH"
  export PATH
  cd "$METRO/playground"
  if [[ ! -f node_modules/.percival-setup-complete ]]; then
    npm ci
    touch node_modules/.percival-setup-complete
  fi
  if [[ "$mode" == preview ]]; then
    npm run build
    vite_args+=(preview)
  fi

  # Refuse to reuse a service already listening on either port.
  local port_to_check
  for port_to_check in 4174 "$port"; do
    if node -e 'const s=require("node:net").createServer(); s.on("error",()=>process.exit(1)); s.listen(Number(process.argv[1]),"127.0.0.1",()=>s.close())' "$port_to_check"; then
      continue
    fi
    printf 'Local port %s is already in use. Stop the other server and retry.\n' "$port_to_check" >&2
    exit 1
  done
  HOST=127.0.0.1 PORT=4174 node --import tsx simulator/server.mjs &
  API_PID=$!
  await_http http://127.0.0.1:4174/api/health "$API_PID"
  ZERO_CLOUD_API_PORT=4174 node node_modules/vite/bin/vite.js "${vite_args[@]}" \
    --host 127.0.0.1 --port "$port" --strictPort &
  WEB_PID=$!
  await_http "http://127.0.0.1:$port/api/health" "$WEB_PID"

  printf '\nOpen in ChromeOS Chrome: http://localhost:%s/#/resort\n' "$port"
  if [[ "$mode" == preview ]]; then
    printf 'Install from the address bar or Chrome menu → Cast, save, and share → Install page as app.\n'
  fi
  printf 'Synthetic resort data. Keep this Terminal open. Press Ctrl+C to stop.\n'
  wait -n "$WEB_PID" "$API_PID"
}

transit() {
  packages git curl ca-certificates xz-utils python3 python3-venv tzdata
  local ref=${PERCIVAL_TRANSIT_REF:-feat/percival-metro-preview}
  local version=${ref//\//-}
  local preview="${PERCIVAL_TRANSIT_LOCAL_CHECKOUT:-$ROOT/transit-previews/$version}" store="$ROOT/transit-data"
  local remote=https://github.com/softnessasastrength/zero-cloud-documentation.git
  mkdir -p "$ROOT/transit-previews" "$store"
  if [[ ! -e "$preview" ]]; then
    git clone --no-checkout "$remote" "$preview"
    git -C "$preview" fetch origin "$ref"
    git -C "$preview" checkout --detach FETCH_HEAD
  fi
  if [[ "$(git -C "$preview" remote get-url origin | sed 's/\.git$//')" != "${remote%.git}" || -n "$(git -C "$preview" status --porcelain --untracked-files=no)" ]]; then
    printf 'Existing Transit checkout differs or contains edits; preserved %s\n' "$preview" >&2
    return 1
  fi
  if [[ "$ref" =~ ^[0-9a-f]{40}$ && "$(git -C "$preview" rev-parse HEAD)" != "$ref" ]]; then
    printf 'Transit checkout does not match the pinned commit; preserved %s\n' "$preview" >&2
    return 1
  fi
  install_node
  local PATH="$NODE/bin:$PATH"
  export PATH
  cd "$preview/transit"
  python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3,11) else 1)'
  if [[ ! -x .venv/bin/python ]]; then python3 -m venv .venv; fi
  local consent feed
  printf '\nOfficial static schedule terms:\nCTtransit: https://www.cttransit.com/about/developers/terms-of-use\nPVTA: https://pvta.com/bus_service/real_time_data.php\n'
  if [[ "${PERCIVAL_TRANSIT_ACCEPT_TERMS:-}" == yes ]]; then consent=y; else
    read -r -p 'After reviewing these terms, accept and refresh the official feeds? [y/N] ' consent
  fi
  if [[ "$consent" == [yY] ]]; then
    for feed in rail cttransit pvta; do
      .venv/bin/python -m percival_transit --store "$store" import --feed "$feed" --accept-source-terms || printf 'Refresh failed for %s; retaining its last valid snapshot.\n' "$feed"
    done
  fi
  # Separate preview ports; never reuse or terminate an existing Metro service.
  local port
  for port in 8765 4183; do
    node -e 'const s=require("node:net").createServer();s.on("error",()=>process.exit(1));s.listen(Number(process.argv[1]),"127.0.0.1",()=>s.close())' "$port" || { printf 'Port %s is occupied; existing service preserved.\n' "$port"; return 1; }
  done
  .venv/bin/python -m percival_transit --store "$store" serve --port 8765 &
  API_PID=$!
  await_http http://127.0.0.1:8765/v1/health "$API_PID"
  cd "$preview/playground"
  if [[ ! -f node_modules/.percival-setup-complete ]]; then npm ci; touch node_modules/.percival-setup-complete; fi
  npm run build
  PERCIVAL_TRANSIT_PORT=8765 node node_modules/vite/bin/vite.js preview --host 127.0.0.1 --port 4183 --strictPort &
  WEB_PID=$!
  await_http http://127.0.0.1:4183/transit-api/v1/health "$WEB_PID"
  printf '\nOpen Chrome: http://localhost:4183/#/transit\nScheduled data only. Ollama is not required. Ctrl+C stops only this preview.\n'
  if command -v xdg-open >/dev/null; then xdg-open "http://localhost:4183/#/transit" >/dev/null 2>&1 || true; fi
  wait -n "$WEB_PID" "$API_PID"
}

chat() {
  packages git curl ca-certificates python3 python3-venv
  python3 -c 'import sys; sys.exit(None if sys.version_info >= (3, 11) else "Percival requires Python 3.11 or newer.")'
  checkout percival feature/model-agents 4d0efd9bedeae255351556a0430a3bd883740ff8 "$PERCIVAL"
  cd "$PERCIVAL"
  if [[ ! -f .venv/.percival-setup-complete ]]; then
    python3 -m venv .venv
    .venv/bin/python -m pip install -e .
    touch .venv/.percival-setup-complete
  fi
  if ! command -v ollama >/dev/null; then
    local consent
    read -r -p 'Install Ollama with its official Linux installer? [y/N] ' consent
    [[ "$consent" == [yY] ]] || return 0
    (set -o pipefail; curl -fsSL https://ollama.com/install.sh | sh)
  fi
  export OLLAMA_HOST=127.0.0.1:11434
  if ! curl -fsS --max-time 2 http://127.0.0.1:11434/api/tags >/dev/null 2>&1; then
    OLLAMA_NO_CLOUD=1 ollama serve &
    OLLAMA_PID=$!
    await_http http://127.0.0.1:11434/api/tags "$OLLAMA_PID"
  fi
  if ! ollama show qwen3:4b >/dev/null 2>&1; then
    printf 'Downloading qwen3:4b for local chat.\n'
    ollama pull qwen3:4b
  fi
  .venv/bin/python -m percival chat --model qwen3:4b
}

if [[ "$(uname -s)" != Linux ]]; then
  printf 'Run this script in the Chromebook Linux Terminal.\n' >&2
  exit 1
fi

choice=${1:-}
if [[ -z "$choice" ]]; then
  printf '\nZeroCloud / Percival\n\n  1) Launch ZeroCloud PWA\n  2) Start Metro development server\n  3) Launch Percival terminal chat\n  4) Launch Transit preview\n  q) Quit\n\n'
  read -r -p 'Choose [1]: ' choice
fi
case "${choice:-1}" in
  1|pwa) mkdir -p "$ROOT"; metro preview 4173 ;;
  2|dev) mkdir -p "$ROOT"; metro dev 5173 ;;
  4|transit) mkdir -p "$ROOT"; transit ;;
  3|chat) mkdir -p "$ROOT"; chat ;;
  q|quit) exit 0 ;;
  *) printf 'Usage: bash %s [pwa|dev|chat|transit]\n' "$0" >&2; exit 2 ;;
esac
