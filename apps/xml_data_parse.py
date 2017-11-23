# -*- coding:utf-8 -*-
""" https://docs.python.org/3/library/xml.etree.elementtree.html """
import xml.etree.ElementTree as ET
import re

f = open('x.xml', mode='r', encoding='utf-8')
txt = f.read()
f.close()

# 替换字符串中的非法字符
txt = re.sub(u"[\x00-\x08\x0b-\x0c\x0e-\x1f]+", u"", txt)

# tree = ET.parse('x.xml')
root = ET.fromstring(txt)
# root = tree.getroot()
print(root.tag)
print(root.attrib)
# print(root.findtext())
# for child in root:
#     # print(child.tag, child.attrib)
#     print(child.findtext(".//page[@id='1']/textbox/textline/text"))

print(root.findall(".//page[@id='1']/textbox/textline/text")[1].text)