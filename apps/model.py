# -*- coding: utf-8-*-
""" 训练模型 """
from sklearn.naive_bayes import GaussianNB, MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn import svm
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.externals import joblib
from data_processing import *
import numpy as np
import pandas as pd

def training(x_train, y_train):
    """ 选择算法并训练生成分类模型 """
    # clf = svm.SVC(class_weight='balanced').fit(x_train, y_train)
    # clf = MultinomialNB().fit(x_train, y_train)
    # clf = LogisticRegression().fit(x_train, y_train)
    # clf = MLPClassifier(solver='lbfgs', alpha=0.0001, hidden_layer_sizes=(10,), random_state=1).fit(x_train, y_train)
    # clf = RandomForestClassifier(class_weight='balanced').fit(x_train, y_train)
    clf = DecisionTreeClassifier().fit(x_train, y_train)
    return clf

def save_model(classifier, save_path="title_classifier.model"):
    """ 保存模型 """
    joblib.dump(classifier, save_path)

def load_model(model_file_path="title_classifier.model"):
    """ 加载模型 """
    clf = joblib.load(model_file_path)
    return clf

def predict(clf, x):
    """ 预测 """
    prediction = clf.predict(x)
    return prediction

if __name__ == '__main__':
    df = read_csv('train.csv')
    # X, y, features_dict = data_encode(df)

    X, y = data_encode(df)
    X = np.array(X, dtype='float32')
    maxs = X.max(0)
    mins = X.min(0)
    X = liner_normalization(X, maxs, mins)
    classifier = training(X, y)
    save_model(classifier)
    # 保存最大值与最小值数组到文件中
    np.savetxt('maxs', maxs)
    np.savetxt('mins', mins)
