# Work Plan for Feature v2.3.3

## Phase 1: Build Setup and Testing
1. Navigate to go-publish-video directory
2. Set required environment variables for CGO
3. Build parent and child binaries
4. Test basic functionality

## Phase 2: README Update
1. Update main README.md with v2.3.3 changes
2. Document build instructions with environment setup
3. Add codec parameter documentation
4. Include example commands

## Phase 3: Testing and Validation
1. Test H264 codec with provided app ID
2. Test VP8 codec
3. Test AV1 codec (if supported)
4. Verify video stream on test page

## Phase 4: Version Control
1. Create v2.3.3 branch
2. Stage all modified files
3. Commit with descriptive message
4. Push to remote repository

## Build Commands
```bash
cd ~/convoai_to_video/go-publish-video
export LD_LIBRARY_PATH=$(pwd)/agora_sdk:$LD_LIBRARY_PATH
export CGO_CFLAGS="-I$(pwd)/agora_sdk/include"
export CGO_LDFLAGS="-L$(pwd)/agora_sdk -lagora_rtc_sdk -Wl,-rpath,$(pwd)/agora_sdk"
go build -o parent parent.go
go build -o child child.go
```

## Test Command
```bash
./parent -appID "20b7c51ff4c644ab80cf5a4e646b0537" -channelName "test" -videoCodec "H264"
```