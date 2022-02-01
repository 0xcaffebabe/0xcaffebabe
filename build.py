from os import removedirs
import httpx
from bs4 import BeautifulSoup
import datetime
import json
import datetime
import os

if ('LOCAL_MACHINE' in os.environ and os.environ['LOCAL_MACHINE'] == 'LOCAL_MACHINE') :
  proxy = 'http://127.0.0.1:54089'
  os.environ['http_proxy'] = proxy 
  os.environ['HTTP_PROXY'] = proxy
  os.environ['https_proxy'] = proxy
  os.environ['HTTPS_PROXY'] = proxy


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
    if count >= 8:
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
  recentCommits = []
  for item in data:
    if item['type'] != 'PushEvent' : continue
    commitList = item['payload']['commits']
    if len(commitList) == 1:
      msg = commitList[0]['message']
      if msg == 'update' or 'Deploy to GitHub pages' in msg or 'Merge pull request' in msg or 'Merge branch' in msg or 'Update dependency' in msg: continue
      time = fetch_commit_datetime(commitList[0]['url'])
      repo = item['repo']['name']
      sha = commitList[0]['sha']
      recentCommits.append({'msg': msg, 'time': time, 'repo': repo, 'sha': sha})
    else:
      for commit in commitList:
        msg = commit['message']
        if msg == 'update' or 'Deploy to GitHub pages' in msg or 'Merge pull request' in msg or 'Merge branch' in msg or 'Update dependency' in msg: break
        if (len(msg) >= 32):
          msg = msg[:32] + "..."
        time = fetch_commit_datetime(commitList[0]['url'])
        repo = item['repo']['name']
        sha = commit['sha']
        recentCommits.append({'msg': msg, 'time': time, 'repo': repo, 'sha': sha})

  for item in recentCommits:
    if i >= 6 : break
    str = """
  * <a href="${link}" target="_blank"> ${title} </a> - ${date} \n
    """

    UTC_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
    utc_time = datetime.datetime.strptime(item['time'], UTC_FORMAT)
    item['time'] = utc_time + datetime.timedelta(hours=8)

    str = str.replace('${link}', 'https://github.com/' + item['repo'] + '/commit/' + item['sha'])
    str = str.replace('${title}', item['msg'])
    str = str.replace('${date}', item['time'].strftime('%Y/%m/%d %H:%M:%S'))
    ret += str
    i += 1
  return ret
    

def fetch_inprogrss_book_list():
  return fetch_form_github_cards('https://github.com/users/0xcaffebabe/projects/4/columns/9526532/cards')

def fetch_inprogrss_backend_task():
  return fetch_form_github_cards('https://github.com/users/0xcaffebabe/projects/1/columns/9443827/cards')

def fetch_inprogress_other_task():
  return fetch_form_github_cards('https://github.com/users/0xcaffebabe/projects/3/columns/9526508/cards')

def fetch_commit_datetime(commit_url):
  text = httpGet(commit_url)
  data = json.loads(text)
  return data['commit']['committer']['date']

readmeTemplate = ''.join(open('./template.md','r',encoding="utf8").readlines())

# readme = readmeTemplate.replace('${code_time}', fetch_code_time())
readme = readmeTemplate.replace("${recent_blogs}",fetch_recent_blog())
readme = readme.replace("${book_list}",fetch_inprogrss_book_list())
readme = readme.replace("${backend_task}",fetch_inprogrss_backend_task())
readme = readme.replace("${other_task}",fetch_inprogress_other_task())
readme = readme.replace("${gen_time}",datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
readme = readme.replace("${commits}",fetch_commits())

print (readme)

if (readme == open('./README.md','r',encoding="utf8").read()):
  print("与上次生成相同 不写入提交")
else:
  open('./README.md','w',encoding="utf8").write(readme)
