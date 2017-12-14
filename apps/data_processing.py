# -*- coding:utf-8 -*-
""" https://docs.python.org/3/library/xml.etree.elementtree.html """
import os
import re
import xml.etree.ElementTree as ET
from collections import Counter
import pandas as pd
import numpy as np

Features = {
    'box_x': 0,
    'box_xt': 1,
    'box_y': 2,
    'box_yt': 3,
    'font': 4,
    'indent': 5,
    'line_h': 6,
    'line_space_bottom': 7,
    'line_space_top': 8,
    'line_w': 9,
    'line_x': 10,
    'line_xt': 11,
    'line_y': 12,
    'line_yt': 13,
    'page': 14,
    'r_line_key': 15,
    'r_line_ref': 16,
    'r_line_x': 17,
    'r_line_xt': 18,
    'r_line_y': 19,
    'r_line_yt': 20,
    'r_page': 21,
    'r_size': 22,
    'size': 23,
    'word_count': 24,
    'word_density': 25,
    'zlabel': 26,
    'ztext': 27
}

model_config = {
    'model_1': {
        'name': 'Title_keyword_author',
        'targets_name': ['标题', '作者', '关键词'],
        'targets': [1, 4, 5],
        'features_name': ['r_line_x', 'r_line_y', 'r_line_xt', 'r_line_yt',
                          'page', 'r_page', 'size', 'r_size'],
        'features': [Features['r_line_x'], Features['r_line_y'], Features['r_line_xt'],
                     Features['r_line_yt'], Features['page'], Features['r_page'],
                     Features['size'], Features['r_size']],
        'data_file': 'data/data.csv',
        'model_file': 'model/Title_keyword_author.model'
    },
    'model_2': {
        'name': 'Chapter_titles',
        'targets_name': ['1级标题', '2级标题', '3级标题'],
        'targets': [2, 3, 8],
        'features_name': ['word_density', 'line_space_top', 'line_space_bottom',
                          'font', 'size', 'indent', 'word_count', 'line_w', 'line_h',
                          'r_line_x', 'r_line_y', 'r_line_xt', 'r_line_yt'],
        'features': [Features['word_density'], Features['line_space_top'],
                     Features['line_space_bottom'], Features['font'], Features['size'],
                     Features['indent'], Features['word_count'], Features['line_w'],
                     Features['line_h'], Features['r_line_x'], Features['r_line_y'],
                     Features['r_line_xt'], Features['r_line_yt']],
        'data_file': 'data/data.csv',
        'model_file': 'model/Chapter_titles.model'
    },
    'model_3': {
        'name': 'References',
        'targets_name': ['参考文献', ],
        'targets': [6, ],
        'features_name': ['r_page', 'line_w', 'box_x', 'box_xt', 'r_size',
                          'r_line_ref','word_density', 'indent', 'word_count', 'line_h'],
        'features': [Features['r_page'], Features['line_w'], Features['box_x'],
                     Features['box_xt'], Features['r_size'], Features['r_line_ref'],
                     Features['word_density'], Features['indent'],
                     Features['word_count'], Features['line_h']],
        'data_file': 'data/data.csv',
        'model_file': 'model/References.model'
    },
    # 'model_4': {
    #     'name': 'Abstract',
    #     'targets_name': ['摘要',],
    #     'targets': [7,],
    #     'features_name': ['word_density', 'line_space_top', 'line_space_bottom', \
    #                  'font', 'size', 'indent', 'word_count', 'line_w', 'line_h', \
    #                  'r_line_x', 'r_line_y', 'r_line_xt', 'r_line_yt'],
    #     'features': [24, 9, 8, 5, 22, 6, 23, 10, 7, 16, 18, 17, 19],
    #     'data_file': 'data/data.csv',
    #     'model_file': 'model/Abstract.model'
    # }
}

Keywords = ['keywords:', 'keyword:', 'key words:',
            'keywords', 'key words', 'keyword']
References = ['references', 'reference', 'acknowledgements']


def read_xml(xml_file='x.xml'):
    """ 读取xml文件，替换其中的非法字符 """
    with open(xml_file, mode='r', encoding='utf-8') as pfile:
        txt = re.sub(u"[\x00-\x08\x0b-\x0c\x0e-\x1f]+", u" ", pfile.read())
    return txt


def data_parse(txt):
    """ 解析由pdf转化成的xml信息，提取并结构化数据，包括：
        box_x: textbox 左下角横坐标
        box_y: textbox 左下角纵坐标
        box_xt: textbox 右上角横坐标
        box_yt: textbox 右上角总坐标
        line_x: 本行左下角横坐标
        line_y: 本行左下角纵坐标
        line_xt: 本行右上角横坐标
        line_yt: 本行右上角纵坐标
        r_line_x: 本行左下角相对页面右上横坐标
        r_line_y: 本行左下角相对页面右上纵坐标
        r_line_xt: 本行右上角相对页面右上横坐标
        r_line_yt: 本行右上角相对页面右上纵坐标
        line_space_top: 行间距（行前）
        line_space_bottom: 行间距（行后）
        indent: 缩进（line相对于textbox的缩进）
        word_count: 一行内的字符数
        word_density: 本行的字密度（行宽除以字数）
        size: text 字体大小
        font： 字体（1粗体、2斜体、0标准）
        r_size: text 当前字体大小相对于正文字体大小的比值
        ztext: textline 文本内容
        zlabel: textline 人工标记的标签信息[1:文章标题, 2:一级标题, 3:二级标题, 4:作者, 5:关键词, 6:参考文献, 7:摘要]
        page: 页码
        r_page: 相对页码，页码标准化到[0,1]区间, (pageid - min_pageid)/(max_pageid - min_pageid)
    """
    data = {}
    pageid = 0
    lineno = 0
    keyword_lineno = 0
    reference_lineno = 0
    reference_enable = True
    size_counter = Counter()
    root = ET.fromstring(txt)
    # pages = root.findall('.//page[@id="1"]')
    pages = root.findall('.//page')
    total_page = float(len(pages))
    for page in pages:
        pageid = int(page.attrib['id'])
        x0, y0, xt0, yt0 = page.attrib['bbox'].split(',')
        x0, y0, xt0, yt0 = float(x0), float(y0), float(xt0), float(yt0)
        for textbox in page.findall(".//textbox"):
            # print(textbox.tag, textbox.attrib)
            textbox_id = int(textbox.attrib['id'])
            x1, y1, xt1, yt1 = textbox.attrib['bbox'].split(',')
            x1, y1, xt1, yt1 = float(x1), float(y1), float(xt1), float(yt1)
            for textline in textbox.findall(".//textline"):
                # print(child.tag, child.attrib)
                if not 'bbox' in textline.attrib:
                    continue
                x2, y2, xt2, yt2 = textline.attrib['bbox'].split(',')
                x2, y2, xt2, yt2 = float(x2), float(y2), float(xt2), float(yt2)
                line_w = xt2 - x2
                line_h = yt2 - y2
                # Get 'label' --> Y.
                if 'label' in textline.attrib:
                    zlabel = int(textline.attrib['label'])
                else:
                    zlabel = 0

                lineno += 1
                text = ''
                size = 0.0
                font = 'KHJHPP+Gulliver'
                charno = 0
                data.setdefault(lineno, {})
                for content in textline.findall(".//text"):
                    # print(content.text, end='')
                    if content.text is None:
                        continue
                    text += content.text
                    charno += 1

                    if not 'size' in content.attrib or not 'font' in content.attrib:
                        continue

                    size_counter.update(content.attrib['size'].split(' '))
                    if size < float(content.attrib['size']):
                        size = float(content.attrib['size'])
                        font = content.attrib['font']

                data[lineno]['zlabel'] = zlabel
                data[lineno]['ztext'] = text
                data[lineno]['r_page'] = pageid
                data[lineno]['page'] = pageid
                data[lineno]['r_size'] = size
                data[lineno]['size'] = size
                data[lineno]['box_x'] = x1
                data[lineno]['box_y'] = y1
                data[lineno]['box_xt'] = xt1
                data[lineno]['box_yt'] = yt1
                data[lineno]['line_x'] = x2
                data[lineno]['line_y'] = y2
                data[lineno]['line_xt'] = xt2
                data[lineno]['line_yt'] = yt2
                data[lineno]['line_w'] = float('%.2f' % line_w)  # 行宽
                data[lineno]['line_h'] = float('%.2f' % line_h)  # 行高
                data[lineno]['word_count'] = charno
                data[lineno]['word_density'] = float(
                    '%.2f' % (line_w / charno))  # 本行的字密度(替代表示字间距)
                data[lineno]['line_space_top'] = 0.0
                data[lineno]['line_space_bottom'] = 0.0

                if total_page == 1:
                    data[lineno]['r_page'] = 0.0
                else:
                    data[lineno]['r_page'] = float(
                        '%.2f' % ((pageid - 1) / (total_page - 1)))

                # 字体是否为斜体、粗体
                if font.lower().find('italic') != -1 \
                    or font.lower().find('-i') != -1 \
                    or font.lower().find('it') != -1 \
                    or font.lower().find('-r') != -1 \
                        or font.lower().find('.i') != -1:
                    data[lineno]['font'] = 2
                elif font.lower().find('bold') != -1 \
                    or font.lower().find('.b') != -1 \
                    or font.lower().find('-b') != -1 \
                        or font.lower().find('bl') != -1:
                    data[lineno]['font'] = 1
                else:
                    data[lineno]['font'] = 0

                # 行间距
                if lineno > 1 and textbox_id > 0:
                    data[lineno]['line_space_top'] = float(
                        '%.2f' % (data[lineno - 1]['line_y'] - yt2))
                    data[lineno - 1]['line_space_bottom'] = data[lineno]['line_space_top']
                elif lineno == 1:
                    data[lineno]['line_space_top'] = 0.0
                else:
                    # print(textbox_id == 0)
                    data[lineno]['line_space_top'] = 0.0
                    data[lineno - 1]['line_space_bottom'] = 0.0

                # 缩进
                data[lineno]['indent'] = float('%.2f' % (x2 - x1))

                # 行在本页中的位置比例
                data[lineno]['r_line_x'] = float('%.2f' % (x2 / xt0))
                data[lineno]['r_line_y'] = float('%.2f' % (y2 / yt0))
                data[lineno]['r_line_xt'] = float('%.2f' % (xt2 / xt0))
                data[lineno]['r_line_yt'] = float('%.2f' % (yt2 / yt0))

                # 相对于References的位置
                data[lineno]['r_line_ref'] = lineno
                if reference_enable and text.lower().strip(' \r\n') in References:
                    reference_lineno = lineno
                    reference_enable = False

                # 相对于Keywords的位置
                data[lineno]['r_line_key'] = lineno
                if text.lower().strip().split(' ')[0] in Keywords or \
                        text.lower().strip().split(':')[0] in Keywords:
                    keyword_lineno = lineno

    print("Font size used mostly: ", size_counter.most_common(1))
    most_font_size = float(size_counter.most_common(1)[0][0])
    for lineno, params in data.items():
        params['r_size'] = float('%.2f' % (params['r_size'] / most_font_size))
        params['r_line_ref'] -= reference_lineno
        params['r_line_key'] = keyword_lineno - params['r_line_key']
    return data, most_font_size, total_page


def dict_to_dataframe(data):
    """ 把字典dict里的数据data，转化为dataframe，并将dataframe转置，
        以便进行机器学习。"""
    dataframe = pd.DataFrame(data).T
    return dataframe


def dataframe_to_csv(dataframe, csv_file='x.csv'):
    """ 保存解析后的DataFrame数据到csv文件中 """
    dataframe.to_csv(csv_file, encoding='utf-8')


def func(frames, file, sortname):
    txt = read_xml(file)
    data, most_font_size, total_page = data_parse(txt)
    df = dict_to_dataframe(data)
    frames.append(df)


def travel_dir(path, frames, callback=func):
    """ 遍历目录，并获取文件的路径、文件名、扩展名 """
    for root, dirs, files in os.walk(path):
        for file in files:
            shortname, extname = os.path.splitext(file)
            print(os.path.join(root, file))
            # print(os.path.splitext(file))
            file = os.path.join(root, file)
            if extname != '.xml':
                continue
            func(frames, file, shortname)
        # for directory in dirs:
        #     travel_dir(directory)


def read_csv(csv_file, encoding='utf-8'):
    df = pd.read_csv(csv_file, encoding=encoding)
    return df


def data_encode(dataframe, feature_list=None):
    """ 将标签列、字符串列进行数字化编码 """
    # class_le = LabelEncoder()
    # y = class_le.fit_transform(df['zlabel'].values)
    y = dataframe['zlabel'].values
    # X = df[['dx', 'dy', 'font', 'h', 'page', 'size', 'w']].values
    # X = df[['dx', 'dy', 'h', 'page', 'size', 'w']].values
    # X = df[['dx', 'dy', 'h', 'page', 'r', 'size', 'w']].values
    # X = df[['dx', 'dy', 'h', 'page', 'r', 'w']].values
    # X = dataframe[['box_x', 'box_y', 'box_yt', 'page', 'r_size', 'size']].values
    # X = df[['box_x', 'box_y', 'box_h', 'page', 'size', 'line_x', 'line_y', 'line_h', 'word_density']].values
    X = dataframe[feature_list].values
    # X = np.array(X, dtype='float32')
    return X, y


def label_select(y_label, targets):
    """ 筛选标签 """
    y = [x if x in targets else 0 for x in y_label]
    return np.array(y)


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
            X[i][j] = (X[i][j] - column_mins[j]) / \
                (column_maxs[j] - column_mins[j])
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
            lg_X[i][j] = (lg_X[i][j]) / (lg_column_maxs[j])
    return lg_X


if __name__ == '__main__':
    frames = []
    travel_dir('./train', frames)
    df = pd.concat(frames)
    dataframe_to_csv(df, 'data/data.csv')
    # dataframe_to_csv(df, 'train_title_author_keyword.csv')
    # dataframe_to_csv(df, 'train_primaryTitle.csv')
    # dataframe_to_csv(df, 'train_references.csv')
