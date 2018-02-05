from prepare_dataset import prep_follower_dataset
from sklearn.multiclass import OneVsRestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

train_xs, train_ys, test_xs, test_ys = prep_follower_dataset(followers_path='../../../users.csv',
                                                             labels_path='../../../700 profiles for claissifier - second round.csv',
                                                             test_size=0.2,
                                                             features=['followers_count', 'following_count', 'num_posts', 'isPrivate'])

prediction = OneVsRestClassifier(LogisticRegression(random_state=0, solver='liblinear')).fit(train_xs, train_ys).predict(test_xs)

print('accuracy: ' + str(accuracy_score(test_ys, prediction)))

