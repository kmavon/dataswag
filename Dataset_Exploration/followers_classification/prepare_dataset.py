import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import KFold
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer


def prep_follower_dataset(account_features, post_features, features_to_scale, new_one=False, folds=4):
    features = account_features + post_features
    x_train_sets = []
    x_test_sets = []
    y_train_sets = []
    y_test_sets = []
    if not new_one:
        for i in range(folds):
            x_train_sets.append(pd.read_csv('data/test/train_xs_' + str(i) + '.csv', usecols=features))
            x_test_sets.append(pd.read_csv('data/test/test_xs_' + str(i) + '.csv', usecols=features))
            y_train_sets.append(pd.read_csv('data/test/train_ys_' + str(i) + '.csv', usecols=['label']).as_matrix().ravel())
            y_test_sets.append(pd.read_csv('data/test/test_ys_' + str(i) + '.csv', usecols=['label']).as_matrix().ravel())
        return x_train_sets, y_train_sets, x_test_sets, y_test_sets
    else:
        result = get_labels()
        if len(account_features) > 0:
            result = pd.merge(result, get_follower_accounts(account_features), on='username')
        if len(post_features) > 0:
            result = pd.merge(result, get_follower_posts(post_features),  on='username')
        if len(features_to_scale) > 0:
            result[features_to_scale] = StandardScaler().fit_transform(X=result[features_to_scale])
        kf = KFold(n_splits=folds, shuffle=True)
        i = 0
        for train_index, test_index in kf.split(result):
            x_train_sets.append(result.iloc[train_index][features])
            result.iloc[train_index][features].to_csv('data/test/train_xs_' + str(i) + '.csv', index=False)
            x_test_sets.append(result.iloc[test_index][features])
            result.iloc[test_index][features].to_csv('data/test/test_xs_' + str(i) + '.csv', index=False)
            y_train_sets.append(result.iloc[train_index]['label'].ravel())
            result.iloc[train_index]['label'].to_csv('data/test/train_ys_' + str(i) + '.csv', index=False, header=True)
            y_test_sets.append(result.iloc[test_index]['label'].ravel())
            result.iloc[test_index]['label'].to_csv('data/test/test_ys_' + str(i) + '.csv', index=False, header=True)
            i += 1
        return x_train_sets, y_train_sets, x_test_sets, y_test_sets


def get_follower_accounts(features):
    names = ['user_id', 'username', 'profile_pic', 'followers_count', 'following_count',
             'num_posts', 'bio', 'isPrivate']
    cols = features and names
    # username column needed to join data with labels
    features.insert(0, 'username')
    followers_data = pd.read_csv('data/users.csv', delimiter=',', names=names, usecols=cols)
    # converting isPrivate from string to boolean
    if 'isPrivate' in cols:
        followers_data['isPrivate'] = followers_data['isPrivate'].map({'True': 1, 'False': 0})
    # removing nan values
    followers_data[['followers_count', 'following_count', 'num_posts']] = followers_data[
        ['followers_count', 'following_count', 'num_posts']].apply(pd.to_numeric, errors='coerce')
    followers_data = followers_data.fillna(0)
    return followers_data


def get_labels():
    labels_data = pd.read_csv('data/700 profiles for claissifier - second round.csv',
                              delimiter=',',
                              usecols=['username', 'consumer', 'retailer', 'others'])
    # changing labels representation: [0,0,0]->0, [0,1,0]->1, [0,0,1]->1 (binary classifier: Consumer or not)
    labels_indices = []
    for label in labels_data.iloc[:, 1:].as_matrix():
        if np.where(label > 0)[0][0] > 0:
            labels_indices.append(1)
        else:
            labels_indices.append(0)
    labels_df = pd.DataFrame(data=labels_indices, columns=['label'], dtype=np.int8)
    labels_data = pd.concat([labels_data['username'], labels_df], axis=1)
    return labels_data


def get_follower_posts(features):
    brands = ['athenaprocopiou', 'daftcollectionofficial', 'dodobaror', 'emporiosirenuse', 'heidikleinswim',
              'lisamariefernandez', 'loupcharmant', 'miguelinagambaccini', 'muzungusisters', 'zeusndione']
    posts_count = pd.DataFrame(columns=['username', 'id_post'])
    posts_mean_likes = pd.DataFrame(columns=['username', 'likes_count'])
    posts_mean_comments = pd.DataFrame(columns=['username', 'comment_count'])
    for brand in brands:
        posts_data = pd.read_csv(
            '../EMPORIOSIRENUSE_20173012/' + brand + '/followers data/' + brand + '_followers_posts.csv',
            usecols=['username', 'id_post', 'likes_count', 'comment_count'])
        posts_count = posts_count.append(
            posts_data.groupby(['username']).count()['id_post'].to_frame().reset_index(), ignore_index=True)
        posts_mean_likes = posts_mean_likes.append(
            posts_data.groupby(['username']).mean()['likes_count'].to_frame().reset_index(), ignore_index=True)
        posts_mean_comments = posts_mean_comments.append(
            posts_data.groupby(['username']).mean()['comment_count'].to_frame().reset_index(), ignore_index=True)

    posts_count = posts_count.rename(index=str, columns={"id_post": "posts_count"})
    posts_mean_likes = posts_mean_likes.rename(index=str, columns={"likes_count": "mean_likes"})
    posts_mean_comments = posts_mean_comments.rename(index=str, columns={"comment_count": "mean_comments"})
    result = pd.merge(pd.merge(posts_count, posts_mean_likes, on='username'), posts_mean_comments, on='username')
    return result[['username'] + features]


def gen_user_tags_files():
    brands = ['athenaprocopiou', 'daftcollectionofficial', 'dodobaror', 'emporiosirenuse', 'heidikleinswim',
              'lisamariefernandez', 'loupcharmant', 'miguelinagambaccini', 'muzungusisters', 'zeusndione']
    for brand in brands:
        tags_data = pd.read_csv('../EMPORIOSIRENUSE_20173012/' + brand + '/followers data/' + brand + '_followers_tags.csv')
        posts_data = pd.read_csv('../EMPORIOSIRENUSE_20173012/' + brand + '/followers data/' + brand + '_followers_posts.csv')
        posts_tags = posts_data.merge(tags_data, on="id_post")
        print(brand + ' tags merged')
        post_tags_list = posts_tags.groupby(['username'])['tag'].apply(list).to_frame()
        print(brand + ' tags listed')
        post_tags_list.to_csv('data/tags_list/' + brand + '_user_tags_list.csv', header=True)
        print(brand + ' tags file created')
        tags_data = []
        posts_data = []
        posts_tags = []
        post_tags_list = []

    brands = ['athenaprocopiou', 'daftcollectionofficial', 'dodobaror', 'emporiosirenuse', 'heidikleinswim',
              'lisamariefernandez', 'loupcharmant', 'miguelinagambaccini', 'muzungusisters', 'zeusndione']
    allbrands_user_tags = pd.DataFrame(columns=['username', 'tag'])
    for brand in brands:
        user_tags = pd.read_csv('data/tags_list/' + brand + '_user_tags_list.csv', encoding='latin-1')
        allbrands_user_tags = allbrands_user_tags.append(user_tags, ignore_index=True)
        print(brand + ' added')
    allbrands_user_tags.drop_duplicates(subset='username')
    allbrands_user_tags.to_csv('data/tags_list/allbrands_user_tags_list.csv', header=True)


def user_tags_vect(user_tags, idf=False):
    corpus = user_tags['tag']
    users = len(corpus)
    if idf:
        vectorizer = TfidfVectorizer()
    else:
        vectorizer = CountVectorizer(min_df=1)
    print('vectorizer initialized')
    X = vectorizer.fit_transform(corpus)
    print('vectorizer fit')
    for i in range(X.shape[0]):
        user_tags.at[i, 'tag'] = X[i].todense()
        print(str(i) + " OF " + str(users))
    return user_tags


def get_emojis(textDF):
    """
        extracts emojis from strings in DataFrame textDF, they're encoded in hex value notation,
        Returns the same df given in input, with a list
        emojis dexcriptions for each user instead of the text
    """
    em_dict = pd.read_csv('emoji_dictionary.csv',
                          delimiter=',',
                          converters={'R_Encoding': (lambda x: clean_em(x))},
                          usecols=['Name', 'R_Encoding']
                          )


def clean_em(em_string):
    em_string = em_string.replace('<', '\\\\x')
    em_string = em_string.replace('>', '')
    return em_string
