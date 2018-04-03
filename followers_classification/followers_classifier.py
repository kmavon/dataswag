import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import VotingClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import recall_score
from sklearn.metrics import precision_score
from sklearn.metrics import f1_score
from prepare_dataset import prep_follower_dataset
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import GridSearchCV

folds = 3
train_xs, train_ys, test_xs, test_ys = prep_follower_dataset(
    account_features=[],
    post_features=['posts_count'],
    derived_features=['face', 'text', 'f2f', 'mentions', 'tags'],
    features_to_scale=['followers_count', 'following_count', 'posts_count', 'tags', 'mentions', 'f2f'],
    new_one=False)

models = [
    LogisticRegression(random_state=1, solver='liblinear', class_weight='balanced'),
    SVC(probability=True, kernel='rbf', class_weight='balanced', gamma=0.1, C=0.5),
    GaussianNB(),
    GradientBoostingClassifier(n_estimators=1000, learning_rate=0.1, max_depth=100, random_state=1)
]

fold_rec = []
fold_prec = []
fold_F1 = []
for i in range(folds):
    predicted = models[1].fit(train_xs[i], train_ys[i]).predict(test_xs[i])
    rec = recall_score(test_ys[i], predicted)
    prec = precision_score(test_ys[i], predicted)
    F1 = f1_score(test_ys[i], predicted)
    fold_rec.append(rec)
    fold_prec.append(prec)
    fold_F1.append(F1)

print('\n')
print('recall mean: ' + '%.4f' % np.mean(fold_rec))
print('precision mean: ' + '%.4f' % np.mean(fold_prec))
print('F1 mean: ' + '%.4f' % np.mean(fold_F1))
