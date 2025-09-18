```markdown
# Design Decisions for Premier League Player Role Discovery

## Feature Catalog

### Final Feature List with Formulas
1. **Progressive Passes**
   - **Category:** Passing
   - **Definition:** Passes that move the ball significantly closer to the opponent's goal.
   - **Formula:** Passes that advance the ball at least 10 yards towards the opponent's goal, or into the penalty area.
   - **Source:** [FBref](https://fbref.com/en/expected-goals-model-explained/)

2. **Expected Assists (xA)**
   - **Category:** Passing
   - **Definition:** The likelihood that a given pass will become a goal assist.
   - **Formula:** Sum of xG values of shots resulting from a player's passes.
   - **Source:** [FBref](https://fbref.com/en/expected-goals-model-explained/)

3. **Shot-Creating Actions (SCA)**
   - **Category:** Attacking
   - **Definition:** The two offensive actions directly leading to a shot, such as passes, dribbles, or drawing fouls.
   - **Formula:** Sum of actions (passes, dribbles, fouls drawn) leading to a shot.
   - **Source:** [FBref](https://fbref.com/en/expected-goals-model-explained/)

4. **Aerials Won**
   - **Category:** Defending
   - **Definition:** The number of aerial duels won by a player.
   - **Formula:** Count of aerial duels won.
   - **Source:** [FBref](https://fbref.com/en/expected-goals-model-explained/)

5. **Pressures**
   - **Category:** Defending
   - **Definition:** The number of times a player applies pressure to an opposing player who is receiving, carrying, or releasing the ball.
   - **Formula:** Count of pressures applied.
   - **Source:** [FBref](https://fbref.com/en/expected-goals-model-explained/)

6. **Performance Index (PI)**
   - **Category:** Composite Index
   - **Definition:** A composite index measuring overall player performance.
   - **Formula:** Weighted sum of normalized player statistics.
   - **Source:** [Kaggle](https://kaggle.com/datasets)

7. **Creative Contribution Index (CCI)**
   - **Category:** Composite Index
   - **Definition:** A composite index measuring a player's creative contributions.
   - **Formula:** Weighted sum of normalized creative actions like key passes and assists.
   - **Source:** [Kaggle](https://kaggle.com/datasets)

8. **Defensive Actions (DA)**
   - **Category:** Composite Index
   - **Definition:** A composite index measuring a player's defensive contributions.
   - **Formula:** Weighted sum of normalized defensive actions like tackles and interceptions.
   - **Source:** [Kaggle](https://kaggle.com/datasets)

9. **Finishing Efficiency (FE)**
   - **Category:** Composite Index
   - **Definition:** A composite index measuring a player's finishing efficiency.
   - **Formula:** Weighted sum of normalized finishing metrics like goals per shot.
   - **Source:** [Kaggle](https://kaggle.com/datasets)

### Winsorization Rules
- Apply winsorization at the 5th and 95th percentiles to mitigate the impact of outliers on clustering results.

## Dimensionality Reduction and Clustering

### PCA Variance Target
- **Variance Target:** 90% of the variance should be captured to ensure that the principal components retain most of the information.

### Clustering Algorithm and Parameters
- **Chosen Algorithms:** K-Means and Gaussian Mixture Models (GMM)
- **K Range and Selection Gates:**
  - **Silhouette Score:** ≥ 0.20
  - **Davies-Bouldin Index (DB):** ≤ 1.40
  - **Adjusted Rand Index (ARI):** ≥ 0.70

### Bootstrap ARI Plan
- Conduct bootstrap sampling to assess the stability of the clustering results. Calculate ARI for each sample to ensure robustness.

## Explainability Plan

### Methods
1. **RandomForest Surrogate Model**
   - Use a RandomForest model to approximate the clustering model for interpretability.

2. **SHAP (SHapley Additive exPlanations)**
   - **Global:** Aggregate SHAP values across players to identify key features defining roles.
   - **Local:** Use SHAP force plots to explain individual player role assignments.

3. **Permutation Importance**
   - Evaluate feature importance by measuring the change in model accuracy when feature values are shuffled.

## UX Design Rules

### Visualization Components
1. **PCA/UMAP Scatter Plots**
   - Use color-coded clusters with interactive tooltips for player details.

2. **Radar Charts**
   - Display role-specific statistics with interactive elements to highlight individual metrics.

3. **SHAP Bar Charts**
   - Visualize global feature importance with bar charts, and use force plots for local explanations.

### Legend and Color Scheme
- Use a consistent color scheme across all visualizations to represent different player roles. Ensure accessibility by choosing colorblind-friendly palettes.

## Licensing and Attribution

### Dataset Licensing
- **FBref Premier League Stats**
  - **License:** Public Domain
  - **Source:** [FBref](https://fbref.com/en/comps/9/Premier-League-Stats)

- **Kaggle Premier League Player Stats**
  - **License:** CC BY-SA 4.0
  - **Source:** [Kaggle](https://www.kaggle.com/datasets/evangower/premier-league-player-stats-202223)

- **GitHub EPL Player Data**
  - **License:** MIT License
  - **Source:** [GitHub](https://github.com/football-data/football-data)

### Attribution Instructions
- Ensure proper attribution for all datasets used, following the specific licensing requirements. Include links to original datasets in the app's documentation and credits section.

## Open Issues
- **Composite Index Weights:** Specific weights for composite indices (PI, CCI, DA, FE) need to be defined based on domain expertise or further research.
- **Explainability Visualization:** Integration of SHAP and permutation importance visualizations in the app requires further design exploration.

This document outlines the design decisions for the Premier League Player Role Discovery project, integrating insights from various research tasks to ensure a comprehensive and user-friendly implementation.
```
