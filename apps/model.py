# -*- coding: utf-8-*-
""" 训练模型 """
import numpy as np
import pandas as pd
from sklearn.naive_bayes import GaussianNB, MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn import svm
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.externals import joblib
from data_processing import read_csv, data_encode, liner_normalization, model_config, label_select
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score


def training(x_train, y_train):
    """ 选择算法并训练生成分类模型 """
    # clf = svm.SVC(class_weight='balanced').fit(x_train, y_train)
    # clf = MultinomialNB().fit(x_train, y_train)
    # clf = LogisticRegression().fit(x_train, y_train)
    # clf = MLPClassifier(solver='lbfgs', alpha=0.0001, hidden_layer_sizes=(10,), random_state=1).fit(x_train, y_train)
    clf = GradientBoostingClassifier(n_estimators=100).fit(x_train, y_train)
    # clf = RandomForestClassifier(class_weight='balanced', random_state=7, max_depth=10).fit(x_train, y_train)
    # clf = DecisionTreeClassifier().fit(x_train, y_train)
    return clf


# def xgboost_model(x_train, y_train):
#     from sklearn.model_selection import KFold
#     from sklean.metrics import confusion_matrix
#     import xgboost as xgb
#     import numpy as np
#     rng = np.random.RandomState(31337)
#     dtrain = xgb.DMatrix(x_train, label=y_train)
#     kf = KFold(n_splits=2, shuffle=True, random_state=rng)
#     xgb_model = xgb.XGBClassifier()
#     for train_index, test_index in kf.split(x_train):
#         xgb_model.fit(x_train[train_index], y_train[train_index])
#         predictions = xgb_model.predict(x_train[test_index])
#         actuals = y_train[test_index]
#         print(confusion_matrix(actuals, predictions))


def save_model(classifier, save_path="model/Title_keyword_author.model"):
    """ 保存模型 """
    joblib.dump(classifier, save_path)


def load_model(model_file_path="model/Title_keyword_author.model"):
    """ 加载模型 """
    clf = joblib.load(model_file_path)
    return clf


def predict(clf, x):
    """ 预测 """
    prediction = clf.predict(x)
    return prediction


def accuracy(y_true, y_pred):
    """ 准确率 """
    print('accuracy: ', accuracy_score(y_true, y_pred))


def precision(y_true, y_pred):
    """ 精确率(查准率) """
    # print('宏平均（Macro-averaging），是先对每一个类统计指标值，然后在对所有类求算术平均值。 ')
    # print('微平均（Micro-averaging），是对数据集中的每一个实例不分类别进行统计建立全局混淆矩阵，然后计算相应指标。')
    # print('micro precision: ', precision_score(y_true, y_pred, average='micro'))
    print('macro precision: ', precision_score(
        y_true, y_pred, average='macro'))


def recall(y_true, y_pred):
    """ 召回率(查全率) """
    # print('micro recall: ', recall_score(y_true, y_pred, average='micro'))
    print('macro recall: ', recall_score(y_true, y_pred, average='macro'))


def f1(y_true, y_pred):
    """ f1值（2*P*R/(P+R)） """
    print('f1-scroe: ', f1_score(y_true, y_pred, average='macro'))


if __name__ == '__main__':
    df = read_csv('data/data.csv')
    print('\nTotal Samples: %d\n' % df.shape[0])

    for model, configs in model_config.items():
        X, y = data_encode(df, configs['features_name'])
        y = label_select(y, configs['targets'])
        # print(X, y)
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2)
        model = training(X_train, y_train)
        y_pred = model.predict(X_test)
        print(classification_report(y_test, y_pred, target_names=None))
        save_model(model, configs['model_file'])
