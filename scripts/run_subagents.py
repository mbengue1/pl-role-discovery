#!/usr/bin/env python3
"""
Parallel subagent executor for Premier League Player Role Discovery research.

This script takes a plan.json file containing research tasks and executes them
in parallel using the OpenAI API. Each task is assigned to a separate subagent,
and the results are saved to the outputs/raw/ directory.
"""

import os
import sys
import time
import argparse
import concurrent.futures
import logging
from typing import Dict, List, Any, Optional
import hashlib

import dotenv
from tqdm import tqdm

# Add the parent directory to the path so we can import from utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.openai_client import OpenAIClient, sanitize_prompt
from utils.io_helpers import (
    read_json,
    write_json,
    write_text,
    read_text,
    safe_filename,
    ensure_directory,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Default directories
DEFAULT_PLAN_PATH = "outputs/plan.json"
DEFAULT_OUTPUT_DIR = "outputs/raw"
DEFAULT_PROMPT_TEMPLATE = "prompts/subagent_template_improved.txt"
DEFAULT_MODEL = "gpt-4o-mini"
DEFAULT_MAX_WORKERS = 6


def load_prompt_template(template_path: str) -> str:
    """
    Load the prompt template from a file, or use the default if the file doesn't exist.
    
    Args:
        template_path: Path to the prompt template file
        
    Returns:
        The prompt template as a string
    """
    default_template = """You are a specialist research subagent for the Premier League Player Role Discovery project.

PROJECT CONTEXT:
This project uses unsupervised machine learning to discover data-driven player roles in the English Premier League. 
Instead of traditional position labels (DEF, MID, FWD), we're clustering players into functional roles based on 
advanced statistics. The final output will be a Streamlit web app that allows users to:
1. Search for any Premier League player
2. View their clustered role and similar players
3. Explore role-specific statistics via radar charts and heatmaps
4. Visualize the player landscape in 2D PCA/UMAP scatter plots
5. Understand which features drive role assignment using explainability tools (SHAP/Permutation Importance)

Key technical components include:
- Feature engineering: Per-90 normalization + composite indices (PI, CCI, DA, FE)
- Clustering: PCA + K-Means/GMM to group players into roles
- Explainability: SHAP/permutation importance with RandomForest surrogates
- Visualization: Interactive radar charts, scatter plots, role heatmaps

You are assigned to research the following task:

<TASK_TITLE>

**Scope:**
<TASK_SCOPE>

**Deliverable Format:**
<TASK_FORMAT>

**Tools Available:**
<TASK_TOOLS>

**Heuristics:**
1. Start with a broad query, then narrow based on findings.
2. Prioritize primary sources and official documentation.
3. Avoid duplicate queries or sources.
4. If sources disagree, summarize all viewpoints.
5. Stop when the stop condition is met: <TASK_STOP_CONDITION>

Your research must be specific to the Premier League Player Role Discovery project context provided above.
Focus on soccer/football analytics, player statistics, and the specific technical approaches mentioned.

Return your result in the specified format, and also include:
- `citations`: List of URLs and short 15–40 word source quotes.
- `gaps`: Any info you expected to find but could not.
- `notes`: Optional insights about conflicting definitions or unclear points.
"""
    
    try:
        return read_text(template_path)
    except FileNotFoundError:
        logger.warning(f"Prompt template not found at {template_path}, using default")
        return default_template


def create_subagent_prompt(task: Dict[str, Any], template: str) -> str:
    """
    Create a prompt for a subagent based on a task and template.
    
    Args:
        task: Task dictionary from the plan
        template: Prompt template string
        
    Returns:
        Formatted prompt string
    """
    # Format the tools as a comma-separated string
    tools_str = ", ".join(task.get("tools", []))
    
    # Replace placeholders in the template
    prompt = template.replace("<TASK_TITLE>", task.get("title", ""))
    prompt = prompt.replace("<TASK_SCOPE>", task.get("scope", ""))
    prompt = prompt.replace("<TASK_FORMAT>", task.get("format", "markdown"))
    prompt = prompt.replace("<TASK_TOOLS>", tools_str)
    prompt = prompt.replace("<TASK_STOP_CONDITION>", task.get("stop_condition", ""))
    
    return prompt


def execute_task(
    task: Dict[str, Any],
    task_index: int,
    template: str,
    model: str,
    output_dir: str,
    dry_run: bool = False,
) -> Optional[Dict[str, Any]]:
    """
    Execute a single task using the OpenAI API.
    
    Args:
        task: Task dictionary from the plan
        task_index: Index of the task in the plan (for ordering)
        template: Prompt template string
        model: OpenAI model to use
        output_dir: Directory to save the results
        dry_run: If True, don't actually call the API
        
    Returns:
        Dictionary with the task results and metadata, or None if dry_run is True
    """
    # Create a safe filename prefix (e.g., "01")
    prefix = f"{task_index+1:02d}"
    
    # Create the prompt
    prompt = create_subagent_prompt(task, template)
    
    # Determine the output format and file extension
    format_type = task.get("format", "markdown").lower()
    if "json" in format_type:
        extension = "json"
    else:
        extension = "md"
    
    # Create safe filenames
    result_filename = safe_filename(prefix, task["title"], extension)
    meta_filename = safe_filename(prefix, f"{task['title']}_meta", "json")
    
    # Full paths
    result_path = os.path.join(output_dir, result_filename)
    meta_path = os.path.join(output_dir, meta_filename)
    
    if dry_run:
        logger.info(f"[DRY RUN] Would execute task: {task['title']}")
        logger.info(f"[DRY RUN] Would save to: {result_path}")
        return None
    
    logger.info(f"Executing task {prefix}: {task['title']}")
    
    try:
        # Initialize the OpenAI client
        client = OpenAIClient()
        
        # Create the messages for the API call
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": f"Research task: {task['title']}. Follow the instructions above."}
        ]
        
        # Call the API
        start_time = time.time()
        response = client.chat(model=model, messages=messages, temperature=0.2)
        elapsed_time = time.time() - start_time
        
        # Extract the content
        content = response["content"]
        
        # Save the result
        if extension == "json":
            # Try to clean up the response if it's supposed to be JSON
            # This handles cases where the model might wrap the JSON in markdown code blocks
            if content.strip().startswith("```") and content.strip().endswith("```"):
                content = content.strip().split("```")[1]
                if content.startswith("json"):
                    content = content[4:].strip()
            
        # Write the result to a file
        write_text(content, result_path)
        
        # Create metadata
        prompt_hash = hashlib.md5(prompt.encode()).hexdigest()
        meta = {
            "task": task,
            "model": model,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "elapsed_time": elapsed_time,
            "token_usage": response["usage"],
            "prompt_hash": prompt_hash,
            "prompt": sanitize_prompt(messages),
            "result_file": result_filename,
        }
        
        # Save metadata
        write_json(meta, meta_path)
        
        logger.info(f"Task {prefix} completed in {elapsed_time:.2f}s, saved to {result_path}")
        
        return {
            "task_index": task_index,
            "title": task["title"],
            "result_path": result_path,
            "meta_path": meta_path,
            "success": True,
        }
        
    except Exception as e:
        logger.error(f"Error executing task {prefix}: {str(e)}")
        return {
            "task_index": task_index,
            "title": task["title"],
            "error": str(e),
            "success": False,
        }


def run_subagents(
    plan_path: str,
    output_dir: str,
    template_path: str,
    model: str,
    max_workers: int,
    dry_run: bool = False,
    task_index: int = None,
) -> List[Dict[str, Any]]:
    """
    Run subagents in parallel for all tasks in the plan.
    
    Args:
        plan_path: Path to the plan.json file
        output_dir: Directory to save the results
        template_path: Path to the prompt template file
        model: OpenAI model to use
        max_workers: Maximum number of workers to use for parallel execution
        dry_run: If True, don't actually call the API
        task_index: If provided, only run the task at this index
        
    Returns:
        List of dictionaries with the results of each task
    """
    # Load the plan
    plan = read_json(plan_path)
    tasks = plan.get("plan", [])
    
    if not tasks:
        logger.error(f"No tasks found in plan: {plan_path}")
        return []
    
    # If task_index is provided, only run that specific task
    if task_index is not None:
        if task_index < 0 or task_index >= len(tasks):
            logger.error(f"Invalid task index: {task_index}. Valid range: 0-{len(tasks)-1}")
            return []
        tasks = [tasks[task_index]]
    
    # Load the prompt template
    template = load_prompt_template(template_path)
    
    # Ensure the output directory exists
    ensure_directory(output_dir)
    
    # Determine the actual number of workers (min of max_workers and number of tasks)
    actual_workers = min(max_workers, len(tasks))
    
    logger.info(f"Running {len(tasks)} tasks with {actual_workers} workers")
    
    # Execute tasks in parallel
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=actual_workers) as executor:
        # Create a dictionary of futures to tasks
        future_to_task = {
            executor.submit(
                execute_task, task, i if task_index is None else task_index, template, model, output_dir, dry_run
            ): (i if task_index is None else task_index, task)
            for i, task in enumerate(tasks)
        }
        
        # Process the results as they complete
        for future in tqdm(
            concurrent.futures.as_completed(future_to_task),
            total=len(tasks),
            desc="Executing tasks",
        ):
            task_index, task = future_to_task[future]
            try:
                result = future.result()
                if result:
                    results.append(result)
            except Exception as e:
                logger.error(f"Task {task_index} failed: {str(e)}")
                results.append({
                    "task_index": task_index,
                    "title": task["title"],
                    "error": str(e),
                    "success": False,
                })
    
    # Sort results by task index
    results.sort(key=lambda x: x["task_index"])
    
    # Save a summary of the results
    if not dry_run:
        summary = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "model": model,
            "tasks_total": len(tasks),
            "tasks_successful": sum(1 for r in results if r.get("success", False)),
            "results": results,
        }
        write_json(summary, os.path.join(output_dir, "summary.json"))
    
    return results


def main():
    """Main entry point for the script."""
    # Load environment variables from .env file
    # First try the default location, then try the planning directory
    if not dotenv.load_dotenv():
        dotenv.load_dotenv("planning/.env")
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run subagents in parallel for research tasks.")
    parser.add_argument(
        "--plan",
        type=str,
        default=DEFAULT_PLAN_PATH,
        help=f"Path to the plan.json file (default: {DEFAULT_PLAN_PATH})",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Directory to save the results (default: {DEFAULT_OUTPUT_DIR})",
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
        "--max-workers",
        type=int,
        default=DEFAULT_MAX_WORKERS,
        help=f"Maximum number of workers to use for parallel execution (default: {DEFAULT_MAX_WORKERS})",
    )
    parser.add_argument(
        "--task-index",
        type=int,
        default=None,
        help="If provided, only run the task at this index (0-based)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Don't actually call the API, just print what would happen",
    )
    
    args = parser.parse_args()
    
    # Check if the API key is set (either OPENAI_API_KEY or OPEN_API_KEY)
    if not (os.environ.get("OPENAI_API_KEY") or os.environ.get("OPEN_API_KEY")) and not args.dry_run:
        logger.error("API key environment variable not set. Please set OPEN_API_KEY in your .env file")
        sys.exit(1)
    
    # Check if the plan file exists
    if not os.path.exists(args.plan):
        logger.error(f"Plan file not found: {args.plan}")
        sys.exit(1)
    
    try:
        # Run the subagents
        results = run_subagents(
            plan_path=args.plan,
            output_dir=args.output_dir,
            template_path=args.template,
            model=args.model,
            max_workers=args.max_workers,
            dry_run=args.dry_run,
            task_index=args.task_index,
        )
        
        # Print a summary
        successful = sum(1 for r in results if r.get("success", False))
        total = len(results)
        
        if args.dry_run:
            logger.info(f"[DRY RUN] Would execute {total} tasks")
        else:
            logger.info(f"Completed {successful}/{total} tasks successfully")
            
            if successful < total:
                logger.warning(f"Failed tasks: {total - successful}")
                for result in results:
                    if not result.get("success", False):
                        logger.warning(f"  - {result['title']}: {result.get('error', 'Unknown error')}")
        
    except Exception as e:
        logger.error(f"Error running subagents: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
