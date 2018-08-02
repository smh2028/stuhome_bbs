# -*- coding: utf-8 -*-
'''
@author  : smh2208
@software: PyCharm
@file    : captcha_test.py
@time    : 2018/8/2 9:58
@desc    :
'''

import tesserocr
from PIL import Image

img = Image.open('ca1.png')
img = img.convert('L')
th = 127
table = []
for i in range(256):
    if i<th:
        table.append(0)
    else:
        table.append(1)
image = img.point(table,'1')
r = tesserocr.image_to_text(image)
print(r)