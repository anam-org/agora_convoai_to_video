#!/usr/bin/env python3
"""
Interactive Session Manager
Connects to the API, starts a session, and maintains a WebSocket connection for interactive use.
"""

import asyncio
import base64
import json
import logging
import os
import sys
import time
import uuid
import wave
from pathlib import Path

import requests
import websockets
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration for API endpoints
BASE_URL = os.getenv("BASE_URL", "http://localhost:8764")
SESSION_TOKEN_ENDPOINT = f"{BASE_URL}/auth/session-token"
SESSION_ENDPOINT = f"{BASE_URL}/engine/session"
API_KEY = os.getenv("API_KEY", "test-api-key-123")
ANAM_CLUSTER = os.getenv("ANAM_CLUSTER", "devspace")
ANAM_POD_NAME = os.getenv("ANAM_POD", "")

# Session configuration
AVATAR_ID = os.getenv("AVATAR_ID", "16cb73e7de08")
APP_ID = os.getenv("AGORA_APP_ID", "dllkSlkdmmppollalepls")
AGORA_TOKEN = os.getenv("AGORA_TOKEN", "lkmmopplek")
CHANNEL = os.getenv("AGORA_CHANNEL", "room1")
UID = os.getenv("AGORA_UID", "333")
QUALITY = os.getenv("VIDEO_QUALITY", "high")
VIDEO_ENCODING = os.getenv("VIDEO_ENCODING", "H264")
ENABLE_STRING_UIDS = os.getenv("ENABLE_STRING_UIDS", "false").lower() == "true"
ACTIVITY_IDLE_TIMEOUT = int(os.getenv("ACTIVITY_IDLE_TIMEOUT", "120"))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class InteractiveSession:
    """Manages an interactive session with the API and WebSocket"""

    def __init__(self):
        self.session_token = None
        self.session_id = None
        self.websocket_address = None
        self.websocket = None
        self.running = False
        self.heartbeat_task = None

    def create_session_token(self):
        """Step 1: Get session token from API"""
        logger.info("Step 1: Creating session token...")

        payload = {
            "personaConfig": {
                "avatarId": AVATAR_ID
            },
            "environment": {
                "cluster": ANAM_CLUSTER,
                "podName": ANAM_POD_NAME,
                "agoraSettings": {
                    "appId": APP_ID,
                    "token": AGORA_TOKEN,
                    "channel": CHANNEL,
                    "uid": UID,
                    "quality": QUALITY,
                    "videoEncoding": VIDEO_ENCODING,
                    "enableStringUids": ENABLE_STRING_UIDS,
                    "activityIdleTimeout": ACTIVITY_IDLE_TIMEOUT
                }
            }
        }

        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "Authorization": f"Bearer {API_KEY}",
            "x-vercel-protection-bypass": "WvrmD1CsSyCzkAdxjyU6Iz1DuJOgKjMZ"

        }

        try:
            response = requests.post(
                SESSION_TOKEN_ENDPOINT,
                headers=headers,
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                logger.info(f"Start session Response: {json.dumps(data, indent=2)}")
                self.session_token = data.get("sessionToken")
                logger.info(f"✅ Session token created: {self.session_token[:20]}...")
                return True
            else:
                logger.error(f"❌ Failed to create session token: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return False

        except requests.exceptions.ConnectionError:
            logger.error("❌ Connection error: Could not connect to API")
            logger.error(f"Make sure the server is running at {BASE_URL}")
            return False
        except Exception as e:
            logger.error(f"❌ Error creating session token: {e}")
            return False

    def start_session(self):
        """Step 2: Start session and get WebSocket address"""
        logger.info("Step 2: Starting session...")

        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "Authorization": f"Bearer {self.session_token}",
            "x-vercel-protection-bypass": "WvrmD1CsSyCzkAdxjyU6Iz1DuJOgKjMZ"
        }

        try:
            response = requests.post(
                SESSION_ENDPOINT,
                headers=headers,
                json={},
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                logger.info(f"Start session Response: {json.dumps(data, indent=2)}")
                self.session_id = data.get("sessionId")
                self.websocket_address = data.get("websocketAddress")
                logger.info(f"✅ Session started: {self.session_id}")
                logger.info(f"✅ WebSocket address: {self.websocket_address}")
                return True
            else:
                logger.error(f"❌ Failed to start session: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return False

        except Exception as e:
            logger.error(f"❌ Error starting session: {e}")
            return False

    def stop_session(self):
        """Stop the session"""
        logger.info("Stopping session...")
        time.sleep(5)


        payload = {
            "sessionId": self.session_id,
        }

        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "Authorization": f"Bearer {API_KEY}"
        }

        try:

            STOP_ENDPOINT = f"{BASE_URL}/engine/session/{self.session_id}/kill"
            response = requests.post(
                STOP_ENDPOINT,
                headers=headers,
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                logger.info("✅ Session stopped successfully")
                return True
            else:
                logger.warning(f"⚠️ Session stop returned status: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"❌ Error stopping session: {e}")
            return False

    async def connect_websocket(self):
        """Connect to WebSocket and send init command"""
        logger.info(f"Connecting to WebSocket: {self.websocket_address}")

        try:
            # Connect with session token in header
            self.websocket = await websockets.connect(
                self.websocket_address,
                additional_headers={}
            )
            logger.info("✅ WebSocket connected successfully")

            # Send init command
            event_id = str(uuid.uuid4())
            init_payload = {
                "command": "init",
                "sessionId": self.session_id,
                "event_id": event_id
            }

            await self.websocket.send(json.dumps(init_payload))
            logger.info("✅ Sent init command to WebSocket")

            # Start listening for messages
            asyncio.create_task(self.listen_for_messages())

            # Start automatic heartbeat task
            self.heartbeat_task = asyncio.create_task(self.heartbeat_loop())
            logger.info("✅ Started automatic heartbeat (every 5 seconds)")

            return True

        except Exception as e:
            logger.error(f"❌ Error connecting to WebSocket: {e}")
            return False

    async def listen_for_messages(self):
        """Listen for incoming WebSocket messages"""
        try:
            async for message in self.websocket:
                data = json.loads(message)
                logger.info(f"📨 Received: {json.dumps(data, indent=2)}")
        except websockets.exceptions.ConnectionClosed:
            logger.warning("WebSocket connection closed")
        except Exception as e:
            logger.error(f"Error listening to messages: {e}")

    async def send_audio_file(self, wav_file):
        """Send audio file through WebSocket"""
        logger.info(f"Sending audio from {wav_file}...")

        try:
            with wave.open(wav_file, 'rb') as wf:
                sr = wf.getframerate()
                ch = wf.getnchannels()
                sw = wf.getsampwidth()
                logger.info(f"Audio: {sr}Hz, {ch}ch, {sw} bytes/sample")

                frames = wf.readframes(wf.getnframes())

                # Calculate chunk size (0.5 seconds of audio)
                chunk_size = int(sr * 0.5)
                sample_bytes = sw * ch
                chunk_bytes = chunk_size * sample_bytes

                idx = 0
                chunk_count = 0

                while idx < len(frames):
                    chunk = frames[idx : idx + chunk_bytes]
                    idx += chunk_bytes

                    if not chunk:
                        break

                    # Encode chunk to base64
                    base64_audio = base64.b64encode(chunk).decode('utf-8')
                    event_id = str(uuid.uuid4())

                    msg = {
                        "command": "voice",
                        "audio": base64_audio,
                        "sample_rate": sr,
                        "encoding": "PCM16",
                        "event_id": event_id
                    }

                    await self.websocket.send(json.dumps(msg))
                    chunk_count += 1
                    logger.info(f"Sent audio chunk {chunk_count}")

                    await asyncio.sleep(0.1)

                # Send voice_end command
                await self.send_voice_end()
                logger.info(f"✅ Finished sending {chunk_count} audio chunks")

        except Exception as e:
            logger.error(f"❌ Error sending audio: {e}")

    async def send_voice_end(self):
        """Send voice_end command"""
        event_id = str(uuid.uuid4())
        msg = {
            "command": "voice_end",
            "event_id": event_id
        }
        await self.websocket.send(json.dumps(msg))
        logger.info("Sent voice_end command")

    async def send_voice_interrupt(self):
        """Send voice_interrupt command"""
        event_id = str(uuid.uuid4())
        msg = {
            "command": "voice_interrupt",
            "event_id": event_id
        }
        await self.websocket.send(json.dumps(msg))
        logger.info("Sent voice_interrupt command")

    async def send_heartbeat(self):
        """Send heartbeat message"""
        event_id = str(uuid.uuid4())
        timestamp = int(time.time() * 1000)

        msg = {
            "command": "heartbeat",
            "event_id": event_id,
            "timestamp": timestamp
        }

        await self.websocket.send(json.dumps(msg))
        logger.info(f"💓 Heartbeat sent (timestamp: {timestamp})")

    async def heartbeat_loop(self):
        """Automatically send heartbeat every 5 seconds"""
        try:
            while True:
                await asyncio.sleep(5)
                if self.websocket:
                    await self.send_heartbeat()
                else:
                    break
        except asyncio.CancelledError:
            logger.info("Heartbeat task cancelled")
        except Exception as e:
            logger.error(f"Error in heartbeat loop: {e}")

    async def send_custom_command(self, command_type, data=None):
        """Send custom command through WebSocket"""
        event_id = str(uuid.uuid4())
        msg = {
            "command": command_type,
            "event_id": event_id
        }
        if data:
            msg.update(data)

        await self.websocket.send(json.dumps(msg))
        logger.info(f"Sent custom command: {command_type}")

    async def disconnect_websocket(self):
        """Close WebSocket connection"""
        # Cancel heartbeat task
        if self.heartbeat_task and not self.heartbeat_task.done():
            self.heartbeat_task.cancel()
            try:
                await self.heartbeat_task
            except asyncio.CancelledError:
                pass

        if self.websocket:
            await self.websocket.close()
            logger.info("WebSocket connection closed")

    async def interactive_loop(self):
        """Interactive command loop"""
        self.running = True
        logger.info("\n" + "="*60)
        logger.info("Interactive Session Started!")
        logger.info("="*60)
        logger.info("Available commands:")
        logger.info("  f [filename]  - Send audio file (defaults to input.wav)")
        logger.info("  i             - Interrupt current audio")
        logger.info("  q             - Quit and stop session")
        logger.info("")
        logger.info("Note: Heartbeats are sent automatically every 5 seconds")
        logger.info("="*60 + "\n")

        # Run input loop in executor to avoid blocking
        loop = asyncio.get_event_loop()

        while self.running:
            try:
                # Get user input in a non-blocking way
                user_input = await loop.run_in_executor(
                    None,
                    input,
                    ">> "
                )

                parts = user_input.strip().split()
                if not parts:
                    continue

                command = parts[0].lower()

                if command == "q":
                    logger.info("Exiting...")
                    self.running = False
                    break

                elif command == "f":
                    # Default to input.wav if no filename provided
                    wav_file = parts[1] if len(parts) > 1 else "input.wav"
                    if Path(wav_file).exists():
                        await self.send_audio_file(wav_file)
                    else:
                        logger.error(f"File not found: {wav_file}")

                elif command == "i":
                    await self.send_voice_interrupt()

                else:
                    logger.warning(f"Unknown command: {command}")
                    logger.info("Available commands: f [filename], i, q")

            except KeyboardInterrupt:
                logger.info("\nInterrupted by user")
                self.running = False
                break
            except Exception as e:
                logger.error(f"Error in interactive loop: {e}")

    async def run(self):
        """Main execution flow"""
        try:
            # Step 1: Create session token
            if not self.create_session_token():
                return False

            # Step 2: Start session
            if not self.start_session():
                return False

            # Step 3: Connect WebSocket
            if not await self.connect_websocket():
                return False

            # Step 4: Interactive loop
            await self.interactive_loop()

            return True

        finally:
            # Cleanup
            await self.disconnect_websocket()
            self.stop_session()


async def main():
    """Main entry point"""
    logger.info("=" * 60)
    logger.info("Interactive Session Manager")
    logger.info("=" * 60)
    logger.info(f"API URL: {BASE_URL}")
    logger.info(f"Avatar ID: {AVATAR_ID}")
    logger.info("=" * 60)

    session = InteractiveSession()

    try:
        success = await session.run()
        if success:
            logger.info("\n✅ Session completed successfully!")
        else:
            logger.error("\n❌ Session failed to start")
            sys.exit(1)

    except KeyboardInterrupt:
        logger.info("\n\nInterrupted by user")
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
