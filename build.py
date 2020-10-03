import httpx
from bs4 import BeautifulSoup

def fetch_code_time():
    return httpx.get(
        "https://gist.githubusercontent.com/0xcaffebabe/8ea5a71947543404d826b1a839b29398/raw"
    )

def fetch_recent_blog():
  text = httpx.get('https://ismy.wang').text
  soup = BeautifulSoup(text)
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

readmeTemplate = """
## Overview

#### 📖 最近博客

<!-- blog starts -->
${recent_blogs}
<!-- blog ends -->

</td>
</tr>
<tr>
<td valign="top" width="50%">

#### 📊 最近一周开发时间

<!-- code_time starts -->

```text
${code_time}
```

<!-- code_time ends -->

</td>

  </tr>
  </table>
"""

readme = readmeTemplate.replace('${code_time}', fetch_code_time().text)
readme = readme.replace("${recent_blogs}",fetch_recent_blog())
print (readme)

open('./README.md','w',encoding="utf8").write(readme)
