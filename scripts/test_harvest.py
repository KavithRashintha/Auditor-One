import asyncio
import time
from backend.scraper.harvester import SelectolaxPageHarvester

async def run_test():
    harvester = SelectolaxPageHarvester()
    url = "https://example.com"
    
    start_time = time.time()
    metrics, _ = await harvester.harvest(url)
    end_time = time.time()
    
    print(f"Harvested {url} in {end_time - start_time:.4f} seconds.")
    print(metrics.model_dump_json(indent=2))

if __name__ == "__main__":
    asyncio.run(run_test())
