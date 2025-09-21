**Premier League Player Role Discovery: Multi-Agent Research Execution Plan**

**Author:** Mouhamed Mbengue

**Phase:** Pre-Build Research Automation (Multi-Agent, API-Based)

---

## Overview

In this phase of my project, I will be executing a **multi-agent research workflow** to finalize the foundational research for my Premier League Player Role Discovery platform. This includes verifying statistical definitions, clustering configurations, explainability frameworks, and UX/UI design patterns.

Rather than running queries manually through the ChatGPT interface, I will  **leverage the OpenAI API to run multiple subagent prompts in parallel** . This will significantly reduce time-to-insight and give me high-confidence decisions before I begin writing code for my ML pipelines and Streamlit app.

## Objectives

* Break down key research areas into scoped prompts.
* Run them as **parallel API calls** (subagents).
* Synthesize their results into actionable design decisions.
* Ensure that features, modeling, explainability, and UX are  **evidence-based and reproducible** .

---

## How I Will Do This (Step-by-Step)

### 1. **Define the Master Planner Prompt**

I will create a single prompt for a **Lead Agent** that outputs a list of 6–8 focused subagent tasks, such as:

* Define key features (progressive passes, pressures, xA, etc.)
* Evaluate clustering strategies (K range, Silhouette, GMM vs K-Means)
* Summarize best practices for SHAP visualizations
* Review UX patterns for PCA/UMAP scatter plots and radar charts
* Summarize public data licensing risks (FBref, Kaggle, etc.)

This list will be returned in JSON so I can easily extract and run each task independently.

### 2. **Set Up Subagent Prompts**

For each task in the plan, I will:

* Craft a prompt with a clear scope
* Define a stop condition (e.g., "when 3 credible sources are reviewed")
* Specify the expected format (Markdown summary, JSON table, bullet points)

### 3. **Build the Parallel Execution Script (Python)**

Using `concurrent.futures.ThreadPoolExecutor`, I will:

* Load the list of subagent prompts
* Call the **OpenAI API** using `openai.ChatCompletion.create()`
* Limit model usage to `gpt-4o` or `gpt-4o-mini` depending on complexity
* Run **all prompts concurrently**

This ensures that I collect all responses within seconds instead of hours.

### 4. **Save Outputs**

Each subagent's output will be saved to the `/outputs/` folder with filenames like:

* `01_feature_definitions.md`
* `02_k_selection_guidelines.md`
* `03_shap_ux_patterns.md`
* `04_license_risks.md`

Each will include citations, reasoning, and synthesis-ready insights.

### 5. **Merge & Synthesize**

Once the subagents return results, I will:

* Review all outputs manually
* Prompt a **Lead Agent (GPT-4o)** to synthesize all the pieces
* Create one unified document: `design_decisions.md`

This doc will finalize:

* My feature list and composite indices (PI, CCI, DA, FE)
* My clustering strategy (algorithm + K + evaluation gates)
* My SHAP explainability approach (global vs per-player)
* My UX structure (radar charts, PCA/UMAP scatter, SHAP barplots)

### 6. **Citation Agent (Verifier)**

I will prompt a separate agent to:

* Cross-check claims made in the synthesis
* Add citation footnotes or mark unverifiable claims

  I will run a dedicated Citation Agent using GPT-4o-mini after the synthesis step. Its job is to:\n\n- Extract factual claims from `design_decisions.md`\n- Match each claim to a verified source URL + short quote\n- Mark each claim as: `VERIFIED`, `PARTIAL`, or `UNVERIFIED`\n- Return a cleaned version of the document with inline references (e.g., [1], [2], etc.)\n- Output a `citation_table.csv` mapping all claims to their sources for full traceability\n\nAny claims marked `UNVERIFIED` will be reviewed manually. If no valid source exists, I will remove or rephrase them before the final freeze.

---

## Tools & Stack

* **Language Model:** OpenAI GPT-4o (primary), GPT-4o-mini (secondary)
* **Python Libraries:** `openai`, `concurrent.futures`, `os`, `dotenv`
* **Output Format:** `.md` and `.json` files per task
* **Hardware:** Local development machine or GitHub Codespace

---

## Timeline

| Day | Task                                                      |
| --- | --------------------------------------------------------- |
| 1   | Finalize Lead Agent prompt + generate subagent prompts    |
| 2   | Build & run Python script for parallel subagent execution |
| 3   | Synthesize outputs + write design_decisions.md            |
| 4   | Optional: Run citation checker + finalize report          |

---

## Benefits

* Saves me **dozens of hours** vs manual Googling
* Produces a **repeatable system** I can reuse for future research projects
* Ensures that my decisions (feature engineering, clustering, UX) are **justified with evidence**
* Positions me to code with **confidence and precision** during the build phase

---

## Next Step

Begin by finalizing the  **Lead Planner Prompt** , then running it through GPT-4o to generate the first set of subagent tasks.

Once those are defined, I'll execute the parallel subagent script and begin collecting and merging results.
