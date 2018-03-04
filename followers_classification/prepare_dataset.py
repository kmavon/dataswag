import pandas as pd
import numpy as np
import re
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import KFold
from sklearn.feature_extraction.text import CountVectorizer


def prep_follower_dataset(account_features=[], post_features=[], features_to_scale=[], new_one=False, folds=None):
    features = account_features + post_features
    x_train_sets = []
    x_test_sets = []
    y_train_sets = []
    y_test_sets = []
    if not new_one:
        if not folds:
            x_train_sets = pd.read_csv('data/test/xs.csv', usecols=features)
            y_train_sets = pd.read_csv('data/test/ys.csv', usecols=['label']).as_matrix().ravel()
            print('users in dataset: ' + str(x_train_sets.shape[0]))
        else:
            for i in range(folds):
                x_train_sets.append(pd.read_csv('data/test/train_xs_' + str(i) + '.csv', usecols=features))
                x_test_sets.append(pd.read_csv('data/test/test_xs_' + str(i) + '.csv', usecols=features))
                y_train_sets.append(pd.read_csv('data/test/train_ys_' + str(i) + '.csv', usecols=['label']).as_matrix().ravel())
                y_test_sets.append(pd.read_csv('data/test/test_ys_' + str(i) + '.csv', usecols=['label']).as_matrix().ravel())
                print('users in train set: ' + str(x_train_sets[0].shape[0]))
                print('users in test set: ' + str(x_test_sets[0].shape[0]))
    else:
        print('generating new dataset')
        result = get_labels()
        if account_features:
            result = pd.merge(result, get_follower_accounts(account_features, result['username'].to_frame()), on='username')
        if post_features:
            result = pd.merge(result, get_follower_posts(post_features, result['username'].to_frame()),  on='username')
        if features_to_scale:
            result[features_to_scale] = StandardScaler().fit_transform(X=result[features_to_scale])
        if not folds:
            x_train_sets = result[features]
            y_train_sets = result['label']
            write_dataset_csv(result, features)
            print('users in dataset: ' + str(x_train_sets.shape[0]))
        else:
            kf = KFold(n_splits=folds, shuffle=True)
            i = 0
            for train_index, test_index in kf.split(result):
                x_train_sets.append(result.iloc[train_index][features])
                x_test_sets.append(result.iloc[test_index][features])
                y_train_sets.append(result.iloc[train_index]['label'].ravel())
                y_test_sets.append(result.iloc[test_index]['label'].ravel())
                i += 1
                write_dataset_csv(result, features, i=i, train_index=train_index, test_index=test_index)
            print('users in train set: ' + str(x_train_sets[0].shape[0]))
            print('users in test set: ' + str(x_test_sets[0].shape[0]))

    return x_train_sets, y_train_sets, x_test_sets, y_test_sets


def get_labels():
    labels_data = pd.read_csv('data/700 profiles for claissifier - second round.csv',
                              delimiter=',',
                              usecols=['username', 'consumer', 'retailer', 'others'])
    # changing labels representation: [1,0,0]->1, [0,1,0]->0, [0,0,1]->0 (binary classifier: Consumer or not)
    labels_indices = []
    for label in labels_data.iloc[:, 1:].as_matrix():
        if np.where(label > 0)[0][0] > 0:
            labels_indices.append(1)
        else:
            labels_indices.append(0)
    labels_df = pd.DataFrame(data=labels_indices, columns=['label'], dtype=np.int8)
    labels_data = pd.concat([labels_data['username'], labels_df], axis=1)
    return labels_data


def get_follower_accounts(features, users=None):
    names = ['user_id', 'username', 'profile_pic', 'followers_count', 'following_count',
             'num_posts', 'bio', 'isPrivate']
    stop_words = ['and', 'or', 'before', 'a', 'an', 'the', 'bio', 'is', 'all', 'to', 'for', 'by', 'in', 'of', 'we',
                  'our', 'at', 'my', 'be']
    features.insert(0, 'username')
    followers_data = pd.read_csv('data/users.csv', delimiter=',', names=names)

    # cleaning
    followers_data['bio'] = followers_data['bio'].fillna('bio')
    followers_data['bio'] = followers_data['bio'].apply(clean_bios)
    followers_data[['followers_count', 'following_count', 'num_posts']] = followers_data[
        ['followers_count', 'following_count', 'num_posts']].apply(pd.to_numeric, errors='coerce')
    followers_data = followers_data.fillna(0)
    followers_data['isPrivate'] = followers_data['isPrivate'].map({'True': 1, 'False': 0})

    # selecting requested users
    if users is not None:
        followers_data = users.merge(followers_data, on='username')

    # adding features
    if 'cons_bio_sim' in features:
        cons_vectorizer = CountVectorizer(min_df=3, stop_words=stop_words,
                                          vocabulary=['fashion', 'com', 'life', 'designer', 'director', 'love',
                                                      'london', 'me', 'creative', 'founder', 'gmail', 'with', 'lover',
                                                      'stylist', 'travel'])

        cons_x = cons_vectorizer.fit_transform(followers_data['bio'])
        followers_data['cons_bio_sim'] = pd.Series(np.squeeze(np.asarray(cons_x.sum(axis=1))))
    if 'oth_bio_sim' in features:
        others_vectorizer = CountVectorizer(min_df=3, stop_words=stop_words,
                                            vocabulary=['com', 'fashion', 'shop', 'new', 'de', 'gmail', 'info', 'with',
                                                        'brand', 'shipping', 'jewelry', 'worldwide', 'online', 'us',
                                                        'world'])
        oth_x = others_vectorizer.fit_transform(followers_data['bio'])
        followers_data['oth_bio_sim'] = pd.Series(np.squeeze(np.asarray(oth_x.sum(axis=1))))
    return followers_data[features]


def get_follower_posts(features, users=None):
    brands = ['athenaprocopiou', 'daftcollectionofficial', 'dodobaror', 'emporiosirenuse', 'heidikleinswim',
              'lisamariefernandez', 'loupcharmant', 'miguelinagambaccini', 'muzungusisters', 'zeusndione']

    # reading posts data
    posts_data = pd.DataFrame(columns=['username', 'id_post', 'likes_count', 'comment_count'])
    for brand in brands:
        posts_data = posts_data.append(pd.read_csv(
            '../EMPORIOSIRENUSE_20173012/' + brand + '/followers data/' + brand + '_followers_posts.csv',
            usecols=['username', 'id_post', 'likes_count', 'comment_count']))

    # posts data cleaning
    posts_data.drop_duplicates(subset='id_post', inplace=True)
    posts_data[['likes_count', 'comment_count']] = posts_data[['likes_count', 'comment_count']].apply(pd.to_numeric)

    if users is not None:
        posts_data = users.merge(posts_data, on='username')

    # aggregating posts data to get user features
    posts_count = posts_data.groupby(['username']).count()['id_post'].to_frame().reset_index()
    posts_mean_likes = posts_data.groupby(['username']).mean()['likes_count'].to_frame().reset_index()
    posts_mean_comments = posts_data.groupby(['username']).mean()['comment_count'].to_frame().reset_index()
    posts_count = posts_count.rename(index=str, columns={"id_post": "posts_count"})
    posts_mean_likes = posts_mean_likes.rename(index=str, columns={"likes_count": "mean_likes"})
    posts_mean_comments = posts_mean_comments.rename(index=str, columns={"comment_count": "mean_comments"})

    # merging features to produce result
    result = pd.merge(pd.merge(posts_count, posts_mean_likes, on='username'), posts_mean_comments, on='username')
    features = ['username'] + features
    return result[features]


def write_dataset_csv(result, features=None, i=None, train_index=None, test_index=None):
    if i is None:
        result[features].to_csv('data/test/xs.csv', index=False)
        result['label'].to_csv('data/test/ys.csv', index=False, header=True)
    else:
        result.iloc[train_index][features].to_csv('data/test/train_xs_' + str(i) + '.csv', index=False)
        result.iloc[test_index][features].to_csv('data/test/test_xs_' + str(i) + '.csv', index=False)
        result.iloc[train_index]['label'].to_csv('data/test/train_ys_' + str(i) + '.csv', index=False, header=True)
        result.iloc[test_index]['label'].to_csv('data/test/test_ys_' + str(i) + '.csv', index=False, header=True)
    print('dataset saved to csv')


def clean_bios(bio):
    bio = bio.replace('b\'', '')
    bio = bio.replace('\\n', '')
    bio = bio.replace('\\r', '')
    bio = bio.replace('\\\\x', '<')
    bio = re.sub('<\w\w', '', bio)
    return bio
