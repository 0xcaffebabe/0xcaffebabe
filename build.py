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

def fetch_leetcode_recent_ac():
    client = httpx.Client(verify = False)
    try:
      resp = client.post(url= 'https://leetcode.cn/graphql/noj-go/', headers={'Content-Type': 'application/json'}, data= '{"query":"    query recentAcSubmissions($userSlug: String!) {  recentACSubmissions(userSlug: $userSlug) {    submissionId    submitTime    question {      title      translatedTitle      titleSlug      questionFrontendId    }  }}    ","variables":{"userSlug":"0xcaffebabe"},"operationName":"recentAcSubmissions"}').text
      data = json.loads(resp)
      ac_list = data['data']['recentACSubmissions']
      ret = ''
      temp = """
  * <a href="${link}" target="_blank"> ${title} </a> - ${date} \n
    """
      ac_list = ac_list[:7]
      for i in ac_list:
        d = datetime.datetime.fromtimestamp(i['submitTime']) + datetime.timedelta(hours=8)
        time = d.strftime("%Y-%m-%d %H:%M:%S")
        ret += temp.replace("${link}", 'https://leetcode.cn/submissions/detail/' + str(i['submissionId']))\
                  .replace("${title}", i['question']['questionFrontendId'] + '.' + i['question']['title'])\
                  .replace("${date}", time)
      return ret
    finally:
      client.close()

def fetch_leetcode_ac_info():
  client = httpx.Client(verify = False)
  try:
    resp = client.post(url= 'https://leetcode.cn/graphql/', headers={'Content-Type': 'application/json'}, data= '{"operationName":"userPublicProfile","variables":{"userSlug":"0xcaffebabe"},"query":"query userPublicProfile($userSlug: String!) { userProfilePublicProfile(userSlug: $userSlug) { username haveFollowed siteRanking profile { userSlug realName userAvatar location contestCount asciiCode __typename }  submissionProgress { totalSubmissions waSubmissions acSubmissions reSubmissions otherSubmissions acTotal questionTotal __typename } __typename } } "}').text
    data = json.loads(resp)
    solved = data['data']['userProfilePublicProfile']['submissionProgress']['acTotal']
    total = data['data']['userProfilePublicProfile']['submissionProgress']['questionTotal']
    ac_rate = data['data']['userProfilePublicProfile']['submissionProgress']['acSubmissions'] / data['data']['userProfilePublicProfile']['submissionProgress']['totalSubmissions']
    return solved, total, round(ac_rate * 100, 2)
  finally:
    client.close()

def generate_leetcode_badge():
  data = fetch_leetcode_ac_info()
  solved = str(data[0]) + '%20/%20' + str(data[1])
  ac_rate = str(data[2]) + '%'
  return '![](${info}) [![leetcode](${solved})](https://leetcode.cn/u/0xcaffebabe/) [![leetcode](${ac})](https://leetcode.cn/u/0xcaffebabe/)'\
    .replace('${info}', 'https://img.shields.io/static/v1?label=LeetCode%20CN&message=0xcaffebabe&color=success')\
    .replace('${solved}', 'https://img.shields.io/static/v1?label=Solved&message='+ solved +'&color=success')\
    .replace('${ac}', 'https://img.shields.io/static/v1?label=Solved&message='+ ac_rate +'&color=success')

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
        time = fetch_commit_datetime(commit['url'])
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
readme = readmeTemplate

readme = readmeTemplate.replace("${recent_blogs}",fetch_recent_blog())
readme = readme.replace("${book_list}",fetch_inprogrss_book_list())
readme = readme.replace("${backend_task}",fetch_inprogrss_backend_task())
readme = readme.replace("${other_task}",fetch_inprogress_other_task())
readme = readme.replace("${commits}",fetch_commits())
readme = readme.replace("${recent_ac}",fetch_leetcode_recent_ac())
readme = readme.replace("${ac_info}",fetch_leetcode_ac_info())

print (readme)

if (readme == open('./README.md','r',encoding="utf8").read()):
  print("与上次生成相同 不写入提交")
else:
  open('./README.md','w',encoding="utf8").write(readme)
