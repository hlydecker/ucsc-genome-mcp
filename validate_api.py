#!/usr/bin/env python3
"""
UCSC Genome Browser API Validation Script

This script tests connectivity to the UCSC Genome Browser API
and validates that endpoints are responding correctly.
"""

import asyncio
import httpx
import sys


async def test_endpoint(client: httpx.AsyncClient, url: str, description: str) -> bool:
    """Test a single API endpoint."""
    try:
        print(f"Testing: {description}...", end=" ")
        response = await client.get(url, timeout=10.0)
        response.raise_for_status()
        data = response.json()
        print("✓ SUCCESS")
        return True
    except Exception as e:
        print(f"✗ FAILED: {str(e)}")
        return False


async def main():
    """Run validation tests."""
    print("="*70)
    print("UCSC Genome Browser API Validation")
    print("="*70)
    print()
    
    base_url = "https://api.genome.ucsc.edu"
    
    tests = [
        (f"{base_url}/list/ucscGenomes", "List UCSC Genomes"),
        (f"{base_url}/list/publicHubs", "List Public Hubs"),
        (f"{base_url}/findGenome?q=human", "Find Human Genome"),
        (f"{base_url}/list/tracks?genome=hg38", "List hg38 Tracks"),
        (f"{base_url}/list/chromosomes?genome=hg38", "List hg38 Chromosomes"),
        (f"{base_url}/getData/sequence?genome=hg38;chrom=chrM;start=0;end=100", 
         "Get DNA Sequence"),
    ]
    
    async with httpx.AsyncClient() as client:
        results = []
        for url, description in tests:
            result = await test_endpoint(client, url, description)
            results.append(result)
            await asyncio.sleep(1)  # Respect rate limits
    
    print()
    print("="*70)
    print(f"Results: {sum(results)}/{len(results)} tests passed")
    print("="*70)
    
    if all(results):
        print("\n✓ All tests passed! The API is accessible and responding correctly.")
        return 0
    else:
        print("\n✗ Some tests failed. Check your internet connection and try again.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
