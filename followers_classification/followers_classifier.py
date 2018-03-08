import matplotlib.pyplot as plt
from sklearn.model_selection import cross_validate
from sklearn.model_selection import cross_val_predict
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix
from prepare_dataset import prep_follower_dataset
from plotting import plot_confusion_matrix


folds = 4
train_xs, train_ys, test_xs, test_ys = prep_follower_dataset(
    account_features=['num_posts', 'cons_bio_sim', 'oth_bio_sim', 'followers_count', 'following_count'],
    post_features=['posts_count'],# 'mean_likes', 'mean_comments'],
    features_to_scale=['num_posts', 'cons_bio_sim', 'oth_bio_sim', 'posts_count', 'followers_count', 'following_count'],
    new_one=False,
    folds=None)

models = [
    LogisticRegression(random_state=0, solver='liblinear'),
    SVC(probability=True, kernel='rbf'),
    KNeighborsClassifier(5),
    RandomForestClassifier()
]

scoring = ['precision', 'recall', 'roc_auc', 'f1_micro', 'f1_macro']

for model in models:
    print('\n' + type(model).__name__ + '\n')
    scores = cross_validate(model, train_xs, train_ys, cv=folds, scoring=scoring, return_train_score=False)
    predicted = cross_val_predict(model, train_xs, train_ys, cv=folds)
    for score in scoring:
        print(score + ' mean: ' + str(scores['test_' + score].mean()))
    cnf_matrix = confusion_matrix(train_ys, predicted)
    plt.figure()
    plot_confusion_matrix(cnf_matrix, ['Consumer', 'Other'], title=type(model).__name__)

plt.show()
