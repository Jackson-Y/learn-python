#-*- coding: utf-8 -*-
""" 线上模型应用：
    1、加载模型及参数；
    2、预测xml中每一行是否为文章标题Title """
import os
from data_processing import read_xml, dataframe_to_csv
from data_processing import model_config, Keywords
from data_processing import data_parse, dict_to_dataframe
from model import load_model, predict


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

    return clf_dict


def recognition(predict_xml_file):
    """ 预测标题，作者，关键词，... """
    clf_dict = load_params()
    txt = read_xml(predict_xml_file)
    data, _, _ = data_parse(txt)
    dataframe = dict_to_dataframe(data)
    dataframe_to_csv(dataframe, 'debug.csv')

    i = 0
    results_file = open('result.txt', 'a+', encoding='utf-8')
    results_file.write(predict_xml_file + '\n')
    # 开始逐行识别文本
    for index in dataframe.index:
        i += 1
        text = dataframe['ztext'][i]
        # pageid = dataframe.loc[index].values[[Features['page'], ]]
        for model, configs in model_config.items():
            test_x = dataframe.loc[index].values[[configs['features']]]
            predict_y = predict(clf_dict[model], [test_x, ])
            if predict_y != 0:
                # 摘要修正
                if predict_y == 7:
                    if text.lower().strip(' \r\n').split(' ')[0] in Keywords or \
                            text.lower().strip(' \r\n').split(':')[0] in Keywords:
                        predict_y = [5]
                elif predict_y in [2, 3, 8]:
                    lower_char = text.lower().strip(' \r\n')
                    if lower_char[-2].isalpha() and not lower_char[-1].isalpha():
                        predict_y = [0]
                        continue

                print(predict_y, LABEL_INFO[predict_y[0]],
                      '-----> ', text.strip(' \r\n'))
                results_file.write('[' + str(predict_y[0]) + ']' +
                                   LABEL_INFO[predict_y[0]] +
                                   '-----> ' + text.strip(' \r\n') + '\n')
                break
    results_file.close()


def application(input_dir):
    """ 遍历目录，并获取文件的路径、文件名、扩展名 """
    if os.path.isfile(input_dir):
        print(input_dir)
        _, extname = os.path.splitext(input_dir)
        if extname != '.xml':
            print("It is NOT a xml file!")
            return
        recognition(input_dir)
        return

    for root, dirs, files in os.walk(input_dir):
        for file in files:
            _, extname = os.path.splitext(file)
            print("------------------------------------------------------------")
            print(os.path.join(root, file))
            file = os.path.join(root, file)
            if extname != '.xml':
                continue
            recognition(file)


if __name__ == '__main__':
    # application('./test/Quantifying-the-resilience-of-machine-learning-clas_2018_Expert-Systems-with.xml')
    # application('./test/Using-machine-learning-to-detect-and-localize-_2018_Engineering-Applications.xml')
    # application('G:/workspace/code/python/data/test_cnki/Optimizedevacuat_省略_ncrowdsimulation_Sai.xml')
    # application('G:/workspace/code/python/data/test_cnki/')
    # application('../learnpython/cnki/test/')
    application('./test/')
