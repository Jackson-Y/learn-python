#-*- coding: utf-8 -*-
""" 线上模型应用：
    1、加载模型及参数；
    2、预测xml中每一行是否为文章标题Title """

from xml_to_csv import read_xml, data_parse, dict_to_dataframe
from data_processing import data_encode, liner_normalization
from model import load_model, predict
from math import fabs
import numpy as np
import os

LABEL_INFO = {
    1: '标题',
    2: '一级标题',
    3: '二级标题',
    4: '作者',
    5: '关键词',
    6: '参考文献',
    7: '摘要',
    0: '其他'
}

def load_params():
    """ 加载模型及参数 """
    clf = load_model()
    maxs = np.loadtxt('maxs')
    mins = np.loadtxt('mins')
    return clf, maxs, mins

keywords = ['keywords:', 'keyword:', 'keywords', 'keyword']
def recognition(predict_xml_file):
    """ 预测标题，作者，关键词，... """
    clf, maxs, mins = load_params()
    txt = read_xml(predict_xml_file)
    data = data_parse(txt)
    df = dict_to_dataframe(data)
    test_x, text_y = data_encode(df)
    test_x = np.array(test_x, dtype='float32')
    test_x = liner_normalization(test_x, maxs, mins)

    i = 0
    keyword_location = []
    had_keyword = False
    start_rule_keyword = False
    for row in test_x:
        i += 1
        # if i < 10:
        #     print(row)
        text = df['ztext'][i]
        predict_y = predict(clf, [row,])
        if predict_y != 0:
            # print(row)
            print(predict_y, LABEL_INFO[predict_y[0]], '-----> ', text.strip(' \r\n'))
            # print(predict_y)
            if predict_y == 5:
                had_keyword = True
                continue

        # For Keyword Recognition
        if row[3] < 0.2: # 第一页和第二页
            if not had_keyword:
                if text.lower().strip() in keywords:
                    keyword_location = row[:4]
                    start_rule_keyword = True
                    print('[r5] 关键词 -----> ', text.strip(' \r\n'))
                    continue
            if start_rule_keyword and fabs(keyword_location[0] - row[0]) < 1e-6 and fabs(keyword_location[1] - row[1]) < 1e-6:
                print('[r5] 关键词 -----> ', text.strip(' \r\n'))
                continue

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
    application('../sciencedirect/test/')
