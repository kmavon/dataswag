import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import VotingClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.model_selection import GridSearchCV
from prepare_dataset import get_entire_dataset

models = [
    LogisticRegression(random_state=1, solver='liblinear', class_weight='balanced'),
    SVC(probability=True, kernel='rbf', class_weight='balanced'),
    GaussianNB(),
    GradientBoostingClassifier(n_estimators=1000, learning_rate=0.1, max_depth=100, random_state=1)
]

xs, ys = get_entire_dataset()
params = {'gamma': np.arange(0.1, 1.0, 0.1), 'C': np.arange(0.1, 5.0, 0.1)}
grid = GridSearchCV(estimator=models[1], param_grid=params, cv=3, scoring='f1', n_jobs=8)
grid.fit(xs, ys)
print(grid.best_score_)
print(grid.best_params_)
