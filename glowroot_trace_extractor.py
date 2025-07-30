#!/usr/bin/env python3
"""
Glowroot Trace JSON Extractor Tool

Extracts important JSON data from Glowroot trace HTML files,
filtering out CSS/JS noise to preserve only critical trace information.

Author: Claude AI Assistant
Version: 1.0.0
"""

import json
import argparse
import sys
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
from bs4 import BeautifulSoup


class GlowrootTraceExtractor:
    """
    Extracts JSON data from Glowroot trace HTML files.
    
    This class parses HTML files and extracts JSON data from specific script tags
    that contain trace information, filtering out CSS/JS noise.
    """
    
    # Script tag IDs that contain important JSON data
    JSON_SCRIPT_IDS = [
        'headerJson',
        'entriesJson', 
        'queriesJson',
        'sharedQueryTextsJson',
        'mainThreadProfileJson',
        'auxThreadProfileJson'
    ]
    
    def __init__(self):
        self.version = "1.0.0"
        self.extracted_data = {}
        self.extraction_metadata = {}
    
    def extract_from_file(self, html_file_path: str) -> Dict[str, Any]:
        """
        Extract JSON data from a Glowroot trace HTML file.
        
        Args:
            html_file_path: Path to the HTML file
            
        Returns:
            Dictionary containing extracted JSON data
            
        Raises:
            FileNotFoundError: If HTML file doesn't exist
            ValueError: If HTML parsing fails
        """
        html_path = Path(html_file_path)
        
        if not html_path.exists():
            raise FileNotFoundError(f"HTML file not found: {html_file_path}")
        
        # Read HTML content
        try:
            with open(html_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
        except UnicodeDecodeError:
            # Try with different encoding if UTF-8 fails
            with open(html_path, 'r', encoding='latin-1') as f:
                html_content = f.read()
        
        # Parse HTML - try both BeautifulSoup and regex approaches
        self.extracted_data = self._extract_json_from_html(html_content)
        
        # Add extraction metadata
        self.extraction_metadata = {
            'source_file': html_path.name,
            'source_path': str(html_path.absolute()),
            'extraction_time': datetime.now().isoformat(),
            'tool_version': self.version,
            'extracted_scripts': list(self.extracted_data.keys())
        }
        
        # Combine metadata and data
        result = {
            'extraction_metadata': self.extraction_metadata,
            **self.extracted_data
        }
        
        return result
    
    def _extract_json_from_html(self, html_content: str) -> Dict[str, Any]:
        """
        Extract JSON data from script tags using regex to handle malformed HTML.
        
        Args:
            html_content: Raw HTML content
            
        Returns:
            Dictionary with extracted JSON data
        """
        extracted = {}
        
        for script_id in self.JSON_SCRIPT_IDS:
            # Use regex to find script tag content, handling malformed HTML
            pattern = rf'<script\s+type="text/json"\s+id="{script_id}"[^>]*>(.*?)(?=<script|</body>|$)'
            match = re.search(pattern, html_content, re.DOTALL | re.IGNORECASE)
            
            if match:
                content = match.group(1).strip()
                
                # Clean up content - remove any trailing script tags or HTML
                content = re.sub(r'</script>.*$', '', content, flags=re.DOTALL)
                content = content.strip()
                
                if content:
                    try:
                        # Parse JSON content
                        json_data = json.loads(content)
                        
                        # Convert camelCase ID to snake_case for output
                        output_key = self._camel_to_snake(script_id.replace('Json', ''))
                        extracted[output_key] = json_data
                        
                        print(f"[OK] Extracted {script_id}: {self._get_data_summary(json_data)}")
                        
                    except json.JSONDecodeError as e:
                        print(f"[WARN] Failed to parse JSON in {script_id}: {e}")
                        print(f"      Content preview: {content[:100]}...")
                        # Store raw content for manual inspection
                        output_key = self._camel_to_snake(script_id.replace('Json', '')) + '_raw'
                        extracted[output_key] = content
                else:
                    print(f"[WARN] Script tag '{script_id}' found but empty")
            else:
                print(f"[WARN] Script tag '{script_id}' not found")
        
        return extracted
    
    def _camel_to_snake(self, camel_str: str) -> str:
        """Convert camelCase to snake_case."""
        result = []
        for i, char in enumerate(camel_str):
            if char.isupper() and i > 0:
                result.append('_')
            result.append(char.lower())
        return ''.join(result)
    
    def _get_data_summary(self, data: Any) -> str:
        """Get a brief summary of the extracted data."""
        if isinstance(data, dict):
            return f"dict with {len(data)} keys"
        elif isinstance(data, list):
            return f"array with {len(data)} items"
        elif isinstance(data, str):
            return f"string ({len(data)} chars)"
        else:
            return f"{type(data).__name__}"
    
    def save_to_file(self, data: Dict[str, Any], output_path: str, 
                     separate_files: bool = False, compact: bool = True) -> None:
        """
        Save extracted data to JSON file(s).
        
        Args:
            data: Extracted data dictionary
            output_path: Output file path
            separate_files: If True, save each data type to separate files
            compact: If True, use compact JSON format (no indentation/extra spaces)
        """
        output_path_obj = Path(output_path)
        
        if separate_files:
            self._save_separate_files(data, output_path_obj, compact)
        else:
            self._save_combined_file(data, output_path_obj, compact)
    
    def _save_combined_file(self, data: Dict[str, Any], output_path: Path, compact: bool = True) -> None:
        """Save all data to a single JSON file."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            if compact:
                json.dump(data, f, separators=(',', ':'), ensure_ascii=False)
            else:
                json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"[OK] Saved combined data to: {output_path}")
    
    def _save_separate_files(self, data: Dict[str, Any], output_path: Path, compact: bool = True) -> None:
        """Save each data type to separate JSON files."""
        base_path = output_path.parent / output_path.stem
        base_path.mkdir(parents=True, exist_ok=True)
        
        # Save metadata
        metadata_file = base_path / "extraction_metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            if compact:
                json.dump(data['extraction_metadata'], f, separators=(',', ':'), ensure_ascii=False)
            else:
                json.dump(data['extraction_metadata'], f, indent=2, ensure_ascii=False)
        print(f"[OK] Saved metadata to: {metadata_file}")
        
        # Save each data type
        for key, value in data.items():
            if key != 'extraction_metadata':
                data_file = base_path / f"{key}.json"
                with open(data_file, 'w', encoding='utf-8') as f:
                    if compact:
                        json.dump(value, f, separators=(',', ':'), ensure_ascii=False)
                    else:
                        json.dump(value, f, indent=2, ensure_ascii=False)
                print(f"[OK] Saved {key} to: {data_file}")


def main():
    """Main entry point for the command-line interface."""
    parser = argparse.ArgumentParser(
        description="Extract JSON data from Glowroot trace HTML files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s trace.html -o extracted_data.json
  %(prog)s trace.html -o data/ --separate
  %(prog)s trace.html --output-dir ./analysis/
        """
    )
    
    parser.add_argument(
        'input_file',
        help='Input Glowroot trace HTML file'
    )
    
    parser.add_argument(
        '-o', '--output',
        default='extracted_trace_data.json',
        help='Output JSON file path (default: extracted_trace_data.json)'
    )
    
    parser.add_argument(
        '--separate',
        action='store_true',
        help='Save each data type to separate JSON files'
    )
    
    parser.add_argument(
        '--pretty',
        action='store_true',
        help='Use pretty-printed JSON format (default: compact format)'
    )
    
    parser.add_argument(
        '--output-dir',
        help='Output directory (overrides --output)'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version=f'%(prog)s 1.0.0'
    )
    
    args = parser.parse_args()
    
    # Determine output path
    if args.output_dir:
        output_dir = Path(args.output_dir)
        if args.separate:
            output_path = output_dir / "extracted_data"
        else:
            output_path = output_dir / "extracted_trace_data.json"
    else:
        output_path = Path(args.output)
    
    # Create extractor and process file
    try:
        extractor = GlowrootTraceExtractor()
        
        print(f"Processing: {args.input_file}")
        print("-" * 50)
        
        # Extract data
        extracted_data = extractor.extract_from_file(args.input_file)
        
        print("-" * 50)
        print(f"Extracted {len(extracted_data) - 1} data types from {len(extractor.JSON_SCRIPT_IDS)} script tags")
        
        # Save data
        compact_mode = not args.pretty  # Default is compact unless --pretty is specified
        extractor.save_to_file(extracted_data, str(output_path), args.separate, compact_mode)
        
        print("-" * 50)
        print("[SUCCESS] Extraction completed successfully!")
        
    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()