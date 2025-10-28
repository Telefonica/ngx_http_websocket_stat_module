#!/usr/bin/env python3
import asyncio
import websockets
import logging
from datetime import datetime
from typing import Set, Any


# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

active_connections: Set[Any] = set()
message_count = 0


async def handle_client(websocket):
    global message_count

    client_info = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"

    active_connections.add(websocket)
    logger.info(f"🔗 New connection from {client_info} (Total: {len(active_connections)})")

    try:
        async for message in websocket:
            message_count += 1
            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]

            logger.info(f"📥 [{timestamp}] {client_info}: {message}")

            echo_message = message  # Simple Echo
            await websocket.send(echo_message)

            logger.info(f"📤 [{timestamp}] Echo → {client_info}: {echo_message}")

            if message_count % 10 == 0:
                logger.info(f"📊 Stats: {message_count} proccesed messages, {len(active_connections)} active connections")

    except websockets.exceptions.ConnectionClosed:
        logger.info(f"🔌 Connection closed by {client_info}")
    except Exception as e:
        logger.error(f"❌ Client error {client_info}: {e}")
    finally:
        active_connections.discard(websocket)
        logger.info(f"👋 Client {client_info} disconnected (Still: {len(active_connections)})")


async def main():
    host = "0.0.0.0"
    port = 8080

    logger.info("🚀 Starting WebSocket Echo...")
    logger.info(f"📡 Host: {host}")
    logger.info(f"🔌 Port: {port}")
    logger.info(f"🌐 URL: ws://{host}:{port}/")
    logger.info("=" * 50)

    server = await websockets.serve(
        handle_client,
        host,
        port,
        ping_interval=20,
        ping_timeout=10,
        max_size=1024*1024,
        compression=None
    )

    logger.info("✅ WebSocket Echo server started")
    logger.info("🔄 Waiting for connections...")
    logger.info("=" * 50)

    try:
        await server.wait_closed()
    except KeyboardInterrupt:
        logger.info("\n🛑 Interrupt")
        logger.info("🔄 Closing server...")
        server.close()
        await server.wait_closed()
        logger.info("👋 Server closed")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
