#!/usr/bin/env python3
"""
Citation verifier for Premier League Player Role Discovery research.

This script takes the synthesized design_decisions.md document and verifies
the factual claims against sources, producing a citation table and a verified
version of the document with inline references.
"""

import os
import sys
import time
import argparse
import logging
import hashlib
from typing import Dict, List, Any, Optional

import dotenv
import pandas as pd

# Add the parent directory to the path so we can import from utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.openai_client import OpenAIClient, sanitize_prompt
from utils.io_helpers import (
    read_json,
    write_json,
    write_text,
    read_text,
    write_csv,
    ensure_directory,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Default directories
DEFAULT_INPUT_PATH = "outputs/synthesis/design_decisions.md"
DEFAULT_OUTPUT_DIR = "outputs/citations"
DEFAULT_PROMPT_TEMPLATE = "prompts/citation_agent.txt"
DEFAULT_MODEL = "gpt-4o"


def load_prompt_template(template_path: str) -> str:
    """
    Load the prompt template from a file, or use the default if the file doesn't exist.
    
    Args:
        template_path: Path to the prompt template file
        
    Returns:
        The prompt template as a string
    """
    default_template = """You are a Citation Verifier for the Premier League Player Role Discovery project.

PROJECT CONTEXT:
This project uses unsupervised machine learning to discover data-driven player roles in the English Premier League. 
Instead of traditional position labels (DEF, MID, FWD), we're clustering players into functional roles based on 
advanced statistics. The final output will be a Streamlit web app that allows users to:
1. Search for any Premier League player
2. View their clustered role and similar players
3. Explore role-specific statistics via radar charts and heatmaps
4. Visualize the player landscape in 2D PCA/UMAP scatter plots
5. Understand which features drive role assignment using explainability tools (SHAP/Permutation Importance)

Input is a Markdown document of research design decisions.
Identify factual claims and verify each with a specific source URL and a 15–40 word snippet.
Return two items:
1) A CSV (as a code block) with columns: claim_id, claim_text, status[VERIFIED|PARTIAL|UNVERIFIED], source_url, snippet
2) A cleaned Markdown body with inline numeric references [1], [2], ... aligned to the CSV rows.
"""
    
    try:
        return read_text(template_path)
    except FileNotFoundError:
        logger.warning(f"Prompt template not found at {template_path}, using default")
        return default_template


def create_citation_prompt(input_content: str, template: str) -> str:
    """
    Create a prompt for the citation verifier based on the input content.
    
    Args:
        input_content: Content of the design_decisions.md file
        template: Prompt template string
        
    Returns:
        Formatted prompt string
    """
    # Start with the template
    prompt = template + "\n\n"
    
    # Add the input content
    prompt += "### Document to Verify\n\n"
    prompt += input_content
    
    return prompt


def extract_csv_from_response(response: str) -> Optional[str]:
    """
    Extract the CSV content from the response.
    
    Args:
        response: Response from the OpenAI API
        
    Returns:
        CSV content as a string, or None if not found
    """
    # Look for CSV content in a code block
    if "```csv" in response:
        parts = response.split("```csv")
        if len(parts) > 1:
            csv_part = parts[1].split("```")[0].strip()
            return csv_part
    
    # Try with just ``` (no language specified)
    if "```" in response:
        parts = response.split("```")
        if len(parts) > 1:
            # Check if the content between ``` looks like CSV
            for i in range(1, len(parts), 2):
                if "," in parts[i] and "claim_id" in parts[i].lower():
                    return parts[i].strip()
    
    return None


def extract_markdown_from_response(response: str) -> Optional[str]:
    """
    Extract the Markdown content from the response.
    
    Args:
        response: Response from the OpenAI API
        
    Returns:
        Markdown content as a string, or None if not found
    """
    # Look for the Markdown content after the CSV
    if "```" in response:
        parts = response.split("```")
        if len(parts) > 2:
            # The Markdown content should be after the last code block
            return parts[-1].strip()
    
    # If we can't find a clear separation, return None
    return None


def verify_citations(
    input_path: str,
    output_dir: str,
    template_path: str,
    model: str,
    dry_run: bool = False,
) -> Optional[Dict[str, Any]]:
    """
    Verify citations in the input document.
    
    Args:
        input_path: Path to the design_decisions.md file
        output_dir: Directory to save the citation table and verified document
        template_path: Path to the prompt template file
        model: OpenAI model to use
        dry_run: If True, don't actually call the API
        
    Returns:
        Dictionary with the verification results and metadata, or None if dry_run is True
    """
    # Check if the input file exists
    if not os.path.exists(input_path):
        logger.error(f"Input file not found: {input_path}")
        return None
    
    # Load the input content
    input_content = read_text(input_path)
    
    # Load the prompt template
    template = load_prompt_template(template_path)
    
    # Create the citation prompt
    prompt = create_citation_prompt(input_content, template)
    
    # Output files
    ensure_directory(output_dir)
    csv_path = os.path.join(output_dir, "citation_table.csv")
    verified_path = os.path.join(output_dir, "design_decisions_verified.md")
    meta_path = os.path.join(output_dir, "citation_meta.json")
    
    if dry_run:
        logger.info(f"[DRY RUN] Would verify citations in: {input_path}")
        logger.info(f"[DRY RUN] Would save to: {csv_path} and {verified_path}")
        return None
    
    logger.info(f"Verifying citations in: {input_path}")
    
    try:
        # Initialize the OpenAI client
        client = OpenAIClient()
        
        # Create the messages for the API call
        messages = [
            {"role": "system", "content": "You are a citation verification expert."},
            {"role": "user", "content": prompt}
        ]
        
        # Call the API
        start_time = time.time()
        response = client.chat(model=model, messages=messages, temperature=0.2)
        elapsed_time = time.time() - start_time
        
        # Extract the content
        content = response["content"]
        
        # Extract the CSV and Markdown from the response
        csv_content = extract_csv_from_response(content)
        markdown_content = extract_markdown_from_response(content)
        
        if not csv_content:
            logger.error("Failed to extract CSV content from response")
            return {
                "error": "Failed to extract CSV content from response",
                "success": False,
            }
        
        if not markdown_content:
            logger.warning("Failed to extract Markdown content from response, using full response")
            markdown_content = content
        
        # Write the CSV to a file
        with open(csv_path, "w", encoding="utf-8") as f:
            f.write(csv_content)
        
        # Write the verified document to a file
        write_text(markdown_content, verified_path)
        
        # Create metadata
        prompt_hash = hashlib.md5(prompt.encode()).hexdigest()
        meta = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "model": model,
            "elapsed_time": elapsed_time,
            "token_usage": response["usage"],
            "prompt_hash": prompt_hash,
            "input_file": os.path.basename(input_path),
            "output_files": [
                os.path.basename(csv_path),
                os.path.basename(verified_path),
            ],
        }
        
        # Save metadata
        write_json(meta, meta_path)
        
        # Try to parse the CSV to get statistics
        try:
            # Read the CSV content into a DataFrame
            from io import StringIO
            df = pd.read_csv(StringIO(csv_content))
            
            # Count the number of claims by status
            status_counts = df["status"].value_counts().to_dict()
            
            # Add to metadata
            meta["claim_counts"] = {
                "total": len(df),
                "by_status": status_counts,
            }
            
            # Update the metadata file
            write_json(meta, meta_path)
            
            logger.info(f"Citation verification completed: {len(df)} claims processed")
            logger.info(f"Status counts: {status_counts}")
            
        except Exception as e:
            logger.warning(f"Failed to parse CSV for statistics: {str(e)}")
        
        logger.info(f"Citation verification completed in {elapsed_time:.2f}s")
        logger.info(f"Results saved to {csv_path} and {verified_path}")
        
        return {
            "csv_path": csv_path,
            "verified_path": verified_path,
            "meta_path": meta_path,
            "success": True,
        }
        
    except Exception as e:
        logger.error(f"Error verifying citations: {str(e)}")
        return {
            "error": str(e),
            "success": False,
        }


def main():
    """Main entry point for the script."""
    # Load environment variables from .env file
    # First try the default location, then try the planning directory
    if not dotenv.load_dotenv():
        dotenv.load_dotenv("planning/.env")
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Verify citations in the design decisions document.")
    parser.add_argument(
        "--input",
        type=str,
        default=DEFAULT_INPUT_PATH,
        help=f"Path to the design_decisions.md file (default: {DEFAULT_INPUT_PATH})",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Directory to save the citation table and verified document (default: {DEFAULT_OUTPUT_DIR})",
    )
    parser.add_argument(
        "--template",
        type=str,
        default=DEFAULT_PROMPT_TEMPLATE,
        help=f"Path to the prompt template file (default: {DEFAULT_PROMPT_TEMPLATE})",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=DEFAULT_MODEL,
        help=f"OpenAI model to use (default: {DEFAULT_MODEL})",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Don't actually call the API, just print what would happen",
    )
    
    args = parser.parse_args()
    
    # Check if the API key is set 
    if not (os.environ.get("OPENAI_API_KEY") or os.environ.get("OPEN_API_KEY")) and not args.dry_run:
        logger.error("API key environment variable not set. Please set OPEN_API_KEY in your .env file")
        sys.exit(1)
    
    try:
        # Run the citation verification
        result = verify_citations(
            input_path=args.input,
            output_dir=args.output_dir,
            template_path=args.template,
            model=args.model,
            dry_run=args.dry_run,
        )
        
        if args.dry_run:
            logger.info("[DRY RUN] Citation verification would be executed")
        elif result and result.get("success"):
            logger.info(f"Citation verification completed successfully")
            logger.info(f"Citation table: {result['csv_path']}")
            logger.info(f"Verified document: {result['verified_path']}")
        else:
            logger.error("Citation verification failed")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Error running citation verification: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
