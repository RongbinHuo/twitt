from sklearn import tree
import numpy as np


train_file = '../data/train_data.csv'
train = np.loadtxt( train_file, delimiter = ',' )
x_train = train[:,0:-1]
y_train = train[:,-1]
y_train = y_train.reshape( -1, 1 )

clf = tree.DecisionTreeClassifier()
clf = clf.fit(x_train, y_train)


result = clf.predict_proba(x_train)

c=len(x_train)
n=0
m=0
for i in range(len(result)):
	r = result[i]
	print r
	print x_train[i]
	if r[0]>r[2] and y_train[i][0]<0:
		n=n+1
	if r[0]<r[2] and y_train[i][0]>0:
		m=m+1
