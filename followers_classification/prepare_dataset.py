import pandas as pd
import numpy as np
import re
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import normalize
from sklearn.model_selection import KFold
from sklearn.feature_extraction.text import CountVectorizer
import cv2
import os
import pytesseract


def build_datasets(users, folds=3):
    i = 0
    kf = KFold(n_splits=folds, shuffle=True)
    for train_index, test_index in kf.split(users):
        users.iloc[train_index].to_csv('data/kfoldsplit/train_' + str(i) + '.csv', index=False, header=True)
        users.iloc[test_index].to_csv('data/kfoldsplit/test_' + str(i) + '.csv', index=False, header=True)
        i += 1


def prep_follower_dataset(account_features=[], post_features=[], derived_features=[], features_to_scale=[], new_one=False, folds=None):
    features = account_features + post_features + derived_features
    x_train_sets = []
    x_test_sets = []
    y_train_sets = []
    y_test_sets = []
    if not new_one:
        if not folds:
            x_train_sets = pd.read_csv('data/datasets/xs.csv', usecols=features)
            y_train_sets = pd.read_csv('data/datasets/ys.csv', usecols=['label']).as_matrix().ravel()
            num_others = y_train_sets.sum()
            print('consumers in dataset: ' + str(y_train_sets.shape[0] - num_others))
            print('others in dataset: ' + str(num_others))

        else:
            for i in range(folds):
                x_train_sets.append(pd.read_csv('data/datasets/train_xs_' + str(i) + '.csv', usecols=features))
                x_test_sets.append(pd.read_csv('data/datasets/test_xs_' + str(i) + '.csv', usecols=features))
                y_train_sets.append(pd.read_csv('data/datasets/train_ys_' + str(i) + '.csv', usecols=['label']).as_matrix().ravel())
                y_test_sets.append(pd.read_csv('data/datasets/test_ys_' + str(i) + '.csv', usecols=['label']).as_matrix().ravel())
                print('users in train set: ' + str(x_train_sets[0].shape[0]))
                print('users in test set: ' + str(x_test_sets[0].shape[0]))
    else:
        print('generating new dataset')
        result = get_labels()
        if account_features:
            result = pd.merge(result, get_follower_accounts(account_features, result['username'].to_frame()), on='username')
        if post_features:
            result = pd.merge(result, get_follower_posts(post_features, result['username'].to_frame()),  on='username')
        if 'likes_per_follower' in derived_features:
            result['likes_per_follower'] = result['mean_likes']/result['followers_count']
            result.drop(columns=['mean_likes', 'followers_count'], inplace=True)
            features_to_scale.append('likes_per_follower')
            features.remove('mean_likes')
            features.remove('followers_count')
        if features_to_scale:
            result[features_to_scale] = normalize(X=result[features_to_scale])
        if not folds:
            x_train_sets = result[features]
            y_train_sets = result['label']
            write_dataset_csv(result, features)
            num_others = y_train_sets.sum()
            print('consumers in dataset: ' + str(y_train_sets.shape[0] - num_others))
            print('others in dataset: ' + str(num_others))
        else:
            result.to_csv('data/result.csv', index=False, header=True)
            """kf = KFold(n_splits=folds, shuffle=True)
            i = 0"""
            for root, dirs, files in os.walk('data/kfoldsplit/'):
                for i in range(len(files)//4):
                    train_users = pd.read_csv('data/kfoldsplit/train_' + str(i) + '.csv')
                    test_users = pd.read_csv('data/kfoldsplit/test_' + str(i) + '.csv')

                    x_train_sets.append(result.merge(train_users, on='username')[features])
                    x_test_sets.append(result.merge(test_users, on='username')[features])
                    y_train_sets.append(result.merge(train_users, on='username')['label'].ravel())
                    y_test_sets.append(result.merge(test_users, on='username')['label'].ravel())
                    write_dataset_csv(result, features=features)

            """for train_index, test_index in kf.split(result):
                x_train_sets.append(result.iloc[train_index][features])
                x_test_sets.append(result.iloc[test_index][features])
                y_train_sets.append(result.iloc[train_index]['label'].ravel())
                y_test_sets.append(result.iloc[test_index]['label'].ravel())
                write_dataset_csv(result, features, i=i, train_index=train_index, test_index=test_index)
                i += 1"""
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
    names = ['id_user', 'username', 'profile_pic_url', 'followers_count', 'following_count', 'num_posts', 'biography',
             'isPrivate']
    stop_words = ['and', 'or', 'before', 'a', 'an', 'the', 'bio', 'is', 'all', 'to', 'for', 'by', 'in', 'of', 'we',
                  'our', 'at', 'my', 'be']
    brands = ['athenaprocopiou', 'daftcollectionofficial', 'dodobaror', 'emporiosirenuse', 'heidikleinswim',
              'lisamariefernandez', 'loupcharmant', 'miguelinagambaccini', 'muzungusisters', 'zeusndione']
    features.insert(0, 'username')

    # reading accounts data
    followers_data = pd.DataFrame(columns=names)
    for brand in brands:
        followers_data = followers_data.append(pd.read_csv(
            '../EMPORIOSIRENUSE_20173012/' + brand + '/followers data/' + brand + '_followers_accounts.csv'))

    # cleaning
    followers_data.rename(index=str, columns={"biography": "bio"}, inplace=True)
    followers_data.drop_duplicates(subset='id_user', inplace=True)
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
                                          vocabulary=['life', 'designer', 'director', 'love',
                                                      'london', 'me', 'creative', 'founder', 'lover'])
        cons_x = cons_vectorizer.fit_transform(followers_data['bio'])
        followers_data['cons_bio_sim'] = pd.Series(np.squeeze(np.asarray(cons_x.sum(axis=1))))
    if 'oth_bio_sim' in features:
        others_vectorizer = CountVectorizer(min_df=3, stop_words=stop_words,
                                            vocabulary=['shop', 'new', 'info', 'brand', 'shipping',
                                                        'jewelry', 'worldwide', 'online', 'world'])
        oth_x = others_vectorizer.fit_transform(followers_data['bio'])
        followers_data['oth_bio_sim'] = pd.Series(np.squeeze(np.asarray(oth_x.sum(axis=1))))
    if 'face' in features:
        followers_data = followers_data.merge(get_faces(), on='username')
    if 'text' in features:
        followers_data = followers_data.merge(get_text(), on='username')
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


def write_dataset_csv(result, features):
    for root, dirs, files in os.walk('data/kfoldsplit/'):
        for i in range(len(files) // 2):
            train_users = pd.read_csv('data/kfoldsplit/train_' + str(i) + '.csv')
            test_users = pd.read_csv('data/kfoldsplit/test_' + str(i) + '.csv')
            result.merge(train_users, on='username')[features].to_csv('data/datasets/train_xs_' + str(i) + '.csv', index=False)
            result.merge(test_users, on='username')[features].to_csv('data/datasets/test_xs_' + str(i) + '.csv', index=False)
            result.merge(train_users, on='username')['label'].to_csv('data/datasets/train_ys_' + str(i) + '.csv', index=False, header=True)
            result.merge(test_users, on='username')['label'].to_csv('data/datasets/test_ys_' + str(i) + '.csv', index=False, header=True)
    print('dataset saved to csv')


def clean_bios(bio):
    bio = bio.replace('b\'', '')
    bio = bio.replace('\\n', '')
    bio = bio.replace('\\r', '')
    bio = bio.replace('\\\\x', '<')
    bio = re.sub('<\w\w', '', bio)
    bio = bio.replace('\\', '')
    return bio


def get_faces():
    folder_path = '/home/moreno/Documents/DataShack/dataswag/followers_classification/data/profile_pics/all/'
    users_faces = pd.DataFrame(columns=['username', 'face'])
    paths = [
        '/home/moreno/anaconda3/envs/datashack/share/OpenCV/haarcascades/haarcascade_frontalface_default.xml',
        '/home/moreno/anaconda3/envs/datashack/share/OpenCV/haarcascades/haarcascade_profileface.xml']
    cascades = [cv2.CascadeClassifier(cascade_path) for cascade_path in paths]
    # looks for faces in profile pics
    for root, dirs, files in os.walk(folder_path):
        print(str(len(files)) + ' files were found at ' + folder_path)
        for filename in files:
            img = cv2.imread(folder_path + filename, 0)
            faces = 0
            for cascade in cascades:
                faces += len(cascade.detectMultiScale(img, scaleFactor=1.1, minNeighbors=5))
            users_faces = users_faces.append({'username': filename[:-4], 'face': int(faces > 0)}, ignore_index=True)
        break
    return users_faces


def get_text():
    folder_path = '/home/moreno/Documents/DataShack/dataswag/followers_classification/data/profile_pics/all/'
    users_text = pd.DataFrame(columns=['username', 'text'])
    for root, dirs, files in os.walk(folder_path):
        print(str(len(files)) + ' files were found at ' + folder_path)
        for filename in files:
            img = cv2.imread(folder_path + filename, 0)
            try:
                text = pytesseract.image_to_string(img)
            except TypeError:
                print(img)
            matches = len(text)
            users_text = users_text.append({'username': filename[:-4], 'text': int(matches > 0)}, ignore_index=True)
        break
    return users_text
