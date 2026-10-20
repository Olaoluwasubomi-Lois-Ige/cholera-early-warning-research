"""Reusable data transformations adapted from the author's MSc research notebook.

The original NGN&BEN.ipynb has not been changed. See docs/IMPLEMENTATION_NOTES.md
for where this code differs from the exploratory notebook.
"""
from pathlib import Path
import numpy as np
import pandas as pd


def extract_country_weekly(year: int, country: str, folder: str | Path = '.') -> pd.DataFrame:
    """Read one HDX country-by-week annual file into Year/Epi_Week/Cases rows.

    Weeks 1--52 are retained, as in the original notebook. The HDX files are
    *not* included in this public-facing starter package.
    """
    folder = Path(folder)
    path = next((folder / f'wca_cases{year}_regcholeraplatformwca{ext}'
                 for ext in ('.xlsx', '.xls', '.csv')
                 if (folder / f'wca_cases{year}_regcholeraplatformwca{ext}').exists()), None)
    if path is None:
        raise FileNotFoundError(f'HDX file for {year} was not found in {folder}')

    df = pd.read_excel(path) if path.suffix in ('.xlsx', '.xls') else pd.read_csv(path)
    df.columns = df.columns.map(lambda c: str(c).strip())
    if 'Country' not in df.columns:
        raise ValueError('Expected a Country column')
    df = df.loc[~df['Country'].astype(str).str.startswith('#')].copy()
    df['Country'] = df['Country'].astype(str).str.strip()
    df = df.loc[df['Country'] == country]
    if df.empty:
        raise ValueError(f'{country!r} not found in {path.name}')

    week_cols = []
    for col in df.columns:
        name = col.upper()
        if name.startswith('WEEK') and name[4:].isdigit():
            week = int(name[4:])
        elif name.startswith('W') and name[1:].isdigit():
            week = int(name[1:])
        else:
            continue
        if 1 <= week <= 52:
            week_cols.append(col)
    if not week_cols:
        raise ValueError('No week columns (W1--W52 or Week1--Week52) found')

    long = df.melt(id_vars=['Country'], value_vars=week_cols,
                   var_name='Week', value_name='Cases')
    long['Epi_Week'] = long['Week'].str.extract(r'(\d+)', expand=False).astype(int)
    long['Cases'] = pd.to_numeric(long['Cases'].replace('-', np.nan), errors='coerce')
    long['Year'] = year
    return long[['Year', 'Epi_Week', 'Cases']].sort_values('Epi_Week').reset_index(drop=True)


def mark_reporting_gaps(df: pd.DataFrame, years: tuple[int, ...] | list[int]) -> pd.DataFrame:
    """Mark *specified* surveillance reporting-gap years as missing.

    Unlike the initial exploratory notebook, this function does not infer that
    every all-zero year is a reporting gap. The study identified Benin 2015
    specifically; Nigeria 2013 was retained and discussed as a limitation.
    """
    result = df.copy()
    result.loc[result['Year'].isin(years), 'Cases'] = np.nan
    return result


def daily_climate_to_weekly(daily_grid: pd.DataFrame, variable: str, year: int) -> pd.DataFrame:
    """Average grid points by day, then aggregate days using the notebook's bins.

    Bin = min((DOY - 1) // 7 + 1, 52). This is a *7-day DOY block*, not an
    independently verified ISO/CDC epidemiological week assignment.
    Temperature is averaged over days; precipitation is summed over days.
    """
    if variable not in ('T2M', 'PRECTOTCORR'):
        raise ValueError("variable must be 'T2M' or 'PRECTOTCORR'")
    if not {'DOY', variable}.issubset(daily_grid.columns):
        raise ValueError('Daily data must include DOY and requested variable')
    source = daily_grid[['DOY', variable]].copy()
    source[variable] = pd.to_numeric(source[variable], errors='coerce').replace(-999, np.nan)
    if source['DOY'].isna().any() or not source['DOY'].between(1, 366).all():
        raise ValueError('DOY must be between 1 and 366')
    daily = source.groupby('DOY', as_index=False)[variable].mean()
    daily['Epi_Week'] = ((daily['DOY'] - 1) // 7 + 1).clip(upper=52)
    output_name = 'Mean_Temp' if variable == 'T2M' else 'Total_Precip'
    aggregator = 'mean' if variable == 'T2M' else 'sum'
    weekly = daily.groupby('Epi_Week', as_index=False)[variable].agg(aggregator)
    weekly = weekly.rename(columns={variable: output_name})
    weekly.insert(0, 'Year', int(year))
    return weekly


def add_lagged_features(df: pd.DataFrame, max_climate_lag: int = 3) -> pd.DataFrame:
    """Make chronological case and climate lags without resetting at year edges.

    Data for one country should be passed per call. Lagged values across any
    reporting gap remain missing; this function does not impute them.
    """
    needed = {'Year', 'Epi_Week', 'Cases', 'Mean_Temp', 'Total_Precip'}
    if not needed.issubset(df.columns):
        raise ValueError(f'Missing columns: {sorted(needed - set(df.columns))}')
    if df.duplicated(['Year', 'Epi_Week']).any():
        raise ValueError('Duplicate country-week observations')
    if max_climate_lag < 1:
        raise ValueError('max_climate_lag must be >= 1')
    result = df.sort_values(['Year', 'Epi_Week']).reset_index(drop=True).copy()
    result['Cases_Lag1'] = result['Cases'].shift(1)
    for k in range(1, max_climate_lag + 1):
        result[f'Temp_Lag{k}'] = result['Mean_Temp'].shift(k)
        result[f'Precip_Lag{k}'] = result['Total_Precip'].shift(k)
    return result


def compute_outbreak_labels(df: pd.DataFrame, train_years: list[int] | tuple[int, ...]) -> pd.DataFrame:
    """Compute epi-week-specific median thresholds using training years alone.

    Outbreak = 1 when cases > training median for the same week; else 0.
    Missing cases or unknown training medians yield a missing label, rather
    than being incorrectly coded as non-outbreak.
    """
    if not train_years:
        raise ValueError('train_years must not be empty')
    needed = {'Year', 'Epi_Week', 'Cases'}
    if not needed.issubset(df.columns):
        raise ValueError(f'Missing columns: {sorted(needed - set(df.columns))}')
    train = df.loc[df['Year'].isin(train_years)]
    if train.empty:
        raise ValueError('No training-year observations found')
    medians = train.groupby('Epi_Week')['Cases'].median()
    result = df.copy()
    result['Train_Week_Median'] = result['Epi_Week'].map(medians)
    valid = result['Cases'].notna() & result['Train_Week_Median'].notna()
    label = (result['Cases'] > result['Train_Week_Median']).astype('Int64')
    result['Outbreak'] = label.where(valid, pd.NA)
    return result
