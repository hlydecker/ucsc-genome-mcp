# UCSC Genome Browser MCP Server

A Model Context Protocol (MCP) server that provides comprehensive access to the UCSC Genome Browser API. This server enables LLM applications to query genomic data, sequences, tracks, and metadata from the UCSC Genome Browser.

## Features

This MCP server exposes 12 tools that cover all major UCSC Genome Browser API endpoints:

### Listing & Discovery Tools
- **find_genome** - Search for genomes using keywords, accession IDs, or organism names
- **list_public_hubs** - List all available public track hubs
- **list_ucsc_genomes** - List all UCSC database genomes
- **list_genark_genomes** - List GenArk assembly hub genomes
- **list_hub_genomes** - List genomes from a specific hub
- **list_files** - List downloadable files for a genome
- **list_tracks** - List data tracks in a genome or hub
- **list_chromosomes** - List chromosomes in a genome or track
- **list_schema** - Get schema/field definitions for a track

### Data Retrieval Tools
- **get_sequence** - Retrieve DNA sequences from genomes
- **get_track_data** - Get track data (genes, variants, annotations, etc.)
- **search_genome** - Search within a genome assembly

## Installation

### Prerequisites
- Python 3.10 or higher
- pip

### Install from source

```bash
# Clone or download the repository
cd ucsc-genome-mcp-server

# Install in development mode
pip install -e .
```

### Required Dependencies
- `mcp>=0.9.0` - Model Context Protocol SDK
- `httpx>=0.27.0` - HTTP client for API requests

## Usage

### Running the Server

The server communicates over stdio, following the MCP protocol:

```bash
python ucsc_genome_mcp_server.py
```

### Configuration with Claude Desktop

Add this to your Claude Desktop configuration file:

**MacOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "ucsc-genome-browser": {
      "command": "/Users/You/.local/bin/uv",
      "args": [
        "--directory",
        "/Users/Path/To/Repository/ucsc-genome-mcp",
        "run",
        "ucsc-genome-mcp.py"
      ],
      "env": {},
      "metadata": {
        "description": "UCSC Genome Browser API",
        "version": "1.0.0"        
      }
  }
}
```

## Tool Examples

### 1. Find Genomes

Search for dog genomes:
```json
{
  "query": "dog"
}
```

Search with advanced operators:
```json
{
  "query": "+white +rhino* -southern",
  "browser": "mustExist"
}
```

### 2. List Available Tracks

List all tracks for human genome (hg38):
```json
{
  "genome": "hg38"
}
```

List tracks without container information:
```json
{
  "genome": "hg38",
  "track_leaves_only": true
}
```

### 3. Get DNA Sequence

Get entire mitochondrial chromosome:
```json
{
  "genome": "hg38",
  "chrom": "chrM"
}
```

Get specific region:
```json
{
  "genome": "hg38",
  "chrom": "chrM",
  "start": 4321,
  "end": 5678
}
```

Get reverse complement:
```json
{
  "genome": "hg38",
  "chrom": "chrM",
  "start": 4321,
  "end": 5678,
  "reverse_complement": true
}
```

### 4. Get Track Data

Get gene annotations for a region:
```json
{
  "genome": "hg38",
  "track": "knownGene",
  "chrom": "chr1",
  "start": 47000,
  "end": 48000
}
```

Get track data from an assembly hub:
```json
{
  "hub_url": "http://hgdownload.gi.ucsc.edu/hubs/mouseStrains/hub.txt",
  "genome": "CAST_EiJ",
  "track": "assembly",
  "chrom": "chr1"
}
```

### 5. Search Within a Genome

Search for BRCA1 in human genome:
```json
{
  "search": "brca1",
  "genome": "hg38"
}
```

Search only in help documentation:
```json
{
  "search": "bigBed",
  "genome": "hg38",
  "categories": "helpDocs"
}
```

## API Details

### Base URL
All requests go to: `https://api.genome.ucsc.edu`

### Rate Limits
- Recommended: Maximum 1 request per second
- The API has a botDelay system to prevent overload
- Excessive queries may result in restricted access

### Coordinate Systems
- **Start coordinates**: 0-based (first base is 0)
- **End coordinates**: 1-based (exclusive)
- Example: `start=0, end=10` retrieves the first 10 bases

### Supported Track Types
The `get_track_data` tool supports these track types:
- bed, bigBed, bigWig
- genePred, bigGenePred
- bigChain, bigPsl, bigMaf
- narrowPeak, bigNarrowPeak
- wiggle/wig, barChart/bigBarChart
- interact/bigInteract
- And many more...

## Advanced Features

### Working with Large Datasets

For tracks with over 1 million items, use pagination:

1. Query by chromosome:
```json
{
  "genome": "hg19",
  "track": "knownGene",
  "chrom": "chr1"
}
```

2. Use start/end coordinates for smaller regions:
```json
{
  "genome": "hg19",
  "track": "knownGene",
  "chrom": "chr1",
  "start": 1000000,
  "end": 2000000
}
```

### Working with Track Hubs

Track hubs allow accessing external genomic data:

```json
{
  "hub_url": "http://hgdownload.gi.ucsc.edu/hubs/mouseStrains/hub.txt",
  "genome": "CAST_EiJ",
  "track": "ensGene",
  "chrom": "chr1"
}
```

## Error Handling

The server handles various error conditions:
- HTTP errors (404, 500, etc.)
- Invalid parameters
- Non-existent genomes/tracks/chromosomes
- Request timeouts (30 second default)

Errors are returned as text responses with descriptive messages.

## Use Cases

This MCP server enables LLM applications to:

1. **Genomic Research**: Query gene locations, sequences, and annotations
2. **Variant Analysis**: Retrieve SNP and variant data
3. **Comparative Genomics**: Access data from multiple species
4. **Sequence Analysis**: Get DNA/RNA sequences for analysis
5. **Data Discovery**: Find available datasets and assemblies
6. **Educational**: Learn about genomics through interactive queries

## API Documentation

For complete API documentation, visit:
https://genome.ucsc.edu/goldenpath/help/api.html

## License

This project interfaces with the UCSC Genome Browser, which has its own terms of use:
https://genome.ucsc.edu/conditions.html

## Support

For issues with the UCSC Genome Browser API, contact UCSC.
For issues with this MCP server, please file an issue in the repository.

## Development

### Project Structure
```
.
├── ucsc_genome_mcp_server.py  # Main server implementation
├── pyproject.toml             # Project metadata and dependencies
└── README.md                  # This file
```

### Adding New Tools

To add new endpoints:

1. Add the tool definition in `list_tools()`
2. Add the handler in `call_tool()`
3. Update this README with examples

### Testing

Test individual endpoints manually:
```bash
# Using curl
curl -L 'https://api.genome.ucsc.edu/list/ucscGenomes'

# Using wget
wget -O- 'https://api.genome.ucsc.edu/getData/sequence?genome=hg38;chrom=chrM;start=4321;end=5678'
```

## Changelog

### Version 0.1.0
- Initial release
- Support for all major UCSC Genome Browser API endpoints
- 12 tools covering listing, discovery, and data retrieval
- Full documentation and examples
