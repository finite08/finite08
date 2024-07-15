import asyncio
import requests
import time

# This script shows newly created liquidity pools added to Raydium DEX and gives us the transaction information about 30-45 minutes after it has been created, still too slow and needs optimizetions
# Raydium DED's URL is where we GET the information from
RAYDIUM_API_URL = "https://api.raydium.io/v2/main/pairs"


def get_current_pools():
    try:
        response = requests.get(RAYDIUM_API_URL)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        print(response.content)  # Print response content for debugging
    except Exception as err:
        print(f"Other error occurred: {err}")
    return []


def detect_new_pools(existing_pools, current_pools):
    existing_pool_ids = {pool['ammId'] for pool in existing_pools}
    new_pools = [pool for pool in current_pools if pool['ammId'] not in existing_pool_ids]
    return new_pools


async def poll_new_pools(interval=60):
    existing_pools = get_current_pools()
    print(f"Initial Pools: {len(existing_pools)} pools fetched.")
    if existing_pools:
        print("Sample of initial pools:", existing_pools[:5])

    try:
        while True:
            print(f"Polling at {time.strftime('%Y-%m-%d %H:%M:%S')}")
            current_pools = get_current_pools()
            print(f"Fetched {len(current_pools)} pools.")
            if current_pools:
                print("Sample of current pools:", current_pools[:5])

                existing_pool_ids = {pool['ammId'] for pool in existing_pools}
                current_pool_ids = {pool['ammId'] for pool in current_pools}
                print(f"Existing Pool IDs (sample): {list(existing_pool_ids)[:5]}")
                print(f"Current Pool IDs (sample): {list(current_pool_ids)[:5]}")

                new_pools = detect_new_pools(existing_pools, current_pools)

                if new_pools:
                    print(f"New Pools Detected: {len(new_pools)}")
                    for pool in new_pools:
                        print(f"New Pool: {pool}")

                    # Update existing_pools with new pools to avoid redundant detections
                    existing_pools.extend(new_pools)
                else:
                    print("No new pools detected.")

            await asyncio.sleep(interval)
    except asyncio.CancelledError:
        print("Polling interrupted. Exiting gracefully...")


if __name__ == "__main__":
    try:
        asyncio.run(poll_new_pools())
    except KeyboardInterrupt:
        print("Script interrupted by user. Exiting...")
