#!/usr/bin/env python3
"""
Synthesizer for Premier League Player Role Discovery research.

This script takes the outputs from all subagents and synthesizes them into a
single, implementation-ready document named "design_decisions.md".
"""

import os
import sys
import time
import argparse
import logging
import hashlib
from typing import Dict, List, Any, Optional

import dotenv

# Add the parent directory to the path so we can import from utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.openai_client import OpenAIClient, sanitize_prompt
from utils.io_helpers import (
    read_json,
    write_json,
    write_text,
    read_text,
    list_files,
    ensure_directory,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Default directories
DEFAULT_INPUT_DIR = "outputs/raw"
DEFAULT_OUTPUT_DIR = "outputs/synthesis"
DEFAULT_PROMPT_TEMPLATE = "prompts/synthesizer.txt"
DEFAULT_MODEL = "gpt-4o"


def load_prompt_template(template_path: str) -> str:
    """
    Load the prompt template from a file, or use the default if the file doesn't exist.
    
    Args:
        template_path: Path to the prompt template file
        
    Returns:
        The prompt template as a string
    """
    default_template = """You are the Lead Researcher for the Premier League Player Role Discovery project. 

PROJECT CONTEXT:
This project uses unsupervised machine learning to discover data-driven player roles in the English Premier League. 
Instead of traditional position labels (DEF, MID, FWD), we're clustering players into functional roles based on 
advanced statistics. The final output will be a Streamlit web app that allows users to:
1. Search for any Premier League player
2. View their clustered role and similar players
3. Explore role-specific statistics via radar charts and heatmaps
4. Visualize the player landscape in 2D PCA/UMAP scatter plots
5. Understand which features drive role assignment using explainability tools (SHAP/Permutation Importance)

Merge the provided subagent outputs (quoted below) into a single, implementation-ready document named "design_decisions.md".
Must include:
- Final feature catalog with formulas (PI, CCI, DA, FE) and winsorization rules
- PCA variance target; chosen clustering algorithm(s); K range and selection gates (Silhouette/DB/CH); bootstrap ARI plan
- Explainability plan (RF surrogate + SHAP global/local + permutation)
- UX rules (PCA/UMAP viz, radar charts, SHAP bars, legend/color scheme)
- Licensing/Attribution instructions

Resolve conflicts, cite trade-offs, and clearly mark any open issues.
Output: a single Markdown document only.
"""
    
    try:
        return read_text(template_path)
    except FileNotFoundError:
        logger.warning(f"Prompt template not found at {template_path}, using default")
        return default_template


def load_subagent_outputs(input_dir: str) -> List[Dict[str, Any]]:
    """
    Load all subagent outputs from the input directory.
    
    Args:
        input_dir: Directory containing the subagent outputs
        
    Returns:
        List of dictionaries with the subagent outputs and metadata
    """
    # Get all files in the input directory
    all_files = list_files(input_dir)
    
    # Filter for result files (not metadata)
    result_files = [f for f in all_files if not f.endswith("_meta.json") and f != os.path.join(input_dir, "summary.json")]
    
    if not result_files:
        logger.error(f"No subagent outputs found in {input_dir}")
        return []
    
    outputs = []
    for file_path in sorted(result_files):
        try:
            # Get the file extension
            _, ext = os.path.splitext(file_path)
            
            # Read the file content
            content = read_text(file_path)
            
            # Get the corresponding metadata file
            meta_path = file_path.replace(ext, "_meta.json")
            if os.path.exists(meta_path):
                meta = read_json(meta_path)
                task = meta.get("task", {})
            else:
                # If no metadata file exists, create minimal metadata
                task = {"title": os.path.basename(file_path)}
                meta = {"task": task}
            
            outputs.append({
                "title": task.get("title", os.path.basename(file_path)),
                "content": content,
                "format": ext.lstrip("."),
                "file_path": file_path,
                "meta": meta,
            })
            
        except Exception as e:
            logger.error(f"Error loading subagent output {file_path}: {str(e)}")
    
    return outputs


def create_synthesis_prompt(outputs: List[Dict[str, Any]], template: str) -> str:
    """
    Create a prompt for the synthesizer based on the subagent outputs.
    
    Args:
        outputs: List of dictionaries with the subagent outputs
        template: Prompt template string
        
    Returns:
        Formatted prompt string
    """
    # Start with the template
    prompt = template + "\n\n"
    
    # Add the subagent outputs
    prompt += "### Subagent Outputs\n\n"
    
    for i, output in enumerate(outputs):
        prompt += f"#### {i+1}. {output['title']}\n\n"
        prompt += f"```{output['format']}\n{output['content']}\n```\n\n"
    
    return prompt


def synthesize(
    input_dir: str,
    output_dir: str,
    template_path: str,
    model: str,
    dry_run: bool = False,
) -> Optional[Dict[str, Any]]:
    """
    Synthesize the subagent outputs into a single document.
    
    Args:
        input_dir: Directory containing the subagent outputs
        output_dir: Directory to save the synthesis
        template_path: Path to the prompt template file
        model: OpenAI model to use
        dry_run: If True, don't actually call the API
        
    Returns:
        Dictionary with the synthesis results and metadata, or None if dry_run is True
    """
    # Load the subagent outputs
    outputs = load_subagent_outputs(input_dir)
    
    if not outputs:
        logger.error(f"No subagent outputs found in {input_dir}")
        return None
    
    # Load the prompt template
    template = load_prompt_template(template_path)
    
    # Create the synthesis prompt
    prompt = create_synthesis_prompt(outputs, template)
    
    # Output files
    ensure_directory(output_dir)
    output_path = os.path.join(output_dir, "design_decisions.md")
    meta_path = os.path.join(output_dir, "synthesis_meta.json")
    
    if dry_run:
        logger.info(f"[DRY RUN] Would synthesize {len(outputs)} subagent outputs")
        logger.info(f"[DRY RUN] Would save to: {output_path}")
        return None
    
    logger.info(f"Synthesizing {len(outputs)} subagent outputs")
    
    try:
        # Initialize the OpenAI client
        client = OpenAIClient()
        
        # Create the messages for the API call
        messages = [
            {"role": "system", "content": "You are a research synthesis expert."},
            {"role": "user", "content": prompt}
        ]
        
        # Call the API
        start_time = time.time()
        response = client.chat(model=model, messages=messages, temperature=0.2)
        elapsed_time = time.time() - start_time
        
        # Extract the content
        content = response["content"]
        
        # Write the synthesis to a file
        write_text(content, output_path)
        
        # Create metadata
        prompt_hash = hashlib.md5(prompt.encode()).hexdigest()
        meta = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "model": model,
            "elapsed_time": elapsed_time,
            "token_usage": response["usage"],
            "prompt_hash": prompt_hash,
            "input_files": [os.path.basename(output["file_path"]) for output in outputs],
            "output_file": os.path.basename(output_path),
        }
        
        # Save metadata
        write_json(meta, meta_path)
        
        logger.info(f"Synthesis completed in {elapsed_time:.2f}s, saved to {output_path}")
        
        return {
            "output_path": output_path,
            "meta_path": meta_path,
            "success": True,
        }
        
    except Exception as e:
        logger.error(f"Error synthesizing: {str(e)}")
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
    parser = argparse.ArgumentParser(description="Synthesize subagent outputs into a single document.")
    parser.add_argument(
        "--input-dir",
        type=str,
        default=DEFAULT_INPUT_DIR,
        help=f"Directory containing the subagent outputs (default: {DEFAULT_INPUT_DIR})",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Directory to save the synthesis (default: {DEFAULT_OUTPUT_DIR})",
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
        # Run the synthesis
        result = synthesize(
            input_dir=args.input_dir,
            output_dir=args.output_dir,
            template_path=args.template,
            model=args.model,
            dry_run=args.dry_run,
        )
        
        if args.dry_run:
            logger.info("[DRY RUN] Synthesis would be executed")
        elif result and result.get("success"):
            logger.info(f"Synthesis completed successfully: {result['output_path']}")
        else:
            logger.error("Synthesis failed")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Error running synthesis: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
