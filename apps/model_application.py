#-*- coding: utf-8 -*-
""" 线上模型应用：
    1、加载模型及参数；
    2、预测xml中每一行是否为文章标题Title """

from data_processing import read_xml, dataframe_to_csv
from data_processing import Features, model_config, Keywords, References
from data_processing import data_parse, data_encode, dict_to_dataframe
from model import load_model, predict
from math import fabs
import numpy as np
import os

LABEL_INFO = {
    1: '标题',
    2: '1级标题',
    3: '2级标题',
    4: '作者',
    5: '关键词',
    6: '参考文献',
    7: '摘要',
    8: '3级标题',
    0: '其他'
}


def load_params():
    """ 加载模型及参数 """
    clf_dict = {}
    for model, configs in model_config.items():
        clf = load_model(configs['model_file'])
        clf_dict[model] = clf
    # clf = load_model()
    # maxs = np.loadtxt('maxs')
    # mins = np.loadtxt('mins')
    # return clf, maxs, mins
    return clf_dict


def recognition(predict_xml_file):
    """ 预测标题，作者，关键词，... """
    # clf, maxs, mins = load_params()
    clf_dict = load_params()
    txt = read_xml(predict_xml_file)
    data, most_font_size, total_page = data_parse(txt)
    df = dict_to_dataframe(data)
    dataframe_to_csv(df, 'debug.csv')

    i = 0
    keyword_location = []
    had_keyword = False
    start_rule_keyword = False
    # 开始逐行识别文本
    for index in df.index:
        i += 1
        text = df['ztext'][i]
        pageid = df.loc[index].values[[Features['page'], ]]
        for model, configs in model_config.items():
            test_x = df.loc[index].values[[configs['features']]]
            predict_y = predict(clf_dict[model], [test_x, ])
            if predict_y != 0:
                print(predict_y, LABEL_INFO[predict_y[0]],
                      '-----> ', text.strip(' \r\n'))
                break

        # if fabs(df['size'] - most_font_size) < 1e-6:
        #     print(0, ' 正文 ', '-----> ', text.strip(' \r\n'))

        # i += 1
        # # if i < 10:
        # #     print(row)
        # text = df['ztext'][i]
        # predict_y = predict(clf, [row,])
        # if predict_y != 0:
        #     # print(row)
        #     print(predict_y, LABEL_INFO[predict_y[0]], '-----> ', text.strip(' \r\n'))
        #     # print(predict_y)
        #     if predict_y == 5:
        #         had_keyword = True
        #         # keyword_location = row[:4]
        #         keyword_location = [df['box_x'][i], df['box_y'][i], df['box_xt'][i]]
        #         start_rule_keyword = True
        #         continue

        # # For Keyword Recognition
        # if df['page'][i] < 3: # 第一页和第二页
        #     if not had_keyword:
        #         if text.lower().strip().split(' ')[0] in keywords or text.lower().strip().split(':')[0] in keywords:
        #             # keyword_location = row[:4]
        #             keyword_location = [df['box_x'][i], df['box_y'][i], df['box_xt'][i]]
        #             start_rule_keyword = True
        #             print('[r5] 关键词 -----> ', text.strip(' \r\n'))
        #             continue
        #     if start_rule_keyword and fabs(keyword_location[0] - df['box_x'][i]) < 1e-6 and fabs(keyword_location[1] - df['box_y'][i]) < 1e-6:
        #         print('[r5] 关键词 -----> ', text.strip(' \r\n'))
        #         continue


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
            print(
                "--------------------------------------------------------------------------")
            print(os.path.join(root, file))
            file = os.path.join(root, file)
            if extname != '.xml':
                continue
            recognition(file)


if __name__ == '__main__':
    application('../sciencedirect/test/')
    # application('../cnki/test/')
    # application('./test/train')
