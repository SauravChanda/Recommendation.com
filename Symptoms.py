import pandas as pd
import pickle
from sklearn.tree import DecisionTreeClassifier
train_data=pd.read_csv("./datasets/Training.csv")
test_data=pd.read_csv("./datasets/Testing.csv")

cols=train_data.columns
cols=cols[:-1]

train_x=train_data[cols]
train_y=train_data['prognosis']
test_x=test_data[cols]
test_y=test_data['prognosis']
class Symptoms:
    def symptoms(self):
        return train_x.columns
    def diseases(self):
        return train_y.unique()
    def fit(self):
        dt=DecisionTreeClassifier()

        dt.fit(train_x,train_y)


        dt.predict(test_x)
        dt.score(test_x,test_y)
        filename="sentiment_model.sav"
        pickle.dump(dt, open(filename, 'wb'))

    def predict(self,symptoms):
        filename="sentiment_model.sav"
        dt = pickle.load(open(filename, 'rb'))
        symptoms=symptoms.split(",")
        print(symptoms)
        x_new=[]
        for i in test_x.columns:
            if i in symptoms:
                x_new=x_new+[1]
            else:
                x_new=x_new+[0]
        x_new=[x_new]

        return dt.predict(x_new)



