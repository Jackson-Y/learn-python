# -*- coding:utf-8 -*-
""" https://docs.python.org/3/library/xml.etree.elementtree.html """
import xml.etree.ElementTree as ET
import re
import pandas as pd

f = open('x.xml', mode='r', encoding='utf-8')
txt = f.read()
f.close()

# 替换字符串中的非法字符
txt = re.sub(u"[\x00-\x08\x0b-\x0c\x0e-\x1f]+", u" ", txt)

# tree = ET.parse('x.xml')
# root = tree.getroot()
root = ET.fromstring(txt)
# print(root.tag)
# print(root.attrib)

lineno = 0
data = {}
# print(root.findall(".//page[@id='1']/textbox/textline/text")[0].text)
for page in root.findall(".//page"):
    pageid = int(page.attrib['id'])
    y0, x0, yt0, xt0 = page.attrib['bbox'].split(',')
    for textbox in page.findall("./textbox"):
        print('-----------------------------------------------')
        print(textbox.tag, textbox.attrib)
        y1, x1, yt1, xt1 = textbox.attrib['bbox'].split(',')
        box_dx = float(x1) - float(x0)
        box_dy = float(y1) - float(y0)
        box_w = float(yt1) - float(y1)
        box_h = float(xt1) - float(x1)
        for child in textbox.findall("./textline"):
            print(child.tag, child.attrib)
            # Get 'label' --> Y.
            if 'label' in child.attrib:
                zlabel = int(child.attrib['label'])
            else:
                zlabel = 0

            lineno += 1
            data.setdefault(lineno, {})
            text = ''
            font = 'KHJHPP+Gulliver'
            size = 0.0
            for content in child.findall("./text"):
                # print(content.text, end='')
                if content.text is None:
                    continue
                if not 'size' in content.attrib or not 'font' in content.attrib:
                    continue

                text += content.text
                if size < float(content.attrib['size']):
                    size = float(content.attrib['size'])
                    font = content.attrib['font']

            data[lineno]['zlabel'] = zlabel
            data[lineno]['ztext'] = text
            data[lineno]['font'] = font
            data[lineno]['size'] = size
            data[lineno]['page'] = pageid
            data[lineno]['dx'] = box_dx
            data[lineno]['dy'] = box_dy
            data[lineno]['w'] = '%.2f' % box_w
            data[lineno]['h'] = '%.2f' % box_h

df = pd.DataFrame(data).T
print(df.head())
df.to_csv('x.csv')
