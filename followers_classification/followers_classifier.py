import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import recall_score
from sklearn.metrics import precision_score
from prepare_dataset import prep_follower_dataset
from sklearn.metrics import confusion_matrix

folds = 3
train_xs, train_ys, test_xs, test_ys = prep_follower_dataset(
    account_features=['face', 'text', 'cons_bio_sim', 'oth_bio_sim'],
    post_features=['posts_count'],
    derived_features=['likes_per_follower'],
    features_to_scale=['posts_count', 'likes_per_follower'],
    new_one=False,
    folds=folds)

models = [
    LogisticRegression(random_state=0, solver='liblinear'),
    SVC(probability=True, kernel='rbf'),
    KNeighborsClassifier(5),
    RandomForestClassifier()
]

precision_scores = []
recall_scores = []

for model in models:
    print('\n' + type(model).__name__ + '\n')
    fold_rec = []
    fold_prec = []
    for i in range(folds):
        # predicted_scores = model.predict_proba(test_xs[i])
        predicted = model.fit(train_xs[i], train_ys[i]).predict(test_xs[i])
        rec = recall_score(test_ys[i], predicted)
        prec = precision_score(test_ys[i], predicted)
        print('recall: ' + str(rec))
        print('precision: ' + str(prec))
        fold_rec.append(rec)
        fold_prec.append(prec)
        cm = confusion_matrix(test_ys[i], predicted)
        print(cm)
    print('recall mean: ' + str(np.mean(fold_rec)))
    print('precision mean: ' + str(np.mean(fold_prec)))
