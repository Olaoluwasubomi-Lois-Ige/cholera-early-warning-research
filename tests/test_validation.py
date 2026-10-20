import math
import numpy as np
import pandas as pd
import pytest
from sklearn.metrics import fbeta_score
from cholera_early_warning import (f2_from_counts, f2_from_labels,
                                  make_walk_forward_splits, run_walk_forward)


def test_f2_from_hand_counted_confusion_matrix():
    # TP=2, FP=1, FN=1 -> 10/(10 + 1 + 4) = 2/3
    assert math.isclose(f2_from_counts(2,1,1),2/3)
    assert f2_from_counts(0,0,0) == 0.0


def test_f2_matches_sklearn_on_known_vectors():
    truth = np.array([1,1,1,0,0,0])
    pred = np.array([1,1,0,1,0,0])
    assert math.isclose(f2_from_labels(truth,pred),
                        fbeta_score(truth,pred,beta=2,zero_division=0))


def test_splits_train_only_on_past_years():
    splits = make_walk_forward_splits(range(2012,2018))
    assert splits[0] == {'train':[2012,2013,2014], 'test':[2015]}
    assert splits[-1] == {'train':[2012,2013,2014,2015,2016], 'test':[2017]}


def test_nonchronological_split_rejected():
    df = pd.DataFrame({'Year':[2012,2013],'Epi_Week':[1,1],
                       'Cases':[1,2], 'Cases_Lag1':[1,1]})
    with pytest.raises(ValueError,match='precede'):
        run_walk_forward(df,['Cases_Lag1'],[{'train':[2013],'test':[2012]}])


def test_walk_forward_runs_with_synthetic_data():
    # One independent toy research task: medians vary by week, and 2015 is held out.
    rows=[]
    for year in [2012,2013,2014,2015]:
        for week in range(1,7):
            cases = (year-2012)*2 + (week%3)
            rows.append({'Year':year,'Epi_Week':week,'Cases':cases,
                         'Cases_Lag1':cases-1,'Temp_Lag2':15+week,
                         'Precip_Lag2':week*2})
    df = pd.DataFrame(rows)
    from sklearn.linear_model import LogisticRegression
    result = run_walk_forward(
        df, ['Cases_Lag1','Temp_Lag2','Precip_Lag2'],
        [{'train':[2012,2013,2014], 'test':[2015]}],
        {'Logistic Regression': LogisticRegression(max_iter=1000,random_state=42)}
    )
    assert len(result) == 1
    assert result.loc[0, 'Test_Year'] == 2015
    assert result.loc[0, 'Train_Rows'] == 18
    assert result.loc[0, 'Test_Rows'] == 6
    assert all(0 <= result.loc[0,key] <= 1 for key in ['F2','AP','F1','Accuracy'])
