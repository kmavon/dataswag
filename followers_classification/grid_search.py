import numpy as np
from sklearn.neural_network import MLPClassifier
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV
from prepare_dataset import get_entire_dataset

model = SVC(probability=True, class_weight='balanced')


xs, ys = get_entire_dataset(['posts_count', 'face', 'text', 'f2f']) #, 'mention var', 'mention mean', 'tag var', 'tag mean'])
# params = {'hidden_layer_sizes': [(x, y) for x in np.arange(5, 40, 5) for y in np.arange(5, 40, 5)],
#           'alpha': np.arange(0.1, 1.0, 0.1)}
params = {'kernel': ['sigmoid', 'rbf'], 'C': np.arange(1, 10000, 10), 'gamma': np.arange(0.1, 1.0, 0.1)}
# params = {'C': np.arange(0.1, 3, 0.1), 'solver': ['newton-cg', 'lbfgs', 'liblinear', 'sag', 'saga']}
# params = {'n_estimators': np.arange(10, 100, 5), 'criterion': ['gini', 'entropy']}
grid = GridSearchCV(estimator=model, param_grid=params, cv=3, scoring='recall', n_jobs=8)
grid.fit(xs, ys)
print(grid.best_score_)
print(grid.best_params_)
