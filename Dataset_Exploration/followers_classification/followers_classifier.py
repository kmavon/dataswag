import matplotlib.pyplot as plt
from sklearn.model_selection import cross_validate
from sklearn.model_selection import cross_val_predict
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import confusion_matrix
from prepare_dataset import prep_follower_dataset
from plotting import plot_confusion_matrix


folds = 4
train_xs, train_ys, test_xs, test_ys = prep_follower_dataset(
    account_features=['followers_count', 'following_count'],
    post_features= ['posts_count', 'mean_likes', 'mean_comments'],
    features_to_scale=['followers_count', 'following_count'] + ['posts_count', 'mean_likes', 'mean_comments'],
    new_one=True,
    folds=None)

models = [
    LogisticRegression(random_state=0, solver='liblinear'),
    SVC(probability=True),
    KNeighborsClassifier(5)
]

scoring = ['average_precision', 'roc_auc', 'f1_micro']

for model in models:
    print('\n' + type(model).__name__ + '\n')
    scores = cross_validate(model, train_xs, train_ys, cv=4, scoring=scoring, return_train_score=False)
    predicted = cross_val_predict(model, train_xs, train_ys, cv=4)

    for score in scoring:
        print(score + ' mean: ' + str(scores['test_' + score].mean()))

    cnf_matrix = confusion_matrix(train_ys, predicted)
    plt.figure()
    plot_confusion_matrix(cnf_matrix, ['Other', 'Consumer'], title=type(model).__name__)
    plt.show()
