# -*- coding:utf-8 -*-
""" 数据预处理：
    1、离散数据编码
    2、标签值获取
    3、特征数据归一化 """
import pandas as pd
from sklearn.preprocessing import LabelEncoder

def read_csv(csv_file, encoding='utf-8'):
    df = pd.read_csv(csv_file, encoding=encoding)
    return df

def data_encode(df):
    """ 将标签列、字符串列进行数字化编码 """
    class_le = LabelEncoder()
    # y = class_le.fit_transform(df['zlabel'].values)
    y = df['zlabel'].values
    # X = df[['dx', 'dy', 'font', 'h', 'page', 'size', 'w']].values
    # X = df[['dx', 'dy', 'h', 'page', 'size', 'w']].values
    # X = df[['dx', 'dy', 'h', 'page', 'r', 'size', 'w']].values
    # X = df[['dx', 'dy', 'h', 'page', 'r', 'w']].values
    X = df[['dx', 'dy', 'h', 'page', 'r', 'size']].values
    # X[:, 2] = class_le.fit_transform(X[:, 2])
    # features_dict = {}
    # features = class_le.classes_
    # for i, val in enumerate(features):
    #     features_dict[i] = val
    # print(pd.DataFrame(X).head())
    # print(y)
    # print(X)
    # return X, y, features_dict
    return X, y

def standard_deviation_normalization(X, column_means, column_stds):
    """ 标准差归一化[-1, 1] """
    # print('means: ', column_means, '\nstds: ', column_stds)
    data_shape = X.shape
    data_rows = data_shape[0]
    data_cols = data_shape[1]

    for i in range(0, data_rows, 1):
        for j in range(0, data_cols, 1):
            X[i][j] = (X[i][j] - column_means[j]) / (column_stds[j])
    return X

def liner_normalization(X, column_maxs, column_mins):
    """ 线性归一化[0, 1]
    参数:
        X, 二维矩阵;
        column_maxs, 二维矩阵每列的最大值;
        column_mins, 二维矩阵每列的最小值;
    return：
        返回归一化后的 X;
    """
    data_shape = X.shape
    rows = data_shape[0]
    cols = data_shape[1]

    for i in range(0, rows, 1):
        for j in range(0, cols, 1):
            X[i][j] = (X[i][j] - column_mins[j]) / (column_maxs[j] - column_mins[j])
    return X

def nonliner_normalization(lg_X, lg_column_maxs):
    """ 非线性归一化[lg10(x)/max_log10(cols)]
    X = numpy.array(X)
    lg_X = numpy.log10(X)
    column_maxs = X.max(0)
    lg_column_maxs = numpy.log10(X.max(0))
    """
    data_shape = lg_X.shape
    rows = data_shape[0]
    cols = data_shape[1]

    for i in range(0, rows, 1):
        for j in range(0, cols, 1):
            lg_X[i][j] = (lg_X[i][j]) /(lg_column_maxs[j])
    return lg_X
