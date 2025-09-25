# Feature v2.3.3: Agora SDK Upgrade and Multi-Codec Support

## Feature Requirements

### Primary Goals
1. Upgrade to Agora Golang Server SDK v2.3.3
2. Support multiple video codecs (H264, VP8, AV1)
3. Enable local SDK library usage without system-wide installation
4. Maintain IPC communication between parent and child processes

### Technical Requirements
- Use local agora_sdk directory with C++ SDK libraries
- Implement codec selection via command-line parameter
- Ensure proper CGO linking with local libraries
- Fix stdout pollution from SDK logs
- Support all existing audio/video parameters

### Success Criteria
- Build completes without errors
- Parent process can launch child with codec specification
- Video streams successfully to Agora channel
- All three codecs (H264, VP8, AV1) function correctly
- Test command works: `./parent -appID "20b7c51ff4c644ab80cf5a4e646b0537" -channelName "test" -videoCodec "H264"`

## Implementation Details

### Modified Components
1. **child.go**
   - Migrate to v2.3.3 SDK API
   - Use RtcConnection with simplified publish methods
   - Remove manual track/sender management
   - Add stdout redirection to prevent SDK pollution

2. **parent.go**
   - Add videoCodec parameter handling
   - Enhance debug logging
   - Pass codec to child process

3. **go.mod**
   - Update SDK version to v2.3.3
   - Fix local SDK path references

4. **Build System**
   - Use local agora_sdk directory
   - Set proper CGO flags for compilation
   - Configure rpath for runtime library loading

## Testing Plan
1. Build both parent and child binaries
2. Test with each codec (H264, VP8, AV1)
3. Verify video appears on test page
4. Check logs for errors or warnings
5. Validate IPC communication integrity