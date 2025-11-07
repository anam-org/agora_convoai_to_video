# Connection Setup API Documentation
This document describes the REST API endpoints for managing video generation sessions and providing WebSocket connection details to the Agora convoAI platform.

## Endpoints Overview
- `POST /session-token` - Get a session token (Step 1)
- `POST /session` - Start a session and get WebSocket address (Step 2)
- `DELETE /session/stop` - Stop an existing session

## Two-Step Session Flow

The session creation process requires two sequential API calls:

1. **POST /session-token** - Authenticate and create a session token
2. **POST /session** - Use the token to start the session and get WebSocket address

---

## Get Session Token Endpoint (Step 1)
```
POST /session-token
```

### Headers
```json
{
  "accept": "application/json",
  "content-type": "application/json",
  "Authorization": "Bearer YOUR_API_KEY"
}
```

### Request Format
```json
{
  "personaConfig": {
    "avatarId": "16cb73e7de08"
  },
  "environment": {
    "agoraSettings": {
      "appId": "dllkSlkdmmppollalepls",
      "token": "lkmmopplek",
      "channel": "room1",
      "uid": "333",
      "quality": "high",
      "videoEncoding": "H264",
      "enableStringUids": false,
      "activityIdleTimeout": "120"
    }
  }
}
```

### Request Fields

#### Headers
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| Authorization | string | Yes | API authentication key in Bearer token format: `Bearer YOUR_API_KEY`. Passed in the request header for security. |

#### Body Fields
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| personaConfig | object | Yes | Configuration object for the persona/avatar to be used in the session. |
| personaConfig.avatarId | string | Yes | Unique identifier for the avatar to be used in the session. This ID determines which virtual avatar will be rendered and animated during the video stream. |
| environment | object | Yes | Configuration object for the runtime environment settings. |
| environment.agoraSettings | object | Yes | Configuration object for Agora RTC (Real-Time Communication) integration. Contains all necessary parameters for establishing the video/audio channel. |

#### Agora Settings Object
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| appId | string | Yes | Agora application identifier. |
| token | string | Yes | Agora authentication token for secure channel access. |
| channel | string | Yes | Name of the Agora channel to join. |
| uid | string | Yes | User ID within the Agora channel. |
| quality | string | Yes | Video quality setting for the avatar stream. Accepted values: `"low"`, `"medium"`, `"high"`. Higher quality settings provide better visual fidelity but require more bandwidth. |
| videoEncoding | string | Yes | Video codec to be used for encoding the avatar stream. Supported values: `"H264"`, `"VP8"`, `"AV1"`. H264 provides the widest compatibility across devices and browsers. |
| enableStringUids | boolean | Yes | Determines whether the uid field should be treated as a string or numeric value. |
| activityIdleTimeout | string | No | Session timeout in seconds after which the session will be automatically terminated if no activity is detected. Default is "120". Set to "0" to disable timeout. |

### Response Format

#### Success Response (200 OK)
```json
{
  "sessionToken": "session_token_a1b2c3d4e5f6"
}
```

#### Response Fields
| Field | Type | Description |
|-------|------|-------------|
| sessionToken | string | JWT token for session authentication. Use this in the Authorization header for the `/session` endpoint (Step 2). |

#### Error Response (400 Bad Request)
```json
{
  "error": "Invalid request",
  "message": "Missing required field: personaConfig.avatarId",
  "code": "VALIDATION_ERROR"
}
```

#### Error Response (401 Unauthorized)
```json
{
  "error": "Unauthorized",
  "message": "Invalid API key",
  "code": "INVALID_API_KEY"
}
```

#### Error Response (403 Forbidden)
```json
{
  "error": "Forbidden",
  "message": "Authorization header missing",
  "code": "MISSING_API_KEY"
}
```

---

## Start Session Endpoint (Step 2)
```
POST /session
```

### Headers
```json
{
  "accept": "application/json",
  "content-type": "application/json",
  "Authorization": "Bearer SESSION_TOKEN_FROM_STEP_1"
}
```

### Request Format
```json
{}
```

The request body should be an empty JSON object.

### Request Fields

#### Headers
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| Authorization | string | Yes | Session token from Step 1 in Bearer token format: `Bearer SESSION_TOKEN`. |

### Response Format

#### Success Response (200 OK)
```json
{
  "sessionId": "550e8400-e29b-41d4-a716-446655440000",
  "websocketAddress": "ws://oai.agora.io:8765"
}
```

#### Response Fields
| Field | Type | Description |
|-------|------|-------------|
| sessionId | string | Unique identifier for this session. Used for session management and stopping the session later. |
| websocketAddress | string | WebSocket URL to connect to for audio streaming. Use this address to establish the WebSocket connection. |

#### Error Response (401 Unauthorized)
```json
{
  "error": "Unauthorized",
  "message": "Invalid session token",
  "code": "INVALID_SESSION_TOKEN"
}
```

#### Error Response (403 Forbidden)
```json
{
  "error": "Forbidden",
  "message": "Authorization header missing",
  "code": "MISSING_SESSION_TOKEN"
}
```

---

## Stop Session Endpoint
```
DELETE /session/stop
```

### Headers
```json
{
  "accept": "application/json",
  "content-type": "application/json",
  "Authorization": "Bearer YOUR_API_KEY"
}
```

### Request Format
```json
{
  "sessionId": "550e8400-e29b-41d4-a716-446655440000",
  "sessionToken": "session_token_a1b2c3d4e5f6"
}
```

### Request Fields

#### Headers
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| Authorization | string | Yes | API authentication key in Bearer token format: `Bearer YOUR_API_KEY`. |

#### Body Fields
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| sessionId | string | Yes | The session ID received from the `/session` endpoint (Step 2). Used to identify which session to terminate. |
| sessionToken | string | Yes | The session token received from the `/session-token` endpoint (Step 1). Used for authentication and session validation. |

### Response Format

#### Success Response (200 OK)
```json
{
  "status": "success",
  "message": "Session terminated successfully"
}
```

#### Error Response (400 Bad Request)
```json
{
  "error": "Invalid request",
  "message": "Missing required field: sessionId",
  "code": "VALIDATION_ERROR"
}
```

#### Error Response (401 Unauthorized)
```json
{
  "error": "Unauthorized",
  "message": "Invalid API key",
  "code": "INVALID_API_KEY"
}
```

#### Error Response (404 Not Found)
```json
{
  "error": "Not found",
  "message": "Session not found or already terminated",
  "code": "SESSION_NOT_FOUND"
}
```

---

## Usage Flow

The complete flow for using the API involves these steps:

1. **POST to `/session-token`** with your API key and session configuration
   - Include API key in Authorization header: `Bearer YOUR_API_KEY`
   - Provide avatarId and Agora settings in request body
2. **Receive `sessionToken`** from the response
3. **POST to `/session`** with the session token
   - Include session token in Authorization header: `Bearer SESSION_TOKEN`
   - Use empty request body `{}`
4. **Receive `sessionId` and `websocketAddress`** from the response
5. **Connect to WebSocket** using the provided websocket address
6. **Send init command** via WebSocket with the same configuration
7. **Stream audio data** using voice commands
8. **DELETE to `/session/stop`** when finished to clean up resources
   - Include API key in Authorization header
   - Provide sessionId and sessionToken in request body

---

## Security Notes
- The API key is passed in the `Authorization` header as a Bearer token for better security
- The session token from Step 1 is also passed as a Bearer token in Step 2
- This prevents credentials from being logged in request bodies or appearing in URL parameters
- Always use HTTPS in production to protect tokens in transit
- Session tokens are single-use and should not be reused across multiple sessions

---

## Installation

Install the required Python packages:

```bash
pip install -r requirements.txt
```

This will install:
- `requests` - For HTTP API calls
- `websockets` - For WebSocket connections
- `python-dotenv` - For loading environment variables from .env file

---

## Configuration

### Environment Variables

The interactive session script uses environment variables for configuration. Create a `.env` file in the `connection-setup` directory:

```bash
cp .env.example .env
```

Then edit `.env` with your actual values:

```bash
# API Configuration
BASE_URL=https://your-api-url.com  # Or http://localhost:8764 for local testing
API_KEY=your-actual-api-key

# Avatar Configuration
AVATAR_ID=your-avatar-id

# Agora Settings
AGORA_APP_ID=your-agora-app-id
AGORA_TOKEN=your-agora-token
AGORA_CHANNEL=your-channel-name
AGORA_UID=your-user-id

# Video Settings
VIDEO_QUALITY=high
VIDEO_ENCODING=H264
ENABLE_STRING_UIDS=false
ACTIVITY_IDLE_TIMEOUT=120
```

**Note:** The `.env` file is automatically ignored by git to protect your credentials.

---

## Interactive Session

The `interactive_session.py` script provides a complete interactive interface for testing the full session lifecycle, including API authentication, WebSocket connection, and real-time audio streaming.

### Running the Interactive Session

Start an interactive session that connects to the API and maintains a WebSocket connection:

```bash
python interactive_session.py
```

### What It Does

The script automatically handles the complete session flow:

1. **Authentication** - Creates a session token using your API key from `.env`
2. **Session Creation** - Starts a session and retrieves the WebSocket address
3. **WebSocket Connection** - Establishes a WebSocket connection with the session token
4. **Initialization** - Sends the `init` command with all configuration details
5. **Auto-Heartbeat** - Maintains connection with automatic heartbeats every 5 seconds
6. **Interactive Interface** - Provides a command prompt for real-time interaction
7. **Message Monitoring** - Displays all incoming WebSocket messages in real-time
8. **Cleanup** - Gracefully closes WebSocket and stops the session on exit

### Interactive Commands

Once the session is running, you'll see a `>>` prompt where you can enter commands:

| Command | Description | Example |
|---------|-------------|---------|
| `audio <file.wav>` | Send an audio file through the WebSocket in 0.5-second chunks | `audio input.wav` |
| `voice_end` | Send voice_end command to signal audio completion | `voice_end` |
| `status` | Show current session information (ID, token, WebSocket status) | `status` |
| `help` | Display available commands | `help` |
| `quit` or `exit` | Exit the session and cleanup resources | `quit` |

### Example Session

```bash
$ python interactive_session.py
============================================================
Interactive Session Manager
============================================================
API URL: http://localhost:8764
Avatar ID: 16cb73e7de08
============================================================

2025-11-07 10:30:15 - INFO - Step 1: Creating session token...
2025-11-07 10:30:15 - INFO - ✅ Session token created: session_token_a1b2c3...
2025-11-07 10:30:15 - INFO - Step 2: Starting session...
2025-11-07 10:30:15 - INFO - ✅ Session started: 550e8400-e29b-41d4-a716-446655440000
2025-11-07 10:30:15 - INFO - ✅ WebSocket address: ws://oai.agora.io:8765
2025-11-07 10:30:15 - INFO - Connecting to WebSocket: ws://oai.agora.io:8765
2025-11-07 10:30:15 - INFO - ✅ WebSocket connected successfully
2025-11-07 10:30:15 - INFO - ✅ Sent init command to WebSocket
2025-11-07 10:30:15 - INFO - ✅ Started automatic heartbeat (every 5 seconds)

============================================================
Interactive Session Started!
============================================================
Available commands:
  audio <file.wav>  - Send audio file
  voice_end         - Send voice_end command
  status            - Show session status
  help              - Show this help
  quit              - Exit and stop session

Note: Heartbeats are sent automatically every 5 seconds
============================================================

>> status
2025-11-07 10:30:20 - INFO - Session ID: 550e8400-e29b-41d4-a716-446655440000
2025-11-07 10:30:20 - INFO - Session Token: session_token_a1b2c3...
2025-11-07 10:30:20 - INFO - WebSocket: Connected
2025-11-07 10:30:20 - INFO - WebSocket Address: ws://oai.agora.io:8765

>> audio input.wav
2025-11-07 10:30:25 - INFO - Sending audio from input.wav...
2025-11-07 10:30:25 - INFO - Audio: 16000Hz, 1ch, 2 bytes/sample
2025-11-07 10:30:25 - INFO - Sent audio chunk 1
2025-11-07 10:30:25 - INFO - Sent audio chunk 2
2025-11-07 10:30:26 - INFO - Sent voice_end command
2025-11-07 10:30:26 - INFO - ✅ Finished sending 2 audio chunks

>> quit
2025-11-07 10:30:30 - INFO - Exiting...
2025-11-07 10:30:30 - INFO - WebSocket connection closed
2025-11-07 10:30:30 - INFO - Stopping session...
2025-11-07 10:30:30 - INFO - ✅ Session stopped successfully
```

### Features

- **Environment Variable Configuration** - All settings loaded from `.env` file
- **Automatic Connection Management** - Handles authentication and WebSocket setup
- **Real-time Message Display** - Shows all incoming WebSocket messages with formatting
- **Audio Streaming** - Chunks audio files into 0.5-second segments for streaming
- **Base64 Encoding** - Automatically encodes audio data for WebSocket transmission
- **PCM16 Audio Support** - Supports WAV files with standard PCM16 encoding
- **Graceful Shutdown** - Properly closes connections and stops sessions on exit
- **Error Handling** - Comprehensive error messages for troubleshooting
- **Keyboard Interrupt Support** - Can exit cleanly with Ctrl+C

### Audio File Requirements

When using the `audio` command:
- Format: WAV files
- Encoding: PCM16
- Recommended: 16000Hz sample rate, mono channel
- Files are automatically chunked into 0.5-second segments for streaming

### Troubleshooting

**Connection Error**
```
❌ Connection error: Could not connect to API
Make sure the server is running at http://localhost:8764
```
Solution: Verify `BASE_URL` in `.env` is correct and the server is running.

**File Not Found**
```
File not found: input.wav
```
Solution: Provide the correct path to your audio file, either relative or absolute.

**WebSocket Connection Failed**
```
❌ Error connecting to WebSocket: [error details]
```
Solution: Check that the WebSocket address returned from the API is accessible.

---

## Testing

Use the provided test scripts to verify the endpoints and WebSocket functionality.

### Mock Server

First, start the mock server for local testing:
```bash
python session_test_receiver.py
```
This will start a mock server on `http://localhost:8764` that simulates the session management endpoints.

### Individual Component Testing

```bash
# Test session start flow (two-step process)
python session_start.py

# Test session stop endpoint
python session_stop.py
```

### Complete Session Flow Testing

```bash
# Start mock server in background, then test the full flow
python session_test_receiver.py &
python session_start.py && python session_stop.py

# Or run sequentially in separate terminals:
# Terminal 1: python session_test_receiver.py
# Terminal 2: python session_start.py && python session_stop.py
```

### Testing Against Your Own Implementation

To test against your own API implementation instead of the mock server:

1. Update the `BASE_URL` variable in the test scripts:
   - In `session_start.py`: Change to your base URL
   - In `session_stop.py`: Change to your base URL

2. Update the `API_KEY` variable with your actual API key

3. Run the test scripts normally

### Testing Notes
- The mock server (`session_test_receiver.py`) uses API key `test-api-key-123` by default
- You can set a custom API key via environment variable: `export TEST_API_KEY='your-custom-key'`
- All test scripts include comprehensive validation and error handling tests
- The mock server provides detailed logging for debugging
- Test scripts verify both the two-step session creation flow and the session termination endpoint

### Example Test Output

When running `session_start.py`, you should see output like:
```
============================================================
SESSION START ENDPOINT TEST (LOCAL)
============================================================

Step 1: Getting session token...
✅ Got session token (length: 32 chars)

Step 2: Starting session with token...
✅ Got websocket address: ws://oai.agora.io:8765
✅ Two-step session flow completed successfully!
```

---

## Field Name Conventions

This API uses **camelCase** naming convention for all field names. Key field mappings:

**Top-level fields:**
- `personaConfig` (not persona_config)
- `sessionId` (not session_id)
- `sessionToken` (not session_token)
- `websocketAddress` (not websocket_address)

**Nested fields:**
- `avatarId` (not avatar_id)
- `agoraSettings` (not agora_settings)
- `videoEncoding` (not video_encoding)
- `activityIdleTimeout` (not activity_idle_timeout)
- `enableStringUids` (not enable_string_uid - note: plural)

**Fields within agoraSettings:**
- `appId` (not app_id)

All other simple fields remain lowercase: `quality`, `version`, `token`, `channel`, `uid`
