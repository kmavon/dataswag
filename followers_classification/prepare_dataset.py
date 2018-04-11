import pandas as pd
import numpy as np
import re
import datetime
from sklearn.preprocessing import RobustScaler
from sklearn.model_selection import KFold
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.mixture import GaussianMixture
import cv2
import os
import pytesseract

CONSUMERS_AVG_N_POST = 160
OTHERS_AVG_N_POST = 335


def build_datasets(users, folds=3):
    i = 0
    kf = KFold(n_splits=folds, shuffle=True)
    for train_index, test_index in kf.split(users):
        users.iloc[train_index].to_csv('data/kfoldsplit/train_' + str(i) + '.csv', index=False, header=True)
        users.iloc[test_index].to_csv('data/kfoldsplit/test_' + str(i) + '.csv', index=False, header=True)
        i += 1


def get_entire_dataset(features):
    result = pd.read_csv('data/result.csv')
    return result[features], result['label']


def impute_n_posts(row):
    if row['posts_count'] == 0:
        if row['label'] == 0:
            row['posts_count'] = CONSUMERS_AVG_N_POST
        else:
            row['posts_count'] = OTHERS_AVG_N_POST
    return row['posts_count']


def prep_follower_dataset(account_features=[], post_features=[], derived_features=[], features_to_scale=[], new_one=False):
    features = account_features + post_features + derived_features
    x_train_sets = []
    x_test_sets = []
    y_train_sets = []
    y_test_sets = []
    if 'bios' in derived_features:
        features.remove('bios')
        features = features + ['cons_bio', 'oth_bio']
        features_to_scale = features_to_scale + ['cons_bio', 'oth_bio']
    if 'f2f' in derived_features:
        account_features = account_features + ['followers_count', 'following_count']
    if 'tags' in derived_features:
        features.remove('tags')
        features = features + ['tag var', 'tag mean']
    if 'mentions' in derived_features:
        features.remove('mentions')
        features = features + ['mention var', 'mention mean']
    if 'tags' in features_to_scale:
        features_to_scale.remove('tags')
        features_to_scale = features_to_scale + ['tag var', 'tag mean']
    if 'mentions' in features_to_scale:
        features_to_scale.remove('mentions')
        features_to_scale = features_to_scale + ['mention var', 'mention mean']
    if not new_one:
        for root, dirs, files in os.walk('data/kfoldsplit/'):
            for i in range(len(files)//2):
                x_train_sets.append(pd.read_csv('data/datasets/train_xs_' + str(i) + '.csv', usecols=features))
                x_test_sets.append(pd.read_csv('data/datasets/test_xs_' + str(i) + '.csv', usecols=features))
                y_train_sets.append(pd.read_csv('data/datasets/train_ys_' + str(i) + '.csv', usecols=['label']).as_matrix().ravel())
                y_test_sets.append(pd.read_csv('data/datasets/test_ys_' + str(i) + '.csv'))
                print('users in train set: ' + str(x_train_sets[0].shape[0]))
                print('users in test set: ' + str(x_test_sets[0].shape[0]))
    else:
        print('generating new dataset')
        result = get_labels()
        if account_features:
            follower_accounts = pd.read_csv('data/features/follower_accounts.csv')
            result = result.merge(follower_accounts[account_features + ['username']], on='username')
        if post_features:
            follower_posts = pd.read_csv('data/features/follower_posts.csv')
            result = pd.merge(result, follower_posts[post_features + ['username']],  on='username', how='left')
            result.fillna(0, inplace=True)
            result['posts_count'] = result.apply(impute_n_posts, axis=1)
        if 'face' in derived_features:
            faces = pd.read_csv('data/features/faces.csv')
            result = result.merge(faces, on='username', how='outer')
            result.fillna(0, inplace=True)
        if 'text' in derived_features:
            texts = pd.read_csv('data/features/text.csv')
            result = result.merge(texts, on='username', how='outer')
            result.fillna(0, inplace=True)
        if 'bios' in derived_features:
            bios = pd.read_csv('data/features/bios.csv')
            result = result.merge(bios, on='username')
        if 'mentions' in derived_features:
            mentions = pd.read_csv('data/features/mentions_vects.csv')
            result = result.merge(mentions, on='username', how='outer')
            result.fillna(0, inplace=True)
        if 'tags' in derived_features:
            tags = pd.read_csv('data/features/tags_vects.csv')
            result = result.merge(tags, on='username', how='outer')
            result.fillna(0, inplace=True)
        if 'f2f' in derived_features:
            result['f2f'] = result['followers_count']/(result['following_count'] + 1000)
        if features_to_scale:
            result[features_to_scale] = RobustScaler().fit_transform(X=result[features_to_scale])

        result.to_csv('data/result.csv', index=False, header=True)
        for root, dirs, files in os.walk('data/kfoldsplit/'):
            for i in range(len(files)//2):
                train_users = pd.read_csv('data/kfoldsplit/train_' + str(i) + '.csv')
                test_users = pd.read_csv('data/kfoldsplit/test_' + str(i) + '.csv')

                x_train = result.merge(train_users, on='username')[features]
                x_test = result.merge(test_users, on='username')[features]
                y_train = result.merge(train_users, on='username')['label']
                y_test = result.merge(test_users, on='username')[['username', 'label']]

                x_train_sets.append(x_train)
                x_test_sets.append(x_test)
                y_train_sets.append(y_train.ravel())
                y_test_sets.append(y_test)

                x_train.to_csv('data/datasets/train_xs_' + str(i) + '.csv', index=False)
                x_test.to_csv('data/datasets/test_xs_' + str(i) + '.csv', index=False)
                y_train.to_csv('data/datasets/train_ys_' + str(i) + '.csv', index=False, header=True)
                y_test.to_csv('data/datasets/test_ys_' + str(i) + '.csv', index=False, header=True)
        print('users in train set: ' + str(x_train_sets[0].shape[0]))
        print('users in test set: ' + str(x_test_sets[0].shape[0]))

    return x_train_sets, y_train_sets, x_test_sets, y_test_sets


def get_labels():
    labels_data = pd.read_csv('data/700 profiles for claissifier - second round.csv',
                              delimiter=',',
                              usecols=['username', 'consumer', 'retailer', 'others'])
    labels_data['label'] = labels_data['consumer'].apply(lambda x: 1 - x)
    return labels_data[['username', 'label']]


def get_follower_accounts(users=None):
    names = ['id_user', 'username', 'profile_pic_url', 'followers_count', 'following_count', 'num_posts', 'biography',
             'isPrivate']
    brands = ['athenaprocopiou', 'daftcollectionofficial', 'dodobaror', 'emporiosirenuse', 'heidikleinswim',
              'lisamariefernandez', 'loupcharmant', 'miguelinagambaccini', 'muzungusisters', 'zeusndione']

    # reading accounts data
    followers_data = pd.DataFrame(columns=names)
    for brand in brands:
        followers_data = followers_data.append(pd.read_csv(
            '../EMPORIOSIRENUSE_20173012/' + brand + '/followers data/' + brand + '_followers_accounts.csv'))

    # cleaning
    followers_data.rename(index=str, columns={"biography": "bio"}, inplace=True)
    followers_data.drop_duplicates(subset='username', inplace=True)
    followers_data['bio'] = followers_data['bio'].fillna('BIOGRAPHYPLACEHOLDER')
    followers_data['bio'] = followers_data['bio'].apply(clean_bios)
    followers_data[['followers_count', 'following_count', 'num_posts']] = followers_data[
        ['followers_count', 'following_count', 'num_posts']].apply(pd.to_numeric, errors='coerce')
    followers_data = followers_data.fillna(0)
    followers_data['isPrivate'] = followers_data['isPrivate'].map({'True': 1, 'False': 0})
    followers_data['isPrivate'] = followers_data['isPrivate'].fillna(0)

    # selecting requested users
    if users is not None:
        followers_data = users.merge(followers_data, on='username')

    followers_data.to_csv('data/features/follower_accounts.csv', index=False, header=True)
    return followers_data


def get_follower_posts(users=None):
    brands = ['athenaprocopiou', 'daftcollectionofficial', 'dodobaror', 'emporiosirenuse', 'heidikleinswim',
              'lisamariefernandez', 'loupcharmant', 'miguelinagambaccini', 'muzungusisters', 'zeusndione']

    # reading posts data
    posts_data = pd.DataFrame()
    for brand in brands:
        posts_data = posts_data.append(pd.read_csv(
            '../EMPORIOSIRENUSE_20173012/' + brand + '/followers data/' + brand + '_followers_posts.csv',
            usecols=['username', 'id_post', 'likes_count', 'comment_count', 'taken_at_timestamp'], converters={'caption': clean_bios}))

    # posts data cleaning
    posts_data.drop_duplicates(subset='id_post', inplace=True)
    posts_data[['likes_count', 'comment_count']] = posts_data[['likes_count', 'comment_count']].apply(pd.to_numeric)

    if users is not None:
        posts_data = users.merge(posts_data, on='username')

    # aggregating posts data to get user features
    #posting_days = get_posting_regularity(posts_data)
    posts_count = posts_data.groupby(['username']).count()['id_post'].to_frame().reset_index()
    posts_mean_likes = posts_data.groupby(['username']).mean()['likes_count'].to_frame().reset_index()
    posts_mean_comments = posts_data.groupby(['username']).mean()['comment_count'].to_frame().reset_index()
    posts_count = posts_count.rename(index=str, columns={"id_post": "posts_count"})
    posts_mean_likes = posts_mean_likes.rename(index=str, columns={"likes_count": "mean_likes"})
    posts_mean_comments = posts_mean_comments.rename(index=str, columns={"comment_count": "mean_comments"})

    # merging features to produce result
    result = pd.merge(posts_count, posts_mean_likes, on='username')
    result = pd.merge(result, posts_mean_comments, on='username')
    #result = pd.merge(result, posting_days, on='username')
    result.to_csv('data/features/follower_posts.csv', index=False, header=True)
    return result


def clean_bios(bio):
    bio = bio.replace('b\'', '')
    bio = bio.replace('\n', '')
    bio = bio.replace('\r', '')
    bio = bio.replace('\\x', '<')
    bio = re.sub('<\w\w', '', bio)
    bio = bio.replace('\\', '')
    return bio


def get_bios(followers_data):
    stop_words = ['and', 'or', 'before', 'a', 'an', 'the', 'bio', 'is', 'all', 'to', 'for', 'by', 'in', 'of', 'we',
                  'our', 'at', 'my', 'be']

    cons_vectorizer = CountVectorizer(min_df=3, stop_words=stop_words,
                                      vocabulary=['life', 'designer', 'director', 'love',
                                                  'london', 'me', 'creative', 'founder', 'lover'])
    cons_x = cons_vectorizer.fit_transform(followers_data['bio'])
    print(followers_data.head())

    followers_data = followers_data.assign(cons_bio=pd.Series(np.squeeze(np.asarray(cons_x.sum(axis=1)))).values)

    others_vectorizer = CountVectorizer(min_df=3, stop_words=stop_words,
                                        vocabulary=['shop', 'new', 'info', 'brand', 'shipping',
                                                    'jewelry', 'worldwide', 'online', 'world'])
    oth_x = others_vectorizer.fit_transform(followers_data['bio'])
    followers_data = followers_data.assign(oth_bio=pd.Series(np.squeeze(np.asarray(oth_x.sum(axis=1)))).values)
    print(followers_data.head())
    followers_data[['username', 'oth_bio', 'cons_bio']].to_csv('data/features/bios.csv', index=False, header=True)
    return followers_data[['username', 'oth_bio', 'cons_bio']]


def get_faces():
    folder_path = '/home/moreno/Documents/DataShack/dataswag/followers_classification/data/profile_pics/all/'
    users_faces = pd.DataFrame(columns=['username', 'face'])
    paths = [
        '/home/moreno/anaconda3/envs/datashack/share/OpenCV/haarcascades/haarcascade_frontalface_alt2.xml',
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
    users_faces.to_csv('data/features/faces.csv', index=False, header=True)
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
    users_text.to_csv('data/features/text.csv', index=False, header=True)
    return users_text


def entropy(X, posts_count):
    print(X)
    X /= posts_count
    logX = np.log(X)
    print(-np.sum(np.multiply(X, logX)))
    return -np.sum(np.multiply(X, logX))


def get_tags_mentions_vects():
    brands = ['athenaprocopiou', 'daftcollectionofficial', 'dodobaror', 'emporiosirenuse', 'heidikleinswim',
              'lisamariefernandez', 'loupcharmant', 'miguelinagambaccini', 'muzungusisters', 'zeusndione']
    users = get_labels()
    tags = pd.DataFrame(columns=['username', 'tag', 'id_post', 'label'])
    mentions = pd.DataFrame(columns=['username', 'mention', 'id_post', 'label'])

    for brand in brands:
        brand_df = pd.read_csv(
            '../EMPORIOSIRENUSE_20173012/' + brand + '/followers data/' + brand + '_followers_posts.csv',
            usecols=['username', 'id_post'])
        brand_df = brand_df.merge(users, on='username')

        brand_tags = pd.read_csv(
            '../EMPORIOSIRENUSE_20173012/' + brand + '/followers data/' + brand + '_followers_tags.csv')
        brand_tags = brand_tags.merge(brand_df, on='id_post')
        tags = tags.append(brand_tags)

        brand_mentions = pd.read_csv(
            '../EMPORIOSIRENUSE_20173012/' + brand + '/followers data/' + brand + '_followers_mentions.csv')
        brand_mentions = brand_mentions.rename(index=str, columns={'username': 'mention'})
        brand_mentions = brand_mentions.merge(brand_df, on='id_post')
        mentions = mentions.append(brand_mentions)

    tags.drop(columns='label', inplace=True)
    tags.drop_duplicates(subset=['id_post', 'tag'], inplace=True)
    tags = tags.groupby(['username', 'tag']).count().groupby('username').agg(['mean', 'var'])
    tags.reset_index(inplace=True)
    tags.rename(index=str, columns={'id_post': 'tag'}, inplace=True)
    tags.columns = [' '.join(col).strip() for col in tags.columns.values]
    tags.to_csv('data/features/tags_vects.csv', index=False, header=True)

    mentions.drop(columns='label', inplace=True)
    mentions.drop_duplicates(subset=['id_post', 'mention'], inplace=True)
    mentions = mentions.groupby(['username', 'mention']).count().groupby('username').agg(['mean', 'var'])
    mentions.reset_index(inplace=True)
    mentions.rename(index=str, columns={'id_post': 'mention'}, inplace=True)
    mentions.columns = [' '.join(col).strip() for col in mentions.columns.values]
    mentions.to_csv('data/features/mentions_vects.csv', index=False, header=True)


def gen_date_from_timestamp(timestamp):
    return int(datetime.datetime.fromtimestamp(int(timestamp)).timetuple().tm_yday)


def get_posting_regularity(posts_data):
    posting_date = posts_data[['taken_at_timestamp', 'username', 'id_post']]
    posting_date.fillna(0.0, inplace=True)
    posting_date['taken_at_timestamp'] = posting_date['taken_at_timestamp'].apply(gen_date_from_timestamp)
    posting_days = posting_date.groupby(['username'], as_index=False)['taken_at_timestamp'].count()
    print(posting_date.head())
    posting_variance = posting_date.groupby(['username'], as_index=False)['taken_at_timestamp'].agg()
    print(posting_variance.head())
    return posting_days.merge(posting_variance, on='username')


def get_cost_files():
    labels = get_labels()
    posts_data = pd.read_csv('data/features/follower_posts.csv').merge(labels, on='username', how='right')
    posts_data.drop(columns='label', inplace=True)
    for root, dirs, files in os.walk('data/kfoldsplit/'):
        for i in range(len(files) // 2):
            test_users = pd.read_csv('data/datasets/test_ys_' + str(i) + '.csv')
            test_posts = test_users.merge(posts_data, how='left', on='username')
            test_posts.fillna(0, inplace=True)
            test_posts['posts_count'] = test_posts.apply(impute_n_posts, axis=1)
            test_posts[['username', 'posts_count']].to_csv('data/cost/cost' + str(i) + '.csv', index=False)
