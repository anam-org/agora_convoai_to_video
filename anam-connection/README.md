
# Anam Connection - Two-Step Authentication Flow

Two-step authentication flow for Agora convoAI platform via Anam API.

**Key difference from `connection-setup/`:** Separate API calls for authentication and session creation instead of single endpoint.

## Quick Setup

```bash
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your credentials
python interactive_session.py
```

## API Flow

### Step 1: Get Session Token

```
POST /auth/session-token
Authorization: Bearer YOUR_API_KEY
```

**Request:**
```json
{
  "personaConfig": {
    "avatarId": "16cb73e7de08",
    "avatarModel": "cara-4"
  },
  "environment": {
    "agoraSettings": {
      "appId": "your-app-id",
      "token": "your-token",
      "channel": "room1",
      "uid": "333",
      "quality": "high",
      "videoEncoding": "H264",
      "enableStringUids": false,
      "activityIdleTimeout": 120,
      "audioSampleRate": 24000,
      "width": 768,
      "height": 1152
    }
  }
}
```

**Response:**
```json
{
  "sessionToken": "eyJhbGc..."
}
```

### Step 2: Start Session

```
POST /engine/session
Authorization: Bearer SESSION_TOKEN_FROM_STEP_1
```

**Request:**
```json
{}
```

**Response:**
```json
{
  "sessionId": "550e8400-e29b-41d4-a716-446655440000",
  "websocketAddress": "wss://api.example.com/ws?sessionId=550..."
}
```

### Step 3: WebSocket Commands

**Note:** These are the **current minimum required fields. Other fields from connection-setup can be included, but not currently used by the engine**.

**Auth**
Connect to `websocketAddress` from Step 2.
Auth is encoded in the url in websocketAddress. A current quirk of our system means that passing the bearer token in the header means the request will be routed differently.

Don't set the authorization header in the websocket connection.

**Wierd naming quirk**: These websocket commands currently use snake_case, wheras the API uses camelCase. I can fix this if it's an issue!

**Init:**
```json
{
  "command": "init",
  "sessionId": "550e8400-e29b-41d4-a716-446655440000",
  "event_id": "uuid-v4"
}
```

**Voice (audio streaming):**
```json
{
  "command": "voice",
  "audio": "base64-encoded-pcm16",
  "sample_rate": 24000,
  "encoding": "PCM16",
  "event_id": "uuid-v4"
}
```

**Voice End:**
```json
{
  "command": "voice_end",
  "event_id": "uuid-v4"
}
```

**Voice Interrupt:**
```json
{
  "command": "voice_interrupt",
  "event_id": "uuid-v4"
}
```

**Heartbeat:**
```json
{
  "command": "heartbeat",
  "event_id": "uuid-v4",
  "timestamp": 1234567890000
}
```

### Step 4: Stop Session

```
POST /engine/session/{sessionId}/kill
Authorization: Bearer YOUR_API_KEY
```

**Request:**
```json
{
  "sessionId": "550e8400-e29b-41d4-a716-446655440000"
}
```

## Interactive Session App

`interactive_session.py` - Complete working example demonstrating the API flow.

**Features:**
- Two-step authentication
- WebSocket connection management
- Audio file streaming (0.5s chunks)
- Auto-heartbeat (5s interval)
- Real-time message display

**Commands:**
- `f [filename]` - Send audio (default: `input.wav`)
- `i` - Interrupt
- `q` - Quit

**Usage:**
```bash
python interactive_session.py

>> f my_audio.wav
>> i
>> q
```

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `BASE_URL` | No | `http://localhost:8764` | API base URL |
| `API_KEY` | Yes | - | Anam API key |
| `AVATAR_ID` | Yes | - | Avatar ID |
| `ANAM_AVATAR_MODEL` | No | default model for the selected avatar | Model to render the avatar  |
| `AGORA_APP_ID` | Yes | - | Agora app ID |
| `AGORA_TOKEN` | Yes | - | Agora token |
| `AGORA_CHANNEL` | Yes | - | Channel name |
| `AGORA_UID` | Yes | - | User ID |
| `VIDEO_QUALITY` | No | `high` | `low`/`medium`/`high` |
| `VIDEO_ENCODING` | No | `H264` | `H264`/`VP8`/`AV1` |
| `ENABLE_STRING_UIDS` | No | `false` | String UIDs |
| `ACTIVITY_IDLE_TIMEOUT` | No | `120` | Seconds |
| `ANAM_AUDIO_SAMPLE_RATE` | No | `24000` | Audio sample rate |
| `VIDEO_WIDTH` | No | 720 or 1152 | Output frame width in pixels. Depends on Avatar Model (Cara-3: 720, Cara-4: 1152). Must be paired with `VIDEO_HEIGHT`. |
| `VIDEO_HEIGHT` | No | 480 or 768 | Output frame height in pixels. Depends on Avatar Model (Cara-3: 480, Cara-4: 768). Must be paired with `VIDEO_WIDTH`. |

## Field Notes

**Always required:**
- `personaConfig.avatarId`
- All `agoraSettings` except `activityIdleTimeout`

**Optional:**
- `agoraSettings.activityIdleTimeout` (defaults to 120)
- `personaConfig.avatarModel` (overwrites the default model for the selected avatar)

## audioSampleRate
- This is the audio sample rate for the incoming Voice Command.
- The service will deliver a synchronised A/V stream, with the ingested audio (at original quality).
- It has to be configured at initialization of the session.
- Any Voice Event sent with a different audio sample rate will be rejected.

## width / height (portrait output)
- Optional. Both must be set together, or both left unset, and only supported resolutions can be used:
  | avatar model | orientation | width | height |
  |--------------|-------------|-------|--------|
  | Cara-3 | landscape | 720 | 480 |
  | Cara-4 | landscape | 1152 | 768 |
  | Cara-4 | portrait | 768 | 1152 |
