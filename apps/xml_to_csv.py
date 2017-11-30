# -*- coding:utf-8 -*-
""" https://docs.python.org/3/library/xml.etree.elementtree.html """
import os
import re
import xml.etree.ElementTree as ET
import pandas as pd
from collections import Counter

def read_xml(xml_file='x.xml'):
    """ 读取xml文件，替换其中的非法字符 """
    # f = open(xml_file, mode='r', encoding='utf-8')
    # txt = f.read()
    # f.close()
    # 替换字符串中的非法字符
    # txt = re.sub(u"[\x00-\x08\x0b-\x0c\x0e-\x1f]+", u" ", txt)
    with open(xml_file, mode='r', encoding='utf-8') as f:
        txt = re.sub(u"[\x00-\x08\x0b-\x0c\x0e-\x1f]+", u" ", f.read())
    return txt

def data_parse(txt):
    """ 解析由pdf转化成的xml信息，提取并结构化数据，包括：
        dx: textbox 距离页面顶端的距离
        dy: textbox 缩进
        w: textbox 宽度
        h: textbox 高度
        size: text 字体大小
        r: text 当前字体大小相对于正文字体大小的比值
        ztext: textline 文本内容
        zlabel: textline 人工标记的标签信息[1:文章标题, 2:一级标题, 3:二级标题, 4:作者, 5:关键词, 6:参考文献]
        page: 页码标准化到[0,1]区间, (pageid - min_pageid)/(max_pageid - min_pageid)
    """
    pageid = 0
    lineno = 0
    data = {}
    size_counter = Counter()
    root = ET.fromstring(txt)
    # pages = root.findall('.//page[@id="1"]')
    pages = root.findall('.//page')
    total_page = float(len(pages))
    for page in pages:
        pageid = int(page.attrib['id'])
        y0, x0, yt0, xt0 = page.attrib['bbox'].split(',')
        for textbox in page.findall("./textbox"):
            # print(textbox.tag, textbox.attrib)
            y1, x1, yt1, xt1 = textbox.attrib['bbox'].split(',')
            box_dx = float(x1) - float(x0)
            box_dy = float(y1) - float(y0)
            box_w = float(yt1) - float(y1)
            box_h = float(xt1) - float(x1)
            for child in textbox.findall("./textline"):
                # print(child.tag, child.attrib)
                # Get 'label' --> Y.
                if 'label' in child.attrib:
                    zlabel = int(child.attrib['label'])
                else:
                    zlabel = 0

                lineno += 1
                text = ''
                size = 0.0
                font = 'KHJHPP+Gulliver'
                data.setdefault(lineno, {})
                for content in child.findall("./text"):
                    # print(content.text, end='')
                    if content.text is None:
                        continue
                    text += content.text

                    if not 'size' in content.attrib or not 'font' in content.attrib:
                        continue

                    size_counter.update(content.attrib['size'].split(' '))
                    if size < float(content.attrib['size']):
                        size = float(content.attrib['size'])
                        font = content.attrib['font']

                data[lineno]['zlabel'] = zlabel
                data[lineno]['ztext'] = text
                # data[lineno]['font'] = font
                data[lineno]['r'] = size
                data[lineno]['size'] = size
                data[lineno]['page'] = (pageid - 1) / (total_page -1)
                data[lineno]['dx'] = box_dx
                data[lineno]['dy'] = box_dy
                data[lineno]['w'] = '%.2f' % box_w
                data[lineno]['h'] = '%.2f' % box_h
    print("Font size used mostly: ", size_counter.most_common(3)[0])
    most_used_font_size = float(size_counter.most_common(3)[0][0])
    if size_counter.most_common(3)[0][0] == '0.000':
        most_used_font_size = size_counter.most_common(3)[1][0]
    for key, value in data.items():
        value['r'] = '%.2f' % (value['r'] / most_used_font_size)
    return data

def dict_to_dataframe(data):
    """ 把字典dict里的数据data，转化为dataframe，并将dataframe转置，
        以便进行机器学习。"""
    dataframe = pd.DataFrame(data).T
    # print(dataframe.head())
    return dataframe

def dataframe_to_csv(dataframe, csv_file='x.csv'):
    """ 保存解析后的DataFrame数据到csv文件中 """
    dataframe.to_csv(csv_file, encoding='utf-8')

def func(frames, file, sortname):
    txt = read_xml(file)
    data = data_parse(txt)
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

if __name__ == '__main__':
    frames = []
    travel_dir('./train', frames)
    df = pd.concat(frames)
    dataframe_to_csv(df, 'train.csv')
    # TEXT = read_xml('x.xml')
    # DATA = data_parse(TEXT)
    # df = dict_to_dataframe(DATA)
    # dataframe_to_csv(df, 'x.csv')
