# -*- coding: utf-8-*-
""" 训练模型 """
import os
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
from sklearn.model_selection import GridSearchCV
import matplotlib.pylab as plt
import pydotplus
from IPython.display import Image
from sklearn.tree import export_graphviz

# 设置环境Graphviz的变量
os.environ["PATH"] += os.pathsep + 'G:/program_files/graphviz/bin'


def training(x_features, y_labels):
    """ 选择算法并训练生成分类模型 """
    # clf = svm.SVC(class_weight='balanced')
    # clf = MultinomialNB()
    # clf = LogisticRegression()
    # clf = DecisionTreeClassifier()
    # clf = MLPClassifier(
    #     solver='lbfgs',
    #     alpha=0.0001,
    #     hidden_layer_sizes=(10,),
    #     random_state=1)
    # clf = GradientBoostingClassifier(
    #     learning_rate=0.1,
    #     max_depth=8,
    #     n_estimators=70,
    #     random_state=10)
    clf = RandomForestClassifier(
        class_weight='balanced',
        n_estimators=100,
        random_state=7,
        max_depth=10,
        n_jobs=4)
    clf.fit(x_features, y_labels)
    return clf


def save_model(classifier, save_path="model/Title_keyword_author.model"):
    """ 保存模型 """
    joblib.dump(classifier, save_path)


def load_model(model_file_path="model/Title_keyword_author.model"):
    """ 加载模型 """
    clf = joblib.load(model_file_path)
    return clf


def predict(clf, x_features):
    """ 预测 """
    prediction = clf.predict(x_features)
    return prediction


def accuracy(y_true, y_predict):
    """ 准确率 """
    print('accuracy: ', accuracy_score(y_true, y_predict))


# print('宏平均（Macro-averaging），是先对每一个类统计指标值，然后在对所有类求算术平均值。 ')
# print('微平均（Micro-averaging），是对数据集中的每一个实例不分类别进行统计建立全局混淆矩阵，然后计算相应指标。')
def precision(y_true, y_predict):
    """ 精确率(查准率) """
    print('macro precision: ', precision_score(
        y_true, y_predict, average='macro'))


def recall(y_true, y_predict):
    """ 召回率(查全率) """
    print('macro recall: ', recall_score(y_true, y_predict, average='macro'))


def f1_measure(y_true, y_predict):
    """ f1值（2*P*R/(P+R)） """
    print('f1-scroe: ', f1_score(y_true, y_predict, average='macro'))


if __name__ == '__main__':
    DF = read_csv('data/data.csv')
    print('\nTotal Samples: %d\n' % DF.shape[0])

    for model, configs in model_config.items():
        X, y = data_encode(DF, configs['features_name'])
        y = label_select(y, configs['targets'])
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2)
        # model = training(X_train, y_train)
        model = training(X, y)
        y_pred = model.predict(X_test)
        print('Features: ', configs['features_name'])
        print('Importances: ', model.feature_importances_)
        print(classification_report(y_test, y_pred, target_names=None))
        save_model(model, configs['model_file'])

        # GridSearch 
        # 网格搜索 --> 参数调优
        # params = {'n_estimators': range(50, 101, 10)}
        # gs = GridSearchCV(
        #     estimator=RandomForestClassifier(
        #         max_depth=10,random_state=10,class_weight='balanced'),
        #     param_grid=params,
        #     scoring=['precision_macro', 'recall_macro'],
        #     n_jobs=4,
        #     # iid=False,
        #     cv=5)
        # gs.fit(X, y)
        # print(gs.cv_results_, '\n')
        # print(gs.best_params_, ' ', gs.best_score_)

        # Features Weight Visualization 
        # 特征权重可视化
        y_importances = model.feature_importances_
        x_importances = configs['features_name']
        y_pos = np.arange(len(x_importances))
        plt.barh(y_pos, y_importances, align='center', alpha=0.4)
        plt.yticks(y_pos, x_importances)
        plt.xlabel('Features')
        plt.xlim(0, 1)
        plt.title('Features Importances')
        plt.show()

        # Tree of RandomForest Visualization 
        # 随机森林中的决策树可视化
        # Estimators = model.estimators_
        # for index, estimators in enumerate(Estimators):
        #     filename = 'Tree_' + str(index) + '.pdf'
        #     dot_data = export_graphviz(estimators, out_file=None,
        #             feature_names=list(configs['features_name']),
        #             class_names=list(configs['targets_name']),
        #             filled=True, rounded=True,
        #             special_characters=True)

        #     graph = pydotplus.graph_from_dot_data(dot_data)
        #     # 保存为pdf文件.
        #     graph.write_pdf(filename)
        #     # 使用 IPython.display 在 Jupyter Notebook 中画图.
        #     Image(graph.create_png())
