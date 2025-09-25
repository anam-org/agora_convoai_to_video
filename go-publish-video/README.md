# Publish Audio and Video into Agora with Golang (v2.3.3)

This document guides you through setting up and publishing YUV video frames and PCM audio into an Agora channel using the Agora Golang SDK v2.3.3.
The steps have been verified on Ubuntu 24.04 but should be compatible with other Debian and Ubuntu versions.
parent.go launches a child.go in its own process and communicates with it using IPC. This ensures efficient movement of data while keeping each call in its own process for stability and threading optimisation.

## Key Features (v2.3.3)
- Support for multiple video codecs: H264, VP8, and AV1
- Simplified SDK API with direct push methods for audio/video
- Local SDK library integration without system-wide installation
- Enhanced IPC communication using FlatBuffers    

## Installation Steps

### 1. Install Build Essentials and Go

```bash
# Update package manager
sudo apt-get update

# Install required build tools
sudo apt-get install -y build-essential git wget unzip

# Download and install Go 1.21 (if not already installed)
wget https://go.dev/dl/go1.21.5.linux-amd64.tar.gz
sudo rm -rf /usr/local/go && sudo tar -C /usr/local -xzf go1.21.5.linux-amd64.tar.gz

# Add Go to PATH
export PATH=$PATH:/usr/local/go/bin

# Install FlatBuffers compiler
sudo apt-get install -y flatbuffers-compiler
```

### 2. Setup Agora Go SDK v2.3.3

```bash
# Clone the Agora Golang Server SDK to home directory
cd ~
git clone https://github.com/AgoraIO-Extensions/Agora-Golang-Server-SDK.git
cd Agora-Golang-Server-SDK

# Checkout v2.3.3 version
git checkout v2.3.3

# Download and build SDK dependencies
make deps
make build
```

### 3. Clone and Setup This Project

```bash
# Clone this repository
cd ~
git clone https://github.com/AgoraIO-Solutions/convoai_to_video.git
cd convoai_to_video/go-publish-video

# Copy SDK libraries from Agora SDK (if not already present)
if [ ! -d "agora_sdk" ]; then
    cp -r ~/Agora-Golang-Server-SDK/agora_sdk ./
fi
```

Note: The `go.mod` file is configured to use the Agora SDK from `~/Agora-Golang-Server-SDK`.

### 4. Build and Run

```bash
# Navigate to the project directory (if not already there)
cd ~/convoai_to_video/go-publish-video

# Set environment variables for build
export CGO_CFLAGS="-I$(pwd)/agora_sdk/include"
export CGO_LDFLAGS="-L$(pwd)/agora_sdk -lagora_rtc_sdk -Wl,-rpath,$(pwd)/agora_sdk"

# Set library path for runtime
export LD_LIBRARY_PATH=$(pwd)/agora_sdk:$LD_LIBRARY_PATH

# Build the binaries
go build -o parent parent.go
go build -o child child.go

# Basic usage
./parent -appID "your_app_id" -channelName "your_channel"

# With VP8 codec
./parent -appID "your_app_id" -channelName "your_channel" -videoCodec "VP8"

# With H264 codec (default)
./parent -appID "your_app_id" -channelName "your_channel" -videoCodec "H264"
```

This will publish the YUV and PCM files from the test_data folder. You can view the stream on Agora Web Demo:
https://webdemo.agora.io/basicVideoCall/index.html

Use your App ID and Channel Name to join the stream.

## Key Parameters

**Required:**
- `-appID`: Your Agora Application ID
- `-channelName`: Channel name to join

**Video Codec (new in v2.3.3):**
- `-videoCodec`: Choose "H264", "VP8", or "AV1" (default: "H264")

**Optional:**
- `-userID`: User ID for the session (default: "100")
- `-token`: Authentication token if required
- `-width`, `-height`: Video resolution (default: 352x288)
- `-frameRate`: Video frame rate (default: 15 fps)
- `-bitrate`: Video bitrate in Kbps (default: 1000)

## Codec Notes

- **H264**: Most widely supported, good balance of quality and performance
- **VP8**: Open source codec, good for web compatibility
- **AV1**: Latest generation codec, better compression but requires more CPU
  - Recommended bitrate: 1500-2000 Kbps
  - Recommended min bitrate: 500-800 Kbps

## Troubleshooting

If you encounter build errors:
1. Ensure the Agora SDK is properly installed in `~/Agora-Golang-Server-SDK`
2. Verify environment variables are set correctly
3. Check that `agora_sdk` directory contains the required .so files

## Next Steps

Modify parent.go to send your own YUV video and PCM audio into Agora. Publish them together in sync and in realtime.   
