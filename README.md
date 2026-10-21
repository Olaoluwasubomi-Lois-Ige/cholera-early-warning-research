# Machine Learning for Weekly Early Warning of Cholera Outbreaks in Nigeria and Benin

**Author:** Olaoluwasubomi Lois Ige  
**Institution:** African Institute for Mathematical Sciences (AIMS), Rwanda  
**Programme:** MSc in Mathematical Sciences, Data Science  
**Research completed:** June 2026

## Project Overview

This repository contains the computational research developed for my MSc thesis, *Machine Learning for Weekly Early Warning of Cholera Outbreaks in Nigeria and Benin*.

The study investigated whether weekly cholera surveillance records and historical climate measurements could support early warning predictions in Nigeria and Benin.

I developed a weekly modelling framework using lagged surveillance and climate variables, chronological model evaluation and Bayesian uncertainty estimation.

## Research Data

The analysis covers **2012–2017** and combines two data sources:

- **Humanitarian Data Exchange (HDX):** Weekly reported cholera cases in Nigeria and Benin.
- **NASA POWER:** Daily temperature and precipitation measurements aggregated into weekly predictors.

Daily climate observations were averaged across geographical grid points, then converted to weekly temperature means and precipitation totals.

The final modelling datasets contained:

| Country | Usable weekly observations |
|---|---:|
| Nigeria | 309 |
| Benin | 256 |

Benin's all-zero surveillance records for 2015 were treated as a reporting gap rather than confirmed absence of cholera.

## Methodology

### 1. Data preparation and feature engineering

The modelling framework uses:

- Reported cholera cases from the previous week.
- Lagged temperature measurements.
- Lagged precipitation measurements.
- Outbreak labels based on historical epidemiological-week median thresholds.

The primary specification uses a one-week lag for reported cases and a two-week lag for climate variables. Additional climate-lag specifications were assessed.

### 2. Chronological evaluation

Models were evaluated using walk-forward validation, where earlier years were used for training and later years for testing.

Outbreak thresholds were calculated from historical training years, and standardisation was fitted using training data only. This prevented future observations from entering the corresponding training calculations.

### 3. Predictive models

Two classification methods were compared:

- Logistic regression
- Random forest

Performance was assessed using F2 score, average precision, F1 score and accuracy.

F2 score was prioritised because missing outbreak weeks is an important concern in early warning applications.

### 4. Bayesian logistic regression

Bayesian logistic regression was implemented using PyMC to estimate posterior distributions for model coefficients and assess uncertainty in predictor effects.

The analysis used the No-U-Turn Sampler (NUTS), with four MCMC chains, 1,000 tuning iterations and 1,000 posterior draws per chain.

Convergence was assessed using R-hat diagnostics, while posterior summaries included 95% highest-density intervals.

## Selected Research Results

The following results are from the principal evaluation rounds reported in the MSc thesis.

| Country | Model | Test year | F2 | Average precision |
|---|---|---:|---:|---:|
| Nigeria | Logistic regression | 2017 | 0.567 | 0.859 |
| Nigeria | Random forest | 2017 | **0.714** | **0.878** |
| Benin | Logistic regression | 2016 | **0.573** | 0.763 |
| Benin | Random forest | 2016 | 0.447 | **0.857** |

Random forest achieved the stronger F2 performance for Nigeria in the final 2017 evaluation round. In Benin's more informative 2016 evaluation, logistic regression performed better on F2, while random forest achieved higher average precision.

The Bayesian analyses showed that prior-week reported cases had the clearest positive association with outbreak probability in both countries. Temperature and precipitation effects were less consistent.

The research demonstrates the potential of surveillance-based early warning while showing how reporting gaps, limited historical records and differences between countries affect model evaluation.

## Repository Structure

```text
cholera-early-warning-research/
├── notebooks/
│   └── NGN_BEN_research_copy.ipynb
├── src/
│   └── cholera_early_warning/
├── tests/
├── docs/
│   ├── IMPLEMENTATION_NOTES.md
│   └── cholera_reproduction_verification.md
├── requirements.txt
└── README.md
```

- **notebooks/** contains the original combined research notebook.
- **src/** contains reusable computational functions extracted from the research workflow.
- **tests/** contains automated tests using synthetic data.
- **docs/** contains implementation notes and computational verification results.

## Testing and Reproducibility

The repository includes automated tests for core computational operations, including temporal data handling and model evaluation.

To install the dependencies for the extracted computational modules and run the tests:

```bash
python -m pip install -r requirements.txt
python -m pytest -q
```

The automated test suite contains 12 tests.

Reproducing the complete original notebook additionally requires the HDX surveillance and NASA POWER climate files, alongside the packages used for the Bayesian and geographical analyses.

The original notebook reads input files relative to its working directory. Dataset filenames and preparation details are documented in the notebook and supporting implementation notes.

Raw datasets are not included in the repository pending confirmation of redistribution permissions.

See [Computational Verification](docs/cholera_reproduction_verification.md) for the independently checked data preparation and predictive modelling results.

## Research Scope

This study was conducted as an academic proof of concept, not as a deployed outbreak forecasting service.

Its principal limitations concern surveillance completeness, the six-year study period, national-level aggregation and the availability of weekly predictors.

Future research could extend the analysis to longer surveillance records, subnational data and additional environmental and public health indicators.

## Author

**Olaoluwasubomi Lois Ige**  
MSc Mathematical Sciences (Data Science)  
African Institute for Mathematical Sciences, Rwanda

Research interests: Statistics, machine learning, biostatistics, infectious disease modelling and public health data science.
