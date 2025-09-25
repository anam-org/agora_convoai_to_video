# ConvoAI to Video Project

## Overview
This project integrates Agora's ConvoAI platform with video generation, enabling real-time audio/video streaming back into Agora channels. The system receives AI agent speech output and publishes synchronized audio/video content for interactive experiences.

## Architecture
- **Connection Setup**: REST API for session establishment
- **WebSocket Audio**: Real-time audio streaming from ConvoAI
- **Go Publisher**: Audio/video publishing to Agora channels using local SDK

## Local Modifications (v2.3.3)

### Key Changes
1. **SDK Integration**: Using Agora Golang Server SDK v2.3.3 with local C++ SDK bindings
2. **Codec Support**: Extended support for H264, VP8, and AV1 video codecs
3. **IPC Module**: Custom Inter-Process Communication using FlatBuffers
4. **Build System**: Modified to use local agora_sdk directory with .so libraries

### Modified Files
- `child.go`: Updated to use new SDK v2.3.3 API with simplified RtcConnection
- `parent.go`: Enhanced debugging and codec configuration
- `go.mod`: Updated dependencies and local SDK path

### Build Requirements
- Go 1.20+
- Agora C++ SDK libraries in `go-publish-video/agora_sdk/`
- Environment variables for CGO linking

## Build Instructions

### Prerequisites
1. Ensure Agora SDK libraries are present:
   ```bash
   ls go-publish-video/agora_sdk/
   # Should contain: libagora_rtc_sdk.so, libaosl.so, etc.
   ```

2. Set environment variables:
   ```bash
   cd ~/convoai_to_video/go-publish-video
   export LD_LIBRARY_PATH=$(pwd)/agora_sdk:$LD_LIBRARY_PATH
   export CGO_CFLAGS="-I$(pwd)/agora_sdk/include"
   export CGO_LDFLAGS="-L$(pwd)/agora_sdk -lagora_rtc_sdk -Wl,-rpath,$(pwd)/agora_sdk"
   ```

### Build Process
```bash
cd ~/convoai_to_video/go-publish-video
go build -o parent parent.go
go build -o child child.go
```

### Running the Application
```bash
./parent -appID "YOUR_APP_ID" -channelName "YOUR_CHANNEL" -videoCodec "VP8"
```

#### Supported Parameters:
- `-appID`: Agora Application ID (required)
- `-channelName`: Channel name to join (required)
- `-videoCodec`: Video codec - H264, VP8, or AV1 (default: H264)
- `-width`: Video width (default: 352)
- `-height`: Video height (default: 288)
- `-frameRate`: Frame rate (default: 15)
- `-bitrate`: Video bitrate in Kbps (default: 1000)
- `-minBitrate`: Minimum video bitrate in Kbps (default: 300)
- `-sampleRate`: Audio sample rate (default: 16000)
- `-audioChannels`: Number of audio channels (default: 1)
- `-token`: Authentication token (optional)
- `-userID`: User ID for the session (default: "0")

## Testing

### Test Scripts
- `test_direct.sh`: Direct testing of child process
- `test_child_output.sh`: Tests IPC communication
- `minimal_test.go`: Minimal test implementation

### Example Test Commands
```bash
# H264 codec test
./parent -appID "20b7c51ff4c644ab80cf5a4e646b0537" -channelName "test" -videoCodec "H264"

# VP8 codec test
./parent -appID "20b7c51ff4c644ab80cf5a4e646b0537" -channelName "vp8" -videoCodec "VP8"

# AV1 codec test (requires higher bitrate)
./parent -appID "20b7c51ff4c644ab80cf5a4e646b0537" -channelName "av1test" -videoCodec "AV1" -bitrate 2000 -minBitrate 800
```

## Technical Details

### IPC Protocol
Uses FlatBuffers for efficient binary serialization between parent/child processes:
- Message types: Connection status, media samples, control commands
- Bidirectional communication over stdin/stdout

### SDK Changes (v2.3.3)
- Simplified API: Direct `PushVideoFrame` and `PushAudioPcmData` methods
- No more manual track/sender management
- Improved codec configuration with AV1 support
- Better connection lifecycle management

### Debugging
- Child process logs to stderr: `[agora_worker]` prefix
- Parent process logs to stdout
- SDK logs written to `agora_child_sdk.log`

## Known Issues
- AV1 codec requires higher bitrates (min 1500 Kbps recommended)
- Stdout redirection needed to prevent SDK pollution of IPC channel
- SDK path must be absolute or use proper rpath in CGO_LDFLAGS