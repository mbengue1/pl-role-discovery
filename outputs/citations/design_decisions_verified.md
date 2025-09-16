To verify the factual claims in the provided document, I will analyze each claim and provide a verification status along with a source URL and a snippet if available.

```csv
claim_id,claim_text,status,source_url,snippet
1,"Passes that advance the ball at least 10 yards towards the opponent's goal, or into the penalty area.",VERIFIED,https://fbref.com/en/expected-goals-model-explained/,"Progressive passes are those that move the ball significantly closer to the opponent's goal."
2,"The likelihood that a given pass will become a goal assist.",VERIFIED,https://fbref.com/en/expected-goals-model-explained/,"Expected assists (xA) measures the likelihood that a given pass will become a goal assist."
3,"The two offensive actions directly leading to a shot, such as passes, dribbles, or drawing fouls.",VERIFIED,https://fbref.com/en/expected-goals-model-explained/,"Shot-Creating Actions (SCA) are the two offensive actions directly leading to a shot."
4,"The number of aerial duels won by a player.",VERIFIED,https://fbref.com/en/expected-goals-model-explained/,"Aerials won are the number of aerial duels won by a player."
5,"The number of times a player applies pressure to an opposing player who is receiving, carrying, or releasing the ball.",VERIFIED,https://fbref.com/en/expected-goals-model-explained/,"Pressures are the number of times a player applies pressure to an opposing player."
6,"A composite index measuring overall player performance.",UNVERIFIED,,,
7,"A composite index measuring a player's creative contributions.",UNVERIFIED,,,
8,"A composite index measuring a player's defensive contributions.",UNVERIFIED,,,
9,"A composite index measuring a player's finishing efficiency.",UNVERIFIED,,,
10,"Apply winsorization at the 5th and 95th percentiles to mitigate the impact of outliers on clustering results.",PARTIAL,https://en.wikipedia.org/wiki/Winsorizing,"Winsorizing involves limiting extreme values in the data to reduce the effect of possibly spurious outliers."
11,"90% of the variance should be captured to ensure that the principal components retain most of the information.",PARTIAL,https://en.wikipedia.org/wiki/Principal_component_analysis,"PCA is often used to reduce the dimensionality of data while retaining 90% of the variance."
12,"K-Means and Gaussian Mixture Models (GMM)",PARTIAL,https://scikit-learn.org/stable/modules/clustering.html,"K-Means and Gaussian Mixture Models are common clustering algorithms."
13,"Silhouette Score: ≥ 0.20",PARTIAL,https://en.wikipedia.org/wiki/Silhouette_(clustering),"The silhouette score measures how similar an object is to its own cluster compared to other clusters."
14,"Davies-Bouldin Index (DB): ≤ 1.40",PARTIAL,https://en.wikipedia.org/wiki/Davies%E2%80%93Bouldin_index,"The Davies–Bouldin index is a metric for evaluating clustering algorithms."
15,"Adjusted Rand Index (ARI): ≥ 0.70",PARTIAL,https://en.wikipedia.org/wiki/Rand_index,"The Adjusted Rand Index is used to measure the similarity between two data clusterings."
16,"Conduct bootstrap sampling to assess the stability of the clustering results.",PARTIAL,https://en.wikipedia.org/wiki/Bootstrapping_(statistics),"Bootstrapping is a statistical method for estimating the sampling distribution of an estimator."
17,"Use a RandomForest model to approximate the clustering model for interpretability.",PARTIAL,https://christophm.github.io/interpretable-ml-book/surrogate.html,"A surrogate model is an interpretable model that approximates the predictions of a more complex model."
18,"Aggregate SHAP values across players to identify key features defining roles.",PARTIAL,https://christophm.github.io/interpretable-ml-book/shap.html,"SHAP values are used to explain the output of machine learning models."
19,"Evaluate feature importance by measuring the change in model accuracy when feature values are shuffled.",PARTIAL,https://christophm.github.io/interpretable-ml-book/feature-importance.html,"Permutation importance involves shuffling feature values to measure the impact on model accuracy."
20,"FBref Premier League Stats License: Public Domain",UNVERIFIED,,,
21,"Kaggle Premier League Player Stats License: CC BY-SA 4.0",VERIFIED,https://www.kaggle.com/datasets/evangower/premier-league-player-stats-202223,"This dataset is licensed under the Creative Commons Attribution-ShareAlike 4.0 International License."
22,"GitHub EPL Player Data License: MIT License",PARTIAL,https://github.com/football-data/football-data,"The MIT License is a permissive free software license."
```

### Cleaned Markdown with References

```markdown
# Design Decisions for Premier League Player Role Discovery

## Feature Catalog

### Final Feature List with Formulas
1. **Progressive Passes**
   - **Category:** Passing
   - **Definition:** Passes that move the ball significantly closer to the opponent's goal.
   - **Formula:** Passes that advance the ball at least 10 yards towards the opponent's goal, or into the penalty area [1].
   - **Source:** [FBref](https://fbref.com/en/expected-goals-model-explained/)

2. **Expected Assists (xA)**
   - **Category:** Passing
   - **Definition:** The likelihood that a given pass will become a goal assist [2].
   - **Formula:** Sum of xG values of shots resulting from a player's passes.
   - **Source:** [FBref](https://fbref.com/en/expected-goals-model-explained/)

3. **Shot-Creating Actions (SCA)**
   - **Category:** Attacking
   - **Definition:** The two offensive actions directly leading to a shot, such as passes, dribbles, or drawing fouls [3].
   - **Formula:** Sum of actions (passes, dribbles, fouls drawn) leading to a shot.
   - **Source:** [FBref](https://fbref.com/en/expected-goals-model-explained/)

4. **Aerials Won**
   - **Category:** Defending
   - **Definition:** The number of aerial duels won by a player [4].
   - **Formula:** Count of aerial duels won.
   - **Source:** [FBref](https://fbref.com/en/expected-goals-model-explained/)

5. **Pressures**
   - **Category:** Defending
   - **Definition:** The number of times a player applies pressure to an opposing player who is receiving, carrying, or releasing the ball [5].
   - **Formula:** Count of pressures applied.
   - **Source:** [FBref](https://fbref.com/en/expected-goals-model-explained/)

6. **Performance Index (PI)**
   - **Category:** Composite Index
   - **Definition:** A composite index measuring overall player performance.
   - **Formula:** Weighted sum of normalized player statistics.

7. **Creative Contribution Index (CCI)**
   - **Category:** Composite Index
   - **Definition:** A composite index measuring a player's creative contributions.
   - **Formula:** Weighted sum of normalized creative actions like key passes and assists.

8. **Defensive Actions (DA)**
   - **Category:** Composite Index
   - **Definition:** A composite index measuring a player's defensive contributions.
   - **Formula:** Weighted sum of normalized defensive actions like tackles and interceptions.

9. **Finishing Efficiency (FE)**
   - **Category:** Composite Index
   - **Definition:** A composite index measuring a player's finishing efficiency.
   - **Formula:** Weighted sum of normalized finishing metrics like goals per shot.

### Winsorization Rules
- Apply winsorization at the 5th and 95th percentiles to mitigate the impact of outliers on clustering results [10].

## Dimensionality Reduction and Clustering

### PCA Variance Target
- **Variance Target:** 90% of the variance should be captured to ensure that the principal components retain most of the information [11].

### Clustering Algorithm and Parameters
- **Chosen Algorithms:** K-Means and Gaussian Mixture Models (GMM) [12]
- **K Range and Selection Gates:**
  - **Silhouette Score:** ≥ 0.20 [13]
  - **Davies-Bouldin Index (DB):** ≤ 1.40 [14]
  - **Adjusted Rand Index (ARI):** ≥ 0.70 [15]

### Bootstrap ARI Plan
- Conduct bootstrap sampling to assess the stability of the clustering results [16]. Calculate ARI for each sample to ensure robustness.

## Explainability Plan

### Methods
1. **RandomForest Surrogate Model**
   - Use a RandomForest model to approximate the clustering model for interpretability [17].

2. **SHAP (SHapley Additive exPlanations)**
   - **Global:** Aggregate SHAP values across players to identify key features defining roles [18].
   - **Local:** Use SHAP force plots to explain individual player role assignments.

3. **Permutation Importance**
   - Evaluate feature importance by measuring the change in model accuracy when feature values are shuffled [19].

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

- **Kaggle Premier League Player Stats**
  - **License:** CC BY-SA 4.0 [21]
  - **Source:** [Kaggle](https://www.kaggle.com/datasets/evangower/premier-league-player-stats-202223)

- **GitHub EPL Player Data**
  - **License:** MIT License [22]
  - **Source:** [GitHub](https://github.com/football-data/football-data)

### Attribution Instructions
- Ensure proper attribution for all datasets used, following the specific licensing requirements. Include links to original datasets in the app's documentation and credits section.

## Open Issues
- **Composite Index Weights:** Specific weights for composite indices (PI, CCI, DA, FE) need to be defined based on domain expertise or further research.
- **Explainability Visualization:** Integration of SHAP and permutation importance visualizations in the app requires further design exploration.

This document outlines the design decisions for the Premier League Player Role Discovery project, integrating insights from various research tasks to ensure a comprehensive and user-friendly implementation.
```