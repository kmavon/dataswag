import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import recall_score
from sklearn.metrics import precision_score
from sklearn.metrics import f1_score
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix
from prepare_dataset import prep_follower_dataset


folds = 3
train_xs, train_ys, test_xs, ys = prep_follower_dataset(
    account_features=[],
    post_features=['posts_count'],
    derived_features=['face', 'text', 'f2f', 'mentions', 'tags', 'bios'],
    features_to_scale=['posts_count', 'tags', 'mentions', 'f2f'],
    new_one=False)

test_ys = [y['label'].ravel() for y in ys]

models = [
    LogisticRegression(random_state=1, solver='liblinear', class_weight='balanced', C=0.1),
    SVC(probability=True, kernel='rbf', class_weight='balanced', C=0.5, gamma=0.1),
    MLPClassifier(hidden_layer_sizes=(25, 10), activation='tanh', solver='lbfgs', alpha=0.8),
    MLPClassifier(hidden_layer_sizes=(20, 45), activation='logistic', solver='lbfgs', alpha=0.4),
    RandomForestClassifier(max_features=None, class_weight='balanced', n_jobs=8, n_estimators=60, criterion='entropy')
]

for model in models:
    fold_rec = []
    fold_prec = []
    fold_F1 = []
    fold_acc = []
    fn_posts = []
    fp_posts = []
    fn_posts_perc = []
    fp_posts_perc = []
    print('\n')
    print(model.__class__.__name__)
    for i in range(folds):
        predicted = model.fit(train_xs[i], train_ys[i]).predict(test_xs[i])
        rec = recall_score(test_ys[i], predicted)
        prec = precision_score(test_ys[i], predicted)
        F1 = f1_score(test_ys[i], predicted)
        acc = accuracy_score(test_ys[i], predicted)
        fold_rec.append(rec)
        fold_prec.append(prec)
        fold_F1.append(F1)
        fold_acc.append(acc)
        tn, fp, fn, tp = confusion_matrix(test_ys[i], predicted).ravel()
        cost = pd.read_csv('data/cost/cost' + str(i) + '.csv').assign(predicted=pd.Series(predicted).values)
        cost = cost.merge(ys[i], on='username', how='right')
        cost = cost.assign(dup=cost.duplicated(subset='username').values)
        cost.to_csv('predictions'+str(i)+'.csv', index=False)
        total_posts = cost['posts_count'].sum()
        fn_posts.append(cost.query('label == 1 & predicted == 0')['posts_count'].sum())
        fp_posts.append(cost.query('label == 0 & predicted == 1')['posts_count'].sum())
        fn_posts_perc.append(cost.query('label == 1 & predicted == 0')['posts_count'].sum()/total_posts)
        fp_posts_perc.append(cost.query('label == 0 & predicted == 1')['posts_count'].sum()/total_posts)

    print('recall mean: ' + '%.4f' % np.mean(fold_rec))
    print('precision mean: ' + '%.4f' % np.mean(fold_prec))
    print('F1 mean: ' + '%.4f' % np.mean(fold_F1))
    print('accuracy mean: ' + '%.4f' % np.mean(fold_acc))
    print('fp posts: ' + '%.1f' % np.mean(fp_posts) +
          ' (%.2f' % (np.mean(fp_posts_perc)*100) + '%)')
    print('fn posts: ' + '%.1f' % np.mean(fn_posts) +
          ' (%.2f' % (np.mean(fn_posts_perc)*100) + '%)')
