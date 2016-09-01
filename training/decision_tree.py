from sklearn import tree
import numpy as np
import cPickle as pickle


output_model_file = '../model/decision_tree.pkl'
train_file = '../data/train_data.csv'
train = np.loadtxt( train_file, delimiter = ',' )
x_train = train[:,0:-1]
y_train = train[:,-1]
y_train = y_train.reshape( -1, 1 )

clf = tree.DecisionTreeClassifier()
clf = clf.fit(x_train, y_train)


result = clf.predict_proba(x_train)




test_file = '../data/validation.csv'
test = np.loadtxt( test_file, delimiter = ',' )
test_x_train = test[:,0:-1]
test_y_train = test[:,-1]
test_y_train = test_y_train.reshape( -1, 1 )
test_result = clf.predict_proba(test_x_train)
c=len(test_x_train)
n=0
m=0
x=0
for i in range(len(test_result)):
	r = test_result[i]
	print r
	print test_x_train[i]
	if r[0]>r[1] and test_y_train[i][0]<0 and r[0]>r[2]:
		n=n+1
	if r[0]<r[2] and test_y_train[i][0]>0 and r[1]<r[2]:
		m=m+1
	if r[1]>r[0] and test_y_train[i][0]==0 and r[1]>r[2]:
		x=x+1

pickle.dump( clf, open( output_model_file, 'wb' ))