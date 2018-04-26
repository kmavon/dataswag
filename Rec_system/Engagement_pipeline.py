
from sklearn import linear_model

class Engagement:
    
    #Initialization
    def __init__(self, train_path, save_path):
        self.train_path = train_path
        self.save_path = save_path
        
    def zscore(x,mu,std):
        zscore = (x-mu)/std
        return(zscore)

    def metrics(self, df): 
        df[['likes_count','followers']] = df[['likes_count','followers']].apply(pd.to_numeric)

        df['likes_score'] = (df['likes_count'])/(df['followers'])

        df['comments_score'] = (df['comment_count'])/(df['followers'])

        df['zscore_likes'] = zscore(df['likes_score'], df.likes_score.std(), df.likes_score.mean())

        df['zscore_comments'] = zscore(df['comments_score'], df.comments_score.std(), df.comments_score.mean())

        df['final_score'] = df['zscore_likes'] + df['zscore_comments']
        
        return df
        
    def prep_model(self, df, columns_to_remove): 
    
        df = df.drop(columns_to_remove, axis = 1, inplace = True)
        
        rands = np.random.seed(9001)
        msk = np.random.rand(len(df)) < 0.25
        data_train = df[~msk]
        data_test = df[msk]
        
        y_train = data_train.final_score
        y_test = data_test.final_score

        predictors = ['R_Mean', 'R_STD', 'R_MED', 'G_Mean', 'G_STD', 'G_MED', 'B_Mean',
               'B_STD', 'B_MED', 'Canny', 'ORB_X', 'ORB_Y',]
        X_train = data_train[predictors]
        X_test = data_test[predictors]
        
        return y_train, y_text, X_train, X_test ### should these be self?
        
    def linear(): ## yes those should be self if this is to run automatically
        
        lm = linear_model.LinearRegression() 
        model = lm.fit(X_train,y_train) 
        predictions = lm.predict(X_train)

        model.score(X_train,y_train), model.score(X_test,y_test)
        
    def Ridge():
        alpha= [10**-5, 10**-4, 10**-3, 10**-2, 10**-1, 10**0, 10**1, 10**2,10**3, ]
        ridge = RidgeCV(alphas=alpha, cv=10, fit_intercept=True)
        ridge.fit(X_train, y_train)
        
        train_score = ridge.score(X_train, y_train)
        test_score = ridge.score(X_test, y_test)
        return(train_score, test_score)



    def Lasso():
        alpha= [10**-5, 10**-4, 10**-3, 10**-2, 10**-1, 10**0, 10**1, 10**2,10**3, ]
        lasso = LassoCV(alphas=alpha, cv=10, max_iter=10000, fit_intercept=True)
        lasso.fit(X_train, y_train)
        
        train_score = lasso.score(X_train, y_train)
        test_score = lasso.score(X_test, y_test)
        
        return(train_score, test_score)

        
        ### I also did Poly Feats but seems poor choice here