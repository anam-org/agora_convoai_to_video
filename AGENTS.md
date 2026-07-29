# AGENTS.md

## Cursor Cloud specific instructions

This repo is a **reference/integration toolkit** (not one deployed app) for connecting Agora's
ConvoAI platform to a third‑party AI avatar video service. It has four loosely‑coupled
components. The three Python components each ship a **mock server**, so they run locally without
live Agora/Anam credentials. The Go component needs the proprietary Agora native SDK and, to
actually publish, live Agora credentials.

### Environment (already provisioned by the startup/update script + VM snapshot)
- Python 3.12 lives in a repo‑root virtualenv at `.venv` (deps: `requests`, `websockets`,
  `python-dotenv`, from `anam-connection/requirements.txt`). Run Python scripts with
  `/workspace/.venv/bin/python <script>` (or `source .venv/bin/activate` first).
- The update script only refreshes the Python venv. System deps (`python3.12-venv`,
  `flatbuffers-compiler`/`flatc`) and the Go SDK below are one‑time setup baked into the VM
  snapshot, intentionally kept out of the update script because they are heavy/network‑bound.
- `uv` is **not** installed even though `uv.lock`/`.python-version` exist; the scripts are plain
  Python, so a standard `venv` + `pip` is used instead. The root `uv.lock` has no real
  dependencies and there is no root `pyproject.toml`, so `uv sync` would not help here anyway.

### Components and how to run them
Standard commands live in each component's `README.md`; notes below are the non‑obvious bits.

1. `connection-setup/` — REST session start/stop API + mock. Fully works end‑to‑end.
   - Terminal 1: `/workspace/.venv/bin/python session_test_receiver.py` (mock on `:8764`).
   - Terminal 2: `/workspace/.venv/bin/python session_start.py` then `session_stop.py`.
   - Clients default to `http://localhost:8764`; mock API key is `test-api-key-123`.

2. `websocket-receive-audio/` — WebSocket audio streaming spec + mock receiver + sender.
   - `websocket_test_receiver.py` starts on `:8765`; `websocket_audio_sender.py` needs an
     `input.wav` in its cwd (you can copy `../anam-connection/input.wav`; `*.wav` is gitignored).
   - GOTCHA (pre‑existing code bug, not an env issue): the committed sender and receiver are
     written against **different `websockets` eras and cannot interoperate on any single version**.
     `websocket_audio_sender.py` calls `websockets.connect(..., additional_headers=...)` (new
     API, needs `websockets>=15`) but passes an **empty** headers dict, so it never sends the
     `Authorization: Bearer <token>` the receiver requires; and `websocket_test_receiver.py`
     reads `request_headers` (legacy API removed in `websockets>=15`). With the installed
     `websockets` (>=16) the receiver rejects the connection with `Invalid session token`
     (`Token validation error: 'Request' object has no attribute 'get'`). Both scripts *launch*
     fine and the receiver *accepts the TCP/WS connection* — the failure is purely in app logic.
     Fixing it (send the token from the sender + read `websocket.request.headers` in the
     receiver) is a code change, out of scope for environment setup.

3. `anam-connection/` — two‑step Anam auth + `interactive_session.py` (streams a WAV over WS).
   - **No mock server exists** for the Anam `/auth/session-token` + `/engine/session` endpoints,
     so this only runs against the **real Anam API**. Requires secrets: `API_KEY` (Anam),
     `AVATAR_ID`, and Agora settings (`AGORA_APP_ID`, `AGORA_TOKEN`, `AGORA_CHANNEL`,
     `AGORA_UID`). Copy `.env.example` to `.env` and fill it in. Blocked without credentials.

4. `go-publish-video/` — publishes YUV video + PCM audio into an Agora channel via the Agora
   Golang Server SDK; `parent.go` spawns `child.go` and talks over FlatBuffers IPC.
   - Prebuilt in the snapshot: `flatc` installed, the SDK cloned to
     `/home/ubuntu/Agora-Golang-Server-SDK` (`make deps && make build`, which downloads Agora's
     native `.so` libs), and `agora_sdk/` copied into `go-publish-video/`. `go.mod` has a
     **hardcoded** `replace => /home/ubuntu/Agora-Golang-Server-SDK`.
   - Build/run needs these env vars (see `go-publish-video/README.md` for the full flow):
     ```
     export PATH=$PATH:/usr/local/go/bin
     cd go-publish-video
     export CGO_CFLAGS="-I$(pwd)/agora_sdk/include"
     export CGO_LDFLAGS="-L$(pwd)/agora_sdk -lagora_rtc_sdk -Wl,-rpath,$(pwd)/agora_sdk"
     export LD_LIBRARY_PATH=$(pwd)/agora_sdk:$LD_LIBRARY_PATH
     make build            # -> ./parent and ./child
     ./parent -appID <AGORA_APP_ID> -channelName <channel> -userID <uid>
     ```
   - `agora_sdk/`, `ipc/ipcgen/`, `parent`, `child`, and `agora_*.db/.dat/.log` are local build
     artifacts (do not commit them; `.so` are already gitignored).
   - GOTCHA: a real publish requires a **valid Agora App ID (+ token)**. With a placeholder App
     ID the binary runs, the SDK initializes, IPC works, and it fails only at channel auth
     (`Token privilege did expire`, connection `Error Code: 8`) — expected. Verify a real stream
     via https://webdemo.agora.io/basicVideoCall/index.html.
