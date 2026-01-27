import pandas as pd
import numpy as np
from xgboost import XGBClassifier
from sklearn.model_selection import RandomizedSearchCV, TimeSeriesSplit
from sklearn.metrics import accuracy_score, log_loss, roc_auc_score
from pathlib import Path
from pipeline_config import config
import joblib

SEASONS = config['seasons']
file_name = file_name = f'{SEASONS[0]}.csv' if len(SEASONS) == 1 else f'{SEASONS[0]}-to-{SEASONS[len(SEASONS) - 1]}.csv'
path = Path(__file__).resolve().parent.parent.parent / 'data' / 'engineered' / file_name
assert path.exists()
df = pd.read_csv(path)

# Training phase

X = df.drop(columns='Win')
y = df['Win']

model = XGBClassifier(
    objective='binary:logistic',
    eval_metric='logloss',
    tree_method='hist',
    random_state=9
)

split = TimeSeriesSplit(n_splits=5)

param_grid = {
    'max_depth': [2, 3, 4],
    'learning_rate': [0.01, 0.05, 0.1],
    'n_estimators': [200, 400, 600],
    'min_child_weight': [1, 5, 10],
    'subsample': [0.6, 0.8, 1.0],
    'colsample_bytree': [0.6, 0.8, 1.0],
    'reg_alpha': [0, 0.1, 0.5],
    'reg_lambda': [1, 2, 5]
}

grid_search = RandomizedSearchCV(
    estimator=model,
    param_distributions=param_grid,
    scoring='neg_log_loss',
    n_iter=50,
    cv=split,
    n_jobs=-1,
    verbose=1
)

grid_search.fit(X, y)

best_model = grid_search.best_estimator_
print('Best hyperparameters: ', grid_search.best_params_)

# Testing phase

test_df = pd.read_csv(Path(__file__).resolve().parent.parent.parent / 'data' / 'engineered' / '20252026.csv')
X_test = test_df.drop(columns='Win')
y_test = test_df['Win']
y_pred = best_model.predict(X_test)

majority = int(y.mean() >= 0.5)
baseline_majority = np.full_like(y_test, majority)
baseline_acc = accuracy_score(y_test, baseline_majority)
print('Majority baseline accuracy:' , baseline_acc)

accuracy = accuracy_score(y_test, y_pred)
print('accuracy:' ,accuracy)

y_prob = best_model.predict_proba(X_test)[:, 1]
print("Log loss:", log_loss(y_test, y_prob))

model_path = Path(__file__).resolve().parent.parent.parent / 'model' / 'model.pkl'
path.parent.mkdir(parents=True, exist_ok=True)
joblib.dump(best_model, model_path)