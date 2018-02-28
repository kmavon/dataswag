import numpy as np
import sklearn
from prepare_dataset import prep_follower_dataset
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import average_precision_score
from sklearn.metrics import roc_auc_score
from sklearn.metrics import precision_score

folds = 4
train_xs, train_ys, test_xs, test_ys = prep_follower_dataset(
    account_features=['followers_count', 'following_count'],
    post_features=['posts_count', 'mean_likes', 'mean_comments'],
    features_to_scale=['followers_count', 'following_count'] + ['posts_count', 'mean_likes', 'mean_comments'],
    new_one=False,
    folds=folds)

models = [
    #LogisticRegression(random_state=0, solver='liblinear'),
    SVC(),
    #KNeighborsClassifier(5)
]


for model in models:
    ap_scores = []
    roc_auc_scores = []
    prec_scores = []
    print('\n' + type(model).__name__ + '\n')
    for i in range(folds):
        print('Fold ' + str(i))
        classifier = model.fit(train_xs[i], train_ys[i])
        if isinstance(model, SVC):
            proba_prediction = classifier.decision_function(test_xs[i])
            class_zero_confidence = proba_prediction
        else:
            proba_prediction = classifier.predict_proba(test_xs[i])
            class_zero_confidence = [p[0] for p in proba_prediction]
        prediction = classifier.predict(test_xs[i])
        ap_scores.append(average_precision_score(test_ys[i], class_zero_confidence))
        roc_auc_scores.append(roc_auc_score(test_ys[i], class_zero_confidence))
        prec_scores.append(precision_score(test_ys[i], prediction))
        print('AP: ' + str(ap_scores[i]))
        print('ROC AUC: ' + str(roc_auc_scores[i]))
        print('Precision: ' + str(prec_scores[i]))
    print('AVG AP: ' + str(np.average(ap_scores)))
    print('AVG ROC AUC: ' + str(np.average(roc_auc_scores)))
    print('AVG Precision: ' + str(np.average(prec_scores)))
