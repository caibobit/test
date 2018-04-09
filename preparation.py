#!usr/bin/python
# -*- coding: utf-8 -*-
import re
f = open('data_2015_1.txt','r')
fw = open('output.txt','w')
for line in f:
     tmp = line.strip()
     res = re.split(r'\t| ',tmp)
     res.pop(0)
     res.pop(-1)
     fw.write('%s' % '\t'.join(res)+'\n')
     
