import numpy as np
import pandas as pd
import pytest
from cholera_early_warning import (add_lagged_features, compute_outbreak_labels,
                                  daily_climate_to_weekly, mark_reporting_gaps)


def test_training_only_threshold_is_immune_to_future_outlier():
    df = pd.DataFrame({'Year':[2012,2013,2014,2015,2016],
                       'Epi_Week':[1]*5, 'Cases':[2,4,10,5,1000]})
    labelled = compute_outbreak_labels(df, [2012,2013,2014])
    assert labelled['Train_Week_Median'].tolist() == [4]*5
    assert labelled['Outbreak'].astype(int).tolist() == [0,0,1,1,1]
    without_future = compute_outbreak_labels(df.iloc[:4], [2012,2013,2014])
    assert labelled.loc[3,'Outbreak'] == without_future.loc[3,'Outbreak'] == 1


def test_unknown_threshold_and_missing_cases_are_not_zero_labelled():
    df = pd.DataFrame({'Year':[2012,2013,2014], 'Epi_Week':[1,1,2],
                       'Cases':[1,np.nan,3]})
    labelled = compute_outbreak_labels(df,[2012])
    assert pd.isna(labelled.loc[1,'Outbreak'])
    assert pd.isna(labelled.loc[2,'Outbreak'])
    assert labelled.loc[0,'Outbreak'] == 0


def test_lags_continue_across_year_boundary():
    df = pd.DataFrame({'Year':[2015,2015,2016,2016],
                       'Epi_Week':[51,52,1,2], 'Cases':[6,7,8,9],
                       'Mean_Temp':[20,21,22,23], 'Total_Precip':[1,2,3,4]})
    out = add_lagged_features(df)
    assert out.loc[2,'Cases_Lag1'] == 7
    assert out.loc[2,'Temp_Lag2'] == 20
    assert out.loc[3,'Precip_Lag3'] == 1


def test_explicit_reporting_gap_keeps_other_zero_year():
    df = pd.DataFrame({'Year':[2014,2015,2016], 'Epi_Week':[1,1,1], 'Cases':[0,0,4]})
    out = mark_reporting_gaps(df,[2015])
    assert out.loc[0,'Cases'] == 0
    assert np.isnan(out.loc[1,'Cases'])
    assert out.loc[2,'Cases'] == 4


def test_climate_blocks_match_notebook_rule():
    df = pd.DataFrame({'DOY':[1,2,8,358,365], 'T2M':[10,20,30,40,50]})
    out = daily_climate_to_weekly(df,'T2M',2015)
    assert out.loc[out['Epi_Week'].eq(1),'Mean_Temp'].iloc[0] == 15
    assert out.loc[out['Epi_Week'].eq(2),'Mean_Temp'].iloc[0] == 30
    assert out.loc[out['Epi_Week'].eq(52),'Mean_Temp'].iloc[0] == 45


def test_precipitation_sums_daily_grid_means():
    df = pd.DataFrame({'DOY':[1,1,2], 'PRECTOTCORR':[2,4,6]})
    out = daily_climate_to_weekly(df,'PRECTOTCORR',2015)
    assert out.loc[0,'Total_Precip'] == 9


def test_duplicate_weeks_rejected():
    df = pd.DataFrame({'Year':[2015,2015],'Epi_Week':[1,1],
                       'Cases':[1,2],'Mean_Temp':[20,21],'Total_Precip':[3,4]})
    with pytest.raises(ValueError,match='Duplicate'):
        add_lagged_features(df)
