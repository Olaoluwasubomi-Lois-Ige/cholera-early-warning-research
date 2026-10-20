"""Chronological validation and F2 computation based on the MSc methodology."""

from collections.abc import Iterable
import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, average_precision_score, f1_score
from sklearn.preprocessing import StandardScaler
from .preprocessing import compute_outbreak_labels


def make_walk_forward_splits(years: Iterable[int], first_test_year: int = 2015) -> list[dict]:
    """Return expanding training-year windows for next-year testing."""
    years = sorted(set(int(year) for year in years))
    return [dict(train=[y for y in years if y < test], test=[test])
            for test in years if test >= first_test_year
            and any(y < test for y in years)]


def f2_from_counts(tp: int, fp: int, fn: int) -> float:
    """F2 = 5 TP / (5 TP + 4 FN + FP); zero if no positive evidence."""
    if min(tp, fp, fn) < 0:
        raise ValueError('Confusion matrix counts cannot be negative')
    denominator = 5 * tp + 4 * fn + fp
    return (5 * tp / denominator) if denominator else 0.0


def f2_from_labels(y_true, y_pred) -> float:
    """Calculate F2 directly from binary outcomes, not by calling sklearn F2."""
    truth = np.asarray(y_true)
    prediction = np.asarray(y_pred)
    if truth.shape != prediction.shape:
        raise ValueError('Prediction and truth shapes must match')
    if not np.isin(truth, [0, 1]).all() or not np.isin(prediction, [0, 1]).all():
        raise ValueError('Labels must be 0 or 1')
    tp = int(np.sum((truth == 1) & (prediction == 1)))
    fp = int(np.sum((truth == 0) & (prediction == 1)))
    fn = int(np.sum((truth == 1) & (prediction == 0)))
    return f2_from_counts(tp, fp, fn)


def run_walk_forward(df: pd.DataFrame, features: list[str], splits: list[dict],
                     models: dict | None = None) -> pd.DataFrame:
    """Evaluate classifiers on past-to-future yearly splits.

    Train-year medians define labels for each round; scaling is fitted only on
    training rows. Empty test periods, such as Benin 2015, are skipped.
    """
    if models is None:
        models = {
            'Logistic Regression': LogisticRegression(max_iter=1000,
                                                       class_weight='balanced', random_state=42),
            'Random Forest': RandomForestClassifier(n_estimators=100,
                                                     class_weight='balanced', random_state=42),
        }
    records = []
    for round_number, split in enumerate(splits, 1):
        if not set(split['train']).isdisjoint(split['test']):
            raise ValueError('Training and test years must not overlap')
        if max(split['train']) >= min(split['test']):
            raise ValueError('Training years must precede test years')
        labelled = compute_outbreak_labels(df, split['train'])
        columns = [*features, 'Outbreak']
        train = labelled.loc[labelled['Year'].isin(split['train']), columns].dropna()
        test = labelled.loc[labelled['Year'].isin(split['test']), columns].dropna()
        if test.empty:
            continue
        if train.empty:
            raise ValueError(f'Round {round_number} has no valid training rows')
        X_train, X_test = train[features], test[features]
        y_train = train['Outbreak'].astype(int)
        y_test = test['Outbreak'].astype(int)
        if y_train.nunique() < 2:
            raise ValueError(f'Round {round_number} requires two training classes')
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        for name, estimator in models.items():
            model = clone(estimator)
            model.fit(X_train_scaled, y_train)
            pred = model.predict(X_test_scaled)
            probability = model.predict_proba(X_test_scaled)[:, 1]
            records.append({
                'Model': name, 'Round': round_number,
                'Train_Years': f"{min(split['train'])}-{max(split['train'])}",
                'Test_Year': min(split['test']), 'Train_Rows': len(train),
                'Test_Rows': len(test), 'Prevalence': float(y_test.mean()),
                'F2': f2_from_labels(y_test, pred),
                'AP': (float(average_precision_score(y_test, probability))
                       if int(y_test.sum()) else 0.0),
                'F1': float(f1_score(y_test, pred, zero_division=0)),
                'Accuracy': float(accuracy_score(y_test, pred)),
            })
    return pd.DataFrame(records)
