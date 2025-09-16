# Premier League Player Role Discovery - Multi-Agent Research Toolchain

This toolchain automates the multi-agent research workflow for the Premier League Player Role Discovery project. It runs subagents in parallel against the OpenAI API, saves their outputs, synthesizes the results, and verifies citations.

## 📋 Overview

The toolchain consists of three main scripts:

1. **`run_subagents.py`**: Executes research tasks in parallel using the OpenAI API.
2. **`synthesize.py`**: Merges subagent outputs into a single design decisions document.
3. **`cite_verify.py`**: Verifies factual claims and generates a citation table.

## 🚀 Setup

### Prerequisites

- Python 3.8+
- OpenAI API key

### Installation

1. Clone this repository or navigate to your project directory.

2. Install the required packages:

```bash
pip install -r requirements.txt
```

3. Your `.env` file should be in the `planning/` directory with your OpenAI API key:

```
OPEN_API_KEY=sk-your-api-key
```

Note: The scripts will automatically look for the `.env` file in both the project root and the `planning/` directory and will recognize both `OPEN_API_KEY` and `OPENAI_API_KEY` variable names.

## 📂 Directory Structure

```
/scripts/
  run_subagents.py             # parallel subagent executor
  synthesize.py                # merges subagent outputs
  cite_verify.py               # verifies citations
/utils/
  openai_client.py             # OpenAI API wrapper with retry/backoff
  io_helpers.py                # file I/O utilities
/prompts/
  subagent_template.txt        # template for subagent prompts
  synthesizer.txt              # template for synthesis
  citation_agent.txt           # template for citation verification
/outputs/
  plan.json                    # research plan
  raw/                         # subagent outputs
  synthesis/                   # synthesized document
  citations/                   # citation table and verified document
```

## 🛠️ Usage

### 1. Run Subagents

Execute research tasks in parallel:

```bash
python scripts/run_subagents.py --plan outputs/plan.json --model gpt-4o-mini --max-workers 6
```

Options:
- `--plan`: Path to the plan.json file (default: `outputs/plan.json`)
- `--output-dir`: Directory to save results (default: `outputs/raw`)
- `--template`: Path to prompt template (default: `prompts/subagent_template.txt`)
- `--model`: OpenAI model to use (default: `gpt-4o-mini`)
- `--max-workers`: Maximum number of parallel workers (default: `6`)
- `--dry-run`: Preview without making API calls

### 2. Synthesize Results

Merge subagent outputs into a single document:

```bash
python scripts/synthesize.py
```

Options:
- `--input-dir`: Directory containing subagent outputs (default: `outputs/raw`)
- `--output-dir`: Directory to save synthesis (default: `outputs/synthesis`)
- `--template`: Path to prompt template (default: `prompts/synthesizer.txt`)
- `--model`: OpenAI model to use (default: `gpt-4o`)
- `--dry-run`: Preview without making API calls

### 3. Verify Citations

Verify factual claims and generate a citation table:

```bash
python scripts/cite_verify.py
```

Options:
- `--input`: Path to the design decisions document (default: `outputs/synthesis/design_decisions.md`)
- `--output-dir`: Directory to save citation table (default: `outputs/citations`)
- `--template`: Path to prompt template (default: `prompts/citation_agent.txt`)
- `--model`: OpenAI model to use (default: `gpt-4o`)
- `--dry-run`: Preview without making API calls

## 🧪 Testing

### Smoke Tests

1. Test the subagent runner with a dry run:

```bash
python scripts/run_subagents.py --dry-run
```

2. Test the synthesizer with a dry run:

```bash
python scripts/synthesize.py --dry-run
```

3. Test the citation verifier with a dry run:

```bash
python scripts/cite_verify.py --dry-run
```

## 📝 Plan Format

The `plan.json` file should follow this format:

```json
{
  "plan": [
    {
      "title": "Feature Definitions",
      "scope": "Define progressive passes, pressures, SCA, xA, take-ons; include formulas and data columns.",
      "format": "json_table",
      "tools": ["web"],
      "stop_condition": "After 3–5 credible primary sources"
    },
    // ... more tasks
  ],
  "global_success_criteria": "Decisions must be source-backed and non-overlapping."
}
```

## 📊 Outputs

- **Subagent results**: `outputs/raw/01_feature_definitions.md`, etc.
- **Synthesized document**: `outputs/synthesis/design_decisions.md`
- **Citation table**: `outputs/citations/citation_table.csv`
- **Verified document**: `outputs/citations/design_decisions_verified.md`

## 🔧 Advanced Usage

### Custom Prompts

You can customize the prompts by editing the files in the `prompts/` directory:

- `subagent_template.txt`: Template for subagent prompts
- `synthesizer.txt`: Template for synthesis
- `citation_agent.txt`: Template for citation verification

### Using Different Models

You can specify different OpenAI models for each step:

```bash
python scripts/run_subagents.py --model gpt-4o-mini
python scripts/synthesize.py --model gpt-4o
python scripts/cite_verify.py --model gpt-4o
```

### Timeout and Error Handling

The OpenAI client includes retry logic with exponential backoff for rate limits and transient errors. The default timeout is 90 seconds per API call.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
