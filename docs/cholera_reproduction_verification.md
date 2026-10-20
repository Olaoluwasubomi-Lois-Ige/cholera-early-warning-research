# Computational reproduction verification

**Project:** Machine Learning for Weekly Early Warning of Cholera Outbreaks in Nigeria and Benin  
**Author of original research:** Olaoluwasubomi Lois Ige  
**Thesis:** MSc Mathematical Sciences, AIMS Rwanda, June 2026  
**Scope of this verification:** Re-execution of the original combined `NGN&BEN.ipynb` notebook's data loading, weekly aggregation, lag construction, training-only outbreak labels, and frequentist walk-forward model evaluations.

## Inputs used

- Six annual HDX workbooks: `wca_cases2012_regcholeraplatformwca.xlsx` through `wca_cases2017_regcholeraplatformwca.xlsx`.
- 48 Nigeria NASA POWER CSV files: temperature and precipitation, four regions, 2012–2017.
- 12 Benin NASA POWER CSV files: temperature and precipitation, 2012–2017.
- The author's original `NGN&BEN.ipynb` notebook.

The input climate files were placed together with the surveillance workbooks in a **temporary working directory** because the notebook expects its files relative to the working directory. Original input files and notebook were not modified. Only the relevant original code cells were executed for this check; cartographic plots and MCMC sampling were not rerun.

## Modelling data reproduced

| Country | Thesis usable weekly rows | Reproduced weekly rows | Difference |
|---|---:|---:|---:|
| Nigeria | 309 | 309 | 0 |
| Benin | 256 | 256 | 0 |

The Benin 2015 all-zero record was set to missing by the original notebook's reporting-gap logic, producing no 2015 test rows; the Benin 2016 test had 51 rows.

## Primary classifier walk-forward results

All metrics below were re-calculated from the supplied source files with the author's original notebook code. Rounded figures reproduce the values in thesis Tables 4.5 and 4.9.

| Country | Classifier | Test year | F2 | AP | F1 | Accuracy |
|---|---|---:|---:|---:|---:|---:|
| Nigeria | Logistic regression | 2015 | 0.131 | 0.725 | 0.190 | 0.346 |
| Nigeria | Random forest | 2015 | 0.424 | 0.805 | 0.519 | 0.500 |
| Nigeria | Logistic regression | 2016 | 0.000 | 0.146 | 0.000 | 0.904 |
| Nigeria | Random forest | 2016 | 0.139 | 0.135 | 0.095 | 0.635 |
| Nigeria | Logistic regression | 2017 | 0.567 | 0.859 | 0.667 | 0.692 |
| Nigeria | Random forest | 2017 | 0.714 | 0.878 | 0.778 | 0.769 |
| Benin | Logistic regression | 2016 | 0.573 | 0.763 | 0.638 | 0.667 |
| Benin | Random forest | 2016 | 0.447 | 0.857 | 0.564 | 0.667 |
| Benin | Logistic regression | 2017 | 0.000 | 0.047 | 0.000 | 0.942 |
| Benin | Random forest | 2017 | 0.000 | 0.066 | 0.000 | 0.885 |

The primary specification uses prior-week reported cases, two-week lagged temperature, and two-week lagged precipitation. The notebook recomputes weekly median outbreak thresholds separately within each training round and standardises predictors using training rows only.

## Climate-lag sensitivity checks

The reproduced one- and three-week sensitivity scores matched the thesis tables, including:

| Country | Model | Test year | Climate lag | Reproduced F2 | Reproduced AP |
|---|---|---:|---|---:|---:|
| Nigeria | Logistic regression | 2017 | 1 week | 0.567 | 0.857 |
| Nigeria | Logistic regression | 2017 | 3 weeks | 0.599 | 0.884 |
| Nigeria | Random forest | 2017 | 1 week | 0.719 | 0.821 |
| Nigeria | Random forest | 2017 | 3 weeks | 0.719 | 0.864 |
| Benin | Logistic regression | 2016 | 1 week | 0.639 | 0.788 |
| Benin | Logistic regression | 2016 | 3 weeks | 0.437 | 0.769 |
| Benin | Random forest | 2016 | 1 week | 0.410 | 0.874 |
| Benin | Random forest | 2016 | 3 weeks | 0.484 | 0.889 |
| Benin | Random forest | 2017 | 1 week | 0.625 | 0.500 |
| Benin | Random forest | 2017 | 3 weeks | 0.000 | 0.051 |

## Synthetic-data unit tests

The starter package's 12 pytest tests were rerun separately and passed: `12 passed`. The user also confirmed `12 passed in 12.11s` using Python 3.13.9 on their computer.

## Bayesian analyses: not independently rerun here

The original notebook **contains saved PyMC sampling outputs** for Nigeria Round 3 and Benin Round 2 which agree with thesis Tables 4.6, 4.7, 4.10, and 4.11. These include R-hat values below 1.01 and posterior summaries. This is a comparison of stored outputs and the thesis, **not** an independent rerun.

In the verification environment, installed `pymc` 5.27.1 failed on import because installed `arviz` 1.1.0 no longer exposes the `concat` interface required by that PyMC version. No alternative sampler was substituted, and the original modelling choices were not changed. A separate verification under a compatible, pinned PyMC/ArviZ environment remains to be done.

## Reproducibility and release cautions

- The original notebook expects all input `.xlsx` and `.csv` files in its working directory. The uploaded climate archive instead has `Dataset/Nigeria` and `Dataset/Benin` subfolders. For a public repository, document file arrangement or supply a clear loader without changing the analysis.
- Original climate day-of-year grouping is in consecutive seven-day blocks capped at week 52. This is the behaviour reproduced here; agreement with external epidemiological-week conventions was not independently assessed.
- Check redistribution permissions and any sensitive content in the raw input files and in Git commit history before making the repository public.
- The repository's `requirements.txt` covers the extracted functions and tests, not the notebook's full PyMC/ArviZ/Cartopy environment. Document full environment requirements before claiming that every original notebook cell is reproducible.

**Verification conclusion:** Frequentist data-processing, validation, classification and lag-sensitivity results were independently reproduced from the supplied raw data using the original notebook code. Independent Bayesian MCMC reproduction remains outstanding.
