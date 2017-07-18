#-*- coding: utf-8 - *-
#!/usr/local/bin/python3

'''
author: rottens
desc  : fang88
'''

from sys import argv
import requests
from lxml import etree
from selenium import webdriver
from time import time, sleep
import json


#ajax请求,返回抓取到的数据
def ajax_post(result):
	# Ajax请求参数list
	data = {
		'result': result,
	}
	url = 'http://www.fang88.com/api/v1_1/postRottensData'
	try:
		response = requests.post(url, data=json.dumps(data))
		if response.status_code == 200:
			return response.text
		return None
	except RequestException:
		print('接口请求出错')
		return None

#获取分页的数据
def get_otherpage(page, facetParams, pageState, headers, results):
	#第一个接口
	url = 'https://cn.lennar.com/Services/REST/Facets.svc/GetFacetResults'
	pageState['pn'] = page
	payload = json.dumps({'searchState':facetParams, 'pageState': pageState})
	response = requests.request("POST", url, data=payload, headers=headers)

	#第二个接口
	url = "https://cn.lennar.com/Services/Rest/SearchMethods.svc/GetCommunityDetails"
	pageState.update({"pt":"C","ic":19,"ss":0,"attr":"No    ne","ius":False})
	payload = json.dumps({'facetResults': response.json()['fr'], 'pageState':pageState})
	response = requests.request("POST", url, data=payload, headers=headers)
	
	#保存数据
	for item in response.json():
		name = item['cnm']
		if item['mcm']:
			name += item['mcm']
		results.append(name)
		#print(name)

#获取首页的数据
def crawl_url(url):
	results = []
	driver = webdriver.PhantomJS(executable_path='/Users/apple/Downloads/phantomjs-2.1.1-macosx/bin/phantomjs')
	driver.get(url)
	selector = etree.HTML(driver.page_source.encode('utf-8'))
	items = selector.xpath('//div[@class="comm-item clearfix"]')
	for item in items:
		temp = item.xpath('./h1/a/text()')
		name = temp[0] if len(temp) > 0 else ''
		temp = item.xpath('./h2/a/text()')
		name = name + ' ' + (temp[0] if len(temp) > 0 else '')
		#print(name)
		results.append(name)
	
	facetParams = driver.execute_script("return facetContextJSON.params")
	pageState = driver.execute_script("return pageState")
	headers = {
		'origin': "https://cn.lennar.com",
		'user-agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36",
		'content-type': "application/json; charset=UTF-8",
		'accept': "application/json, text/javascript, */*; q=0.01",
		'referer': url,
		'accept-encoding': "gzip, deflate, br",
		'accept-language': "zh-CN,zh;q=0.8,en;q=0.6",
		'cookie': "BHISession=sid=b5ca8bf7-093f-4407-98e2-036391808fd4; ASP.NET_SessionId=yq4f42cveqhlvwh45jsaks12; sdsat_lennar_refdom=none (direct); _hjIncludedInSample=1; rl_visitor_history=7049adbb-7f08-463b-bdd3-f1039659f9f6; optimizelyEndUserId=oeu1500299531522r0.13042656023112675; optimizelySegments=%7B%222330241343%22%3A%22direct%22%2C%222351440127%22%3A%22gc%22%2C%222356570031%22%3A%22false%22%2C%222385820548%22%3A%22none%22%2C%224934141097%22%3A%22true%22%7D; optimizelyBuckets=%7B%7D; _uetsid=_uet24fa0388; DLUserProfile=c9015001-f82d-4bc3-bc80-33452fc073dd; sdsat_lennar_campaign=no campaign name; _ga=GA1.2.397504118.1500246126; _gid=GA1.2.1312573258.1500246126; icxid=1500246287565-1880807202851972; icxid=1500246287565-1880807202851972; 1=1; visitor_id294192=23738911; visitor_id294192-hash=b89f2855140d169e7eb51727218ab1e302acefd51d8d8edc4ea28e56a42bdfc747400469c8ae836b5b64cc4d0de1671da7b14fa6; caoPopInMode=max"
	}
	sleep(5)	
	#通过xpath获取页数
	pagenum = selector.xpath('//div[@class="sptop"]//span[@class="spnPager"]/text()')
	if pagenum:
		for page in range(2, int(pagenum[0].split(':')[-1].strip())+1):		
			get_otherpage(page, facetParams, pageState, headers, results)
	
	driver.quit()
	
	print(results)
	#上传抓取结果，需要配置url与接口参数
	#ajax_post(results)

def run(url):
	crawl_url(url)

if __name__ == '__main__':
	if len(argv) != 2:
		print('参数格式错误')
	else:
		run(argv[1])
