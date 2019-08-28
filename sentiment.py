class nb:

    def fit(self,ipos,ineg,ireviews):
        
        import pandas as pd
        import nltk
        nltk.download('stopwords')
        from nltk.corpus import stopwords
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.model_selection import train_test_split
        from sklearn import naive_bayes
        from sklearn.metrics import roc_auc_score
        
        neg=pd.DataFrame.from_records(ineg,columns=['review', 'sentiment'])
        pos=pd.DataFrame.from_records(ipos,columns=['review', 'sentiment'])
        reviews=pd.DataFrame.from_records(ireviews,columns=['id', 'review'])

        r = pd.concat([pos, neg]).sample(frac=1).reset_index(drop=True)

        stopset=set(stopwords.words('english'))
        vectorizer=TfidfVectorizer(use_idf=True,lowercase=True,strip_accents='ascii',stop_words=stopset)

        y=r.sentiment

        x=vectorizer.fit_transform(r.review)

        x_train,x_test,y_train,y_test=train_test_split(x,y,random_state=42)

        clf=naive_bayes.MultinomialNB()
        clf.fit(x_train,y_train)

        roc_auc_score(y_test,clf.predict_proba(x_test)[:,1])

        test=reviews

        test['liked']=0
        test.review[759]

        #review=["bad doctor"]
        #vector=vectorizer.transform(review)
        #print(clf.predict(vector))

        i=0
        while i<len(test):
            vector=vectorizer.transform([test.review[i]])
            test.liked[i]=clf.predict(vector)
            print(i)
            i=i+1
           
        return test




