import httpx
from bs4 import BeautifulSoup

def fetch_code_time():
    return httpx.get(
        "https://gist.githubusercontent.com/0xcaffebabe/8ea5a71947543404d826b1a839b29398/raw"
    )

def fetch_recent_blog():
  text = httpx.get('https://ismy.wang').text
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

def fetch_inprogrss_book_list():
  text = httpx.get('https://github.com/users/0xcaffebabe/projects/4/columns/9526532/cards').text
  soup = BeautifulSoup(text,features="html.parser")
  taskList = soup.select('.js-task-list-container')
  html = ""
  for i in taskList:
    html += "  - " + i.p.text + "\n"
  return html

def fetch_inprogrss_backend_task():
  text = httpx.get('https://github.com/users/0xcaffebabe/projects/1/columns/9443827/cards').text
  soup = BeautifulSoup(text,features="html.parser")
  taskList = soup.select('.js-task-list-container')
  html = ""
  for i in taskList:
    html += "  - " + i.p.text + "\n"
  return html

readmeTemplate = ''.join(open('./template.md','r',encoding="utf8").readlines())

readme = readmeTemplate.replace('${code_time}', fetch_code_time().text)
readme = readme.replace("${recent_blogs}",fetch_recent_blog())
readme = readme.replace("${book_list}",fetch_inprogrss_book_list())
readme = readme.replace("${backend_task}",fetch_inprogrss_backend_task())

print (readme)

open('./README.md','w',encoding="utf8").write(readme)
