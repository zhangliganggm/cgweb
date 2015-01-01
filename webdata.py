# -*- coding=utf-8 -*-
import urllib2
import re

def get_image_from_cgtalk(page=1):

    url="http://forums.cgsociety.org/forumdisplay.php?f=121&page={page}".format(page=page)
    #url = "http://forums.cgsociety.org/showthread.php?f=121&t=1236306"
    req_header = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
                  #'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                 # 'Accept-Encoding': 'gzip,deflate',
                  #'Accept-Language': 'zh-CN,zh;q=0.8'

    }

    req_timeout = 60
    req = urllib2.Request(url, None, req_header)

    resp = urllib2.urlopen(req, None, req_timeout)
    html = resp.read()
    rex = r'<a href="showthread.php\?f=121&s=\S+amp;t=\d+"><img src="(\S+)" width="(\d+)" height="(\d+)" border="\d+" /></a>[\S\d\s\w]+?;t=\d+">([\s\S\d\w]+?)\)</a>'
    found = re.findall(rex, html)
    return found

    # #print [html]
    

#html = open("d:\\scripts\\cg_hub\\test.html","rb").read()


if __name__ == '__main__':
	for b in range(35):
		for a in get_image_from_cgtalk(b):
			if '22416_1203406916_small.jpg' in a[0]:
				print a[0], a, b





