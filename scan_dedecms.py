#coding=utf-8
import requests,json,urllib,sys,os
from bs4 import BeautifulSoup
import socket
import time
import re
'''
IP����������
demo:
��ȡ��202.20.2.1�󶨵������б�
ipre = IPReverse();
ipre.getDomainsList('202.20.2.1')
'''
class IPReverse():
	#��ȡҳ������
	def getPage(self,ip,page):
	    r = requests.get("http://dns.aizhan.com/index.php?r=index/domains&ip=%s&page=%d" % (ip,page))
	    return r

	#��ȡ����ҳ��
	def getMaxPage(self,ip):
	    r = self.getPage(ip,1)
	    json_data = {}
	    json_data = r.json()
	    if json_data == None:
	    	return None
	    maxcount = json_data[u'conut']
	    maxpage = int(int(maxcount)/20) + 1    
	    return maxpage

	#��ȡ�����б�
	def getDomainsList(self,ip):
	    maxpage = self.getMaxPage(ip)
	    if maxpage == None:
	    	return None
	    result = []
	    for x in xrange(1,maxpage+1):
	        r = self.getPage(ip,x)
	        result.append(r.json()[u"domains"])
	    return result
'''
����ɨ����
����һ��IP��   ɨ��ָ���˿�
Demo��
����202.203.208.8/24��ɨ��80�˿�
myscanner = Scanner()
ip_list = myscanner.WebScanner('202.203.208.0','202.203.208.255')
'''
class Scanner():
	#��ָ֤����IP��port�Ƿ񿪷�
	def portScanner(self,ip,port=80):
	    server = (ip,port)
	    sockfd = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	    sockfd.settimeout(0.8)
	    ret = sockfd.connect_ex(server)  #����0��ɹ�
	    print ret
	    if not ret:
	        sockfd.close()
	        print '%s:%s is opened...' % (ip,port)
	        return True
	    else:
	        sockfd.close()
	        return False

	#�ַ���IPת��Ϊ���ֵ�IP
	def ip2num(self,ip):
	    lp = [int(x) for x in ip.split('.')]
	    return lp[0] << 24 | lp[1] << 16 | lp[2] << 8 |lp[3]

	#���ֵ�IPת��Ϊ�ַ���
	def num2ip(self,num):
	    ip = ['','','','']
	    ip[3] = (num & 0xff)
	    ip[2] = (num & 0xff00) >> 8
	    ip[1] = (num & 0xff0000) >> 16
	    ip[0] = (num & 0xff000000) >> 24
	    return '%s.%s.%s.%s' % (ip[0],ip[1],ip[2],ip[3])

	#���������ip��Χ
	def iprange(self,ip1,ip2):
	    num1 = self.ip2num(ip1)
	    num2 = self.ip2num(ip2)
	    tmp = num2 - num1
	    if tmp < 0:
	        return None
	    else:
	        return num1,num2,tmp
	#ɨ�躯��
	def WebScanner(self,startip,endip,port=80):
	    ip_list = []
	    res = ()
	    res = self.iprange(startip,endip)
	    if res < 0:
	        print 'endip must be bigger than startone'
	        return None
	        sys.exit()
	    else:
	        for x in xrange(int(res[2])+1):
	            startipnum = self.ip2num(startip)
	            startipnum = startipnum + x
	            if self.portScanner(self.num2ip(startipnum),port):
	                ip_list.append(self.num2ip(startipnum))
	        return ip_list
'''
���DEDEcms
1.robots.txt
2.�����ҳPowered by ����
'''
class DetectDeDeCMS():
	#���robots.txt
	def detectingRobots(self,url):
		robots_content = ("Disallow: /plus/feedback_js.php" or "Disallow: /plus/mytag_js.php"
		or "Disallow: /plus/rss.php" or "Disallow: /plus/search.php" or "Disallow: /plus/recommend.php"
		or "Disallow: /plus/stow.php" or "Disallow: /plus/count.php")
		robots_url = "%s/%s" % (url,'robots.txt')
		robots_page = requests.get(robots_url)
		if robots_page.status_code != 200:
			return False
		content = robots_page.content
		if content.count(robots_content) != 0:
			return True
		else:
			return False

	#powered by dede ���
	def detectingPoweredBy(self,raw_page):
		soup = BeautifulSoup(raw_page)
		pattern = re.compile(r'DedeCMS.*?')
		try:
			text = soup.a.text
		except Exception, e:
			return False
		if pattern.findall(text) != []:
			return True
		else:
			return False

	def getResult(self,url):
		url = 'http://%s' % url
		try:
			r = requests.get(url)
			raw_page = r.content
		except Exception, e:
			return False
		if (not r) or (r.status_code != 200) or (not raw_page):
			return False
		is_robots_exists = self.detectingRobots(url)
		is_poweredby_exists = self.detectingPoweredBy(raw_page)
		if is_poweredby_exists or is_robots_exists:
			return True
		else:
			return False

class Worker():
	def __init__(self,ip1,ip2):
		self.startip = ip1
		self.endip = ip2
	def doJob(self):
		myscanner = Scanner()
		ipreverse = IPReverse()
		dededetector = DetectDeDeCMS()
		domain_list = []
		tmp_list = []
		dede_res = []
		ip_list = myscanner.WebScanner(self.startip,self.endip)
		for x in ip_list:
			tmp_list = ipreverse.getDomainsList(x)
			if tmp_list == None:
				continue
			domain_list = domain_list + tmp_list
		for x in domain_list:
			if not x:
				continue
			for i in x:
				if dededetector.getResult(i):
				    dede_res.append(i)
				else:
					continue
		return dede_res

if __name__ == '__main__':
	begin = time.time()
	dede_res = []
	myworker = Worker('219.235.5.52','219.235.5.52')
	dede_res = myworker.doJob()
	current = time.time() - begin
	print 'Cost :%s' % str(current)
	if dede_res == []:
		print 'û�м�⵽'
	else:
		print  '�����:' , dede_res

