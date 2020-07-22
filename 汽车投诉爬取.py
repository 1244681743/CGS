#!/usr/bin/env python
# coding: utf-8

# In[1]:


from lxml import etree #y用来加载网页解析
import requests #用来网页请求
import time #计时
import pandas as pd
from tkinter import _flatten
import random
import math
import re


# In[2]:


url = 'http://tousu.315che.com/tousulist/serial/55467/'#网址
rq = requests.get(url)
rq.encoding = 'utf-8'
dom = etree.HTML(rq.text) 
#获取到每个页面下的品牌
name = dom.xpath('//*[@id="letterTabList"]/div/a/text()')
#获取到每个页面下的网址
url_all = dom.xpath('//*[@id="letterTabList"]/div/a/@href')
del name[url_all.index('javascript:;')]
url_all = [i for i in url_all if i != 'javascript:;']   #剔除'javascript:;'的错误网址


# In[3]:


url_all  #清洗后的品牌网址


# In[7]:


#获取每个品牌对应的举报url
report_all = []
bb = 1
for i in url_all:
    rqq1 = requests.get(i) #解析品牌网址
    html1 = etree.HTML(rqq1.content, etree.HTMLParser(encoding='utf-8'))
    ##获取到当前品牌的投诉页数
    yeshu_list = html1.xpath('//*[@class="pagination pdtb20"]/a[last()-1]/text()')
    #对投诉页数进行一个判断，if 为空，我们就pass，
    if ''.join(yeshu_list) == '':
        yeshu = 0
    else:
        yeshu = int(''.join(yeshu_list))
    for y in range(1,yeshu+1):
        print('正在获取第%d品牌的的第%d页'%(bb,y))
        url2 = 'http://tousu.315che.com/tousulist/serial/93/0/0/0/{}.htm'.format(y)#得到每个页面的网址
        rqq2 = requests.get(url2) #请求网址
        html2 = etree.HTML(rqq2.content, etree.HTMLParser(encoding='utf-8'))#解析网址
            #存放网址

        report_all.append(html2.xpath('//*[@class="tousu-filter-list"]/ul/li/a/@href'))
    bb=bb+1
    


# In[9]:


report_all = list(_flatten(report_all))
print(len(report_all))
report_all


# In[10]:


pd.Series(report_all).to_csv('./tousu_web.csv', encoding='GBK', header=None)


# In[ ]:


#读取数据
# report_all = pd.read_csv('./tousu_web.csv',encoding='gbk',header=None)
# report_all=list(report_all[1])


# In[11]:


brand = [] #品牌
Complaint_no = []  #投诉单号
Model = []      #车型
Complaint_time = []  #投诉时间
Appeal_question = []  #诉求问题
Complaint_details = []  #投诉明细
distributor = []   #经销商
Resolution_status = []   #  解决状态


# In[13]:


all_data = pd.DataFrame()
b = 1
for yy in report_all[:100]:   #分段爬取
    print('正在爬取第%d条数据...'%b)
    heads = {'User-Agent':"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36"}
    rqq_info = requests.get(yy,headers = heads)
    html_info = etree.HTML(rqq_info.content, etree.HTMLParser(encoding='utf-8'))
    try:
        #品牌
        brand = [i for i in html_info.xpath('//*[@class="container breadnav"]/a[3]/text()')]
        #车型
        Model = [i.split('：')[1] for i in html_info.xpath('/html/body/div[1]/div[2]/div[2]/div[1]/div[1]/div/div[3]/p[1]/text()')]
        #单号
        Complaint_no = [i.split('：')[1] for i in html_info.xpath('/html/body/div[1]/div[2]/div[2]/div[1]/div[1]/div/div[3]/p[2]/text()')]
        #诉求问题
        Appeal_question = [i.split('：')[1] for i in html_info.xpath('/html/body/div[1]/div[2]/div[2]/div[1]/div[1]/div/div[3]/p[3]/text()')]
        #投诉时间
        Complaint_time = [i.split('：')[1] for i in html_info.xpath('/html/body/div[1]/div[2]/div[2]/div[1]/div[1]/div/div[3]/p[4]/text()')]
        #经销商
        distributor = [i.split('：')[1] for i in html_info.xpath('/html/body/div[1]/div[2]/div[2]/div[1]/div[1]/div/div[3]/p[5]/text()')]
        #投诉明细
        Complaint_details =[i.text for i in html_info.xpath('//*[@class="describe"]/p')]
        #解决状态
        Resolution_status = [i.text for i in html_info.xpath('//*[@class="article-tag unsolved"]')]
    
        data = pd.DataFrame({
            '品牌': brand,
            '车型': Model,
            '单号':Complaint_no,
            '诉求问题': Appeal_question,
            '投诉时间': Complaint_time,
            '经销商': distributor,
            '投诉明细':Complaint_details,
            '解决状态': Resolution_status
        })
        all_data = pd.concat([all_data, data])
        b = b+1
        data.to_csv(r'C:\Users\12446\Desktop\tousu_data.csv',encoding='GBK',mode = 'a+',header = None)
        
    except:
        print('此页数据未爬取成功或者网页不存在，跳过')
        pass
print('***Good!*** 总共%d条数据，爬取完毕~'%all_data.shape[0])


# In[15]:


# rqq_info = requests.get(report_all[1])
# html_info = etree.HTML(rqq_info.content, etree.HTMLParser(encoding='utf-8'))
# brand = [i for i in html_info.xpath('//*[@class="container breadnav"]/a[3]/text()')]
# brand


# In[16]:


all_data


# In[17]:


len(all_data)


# In[19]:


import pandas as pd
import numpy as np
all_data = pd.read_csv('./tousu_data.csv',encoding='utf-8',header=None)


# In[25]:


all_data.to_csv(r'C:\Users\Lenovo\Desktop\tousu_data.csv', encoding='GB18030', header=None)


# In[26]:


all_data[1]


# In[27]:


all_data


# # 对品牌出现的次数进行分析

# In[83]:


size = all_data.loc[:,[1]] 
size=dict(zip(*np.unique(size, return_counts=True)))
size
PP = []  #存放品牌
number = []  #存放次数
for i in size:  
    
    PP.append(i)    # 遍历的字典值
    number.append(size[i])
print(PP)
print(number)


# ## 分析品牌次数的条形图

# In[87]:


import matplotlib.pyplot as plt

#中文显示方法
import matplotlib as mpl
mpl.rcParams['font.sans-serif'] = ['SimHei']
mpl.rcParams['font.serif'] = ['SimHei']
mpl.rcParams['axes.unicode_minus'] = False 

plt.bar(PP, number)
plt.title('汽车品牌被投诉的次数')
plt.show()
# plt.savefig(r'C:\Users\Lenovo\Desktop\tousu_PP.png')


# # 对大众品牌进行单一分析

# In[35]:


data_AZ = all_data.loc[all_data[1] == '大众',:]
data_AZ


# ## 对大众车型进行分析

# In[104]:


size1 = data_AZ.loc[:,[2]] 
size1=dict(zip(*np.unique(size1, return_counts=True)))

PP_A = []  #存放大众品牌车型
num = []  #存放次数
for i in size1:         # 遍历字典a的键名
    
    PP_A.append(i)    # 遍历的字典值
    num.append(size1[i])
print(PP_A)
print(num)
PP_A=PP_A[0:5]  #获取大众品牌车型前五个
num=num[0:5]


# ## 大众车型被投诉占比图

# In[126]:


#中文显示方法
import matplotlib as mpl
mpl.rcParams['font.sans-serif'] = ['SimHei']
mpl.rcParams['font.serif'] = ['SimHei']
mpl.rcParams['axes.unicode_minus'] = False 

p =plt.figure(figsize=(6,6))
explode = [0.01,0.01,0.01,0.01,0.01]
plt.pie(num,explode = explode,labels = PP_A,autopct = '%1.1f%%')
plt.title('大众汽车车型投诉占比')
# plt.savefig(r'Users\Lenovo\Desktop\tousu_CX.png')
plt.show()


# # 大众汽车发生故障被投诉的年份

# In[119]:


year = data_AZ.loc[:,[3,5]]
year1 = list(year[5])
year1
year2 = []   #年份
for i in year1:
    try:  
        if int(i[0:4]):
            year2.append(int(i[0:4]))
    except:
        pass


# In[162]:


year_AZ = dict(zip(*np.unique(year2, return_counts=True)))
year_AZ.keys()
year_AZ.values()
year_AZ1=pd.DataFrame({'year':list(year_AZ.keys()),'num':list(year_AZ.values())})


# In[163]:


# # def text_save(filename, year_AZ):#filename为写入CSV文件的路径，data为要写入数据列表.
# file = open(r'C:\Users\Lenovo\Desktop\year_AZ.txt','w')
# #   for i in range(len(year_AZ)):
# s = str(year_AZ1)
# # .replace('{','').replace('}','').replace(',',' ').replace(':','年：')  #去除{}，：,这两行按数据不同，可以选择
# file.write(s)
# file.close()
# print("保存文件成功")


# In[122]:


year = []  #存放年份
number = []  #存放次数
for i in year_AZ:         # 遍历字典a的键名
    
    year.append(i)    # 遍历的字典值
    number.append(year_AZ[i])


# ## 大众汽车故障被投诉的年份占比图

# In[125]:


#中文显示方法
import matplotlib as mpl
mpl.rcParams['font.sans-serif'] = ['SimHei']
mpl.rcParams['font.serif'] = ['SimHei']
mpl.rcParams['axes.unicode_minus'] = False 

p =plt.figure(figsize=(6,6))
explode = [0.01,0.01,0.01,0.01,0.01]
plt.pie(number,explode = explode,labels = year,autopct = '%1.1f%%')
plt.title('大众汽车年度投诉占比')
# plt.savefig(r'Users\Lenovo\Desktop\tousu_year.png')
plt.show()


# In[166]:


# from wordcloud import WordCloud
# import matplotlib.pyplot as plt #绘制图像的模块
# import  jieba #jieba分词

# path_txt=r'C:\Users\Lenovo\Desktop\year_AZ.txt'
# f = open(path_txt,'r',encoding='GBK').read()

# # 结巴分词，生成字符串，wordcloud无法直接生成正确的中文词云
# cut_text = " ".join(jieba.cut(f))

# wordcloud = WordCloud(
#    #设置字体，不然会出现口字乱码，文字的路径是电脑的字体一般路径，可以换成别的
#    font_path="msyh.ttc",
#    #设置了背景，宽高
#    background_color="white",width=1000,height=1000).generate(cut_text)

# plt.imshow(wordcloud, interpolation="bilinear")
# plt.axis("off")
# plt.show()


# In[ ]:




