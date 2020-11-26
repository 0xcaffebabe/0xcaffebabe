from os import removedirs
import httpx
from bs4 import BeautifulSoup
import datetime
import json

def fetch_code_time():
    return httpGet(
        "https://gist.githubusercontent.com/0xcaffebabe/8ea5a71947543404d826b1a839b29398/raw"
    )

def httpGet(url):
  client = httpx.Client(verify = False)
  try:
    return client.get(url).text
  finally:
    client.close()

def fetch_recent_blog():
  text = httpGet('https://ismy.wang')
  soup = BeautifulSoup(text,features="html.parser")
  postList = soup.select(".post-list li")
  count = 0
  html = ""
  for i in postList:
    if count >= 5:
      break
    blogTitle = i.a.text
    blogLink = i.a['href']
    blogDate = i.select('.post-list-meta')[0].text
    str = """
* <a href="${link}" target="_blank"> ${title} </a> - ${date} \n
    """
    str = str.replace('${link}', blogLink.strip())
    str = str.replace('${title}', blogTitle.strip())
    str = str.replace('${date}', blogDate.strip())
    html += str
    count = count + 1
  return html

def fetch_form_github_cards(url):
  text = httpGet(url)
  soup = BeautifulSoup(text,features="html.parser")
  taskList = soup.select('.js-task-list-container')
  html = ""
  for i in taskList:
    html += "  - " + i.p.text + "\n"
  return html

def fetch_commits():
  text = httpGet('https://api.github.com/users/0xcaffebabe/events/public')
  data = json.loads(text)
  ret = ''
  i = 0
  for item in data:
    if i >=7 : break
    if not 'commits' in item['payload'] : continue
    msg = item['payload']['commits'][0]['message']
    time = item['created_at']
    repo = item['repo']['name']

    if msg == 'update': continue
    
    i = i + 1
    str = """
* <a href="${link}" target="_blank"> ${title} </a> - ${date} \n
    """
    str = str.replace('${link}', 'https://github.com/' + repo)
    str = str.replace('${title}', msg)
    str = str.replace('${date}', time)
    ret += str
  return ret
    

def fetch_inprogrss_book_list():
  return fetch_form_github_cards('https://github.com/users/0xcaffebabe/projects/4/columns/9526532/cards')

def fetch_inprogrss_backend_task():
  return fetch_form_github_cards('https://github.com/users/0xcaffebabe/projects/1/columns/9443827/cards')

def fetch_inprogress_other_task():
  return fetch_form_github_cards('https://github.com/users/0xcaffebabe/projects/3/columns/9526508/cards')

readmeTemplate = ''.join(open('./template.md','r',encoding="utf8").readlines())

readme = readmeTemplate.replace('${code_time}', fetch_code_time())
readme = readme.replace("${recent_blogs}",fetch_recent_blog())
readme = readme.replace("${book_list}",fetch_inprogrss_book_list())
readme = readme.replace("${backend_task}",fetch_inprogrss_backend_task())
readme = readme.replace("${other_task}",fetch_inprogress_other_task())
readme = readme.replace("${gen_time}",datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
readme = readme.replace("${commits}",fetch_commits())

print (readme)

open('./README.md','w',encoding="utf8").write(readme)
