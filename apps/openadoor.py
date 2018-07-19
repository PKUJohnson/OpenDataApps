# author: 微信号 rdex
# author: 公众号 BlingBlingMoney
import pymongo
from PIL import Image
import json
import win32com.client
import os
from selenium import webdriver
import pandas as pd
import numpy as np
import re
from pyecharts import Bar
import urllib
from pyecharts import Pie
import tushare as ts
import hmac
import hashlib
import base64
import time
import random
import requests


class RemoteExcel:
    """对excel表格的操作

    """

    def __init__(self, filename=None):
        """初始化函数

        Args:
            filename: 要进行操作的文件名，如果存在此文件则打开，不存在则新建
                        此文件名一般包含路径

        """
        self.xlApp = win32com.client.Dispatch('Excel.Application')
        self.xlApp.Visible = 0
        self.xlApp.DisplayAlerts = 0  # 后台运行，不显示，不警告
        if filename:
            self.filename = filename
            if os.path.exists(self.filename):
                self.xlBook = self.xlApp.Workbooks.Open(filename)
            else:
                self.xlBook = self.xlApp.Workbooks.Add()  # 创建新的Excel文件
                self.xlBook.SaveAs(self.filename)
        else:
            self.xlBook = self.xlApp.Workbooks.Add()
            self.filename = ''

    def get_cell(self, row, col, sheet=None):
        """读取单元格的内容

        Args:
            row: 行
            col: 列
            sheet: 表格名（不是文件名）

        """
        if sheet:
            sht = self.xlBook.Worksheets(sheet)
        else:
            sht = self.xlApp.ActiveSheet
        return sht.Cells(row, col).Value

    def set_cell(self, sheet, row, col, value):
        """向表格单元格写入

        Args:
            sheet: 表格名（不是文件名）
            row: 行
            col: 列
            value: 定入内容
        """
        try:
            sht = self.xlBook.Worksheets(sheet)
        except:
            self.new_sheet(sheet)
            sht = self.xlBook.Worksheets(sheet)
        sht.Cells(row, col).Value = value

    def save(self, newfilename=None):
        """保存表格"""
        if newfilename:
            self.filename = newfilename
            self.xlBook.SaveAs(self.filename)
        else:
            self.xlBook.Save()

    def close(self):
        """保存表格、关闭表格，结束操作"""
        self.save()
        self.xlBook.Close(SaveChanges=0)
        del self.xlApp

    def new_sheet(self, newsheetname):
        """新建一个新表格"""
        sheet = self.xlBook.Worksheets.Add()
        sheet.Name = newsheetname
        sheet.Activate()

    def active_sheet(self):
        return self.xlApp.ActiveSheet

    def add_pic(self, sheet, picturepath, row, column, width, height):
        # "Insert a picture in sheet"
        sht = self.xlBook.Worksheets(sheet)
        sht.Shapes.AddPicture(picturepath, 1, 1, sht.cells(row, column).left, sht.cells(row, column).top, width, height)


class RemoteWord:
    def __init__(self, filename=None):
        self.xlApp = win32com.client.DispatchEx('Word.Application')
        self.xlApp.Visible = 0
        self.xlApp.DisplayAlerts = 0  # 后台运行，不显示，不警告
        if filename:
            self.filename = filename
            if os.path.exists(self.filename):
                self.doc = self.xlApp.Documents.Open(filename)
            else:
                self.doc = self.xlApp.Documents.Add()  # 创建新的文档
                self.doc.SaveAs(filename)
        else:
            self.doc = self.xlApp.Documents.Add()
            self.filename = ''

    def add_what(self, string):
        '''在文档末尾添加内容'''

        rangee = self.doc.Range()
        rangee.InsertAfter(string + '\n')

    def add_pic(self, picpath):
        self.xlApp.selection.InlineShapes.AddPicture(FileName=picpath, LinkToFile=False, SaveWithDocument=True)

    def save(self):
        '''保存文档'''
        self.doc.Save()

    def save_as(self, filename):
        '''文档另存为'''
        self.doc.SaveAs(filename)

    def close(self):
        '''保存文件、关闭文件'''
        # self.save()
        self.xlApp.Documents.Close()
        self.xlApp.Quit()


# 存储为txt
def text_save(content1, filename, mode='a'):
    # Try to save a list variable in txt file.
    file = open(filename, mode)
    for i in range(len(content1)):
        file.write(str(content1[i]))
    file.close()


# 读取txt
def text_read(filename):
    # Try to read a txt file and return a list.Return [] if there was a mistake.
    try:
        file = open(filename, 'r')
    except IOError:
        error = []
        return error
    content1 = file.readlines()
    file.close()
    return content1


# 开启数据库连接，iciba每日一句
def iciba(date_iciba, save_path_iciba):
    client = pymongo.MongoClient(host='localhost', port=27017)
    db = client['openadoor']
    collection = db['wwwWordsEveryday']
    iciba_info_everyday(collection, date_iciba, save_path_iciba)
    client.close()
    print('iciba done: ' + save_path_iciba)
    return save_path_iciba


# iciba每日一句
#  API 'http://open.iciba.com/dsapi'
def iciba_info_everyday(innercollection, date_iciba_mongo, save_path_iciba_mongo):
  a = innercollection.find_one({'date': date_iciba_mongo})
  if a is None:
    try:
        # requests找到一个网址
        user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'
        headers = {"User-Agent": user_agent}
        allpageurl = 'http://open.iciba.com/dsapi'
        allpageurlresponse = requests.get(allpageurl, headers=headers, timeout=3)
        allpageurlcontent = allpageurlresponse.json()
        '''
        text_for_write = date_iciba_mongo + '___' + allpageurlcontent['content'] + '___' \
                         + allpageurlcontent['note'] + '___' + allpageurlcontent['love'] + '___' \
                         + allpageurlcontent['translation'].replace(' ', '') + '___' + allpageurlcontent[
                             'picture'] + '___' \
                         + allpageurlcontent['picture2'] + '___' + allpageurlcontent['fenxiang_img'] \
                         + '\n'
        text_save(text_for_write, "WordsEveryday_iciba.txt")
        '''

        # 下载三张图片
        path_pic_thumb = download_documents(allpageurlcontent['picture2'], save_path_iciba_mongo[0:-12] + 'big' + date_iciba_mongo + '.jpg')
        # 调整图片大小一致
        pic_zoom(path_pic_thumb, save_path_iciba_mongo, 750)
        download_documents(allpageurlcontent['picture'], save_path_iciba_mongo[0:-12] + 'small' + date_iciba_mongo + '.jpg')
        crop_path = download_documents(allpageurlcontent['fenxiang_img'], save_path_iciba_mongo[0:-12] + 'fenxiang' + date_iciba_mongo + '.jpg')
        # 裁剪图片水印
        crop_picture(crop_path, save_path_iciba_mongo[0:-12] + 'fenxiang_crop_watermark' + date_iciba_mongo + '.jpg')

        data_for_mongo = {
            'date': date_iciba_mongo,
            'love': allpageurlcontent['love'],
            'content': allpageurlcontent['content'],
            'note': allpageurlcontent['note'],
            'translation': allpageurlcontent['translation'].replace(' ', ''),
            'picture': allpageurlcontent['picture'],
            'picture2': allpageurlcontent['picture2'],
            'fenxiang_img': allpageurlcontent['fenxiang_img']}
        innercollection.insert_one(data_for_mongo)
    except requests.Timeout:
        # print('www 反扒' + time.strftime("%H:%M:%S"))
        time.sleep(10)
        iciba_info_everyday(innercollection, date_iciba_mongo, save_path_iciba_mongo)
  print('iciba_info_everyday done: ' + save_path_iciba_mongo)
  return save_path_iciba_mongo


def download_documents(doc_url, save_path):
    f = open(save_path, 'wb')
    # print(save_path)
    picture_data = requests.get(doc_url)
    # print(picture_data.content)
    f.write(picture_data.content)
    f.close()
    print('download_documents done: ' + save_path)
    return save_path


# 裁剪图片每日一图
def crop_picture(picture_path, save_path_crop_pic):
    im = Image.open(picture_path)
    # 图片的宽度和高度
    img_size = im.size
    # print("图片宽度和高度分别是{}".format(img_size))
    ''' 裁剪：传入一个元组作为参数 元组里的元素分别是：
    （距离图片左边界距离x， 距离图片上边界距离y，
    距离图片左边界距离+裁剪框宽度x+w，距离图片上边界距离+裁剪框高度y+h） '''
    # 截取图片中一块宽和高都是250的
    x = 0
    y = 0
    w = img_size[0]
    h = img_size[1] - 100
    region = im.crop((x, y, x + w, y + h))
    region.save(save_path_crop_pic)
    # 截取图片中一块宽是250和高都是300的
    # x = 100
    # y = 100
    # w = 250
    # h = 300
    # region = im.crop((x, y, x+w, y+h))
    # region.save("./crop_test2.jpeg")
    print('crop_picture done: ' + save_path_crop_pic)
    return save_path_crop_pic


# 裁剪图片网易下载的图
def crop_163_stock_picture(picture_path, save_path_crop_pic, cut_pixel):
    im = Image.open(picture_path)
    # 图片的宽度和高度
    img_size = im.size
    # print("图片宽度和高度分别是{}".format(img_size))
    ''' 裁剪：传入一个元组作为参数 元组里的元素分别是：
    （距离图片左边界距离x， 距离图片上边界距离y，
    距离图片左边界距离+裁剪框宽度x+w，距离图片上边界距离+裁剪框高度y+h） '''
    # 截取图片中一块宽和高都是250的
    x = 0
    y = 0
    w = img_size[0]
    h = img_size[1] - cut_pixel
    region = im.crop((x, y, x + w, y + h))
    region.save(save_path_crop_pic)
    # 截取图片中一块宽是250和高都是300的
    # x = 100
    # y = 100
    # w = 250
    # h = 300
    # region = im.crop((x, y, x+w, y+h))
    # region.save("./crop_test2.jpeg")
    print('crop_picture done: ' + save_path_crop_pic)
    return save_path_crop_pic


# 图片压缩
def pic_thumb(pic_path_thumb, save_path_thumb, pic_width):
    im = Image.open(pic_path_thumb).convert('RGB')
    # print('格式', im.format, '，分辨率', im.size, '，色彩', im.mode)
    im.thumbnail((pic_width, int(im.size[1]/(im.size[0]/pic_width))))
    im.save(save_path_thumb, 'JPEG', quality=100)
    print('pic_thumb done: ' + save_path_thumb)
    return save_path_thumb


# 图片放大缩小
def pic_zoom(from_path, save_path_163, zoom_pixel):
    im = Image.open(from_path)
    # print('格式', im.format, '，分辨率', im.size, '，色彩', im.mode)
    out = im.resize((zoom_pixel, int(im.size[1]/(im.size[0]/zoom_pixel))), Image.ANTIALIAS)
    out.save(save_path_163, 'png', quality=100)
    print('pic_zoom done: ' + save_path_163)
    return save_path_163[:-4] + '.png'


# 图片识别
def pic_recognize(url_pic):
    appid = "1251627875"
    bucket = "ztfp"
    secret_id = "AKIDUt7A1hcdu0veBWfdS8e0A9wXyDH9sb4L"
    secret_key = "DF7nIbyFLFxToxvhIhjbHl4B6uXyKYbY"
    expired = time.time() + 2592000
    onceExpired = 0
    current = time.time()
    rdm = ''.join(random.choice("0123456789") for i in range(10))
    userid = "0"
    fileid = "tencentyunSignTest"

    info = "a=" + appid + "&b=" + bucket + "&k=" + secret_id + "&e=" + str(expired) + "&t=" + str(current) + "&r="  + str(rdm) + "&u=0&f="
    # info = bytes(info, 'utf8')

    signindex = hmac.new(secret_key.encode("utf8"), info.encode("utf8"), hashlib.sha1).digest()  # HMAC-SHA1加密
    sign = base64.b64encode(signindex + info.encode("utf8"))  # base64转码

    url = "http://recognition.image.myqcloud.com/ocr/general"
    headers = {'Host': 'recognition.image.myqcloud.com',
                "Content-Length": "187",
                "Content-Type": "application/json",
                "Authorization": sign
                }

    payload = { "appid": appid,
                "bucket": bucket,
                "url": url_pic
                }

    r = requests.post(url, json=payload, headers=headers)
    responseinfo = r.json()
    print(responseinfo)
    for i in range(0, len(responseinfo['data']['items'])):
        print(responseinfo['data']['items'][i]['itemstring'])


# 云财经 龙虎榜评析图片
# www.yuncaijing.com/apps/hdd/observe/id_452.html
def lhb_yuncaijing():
    a = requests.get('http://www.yuncaijing.com/apps/hdd/observelist_1.html')
    url = 'http://stock.10jqka.com.cn/fupan/#fp_item_8'
    url1 = 'http://yuanchuang.10jqka.com.cn/djpingpan_list/'
    # a =requests.get(url1)
    print(a.text)


# jrj data
def jrj_data():
    jrjdata = requests.get('http://stock.jrj.com.cn/action/stock-dynamic/dpwdj/getWdjInfo.jspa?vname=wdjData')
    jrjd = jrjdata.text
    jrjd = json.loads(jrjd[12:-1])
    print(jrjd['data']['fundFlowList'][0]['fiveDaysNetInflow'])


# 同花顺涨停原因分析
# http://www.iwencai.com/stockpick/export?random=3225175330&token=230f0e5b4154b3abe0e21c18d3274f75
def ths_zt_data():
    p = requests.session()
    # headers = {'X-Requested-With':'XMLHttpRequest',"Referer": 'http://www.iwencai.com/stockpick/search?typed=0&preParams=&ts=1&f=1&qs=result_original&selfsectsn=&querytype=stock&searchfilter=&tid=stockpick&w=%E4%BB%8A%E6%97%A5%E8%87%AA%E7%84%B6%E6%B6%A8%E5%81%9C%EF%BC%8C%E6%B6%A8%E5%81%9C%E5%8E%9F%E5%9B%A0%EF%BC%8C%E6%88%90%E4%BA%A4%E9%A2%9D&queryarea='}

    # requests.add_header('Referer', "http://www.iwencai.com/stockpick/search?typed=0&preParams=&ts=1&f=1&qs=result_original&selfsectsn=&querytype=stock&searchfilter=&tid=stockpick&w=%E4%BB%8A%E6%97%A5%E8%87%AA%E7%84%B6%E6%B6%A8%E5%81%9C%EF%BC%8C%E6%B6%A8%E5%81%9C%E5%8E%9F%E5%9B%A0%EF%BC%8C%E6%88%90%E4%BA%A4%E9%A2%9D&queryarea=")
    # a = p.get('http://www.iwencai.com/stockpick/cache?token=912fcddfc6130366ca48325ec3c999ab&p=1&perpage=30&showType=[%22%22,%22%22,%22onTable%22,%22onTable%22,%22onTable%22,%22onTable%22,%22onTable%22,%22onTable%22,%22onTable%22,%22onTable%22,%22onTable%22,%22onTable%22,%22onTable%22,%22onTable%22,%22onTable%22,%22onTable%22,%22onTable%22,%22onTable%22,%22onTable%22]', headers=headers)
    # a = p.get('http://www.iwencai.com/stockpick/cache?token=b9227ab58658e6c1c81c4d654b6cc0161531564218&p=2&perpage=30&showType=[%22%22,%22%22,%22onTable%22,%22onTable%22,%22onTable%22,%22onTable%22,%22onTable%22,%22onTable%22,%22onTable%22,%22onTable%22,%22onTable%22,%22onTable%22,%22onTable%22,%22onTable%22,%22onTable%22,%22onTable%22,%22onTable%22,%22onTable%22,%22onTable%22]')
    a = p.get(
        'http://search.10jqka.com.cn/search?w=%E6%B6%A8%E5%81%9C%E5%A4%8D%E7%9B%98&tid=info&tr=0&ft=1&st=0&tr=2&qs=pf')
    print(a.text)
    # b = json.loads(a.text)
    print(tuple(a.cookies))


# excel生成
def excel_generate(date_eg):
    datestrtitle = time.strftime('%m.%d', time.localtime(time.time()))
    datestrxls = time.strftime('%Y-%m-%d', time.localtime(time.time()))
    xls = RemoteExcel('D:\\60_openadoor\BlingBlingMoney\\模板.xlsx')
    xls.set_cell('今日', 1, 1, '[' + datestrtitle + ']今日股市股票行情')
    # im = Image.open('D:\\60_openadoor\Pictures_FastStoneCapture\每日一句配图.jpg')
    # img_size = im.size
    # xls.add_pic('今日', 'D:\\60_openadoor\Pictures_FastStoneCapture\每日一句配图.jpg', 2, 1, img_size[0], img_size[1])
    xls.set_cell('今日', 3, 1, '每日一句:')
    client = pymongo.MongoClient(host='localhost', port=27017)
    db = client['openadoor']
    collection = db['wwwWordsEveryday']
    words_everyday_mongodb = collection.find_one({"date": date_eg})
    client.close()
    xls.set_cell('今日', 4, 1, '    ' + words_everyday_mongodb['content'])
    xls.set_cell('今日', 5, 1, '    ' + words_everyday_mongodb['note'])
    xls.set_cell('今日', 7, 1, '    ' + '市场总览:')
    xls.set_cell('今日', 8, 1, '    ' + words_everyday_mongodb['note'])

    xls.save("D:\\60_openadoor\BlingBlingMoney\\" + date_eg + '.xlsx')
    xls.close()


# ths网页另存为图片
# http://yuanchuang.10jqka.com.cn/mrnxgg_list/
def www2pic(fromurl, savepath):
    driver = webdriver.PhantomJS(
        executable_path=r'C:\ProgramData\Anaconda3\Lib\site-packages\phantomjs-2.1.1-windows\bin\phantomjs.exe')
    driver.set_page_load_timeout(500)
    driver.set_window_size(1680, 1050)
    driver.get(fromurl)
    imgelement = driver.find_element_by_class_name('main_box')
    datestrxls = time.strftime('%Y-%m-%d', time.localtime(time.time()))
    savepath = "D:\\60_openadoor\BlingBlingMoney\\" + savepath + datestrxls + '.png'
    driver.save_screenshot(savepath)
    im = Image.open(savepath)
    im = im.crop((342, 515, 1079, 825))
    im.save(savepath)


# 涨跌分布
def zdfb2pic(fromurl, savepath):
    driver = webdriver.PhantomJS(
        executable_path=r'C:\ProgramData\Anaconda3\Lib\site-packages\phantomjs-2.1.1-windows\bin\phantomjs.exe')
    driver.set_page_load_timeout(500)
    driver.set_window_size(1680, 1050)
    driver.get(fromurl)
    time.sleep(3)
    imgelement = driver.find_element_by_id('highcharts-0')
    datestrxls = time.strftime('%Y-%m-%d', time.localtime(time.time()))
    savepath = "D:\\60_openadoor\\BlingBlingMoney\\" + savepath + datestrxls + '.png'
    driver.save_screenshot(savepath)
    im = Image.open(savepath)
    im = im.crop((485, 142, 1050, 505))
    im.save(savepath)


def sina2pic(date_sina):
    driver = webdriver.PhantomJS(
        executable_path=r'C:\ProgramData\Anaconda3\Lib\site-packages\phantomjs-2.1.1-windows\bin\phantomjs.exe')
    driver.set_page_load_timeout(500)
    driver.set_window_size(1680, 1050)
    driver.get('http://img1.money.126.net/chart/hs/kline/day/30/0000300.png')
    time.sleep(3)
    datestrxls = date_sina
    savepath = "D:\\60_openadoor\BlingBlingMoney\\hqsh000001" + date_sina + '.png'
    driver.save_screenshot(savepath)
    im = Image.open(savepath)
    im = im.crop((342, 515, 1088, 825))
    im.save(savepath)


# 返回最后一个交易日
# api = 'http://hqdata.jrj.com.cn/zrztjrbx/five_day.js'
def last_trade_date():
    date_str_www = requests.get('http://hqdata.jrj.com.cn/zrztjrbx/five_day.js')
    date_str_temp1 = date_str_www.text
    date_str_temp2 = re.findall(r'\d{8}', date_str_temp1)
    return date_str_temp2[0]


# tushare获取当日涨跌幅分布,返回各段数据[10,>7,>5>3>1>-1>-3>-5>-7>-10,-10]
def zdf_distribution(date_zdffb, save_path_zdffb):
    # tushare
    stockbasicinfo = ts.get_stock_basics()

    '''代码排序'''
    stockbasicinfo = stockbasicinfo.sort_index()

    '''股票总数'''
    stocknum = len(stockbasicinfo)
    # stockcode = stockbasicinfo.index[0]

    # 所有票的url拼接地址，用sina api去获取数据，因为tushare获取实时数据不稳定
    urllist = []
    for i in range(0, stocknum):
        stockcode = stockbasicinfo.index[i]
        stockcodeint = int(stockbasicinfo.index[i])
        if stockcodeint >= 600000:
            urllist.append('sh' + str(stockcode))
        else:
            urllist.append('sz' + str(stockcode))
    urllen = len(urllist)
    # print(urllen, urllist)
    (x, y) = divmod(urllen, 9)
    urlchar = ','.join(urllist)
    # print(urlchar)
    # 总共分成9份，因为sina每次请求不超过800
    urlbase = 'http://hq.sinajs.cn/list='
    url1 = urlbase + urlchar[0:9*x-1]
    url2 = urlbase + urlchar[9*x*1:9*x*2-1]
    url3 = urlbase + urlchar[9*x*2:9*x*3-1]
    url4 = urlbase + urlchar[9*x*3:9*x*4-1]
    url5 = urlbase + urlchar[9*x*4:9*x*5-1]
    url6 = urlbase + urlchar[9*x*5:9*x*6-1]
    url7 = urlbase + urlchar[9*x*6:9*x*7-1]
    url8 = urlbase + urlchar[9*x*7:9*x*8-1]
    url9 = urlbase + urlchar[9*x*8:]
    datatemp1 = requests.get(url1)
    datatemp2 = requests.get(url2)
    datatemp3 = requests.get(url3)
    datatemp4 = requests.get(url4)
    datatemp5 = requests.get(url5)
    datatemp6 = requests.get(url6)
    datatemp7 = requests.get(url7)
    datatemp8 = requests.get(url8)
    datatemp9 = requests.get(url9)
    # 获取的数据进行合并
    urldata = datatemp1.text + datatemp2.text + datatemp3.text + datatemp4.text + datatemp5.text + datatemp6.text + datatemp7.text + datatemp8.text + datatemp9.text
    urlsplit = re.split(r'=', urldata)
    # print(len(urlsplit))
    validnum = 0
    validzflist = []
    validyes10 = 0
    validyes7 = 0
    validyes5 = 0
    validyes3 = 0
    validyes1 = 0
    validyes0 = 0
    valid0 = 0
    validno0 = 0
    validno1 = 0
    validno3 = 0
    validno5 = 0
    validno7 = 0
    validno10 = 0
    # 数据分割，提取，整理
    for i in range(1, len(urlsplit)):
        if len(urlsplit[i]) > 100:
            urldataone = re.split(r',', urlsplit[i])
            yesprice = float(urldataone[2])
            nowprice = float(urldataone[3])
            amount = float(urldataone[9])
            buyonevol = float(urldataone[10])
            sellonevol = float(urldataone[20])
            if amount < 0.1:
                pass
            else:
                if nowprice < 0.1:
                    pass
                else:
                    if yesprice < 0.1:
                        pass
                    else:
                        zdf = int(10000*(nowprice/yesprice - 1) + 0.5)/100
                        if abs(zdf) < 11:
                            validnum += 1
                            validzflist.append(zdf)
                            if zdf >= 9.8 and sellonevol < 0.1:
                                validyes10 += 1
                            if zdf >= 7 and sellonevol > 0.1:
                                validyes7 += 1
                            if 5 <= zdf < 7:
                                validyes5 += 1
                            if 3 <= zdf < 5:
                                validyes3 += 1
                            if 1 <= zdf < 3:
                                validyes1 += 1
                            if 0.0001 <= zdf < 1:
                                validyes0 += 1
                            if abs(zdf) <= 0.0001:
                                valid0 += 1
                            if -1 < zdf < -0.0001:
                                validno0 += 1
                            if -3 < zdf <= -1:
                                validno1 += 1
                            if -5 < zdf <= -3:
                                validno3 += 1
                            if -7 < zdf <= -5:
                                validno5 += 1
                            if zdf <= -7 and buyonevol > 0.1:
                                validno7 += 1
                            if zdf <= -9.8 and buyonevol < 0.1:
                                validno10 += 1
    # 数据整理
    v11 = [0, 0, 0, 0, 0, 0, 0, validyes0, validyes1, validyes3, validyes5, validyes7, 0]
    v22 = [0, validno7, validno5, validno3, validno1, validno0, 0, 0, 0, 0, 0, 0, 0]
    v00 = [0, 0, 0, 0, 0, 0, valid0, 0, 0, 0, 0, 0, 0]
    vzt = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, validyes10]
    vdt = [validno10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    attr = ['-10%', '>-7%', '-7~5%', '-5~3%', '-3~1%', '-1~0%', '0', '0~1%', '1~3%', '3~5%', '5~7%', '>7%', '10%']

    # 调用pyecharts
    title = ' 涨跌分布：↑' + str(validyes0+validyes1+validyes3+validyes5+validyes7+validyes10) +  \
            ' ↓' + str(validno0+validno1+validno3+validno5+validno7+validno10) + '  →' + str(valid0)
    subtitle = ' Add_wx_friends: sleepingmoney'
    # bar
    bar = Bar(title, subtitle, title_pos=0.1, subtitle_text_size=15, subtitle_color='#aa8')
    bar.use_theme("shine")
    bar.add("涨", attr, v11, bar_category_gap=0, mark_point=['max', 'average'])
    bar.add("", attr, vzt, bar_category_gap=0, mark_point=['max'])
    bar.add("平", attr, v00, bar_category_gap=0, mark_point=['max'])
    bar.add("跌", attr, v22, bar_category_gap=0, mark_point=['max', 'average'])
    bar.add("", attr, vdt,  bar_category_gap=0, mark_point=['max'])
    # pie
    attrpie = ['涨', '平', '跌']
    vpie = [validyes0+validyes1+validyes3+validyes5+validyes7+validyes10,valid0, validno0+validno1+validno3+validno5+validno7+validno10]
    pie = Pie("涨跌饼图", title_pos='center', width=400, height=400)
    pie.add("", attrpie, vpie, radius=[6, 15], label_text_color=None, is_label_show=True, legend_orient='vertical', legend_pos='left')
    bar_render_path = save_path_zdffb[:-12] + 'bar_tozoom_' + date_zdffb + '.png'
    pie_render_path = save_path_zdffb[:-12] + 'pie_tozoom_' + date_zdffb + '.png'
    pie.render(path=pie_render_path)
    bar.render(path=bar_render_path)
    pic_zoom(bar_render_path, save_path_zdffb, 830)
    print('zdf_distribution done: ' + save_path_zdffb)
    return save_path_zdffb


# 163大盘分时
# http://img1.money.126.net/chart/hs/time/540x360/0000001.png

# tgbhotstock
def hot_tgb(date_tgbhotstock, save_path_tgbhotstock):
    a = requests.get('https://www.taoguba.com.cn/hotPop')
    b = a.text.split('相关链接')
    c = b[1].split('24小时个股搜索热度')
    d = c[0]
    stockcode = re.findall(r'[sz,sh]{1}\d{6}', d)  # 30
    stockno = re.findall(r'<td>\d+</td>', d)        # 10
    stockhotvalue = re.findall(r'<td >\d+</td>', d)  # 20
    stockname = re.findall(r'[\*ST,ST,\*,SST,GQY,S,N,TCL,XD,G,XR]{0,1}[\u4e00-\u9fa5]{3,4}', d)  # 10
    v1 = []  # 今日搜索
    v2 = []  # 最近7天搜索
    for i in range(0, len(stockhotvalue)):

        (x, y) = divmod(i, 2)
        if y == 0:
            v1.append(int(stockhotvalue[i].replace('<td >', "").replace('</td>', "")))
        else:
            v2.append(int(stockhotvalue[i].replace('<td >', "").replace('</td>', "")))
    title = ' 人气妖股 - 搜索热度'
    subtitle = ' Add_wx_friends: sleepingmoney'
    bar = Bar(title, subtitle, title_pos=0.1, subtitle_text_size=15, subtitle_color='#aa8')
    bar.use_theme("macarons")
    bar.add("7day", stockname, v2, bar_category_gap='80%', is_stack=True)
    bar.add("today", stockname, v1, bar_category_gap='80%', is_stack=True)
    render_path = save_path_tgbhotstock[:-12] + 'hot_stock_tgb_' + date_tgbhotstock + '.png'
    bar.render(path=render_path)
    pic_zoom(render_path, save_path_tgbhotstock, 830)
    print('pic_ztnum_hist_pyecharts done: ' + save_path_tgbhotstock)
    return save_path_tgbhotstock


# 根据zt_hum_history函数返回的df数据，提取历史涨停数据生成图片
def pic_ztnum_hist_pyecharts(df_ztnum_hist, pic_ztnum_hist_path, date_str_ztnum_hist):

    # 为什么取最前的21天的数据，因为和历史K线每月有21根，相对应
    ztnum = df_ztnum_hist.head(21)

    # 提取月份
    month = (ztnum.iloc[:, 0].str[4:8])
    month = np.sort(month.map(lambda c: c))
    attr = ['{}'.format(i) for i in month]

    # 切片
    v1 = ztnum.iloc[:, 1]
    # v1 = ['{}'.format(i) for i in v1.values]
    v11 = []
    for x in v1:
        a = min(100, int(x))
        v11.append(a)
    v22 = []
    v2 = ztnum.iloc[:, 3]
    for x in v2:
        a = min(100, int(x))
        v22.append(a)
    # print(v11)
    # print(v22)
    # pyecharts参数
    title = ' 历史数据 - 每日涨跌停'
    subtitle = ' Add_wx_friends: sleepingmoney'
    bar = Bar(title, subtitle, title_pos=0.1, subtitle_text_size=15, subtitle_color='#aa8')
    bar.use_theme("infographic")
    bar.add("涨停数", attr, v11[::-1],   mark_line=['average'])
    bar.add("跌停数", attr, v22[::-1],   mark_line=['average'])
    render_path = pic_ztnum_hist_path[:-12] + 'tozoom_' + date_str_ztnum_hist + '.png'
    bar.render(path=render_path)
    pic_zoom(render_path, pic_ztnum_hist_path, 830)
    print('pic_ztnum_hist_pyecharts done: ' + pic_ztnum_hist_path)
    return pic_ztnum_hist_path


# 历史涨跌停数量，最近一个月的,递归算法
# api = 'http://home.flashdata2.jrj.com.cn/limitStatistic/month/201807.js'
def zt_hum_history(zt_his_text, date_zt_his, zt_next_num):

    # 如果递归数字<0，那就终止递归 return df，此处是统计数据
    # 第一次递归的zt_his_text=''是空的，逐步延长，最后一次递归统计此字符串
    if zt_next_num < 0:
        zt_np = []
        # 分割，提取，循环append成list
        zt_list = re.split(r'],\[', zt_his_text[1:-2])
        for j in range(0, len(zt_list), 1):
            zt_list_one = re.split(r',', zt_list[j])
            for k in range(0, len(zt_list_one), 1):
                if len(zt_list_one[k]) == 0:
                    zt_list_one[k] = 0
                zt_np.append(zt_list_one[k])
        # 转成数组，转成矩阵，转成df
        zt_np = np.array(zt_np)
        matrix = [[0 for p in range(0, len(zt_list_one), 1)] for q in range(0, len(zt_list), 1)]
        for m in range(0, len(zt_np)):
            a, b = divmod(m, 7)
            matrix[a][b] = zt_np[m]  # 将切分后的数据存入df中
            # print(a, b, matrix[a][b])
        df = pd.DataFrame(matrix, columns=pd.MultiIndex.from_product([['date', 'ztnum', 'ztnumcmp', 'dtnum', 'dtnumcmp',  'cash', 'cashcmp']]))
        print('zt_hum_history done: df数据已生成')
        return df

    month0 = int(date_zt_his[4:6])
    year0 = int(date_zt_his[0:4])
    month0url = date_zt_his[0:6]
    month0_data_tmp = requests.get('http://home.flashdata2.jrj.com.cn/limitStatistic/month/' + month0url + '.js')
    month0_data = month0_data_tmp.text
    month0_split1 = re.split(r'\[\[', month0_data)
    month0_split2 = re.split(r']]', month0_split1[1])
    if month0-1 == 0:
        month1 = 12
        year1 = year0-1
    else:
        month1 = month0-1
        year1 = year0
    month0_data_list = zt_his_text + '[' + month0_split2[0] + '],'
    zt_next_num -= 1
    print('zt_hum_history done: 还需递归次数 ' + str(zt_next_num + 1))
    return zt_hum_history(month0_data_list, str(year1) + str(month1).zfill(2), zt_next_num)


def other_download_pic():
    urllib.request.urlretrieve('http://img1.money.126.net/chart/hs/kline/day/30/0000300.png', '.\Pictures_FastStoneCapture\sinash000001' + date_str_today + '.png')


# 识别图片中的文字，判定是否识别过，如果识别过，返回存储的文件地址，如果没有，则识别并存储且返回地址
def pic_ocr(url_pic, save_path_pic2json, date_pic2json):
    output_dir = save_path_pic2json[0:-5] + date_pic2json + '.json'
    if os.path.isfile(output_dir):
        print('pic_ocr done: json already exists ' + output_dir)
        return save_path_pic2json[0:-5] + date_pic2json + '.json'
    else:
        appid = "1251627875"
        bucket = "ztfp"
        secret_id = "AKIDUt7A1hcdu0veBWfdS8e0A9wXyDH9sb4L"
        secret_key = "DF7nIbyFLFxToxvhIhjbHl4B6uXyKYbY"
        expired = time.time() + 2592000
        onceExpired = 0
        current = time.time()
        rdm = ''.join(random.choice("0123456789") for i in range(10))
        userid = "0"
        fileid = "tencentyunSignTest"
        info = "a=" + appid + "&b=" + bucket + "&k=" + secret_id + "&e=" + str(expired) + "&t=" + str(current) + "&r="  + str(rdm) + "&u=0&f="
        signindex = hmac.new(secret_key.encode("utf8"), info.encode("utf8"), hashlib.sha1).digest()  # HMAC-SHA1加密
        sign = base64.b64encode(signindex + info.encode("utf8"))  # base64转码
        url = "http://recognition.image.myqcloud.com/ocr/general"
        headers = {'Host': 'recognition.image.myqcloud.com',
                "Content-Length": "187",
                "Content-Type": "application/json",
                "Authorization": sign}
        payload = {"appid": appid,
                "bucket": bucket,
                "url": url_pic}
        r = requests.post(url, json=payload, headers=headers)
        responseinfo = r.json()
        # print(responseinfo)
        # for i_pic in range(0, len(responseinfo['data']['items'])):
        #     print(responseinfo['data']['items'][i_pic]['itemstring'])

        jsobj = json.dumps(responseinfo)
        with open(output_dir, "w") as f:
            f.write(jsobj)
            f.close()
        with open(save_path_pic2json, "w") as f:
            f.write(jsobj)
            f.close()
        # 存入数据库
        client = pymongo.MongoClient(host='localhost', port=27017)
        db = client['openadoor']
        collection = db['wwwPic2Json_THS']
        a = collection.find_one({'date': date_pic2json})
        if a is None:
            data_for_mongo = {'date': date_pic2json,
                              'json': responseinfo}
            collection.insert_one(data_for_mongo)
            client.close()
        print('pic_ocr done: json already write in text file: ' + output_dir)
        return output_dir


# 把json文件的内容读出来并提取数据，return list 做下一步的分析
def json_pic_data2list(date_jsondata2list, josn_path):

    emb_filename = josn_path
    fr = open(emb_filename)
    a = json.load(fr)
    ystep = []
    ynum = []
    gnnum = 1
    gnname = []
    ztreason = []
    for i in range(1, len(a['data']['items'])):

        x = a['data']['items'][i]
        # print(x)
        b = x['itemcoord']['y']
        if i == 1:
            ystep.append(b)
            ynum.append(1)
            gnname.append(x['itemstring'])
            ztreason.append(' ')
            gnnum += 1
        else:
            if abs(b - ystep[-1]) > 8:
                ystep.append(b)
                ynum.append(1)
                gnname.append(x['itemstring'].replace(' ', '').replace('|', ''))
                ztreason.append(' ')
                gnnum += 1

            else:
                c = ynum[-1]
                c += 1
                ynum[-1] = c
                if len(re.findall(r'\d{1,2}:\d{1,2}:\d{1,2}', x['itemstring'])):
                    ztreason[-1] = ' '
                elif len(x['itemstring']) <= 1:
                    ztreason[-1] = ' '
                else:
                    ztreason[-1] = x['itemstring'].replace(' ', '').replace('|', '')

    # 第一行万一出错，那么使用第一个股票的涨停原因作为 第一个板块分类的名称，如果有+号，那么取+前面的部分
    for i in range(0, len(ystep)):
        if i == 0:
            if ynum[0] != 1:
                ynum[0] = 1
                gnname[0] = re.split('\+', ztreason[1])[0]
                ztreason[0] = ' '
        if gnname[i] == '真颠':
            gnname[i] = '其他'
        if ztreason[i] == '真颠':
            ztreason[i] = '其他'
        if ztreason[i] == ' ':
            ztreason[i] = '其他'
    print('json_pic_data2list done: json data → list data')
    if ynum[0] == 1 and ynum[1] == 1:
        return [gnnum-1, ynum[1:], gnname[1:], ztreason[1:]]
    else:
        return [gnnum, ynum, gnname, ztreason]


# 从同花顺爬取两个内容，一个是《涨停复盘》的图片，一个是《收评》的分时板块异动的时间顺序
def acq_pic_path_ths(date_wwwths_ztfp, savepath_wwwths_ztfp):

    url_www_ths = 'http://stock.10jqka.com.cn/jiepan_list/'
    b = requests.get(url_www_ths)

    c = re.findall(r'title="涨停复盘[\s\S]*?>涨停复盘', b.text)
    d = re.findall(r'http[\s\S]*?html', c[0])
    e = requests.get(d[0].replace('stock.', 'm.'))
    f = re.findall(r'查看更多涨停[\s\S]*?\.png', e.text)
    g = re.findall(r'http[\s\S]*?\.png', f[0])
    download_documents(g[0], 'D:\\60_openadoor\\Pictures_FastStoneCapture\\ztfp_ths' + date_wwwths_ztfp + '.png')
    h = json_pic_data2list(date_wwwths_ztfp, pic_ocr(g[0], savepath_wwwths_ztfp, date_wwwths_ztfp))
    # print(json_pic_data2list)

    j = re.findall(r'title="收评[\s\S]*?>收评', b.text)
    k = re.findall(r'http[\s\S]*?html', j[0])
    l = requests.get(k[0].replace('stock.', 'm.'))
    # print(k[0].replace('stock.', 'm.'))
    m = re.findall(r'(\d{2}:\d{2}\s\S*?板块|\d{2}:\d{2}\s\S{4})', l.text)
    # print([h, m])
    # print('acq_pic_from_ths done: data_list be returned...')
    print('acq_pic_path_ths done: ths 涨停复盘数据和收评数据已提取...')
    return [h, m]


# 从金融街获取今日涨停详细数据，和图片解析后，合并一起，生成今日涨停板块复盘图
# http://home.flashdata2.jrj.com.cn/limitStatistic/ztForce/20180718.js
def zt_detail_today(date_zt_detail):
    a = requests.get('http://home.flashdata2.jrj.com.cn/limitStatistic/ztForce/' + date_zt_detail + '.js')
    b = '{' + re.findall(r'"Data":[\s\S]*}', a.text)[0]
    c = json.loads(b)
    d = c['Data']
    print('zt_detail_today done: 今日涨停详细数据已提取...')
    return [len(d), d]


def zt_detail_yestoday():
    a = requests.get('http://hqdata.jrj.com.cn/zrztjrbx/limitup.js')
    b = '{' + re.findall(r'"Data":[\s\S]*}', a.text)[0]
    c = json.loads(b)
    d = c['Data']
    print('zt_detail_yestoday done: 昨板今温数据已提取...')
    return [len(d), d]


# 同花顺涨停复盘数据数据生成图片，tencent解析之后，从金融街获取今日涨停详细数据，和图片解析后，合并一起，生成今日涨停板块复盘图
def data2pic_ths_ztfp_sp(date_data2pic, savepath_data2pic, data2pic, data2jrjapi, data2jrjzbjwapi):

    text_html_data = '<div style="position:relative;left:100px"><table border="0" cellpadding="0" cellspacing="1" >'
    ztnum = data2pic[0][0]
    gnlabel = data2pic[0][1]
    gnname = data2pic[0][2]
    ztreason = data2pic[0][3]
    zt_detail_today(date_data2pic)
    ztnumapi = data2jrjapi[0]
    ztdataapi = data2jrjapi[1]
    ztzbjwnumapi = data2jrjzbjwapi[0]
    ztzbjwdataapi = data2jrjzbjwapi[1]
    print(gnlabel)
    for zt in range(0, len(gnlabel)):
        # print(gnlabel[zt])
        if gnlabel[zt] == 1:
            text_html_data = text_html_data + '<tr><th colspan="6"><big><b><font color="red">【' + gnname[zt] + '】</font></b></big></th></tr>'
        else:
            ztcontinue = 1
            for ztzbjwapi in range(0, ztzbjwnumapi):
                # print(gnname[zt][0:6])
                # print(ztzbjwdataapi[ztzbjwapi][1])
                if str(gnname[zt][0:6]) == str(ztzbjwdataapi[ztzbjwapi][1]):
                    ztcontinue = ztzbjwdataapi[ztzbjwapi][9]
            if ztcontinue == 1:
                ztcontinuecolor = '<td width="80" align="center">' + str(ztcontinue) + '</td>'
            elif ztcontinue == 2:
                ztcontinuecolor = '<td width="80" align="center"><font color="da70d6"><b>' + str(ztcontinue) + '</b></font></td>'
            elif ztcontinue == 3:
                ztcontinuecolor = '<td width="50" align="center"><font color="#FF00FF   "><big><b>' + str(ztcontinue) + '</b></big></font></td>'
            else:
                ztcontinuecolor = '<td width="50" align="center"><font color="#ff0000"><big><b>' + str(ztcontinue) + '</b></big></font></td>'
            for ztapi in range(0, ztnumapi):
                if ztdataapi[ztapi][7][0:5] == '09:25':
                    ztdataapi[ztapi][7] = '一字板'
                # if ztdataapi[ztapi][7][0:5] == '09:30':
                #     ztdataapi[ztapi][7] = '秒板'
                if gnname[zt][0:6] == ztdataapi[ztapi][0]:
                    text_html_data = text_html_data + '<tr>' + \
                                                          '<td width="80" align="left">' + ztdataapi[ztapi][0] + '</td> ' \
                                                          '<td width="80" align="left">' + ztdataapi[ztapi][1] + '</td>'\
                                                          '<td width="80" align="right">' + ztdataapi[ztapi][7] + '</td>'\
                                                          + ztcontinuecolor + \
                                                          '<td align="left">' + ztreason[zt] + '</td>'\
                                                          '<td width="80" align="center">' + str(int(ztdataapi[ztapi][11])) + '</td>'\
                                                    + '</tr>'
    print('data2pic_ths_ztfp_sp done: 已生成html格式的涨停分类复盘图...' )
    return text_html_data + '</table></div>'


# 把所有的内容汇总到html内，然后把html改变成图片
def to_html(date_html, save_path, list_path_pic_to_html):

    # 连接数据库读取文章内容
    client = pymongo.MongoClient(host='localhost', port=27017)
    db = client['openadoor']
    collection = db['wwwWordsEveryday']
    words_everyday_mongodb = collection.find_one({"date":  date_html})
    client.close()

    # 标题栏日期红色显示
    title_date = '【' + date_html[4:] + '】'
    # 标题栏内容
    title_fpan = '今日股市股票行情'
    # 每日一句英语
    words_en = words_everyday_mongodb['content']
    # 每日一句翻译
    words_zh = words_everyday_mongodb['note']
    # 每日一句配图，压缩成和上证日K一样的尺寸
    url_words_everyday = list_path_pic_to_html[0]

    # 上证今日K线，共有30根K线
    url_sh000001_daily = list_path_pic_to_html[1]
    url_ztnum_hist = list_path_pic_to_html[2]
    url_zffb = list_path_pic_to_html[3]
    url_detail_pv = list_path_pic_to_html[4]
    url_hotstock = list_path_pic_to_html[5]
    text_ztfp = list_path_pic_to_html[6]
    f = open(save_path, 'w')
    message = """

    <h2><font color=red>%s</font>%s</h2>
    <p> </br></p>

    <img src=%s></img>
    <p> </br></p>

    <p>%s</br>%s</p>
    <p> </br></p>
    <img src=%s></img>
    <p> </br></p>

    <img src=%s></img>
    <p> </br></p>
    <img src=%s></img>
    <p> </br></p>
    <img src=%s></img>
    <p> </br></p>
    <img src=%s></img>
    <p> </br></p>
    <p> %s</p>
    <p> </br></p>

    """ % (
        title_date,
        title_fpan,
        url_words_everyday,
        words_en,
        words_zh,
        url_sh000001_daily,
        url_ztnum_hist,
        url_zffb,
        url_detail_pv,
        url_hotstock,
        text_ztfp)

    f.write(message)
    f.close()
    print('to_html done: ' + save_path)
    return save_path


# 把最后的网页生成图片，切割成三份存储
def html2pic_final(date_sina, path_heml_final, save_path_html2pic_final):

    driver = webdriver.PhantomJS(
        executable_path=r'C:\ProgramData\Anaconda3\Lib\site-packages\phantomjs-2.1.1-windows\bin\phantomjs.exe')
    driver.set_page_load_timeout(500)
    driver.set_window_size(1680, 1050)
    driver.get('path_heml_final')
    time.sleep(3)
    driver.save_screenshot(save_path_html2pic_final)
    # im = Image.open(save_path_html2pic_final)
    # im = im.crop((342, 515, 1088, 825))
    # im.save(savepath)
    print('html2pic_final done: ' + save_path_html2pic_final)


# 裁剪图片分为三图
def crop_html_picture(date_crop_html_pic, picture_path, save_path_crop_pic):
    im = Image.open(picture_path)
    # 图片的宽度和高度
    img_size = im.size
    # print("图片宽度和高度分别是{}".format(img_size))
    ''' 裁剪：传入一个元组作为参数 元组里的元素分别是：
    （距离图片左边界距离x， 距离图片上边界距离y，
    距离图片左边界距离+裁剪框宽度x+w，距离图片上边界距离+裁剪框高度y+h） '''
    # 截取图片中一块宽和高都是250的
    x = 0
    y = 0
    w = img_size[0]
    h1 = int(img_size[1]/3)
    h2 = int((img_size[1] - h1)/2)
    h3 = img_size[1] - h1 - h2

    region = im.crop((x, y, x + w, y + h1))
    region.save(save_path_crop_pic + date_crop_html_pic + '_h1.png')

    region = im.crop((x, y + h1, x + w, y + h1 + h2))
    region.save(save_path_crop_pic + date_crop_html_pic + '_h2.png')

    region = im.crop((x, y + h1 + h2, x + w, y + h1 + h2 + h3))
    region.save(save_path_crop_pic + date_crop_html_pic + '_h3.png')
    # 截取图片中一块宽是250和高都是300的
    # x = 100
    # y = 100
    # w = 250
    # h = 300
    # region = im.crop((x, y, x+w, y+h))
    # region.save("./crop_test2.jpeg")
    print('crop_html_picture done: ' + save_path_crop_pic + date_crop_html_pic + '_h1.jpeg')
    print('crop_html_picture done: ' + save_path_crop_pic + date_crop_html_pic + '_h2.jpeg')
    print('crop_html_picture done: ' + save_path_crop_pic + date_crop_html_pic + '_h3.jpeg')
    return save_path_crop_pic

if __name__ == '__main__':
    date_str_today = last_trade_date()  # 20180713
    pic_base_path = 'D:\\60_openadoor\\Pictures_FastStoneCapture\\'
    html_save_path = 'D:\\60_openadoor\\BlingBlingMoney\\CheckEveryday' + date_str_today + '.html'
    pic_words_everyday_iciba = pic_base_path + 'iciba_everyday_' + date_str_today + '.jpg'
    kline_sh000001_163_path = 'http://img1.money.126.net/chart/hs/kline/day/30/0000001.png'
    kline_sh000001_save_path = pic_base_path + 'kline_sh000001_' + date_str_today + '.png'
    kline_sh000001_zoom_path = pic_base_path + 'kline_sh000001_zoom_' + date_str_today + '.png'
    pic_ztnum_history_path = pic_base_path + 'ztnum_history_' + date_str_today + '.jpg'
    pic_zdffb_path = pic_base_path + 'zdffb_' + date_str_today + '.jpg'
    detailpv_sh000001_163_path = 'http://img1.money.126.net/chart/hs/time/540x360/0000001.png'
    detailpv_sh000001_save_path = pic_base_path + 'detailpv_sh000001_' + date_str_today + '.png'
    detailpv_sh000001_zoom_path = pic_base_path + 'detailpv_sh000001_zoom_' + date_str_today + '.png'
    pic_hotstock_tgb_path = pic_base_path + 'hotstock_tgb_' + date_str_today + '.png'
    pic2text_json_out_path = 'D:\\60_openadoor\\StockInfo_ZT_THS\\data_json_pic_ths.json'
    pic_wxgzh_path = pic_base_path + 'wxgzh_pic' + date_str_today + '.jpg'
    html_pic_path = pic_base_path + '2018-07-19_193746.png'
    pic_croped_html_pic_path = 'D:\\60_openadoor\\BlingBlingMoney\\wxgzh'
    list_pic_path = [iciba(date_str_today, pic_words_everyday_iciba),  # 0.每日一图
                    crop_163_stock_picture(pic_zoom(download_documents(kline_sh000001_163_path, kline_sh000001_save_path), kline_sh000001_zoom_path, 730), kline_sh000001_zoom_path, 130),  # 1.上证指数日K图
                    pic_ztnum_hist_pyecharts(zt_hum_history('', date_str_today, 1), pic_ztnum_history_path, date_str_today),  # 2. 历史涨跌停数据
                    zdf_distribution(date_str_today, pic_zdffb_path),  # 3.每日涨跌幅分布图片
                    crop_163_stock_picture(pic_zoom(download_documents(detailpv_sh000001_163_path, detailpv_sh000001_save_path), detailpv_sh000001_zoom_path, 800), detailpv_sh000001_zoom_path, 140), # 4. 上证当日分时图
                    hot_tgb(date_str_today, pic_hotstock_tgb_path),  # 5.tgb hot stock
                    data2pic_ths_ztfp_sp(date_str_today, '', acq_pic_path_ths(date_str_today, pic2text_json_out_path), zt_detail_today(date_str_today), zt_detail_yestoday()) ] # 6.ztfp

    html_path_final = to_html(date_str_today, html_save_path, list_pic_path)
    html2pic_final(date_str_today, html_path_final, pic_wxgzh_path)

    # crop_html_picture(date_str_today, html_pic_path, pic_croped_html_pic_path)
    # acq_pic_from_ths(date_str_today, pic2text_json_out_path)
    # download_documents('http://u.thsi.cn/fileupload/data/Input/2018/bf7e1737b217d255de478d30e6f11b1f.png','a.png')
    # pic_recognize('http://u.thsi.cn/fileupload/data/Input/2018/bf7e1737b217d255de478d30e6f11b1f.png')
    # lhb_yuncaijing()
    # http://stock.10jqka.com.cn/jiepan_list/
    # http://yuanchuang.10jqka.com.cn/djpingpan_list/
    # href="http://stock.10jqka.com.cn/[\s\S]*>涨停复盘

    # lhb_yuncaijing()
    # jrj_data()
    # ths_zt_data()
    # excel_generate()
    # www2pic('http://stock.10jqka.com.cn/wenduji/', 'ztgs')
    # zdfb2pic('http://q.10jqka.com.cn/', 'zdfb')


    # sina2pic(date_str)


    # pic_zoom('.\\Pictures_FastStoneCapture\\sinash000001' + date_str + '.gif', 'D:\\60_openadoor\\Pictures_FastStoneCapture\\163sh000001' + date_str + '.gif')


    # hot_tgb(date_str)

    # ocr图片识别
    # '''
    #
    # url = 'http://u.thsi.cn/fileupload/data/Input/2018/947784d451d3b16b529296a873eeae3e.png'
    # json_out_path = 'D:\\60_openadoor\\StockInfo_ZT_THS\\data_json_pic_ths.json'
    # json_pic_data2list(pic_ocr(url, json_out_path , date_str_today), date_str_today)
    # '''


