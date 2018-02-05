import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split


def prep_follower_dataset(followers_path, labels_path, test_size, features=['followers_count', 'following_count', 'num_posts']):
    """
        followers_path: path to <brand_name>_followers_accounts.csv file
        labels_path: path to 700 profiles for claissifier - second round.csv file
        cols: name of the columns in followers file to be used as features
    """
    #username column needed to join data with labels
    features.insert(0, 'username')

    followers_data = pd.read_csv(followers_path,
                                 delimiter=',',
                                 names=['user_id', 'username', 'profile_pic', 'followers_count', 'following_count', 'num_posts', 'bio', 'isPrivate'],
                                 usecols=features,
                                 )
    #converting isPrivate from string to boolean
    followers_data['isPrivate'] = followers_data['isPrivate'].map({'True': True, 'False': False})
    #removing nan values
    followers_data[['followers_count', 'following_count', 'num_posts']] = followers_data[['followers_count', 'following_count', 'num_posts']].apply(pd.to_numeric, errors='coerce')
    followers_data = followers_data.fillna(0)

    labels_data = pd.read_csv(labels_path, delimiter=',', usecols=['username', 'consumer', 'retailer', 'others'])
    #changing labels representation: [0,0,0]->0, [0,1,0]->1, [0,0,1]->2
    labels_indices = []
    for label in labels_data.iloc[:, 1:].as_matrix():
        #there are some unclassified samples, assuming consumers (0)
        if np.sum(label) <= 0:
            labels_indices.append(0)
        else:
            labels_indices.append(np.where(label > 0)[0][0])
    labels_df = pd.DataFrame(data=labels_indices, columns=['label'], dtype=np.int8)
    labels_data = pd.concat([labels_data['username'], labels_df], axis=1)

    result = pd.merge(followers_data, labels_data, on=['username', 'username'])
    train, test = train_test_split(result, test_size=test_size)

    return train[features[1:]], train['label'], test[features[1:]], test['label']
