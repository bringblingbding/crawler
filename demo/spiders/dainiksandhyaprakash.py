
# 此文件包含的头文件不要修改
import requests
import scrapy
from demo.util import Util
from demo.items import DemoItem
from bs4 import BeautifulSoup
from scrapy.http import Request, Response
import re
import time
from datetime import datetime

#将爬虫类名和name字段改成对应的网站名
class dainiksandhyaprakashSpider(scrapy.Spider):
    name = 'dainiksandhyaprakash'
    website_id = 999 # 网站的id(必填)
    language_id = 1930  # 所用语言的id
    start_urls = ['http://dainiksandhyaprakash.com/']
    sql = {  # sql配置
        'host': '192.168.235.162',
        'user': 'dg_lhl',
        'password': 'dg_lhl',
        'db': 'dg_test'
    }


    # 这是类初始化函数，用来传时间戳参数
    def __init__(self, time=None, *args, **kwargs):
        super(dainiksandhyaprakashSpider, self).__init__(*args, **kwargs) # 将这行的DemoSpider改成本类的名称
        self.time = time


    def parse(self, response):
        soup = BeautifulSoup(response.text, features="lxml")
        category_hrefList = []
        # category_nameList = []
        categories = soup.select_one('ul#menu-main-1').select('li a') if soup.select_one('ul#menu-main-1').select('li a') else None
        categories.pop(0)
        for category in categories:
            category_hrefList.append(category.get('href'))
            # category_nameList.append(category.text.replace('\n', ''))

        for category in category_hrefList:
            yield scrapy.Request(category, callback=self.parse_category)

    def parse_category(self, response):
        soup = BeautifulSoup(response.text, features="lxml")

        articles = soup.select('div.td-block-span6 div h3 a') if soup.select('div.td-block-span6 div h3 a') else None
        article_hrefs = []
        if articles:
            for article in articles:
                article_hrefs.append(article.get('href'))
            for detail_url in article_hrefs:
                yield Request(detail_url, callback=self.parse_detail)



            # check_soup = BeautifulSoup(requests.get(article_hrefs[-1]).content)     #不加content会出错，原因是因为这里的wb_data是requests对象，无法用BeautifulSoup解析
            temp_time = soup.select('div.td-ss-main-content span.td-post-date')[-1].text if soup.select('div.td-ss-main-content span.td-post-date')[-1].text else None
            adjusted_time = time_adjustment(temp_time)
            if self.time == None or Util.format_time3(adjusted_time) >= int(self.time):
                if soup.find('div', class_="page-nav td-pb-padding-side").select_one('i.td-icon-menu-right'):
                    yield Request(soup.find('div', class_="page-nav td-pb-padding-side").select('a')[-1].get('href'), callback=self.parse_category)
                else:
                    self.logger.info("最后一页了")
            else:
                self.logger.info("时间截止")
        else:
            self.logger.info("标签页内容为空")

    def parse_detail(self, response):
        item = DemoItem()
        soup = BeautifulSoup(response.text, features='lxml')
        temp_time = soup.select_one('div.meta-info span.td-post-date').text if soup.select_one('div.meta-info span.td-post-date').text else None
        item['pub_time'] = time_adjustment(temp_time)
        image_list = []
        imgs = soup.find('div', class_="td-post-content td-pb-padding-side").select_one('div.td-post-featured-image').select('img') if soup.find('div', class_="td-post-content td-pb-padding-side").select_one('div.td-post-featured-image').select('img') else None
        if imgs:
            for img in imgs:
                image_list.append(img.get('src'))
            item['images'] = image_list
        p_list = []
        all_p = soup.find('div', class_="td-post-content td-pb-padding-side").select('p') if soup.find('div', class_="td-post-content td-pb-padding-side").select('p') else None
        for paragraph in all_p:
            p_list.append(paragraph.text)
        body = '\n'.join(p_list)
        item['abstract'] = p_list[0]
        item['body'] = body
        item['category1'] = soup.select_one('li.entry-category a').text if soup.select_one('li.entry-category a').text else None

        item['title'] = soup.select_one('h1.entry-title').text if soup.select_one('h1.entry-title').text else None
        yield item



def time_adjustment(input_time):
    get_year = input_time.split(", ")
    get_month_day = get_year[0].split(" ")

    if get_month_day[0] == "January":
        month = "01"
    elif get_month_day[0] == "February":
        month = "02"
    elif get_month_day[0] == "March":
        month = "03"
    elif get_month_day[0] == "April":
        month = "04"
    elif get_month_day[0] == "May":
        month = "05"
    elif get_month_day[0] == "June":
        month = "06"
    elif get_month_day[0] == "July":
        month = "07"
    elif get_month_day[0] == "August":
        month = "08"
    elif get_month_day[0] == "September":
        month = "09"
    elif get_month_day[0] == "October":
        month = "10"
    elif get_month_day[0] == "November":
        month = "11"
    elif get_month_day[0] == "December":
        month = "12"
    else:
        month = "None"

    if int(get_month_day[1]) < 10:
        day = "0" + get_month_day[1]
    else:
        day = get_month_day[1]

    return "%s-%s-%s" % (get_year[1], month, day) + " 00:00:00"