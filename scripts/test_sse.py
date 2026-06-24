import asyncio
import httpx
import json

async def main():
    async with httpx.AsyncClient() as client:
        url = "http://127.0.0.1:8000/api/v1/audit"
        payload = {"url": "https://example.com"}
        
        print(f"Connecting to {url}...")
        async with client.stream("POST", url, json=payload) as response:
            if response.status_code != 200:
                print(f"Error: {response.status_code}")
                print(await response.aread())
                return
                
            async for line in response.aiter_lines():
                if line:
                    print(line)

if __name__ == "__main__":
    asyncio.run(main())
