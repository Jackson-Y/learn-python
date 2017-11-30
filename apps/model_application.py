#-*- coding: utf-8 -*-
""" 线上模型应用：
    1、加载模型及参数；
    2、预测xml中每一行是否为文章标题Title """

from xml_to_csv import read_xml, data_parse, dict_to_dataframe
from data_processing import data_encode, liner_normalization
from model import load_model, predict
import numpy as np
import os

def load_params():
    """ 加载模型及参数 """
    clf = load_model()
    maxs = np.loadtxt('maxs')
    mins = np.loadtxt('mins')
    return clf, maxs, mins

def recognition(predict_xml_file):
    """ 预测标题... """
    clf, maxs, mins = load_params()
    txt = read_xml(predict_xml_file)
    data = data_parse(txt)
    df = dict_to_dataframe(data)
    test_x, text_y = data_encode(df)
    test_x = np.array(test_x, dtype='float32')
    test_x = liner_normalization(test_x, maxs, mins)
    i = 0
    for row in test_x:
        i += 1
        predict_y = predict(clf, [row,])
        if predict_y == 1:
            print(row)
            print(df['ztext'][i], end=' ----> ')
            print(predict_y)

def application(input_dir):
    """ 遍历目录，并获取文件的路径、文件名、扩展名 """
    if os.path.isfile(input_dir):
        print(input_dir)
        shortname, extname = os.path.splitext(input_dir)
        if extname != '.xml':
            print("It is NOT a xml file! Exit!")
            return
        recognition(input_dir)
        return

    for root, dirs, files in os.walk(input_dir):
        for file in files:
            shortname, extname = os.path.splitext(file)
            print("------------------------------------------------------------")
            print(os.path.join(root, file))
            file = os.path.join(root, file)
            if extname != '.xml':
                continue
            recognition(file)

if __name__ == '__main__':
    application('../sciencedirect/test')
