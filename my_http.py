import asyncio

import httpx


async def send_request(url, payload, headers=None):
    async with httpx.AsyncClient() as client:
        try:
            print(f"Communicating with device at {url}...")
            response = await client.post(url, json=payload, headers=headers, timeout=10.0)
            print(f"Device Response: {response.text}")
        except Exception as e:
            print(f"Failed: {e}")

