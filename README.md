# Glowroot Trace JSON Extractor

A Python tool to extract important JSON data from Glowroot trace HTML files, filtering out CSS/JS noise to preserve only critical trace information.

## Features

- Extracts JSON data from 6 key script tags:
  - `headerJson`: Basic trace metadata (agent, timing, transaction info)
  - `entriesJson`: Detailed trace entries with execution timeline
  - `queriesJson`: SQL query performance statistics
  - `sharedQueryTextsJson`: Actual SQL query text content
  - `mainThreadProfileJson`: Main thread profiling data
  - `auxThreadProfileJson`: Auxiliary thread profiling data

- **Optimized file size**: Default compact format reduces file size by ~25%
- Handles malformed HTML gracefully using regex parsing
- Supports both single combined output and separate files per data type
- Includes extraction metadata for traceability
- Command-line interface with comprehensive options

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage
```bash
python glowroot_trace_extractor.py trace.html -o extracted_data.json
```

### Separate Files Output
```bash
python glowroot_trace_extractor.py trace.html -o data/ --separate
```

### Command Options
```
usage: glowroot_trace_extractor.py [-h] [-o OUTPUT] [--separate] [--pretty] [--output-dir OUTPUT_DIR] [--version] input_file

Extract JSON data from Glowroot trace HTML files

positional arguments:
  input_file            Input Glowroot trace HTML file

options:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        Output JSON file path (default: extracted_trace_data.json)
  --separate            Save each data type to separate JSON files
  --pretty              Use pretty-printed JSON format (default: compact format)
  --output-dir OUTPUT_DIR
                        Output directory (overrides --output)
  --version             show program's version number and exit
```

## Output Format

### Combined Output
```json
{
  "extraction_metadata": {
    "source_file": "trace-20250730-demo.html",
    "source_path": "/path/to/trace-20250730-demo.html",
    "extraction_time": "2025-01-30T23:05:34.110311",
    "tool_version": "1.0.0",
    "extracted_scripts": ["header", "entries", "queries", ...]
  },
  "header": {...},
  "entries": [...],
  "queries": [...],
  "shared_query_texts": [...],
  "main_thread_profile": {...}
}
```

### Separate Files Output
When using `--separate`, creates individual JSON files:
- `extraction_metadata.json`
- `header.json`
- `entries.json`
- `queries.json`
- `shared_query_texts.json`
- `main_thread_profile.json`

## Examples

### Example 1: Basic extraction
```bash
python glowroot_trace_extractor.py trace-20250730-demo.html -o analysis_data.json
```

### Example 2: Separate files in custom directory
```bash
python glowroot_trace_extractor.py trace-20250730-demo.html --output-dir ./analysis/ --separate
```

### Example 3: Pretty-printed format for readability
```bash
python glowroot_trace_extractor.py trace-20250730-demo.html -o readable_data.json --pretty
```

## File Size Optimization

The tool now uses compact JSON format by default to significantly reduce file size:

- **Compact format** (default): 1,645 bytes
- **Pretty format** (`--pretty`): 2,182 bytes
- **Size reduction**: ~25% smaller files

The compact format removes all unnecessary whitespace and line breaks while maintaining data integrity.

## Error Handling

The tool includes comprehensive error handling:
- **Malformed HTML**: Uses regex parsing to handle broken script tags
- **Invalid JSON**: Saves raw content for manual inspection when JSON parsing fails
- **Missing script tags**: Reports warnings for missing data types
- **File encoding**: Automatically tries different encodings (UTF-8, Latin-1)

## Tool Architecture

- **GlowrootTraceExtractor**: Main extraction class
- **Regex-based parsing**: Handles malformed HTML gracefully
- **JSON validation**: Ensures data integrity
- **Flexible output**: Single file or separate files per data type
- **Metadata tracking**: Records extraction context and success metrics

## Requirements

- Python 3.6+
- BeautifulSoup4 4.9.0+