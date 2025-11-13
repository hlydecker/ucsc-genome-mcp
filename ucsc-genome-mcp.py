#!/usr/bin/env python3
"""
UCSC Genome Browser MCP Server

An MCP server that provides tools to interact with the UCSC Genome Browser API.
This server exposes various endpoints for querying genomic data, sequences, tracks,
and metadata from the UCSC Genome Browser.
"""

import asyncio
import json
from typing import Any, Optional
from urllib.parse import urlencode

import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Base URL for UCSC Genome Browser API
BASE_URL = "https://api.genome.ucsc.edu"

# Initialize the MCP server
app = Server("ucsc-genome-browser")


def build_api_url(endpoint: str, params: dict[str, Any]) -> str:
    """Build the complete API URL with parameters."""
    # Filter out None values
    filtered_params = {k: v for k, v in params.items() if v is not None}
    
    # Convert parameters to URL format (using semicolons as per UCSC API spec)
    if filtered_params:
        param_str = ";".join(f"{k}={v}" for k, v in filtered_params.items())
        return f"{BASE_URL}{endpoint}?{param_str}"
    return f"{BASE_URL}{endpoint}"


async def make_api_request(url: str) -> dict[str, Any]:
    """Make an HTTP request to the UCSC API and return JSON response."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List all available tools for UCSC Genome Browser API."""
    return [
        Tool(
            name="find_genome",
            description="Search for a genome in the UCSC browser using a search string. Supports advanced search with +word (force inclusion), -word (exclusion), and word* (wildcard).",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search string to find genomes (e.g., 'dog', 'GRCh38', 'GCF_028858775.2')"
                    },
                    "browser": {
                        "type": "string",
                        "enum": ["mustExist", "mayExist", "notExist"],
                        "description": "Filter by browser availability (default: mustExist)"
                    },
                    "stats_only": {
                        "type": "boolean",
                        "description": "Only show statistics about search results"
                    },
                    "year": {
                        "type": "integer",
                        "description": "Filter results by year"
                    },
                    "category": {
                        "type": "string",
                        "enum": ["reference", "representative"],
                        "description": "Filter by NCBI category"
                    },
                    "status": {
                        "type": "string",
                        "enum": ["reference", "representative"],
                        "description": "Filter by NCBI status"
                    },
                    "level": {
                        "type": "string",
                        "enum": ["complete", "chromosome", "scaffold", "contig"],
                        "description": "Filter by NCBI assembly level"
                    },
                    "max_items": {
                        "type": "integer",
                        "description": "Maximum number of items to return (default: 1000000, use -1 for max)"
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="list_public_hubs",
            description="List all available public track hubs in the UCSC Genome Browser.",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="list_ucsc_genomes",
            description="List all UCSC Genome Browser database genomes available on the database host.",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="list_genark_genomes",
            description="List UCSC Genome Browser database genomes from assembly hub host (GenArk). Can also test for existence of a specific genome.",
            inputSchema={
                "type": "object",
                "properties": {
                    "genome": {
                        "type": "string",
                        "description": "Specific genome to test for existence (optional)"
                    },
                    "max_items": {
                        "type": "integer",
                        "description": "Maximum number of items to return (default: 1000000)"
                    }
                }
            }
        ),
        Tool(
            name="list_hub_genomes",
            description="List all genomes available in a specified track or assembly hub.",
            inputSchema={
                "type": "object",
                "properties": {
                    "hub_url": {
                        "type": "string",
                        "description": "URL of the track hub or assembly hub"
                    }
                },
                "required": ["hub_url"]
            }
        ),
        Tool(
            name="list_files",
            description="List download files available for a specified UCSC genome assembly.",
            inputSchema={
                "type": "object",
                "properties": {
                    "genome": {
                        "type": "string",
                        "description": "Genome assembly name (e.g., 'hg38', 'mm10')"
                    },
                    "format": {
                        "type": "string",
                        "enum": ["json", "text"],
                        "description": "Output format (default: json)"
                    },
                    "max_items": {
                        "type": "integer",
                        "description": "Maximum number of items to return"
                    }
                },
                "required": ["genome"]
            }
        ),
        Tool(
            name="list_tracks",
            description="List all data tracks available in a specified hub or UCSC database genome.",
            inputSchema={
                "type": "object",
                "properties": {
                    "genome": {
                        "type": "string",
                        "description": "Genome assembly name"
                    },
                    "hub_url": {
                        "type": "string",
                        "description": "URL of track/assembly hub (optional, required with genome for hub tracks)"
                    },
                    "track_leaves_only": {
                        "type": "boolean",
                        "description": "Only show tracks without composite container information"
                    }
                },
                "required": ["genome"]
            }
        ),
        Tool(
            name="list_chromosomes",
            description="List chromosomes in an assembly hub, track hub, or UCSC database genome. Optionally filter by specific track.",
            inputSchema={
                "type": "object",
                "properties": {
                    "genome": {
                        "type": "string",
                        "description": "Genome assembly name"
                    },
                    "hub_url": {
                        "type": "string",
                        "description": "URL of track/assembly hub (optional)"
                    },
                    "track": {
                        "type": "string",
                        "description": "Specific track name to list chromosomes from (optional)"
                    }
                },
                "required": ["genome"]
            }
        ),
        Tool(
            name="list_schema",
            description="List the schema (field definitions) for a specified data track.",
            inputSchema={
                "type": "object",
                "properties": {
                    "genome": {
                        "type": "string",
                        "description": "Genome assembly name"
                    },
                    "track": {
                        "type": "string",
                        "description": "Track name"
                    },
                    "hub_url": {
                        "type": "string",
                        "description": "URL of track/assembly hub (optional)"
                    }
                },
                "required": ["genome", "track"]
            }
        ),
        Tool(
            name="get_sequence",
            description="Retrieve DNA sequence from a specified genome assembly. Can retrieve entire chromosome or specific coordinates.",
            inputSchema={
                "type": "object",
                "properties": {
                    "genome": {
                        "type": "string",
                        "description": "Genome assembly name (e.g., 'hg38')"
                    },
                    "chrom": {
                        "type": "string",
                        "description": "Chromosome name (e.g., 'chr1', 'chrM')"
                    },
                    "start": {
                        "type": "integer",
                        "description": "Start coordinate (0-based, optional, requires end)"
                    },
                    "end": {
                        "type": "integer",
                        "description": "End coordinate (1-based, optional, requires start)"
                    },
                    "hub_url": {
                        "type": "string",
                        "description": "URL of assembly hub (optional)"
                    },
                    "reverse_complement": {
                        "type": "boolean",
                        "description": "Return reverse complement of sequence"
                    }
                },
                "required": ["genome", "chrom"]
            }
        ),
        Tool(
            name="get_track_data",
            description="Retrieve data from a specified track in a hub or UCSC database genome. Can be filtered by chromosome and coordinates.",
            inputSchema={
                "type": "object",
                "properties": {
                    "genome": {
                        "type": "string",
                        "description": "Genome assembly name"
                    },
                    "track": {
                        "type": "string",
                        "description": "Track name"
                    },
                    "chrom": {
                        "type": "string",
                        "description": "Chromosome name (optional)"
                    },
                    "start": {
                        "type": "integer",
                        "description": "Start coordinate (0-based, optional, requires end)"
                    },
                    "end": {
                        "type": "integer",
                        "description": "End coordinate (1-based, optional, requires start)"
                    },
                    "hub_url": {
                        "type": "string",
                        "description": "URL of track/assembly hub (optional)"
                    },
                    "max_items": {
                        "type": "integer",
                        "description": "Maximum number of items to return (default: 1000000)"
                    },
                    "json_output_arrays": {
                        "type": "boolean",
                        "description": "Return data as JSON arrays instead of objects"
                    }
                },
                "required": ["genome", "track"]
            }
        ),
        Tool(
            name="search_genome",
            description="Search for matches within a UCSC Genome Browser genome assembly across tracks, help docs, and public hubs.",
            inputSchema={
                "type": "object",
                "properties": {
                    "search": {
                        "type": "string",
                        "description": "Search term"
                    },
                    "genome": {
                        "type": "string",
                        "description": "Genome assembly to search in"
                    },
                    "categories": {
                        "type": "string",
                        "enum": ["helpDocs", "publicHubs", "trackDb"],
                        "description": "Restrict search to specific categories"
                    }
                },
                "required": ["search", "genome"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls for UCSC Genome Browser API."""
    
    try:
        if name == "find_genome":
            params = {
                "q": arguments["query"],
                "browser": arguments.get("browser"),
                "statsOnly": 1 if arguments.get("stats_only") else None,
                "year": arguments.get("year"),
                "category": arguments.get("category"),
                "status": arguments.get("status"),
                "level": arguments.get("level"),
                "maxItemsOutput": arguments.get("max_items")
            }
            url = build_api_url("/findGenome", params)
            result = await make_api_request(url)
            
        elif name == "list_public_hubs":
            url = build_api_url("/list/publicHubs", {})
            result = await make_api_request(url)
            
        elif name == "list_ucsc_genomes":
            url = build_api_url("/list/ucscGenomes", {})
            result = await make_api_request(url)
            
        elif name == "list_genark_genomes":
            params = {
                "genome": arguments.get("genome"),
                "maxItemsOutput": arguments.get("max_items")
            }
            url = build_api_url("/list/genarkGenomes", params)
            result = await make_api_request(url)
            
        elif name == "list_hub_genomes":
            params = {"hubUrl": arguments["hub_url"]}
            url = build_api_url("/list/hubGenomes", params)
            result = await make_api_request(url)
            
        elif name == "list_files":
            params = {
                "genome": arguments["genome"],
                "format": arguments.get("format"),
                "maxItemsOutput": arguments.get("max_items")
            }
            url = build_api_url("/list/files", params)
            result = await make_api_request(url)
            
        elif name == "list_tracks":
            params = {
                "genome": arguments["genome"],
                "hubUrl": arguments.get("hub_url"),
                "trackLeavesOnly": 1 if arguments.get("track_leaves_only") else None
            }
            url = build_api_url("/list/tracks", params)
            result = await make_api_request(url)
            
        elif name == "list_chromosomes":
            params = {
                "genome": arguments["genome"],
                "hubUrl": arguments.get("hub_url"),
                "track": arguments.get("track")
            }
            url = build_api_url("/list/chromosomes", params)
            result = await make_api_request(url)
            
        elif name == "list_schema":
            params = {
                "genome": arguments["genome"],
                "track": arguments["track"],
                "hubUrl": arguments.get("hub_url")
            }
            url = build_api_url("/list/schema", params)
            result = await make_api_request(url)
            
        elif name == "get_sequence":
            params = {
                "genome": arguments["genome"],
                "chrom": arguments["chrom"],
                "start": arguments.get("start"),
                "end": arguments.get("end"),
                "hubUrl": arguments.get("hub_url"),
                "revComp": 1 if arguments.get("reverse_complement") else None
            }
            url = build_api_url("/getData/sequence", params)
            result = await make_api_request(url)
            
        elif name == "get_track_data":
            params = {
                "genome": arguments["genome"],
                "track": arguments["track"],
                "chrom": arguments.get("chrom"),
                "start": arguments.get("start"),
                "end": arguments.get("end"),
                "hubUrl": arguments.get("hub_url"),
                "maxItemsOutput": arguments.get("max_items"),
                "jsonOutputArrays": 1 if arguments.get("json_output_arrays") else None
            }
            url = build_api_url("/getData/track", params)
            result = await make_api_request(url)
            
        elif name == "search_genome":
            params = {
                "search": arguments["search"],
                "genome": arguments["genome"],
                "categories": arguments.get("categories")
            }
            url = build_api_url("/search", params)
            result = await make_api_request(url)
            
        else:
            return [TextContent(
                type="text",
                text=f"Unknown tool: {name}"
            )]
        
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]
        
    except httpx.HTTPStatusError as e:
        error_msg = f"HTTP error occurred: {e.response.status_code} - {e.response.text}"
        return [TextContent(type="text", text=error_msg)]
    except Exception as e:
        error_msg = f"Error executing {name}: {str(e)}"
        return [TextContent(type="text", text=error_msg)]


async def main():
    """Main entry point for the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
