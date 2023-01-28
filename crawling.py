import asyncio

async def crawling(keyword, speed):
  import pandas as pd
  if speed == 'normal':
    n_db = naver_crawling(keyword, speed)
    n2_db = naver_crawl(keyword, speed)
    pan_db = pan_crawling(keyword)
    maily_db = maily_crawling(keyword)
    youtube_db = youtube_crawling(keyword)
    dc_db = dc_crawling(keyword)
    brunch_db = brunch_crawl(keyword)
    instiz_db = instiz_crawl(keyword)
    newsletter_db = newsletter(keyword)
    ppo_db = ppompu_crawl(keyword)
    clien_db = clien_crawl(keyword)

    result = await asyncio.gather(
                            n_db, n2_db, pan_db, maily_db,
                            youtube_db, dc_db, brunch_db, instiz_db,
                            newsletter_db, ppo_db, clien_db
    )
    context_db = pd.concat(result)
    return context_db
  elif speed == 'fast':
    n_db = naver_crawling(keyword, speed)
    n2_db = naver_crawl(keyword, speed)
    newsletter_db = newsletter(keyword)
    ppo_db = ppompu_crawl(keyword)

    result = await asyncio.gather(
                            n_db, n2_db, newsletter_db, ppo_db
    )
    context_db = pd.concat(result)
    return context_db

### 재도
async def naver_crawling(keyword, speed):
  import requests
  from bs4 import BeautifulSoup
  import pandas as pd

  n_api_news = f'https://openapi.naver.com/v1/search/news.xml?query={keyword}'
  n_api_web = f'https://openapi.naver.com/v1/search/webkr.xml?query={keyword}'
  n_api_cafe = f'https://openapi.naver.com/v1/search/cafearticle.xml?query={keyword}'
  
  if speed == 'fast':
    naver_api = [n_api_news, n_api_cafe]
  elif speed == 'normal':
    naver_api = [n_api_news, n_api_web, n_api_cafe]

  headers = { 'X-Naver-Client-Id' : "G5yG2v2TKiOu77qmrEeq",
              'X-Naver-Client-Secret' : "8SzLOPImH7"}

  for url in naver_api:
      # start = 1000까지 설정 가능
      # mz세대라는 용어 앞뒤로 적힌 문장들 위주로 사용할 수 있다.
      start = 1
      for st in range(10):
          q = '&display=100&start=' + str(start + st*100)
          response = requests.get(url + q, headers=headers)
          soup = BeautifulSoup(response.content, 'xml')
          des_lst = soup.find_all('description')

          index_ = 1
          api_lst = list()
          for description in des_lst[1:]:
              api_lst.append([url.split('search/')[1].split('?')[0], (start-1)*100 + index_, description.get_text()])
              index_ += 1
          NapiDb = pd.DataFrame(api_lst, columns=['출처', 'index', '내용'])
          start += 1
  return NapiDb

async def pan_crawling(keyword):
  import requests
  from bs4 import BeautifulSoup
  import pandas as pd

  pan = f'https://pann.nate.com/search/talk?q={keyword}&page='

  pan_db = pan_df = pd.DataFrame(columns=['출처', 'index', '내용'])
  index_ = 1
  for page in range(1, 19):
      response = requests.get(pan + str(page))
      soup = BeautifulSoup(response.content, 'html.parser')

      pan_datas = soup.select('ul.s_list > li > div.txt')
      pan_lst = list()
      for pan_data in pan_datas:
          pan_data = pan_data.get_text().replace('\n', '')
          pan_lst.append(['pan', index_, pan_data])
          index_ += 1
      pan_df = pd.DataFrame(pan_lst, columns=['출처', 'index', '내용'])
      pan_db = pd.concat([pan_db, pan_df])
  return pan_db

async def maily_crawling(keyword):
  import requests
  from bs4 import BeautifulSoup
  import pandas as pd

  mail_ = f'https://maily.so/?keyword={keyword}'

  mail_db = mail_df = pd.DataFrame(columns=['출처', 'index', '내용'])

  response = requests.get(mail_)
  soup = BeautifulSoup(response.content, 'html.parser')

  page_lst = list()
  href_lst = soup.find_all('div', class_='block')
  for page_url in href_lst:
      page_lst.append(page_url.find('a', class_='w-full').attrs['href'])

  index_ = 1
  for page in page_lst:
      response = requests.get(page)
      soup = BeautifulSoup(response.content, 'html.parser')

      mail_datas = soup.find_all('p')
      mail_lst = list()
      for p in mail_datas:
          mail_data = p.get_text().replace('\n', '')
          if keyword in mail_data or keyword.upper() in mail_data or keyword.lower() in mail_data:
              mail_lst.append(['maily', index_, mail_data])
              index_ += 1
      mail_df = pd.DataFrame(mail_lst, columns=['출처', 'index', '내용'])
      mail_db = pd.concat([mail_db, mail_df])

  return mail_db

async def youtube_crawling(keyword):
  import requests
  import pandas as pd

  url = f'https://www.googleapis.com/youtube/v3/search?q={keyword}&maxResults=50'

  headers = {'key' : 'AIzaSyAPxogTdMNujoE4KbQCBTL4j693FKTWA5c'}
  response = requests.get(url, headers)

  data = response.json()

  videoId_lst = list()
  for item in data['items']:
    try:
      videoId_lst.append(item['id']['videoId'])
    except:
      pass

  url1 = 'https://www.googleapis.com/youtube/v3/commentThreads?maxResults=100&part=id,replies,snippet&videoId='

  comment_lst = list()
  for videoId in videoId_lst:
    url = url1 + videoId
    headers = {'key' : 'AIzaSyAPxogTdMNujoE4KbQCBTL4j693FKTWA5c'}
    response = requests.get(url, headers)

    data = response.json()
    try:
      for item in data['items']:
        comment = item['snippet']['topLevelComment']['snippet']['textOriginal']
        if keyword in comment:
          comment_lst.append(comment.replace('\n', ''))
    except:
      pass
  
  youtube_df = pd.DataFrame({'출처':'youtube_comment', 'index':[ i+1 for i in range(len(comment_lst))], '내용': comment_lst})
  return youtube_df

async def dc_crawling(keyword):

  import requests
  from bs4 import BeautifulSoup
  import pandas as pd

  i = 1
  data2_lst = list()
  all_data_lst = list()
  while True:
    dcurl = f'https://search.dcinside.com/post/p/{i}/q/{keyword}'
    response = requests.get(dcurl)
    
    soup = BeautifulSoup(response.content, 'html.parser')
    li_tag = soup.select("li")
    data_lst = list()
    for li in li_tag:
      try:
        data = li.select("p")[0].get_text()
        if keyword in data:
          data_lst.append(data)
      except:
        pass

    if data2_lst == data_lst:
      break
    else:
      data2_lst = data_lst
    
    all_data_lst.extend(data_lst)
    i += 1

  dc_db = pd.DataFrame({'출처':'dc', 'index': [i+1 for i in range(len(all_data_lst))],
                        '내용' :all_data_lst})
  return dc_db


### 세은
async def naver_crawl(keyword, speed):
  import pandas as pd
  import requests
  import re
  
  client_id = "RvshcKHg5cr5eHrhcUdD"
  client_secret = "jYR3TYHwlR"

  blog_api = "https://openapi.naver.com/v1/search/blog?query=" 
  book_api = 'https://openapi.naver.com/v1/search/book.json?query='
  kin_api = 'https://openapi.naver.com/v1/search/kin.json?query='

  if speed == 'fast':
    naver_apis = [blog_api, kin_api]
  elif speed == 'normal':
    naver_apis = [blog_api, book_api, kin_api]

  
  naver_DB = pd.DataFrame(columns=['출처', 'index', '내용'])

  for link in naver_apis:
      content = [] ; index = [] ; links = [] ; in_num = 1
      for num in range (1,901,100):
          naver_open_api = link + str(keyword)+'&sort=sim&display=100&start='+str(num)
          header_params = {'X-Naver-Client-Id':client_id, "X-Naver-Client-Secret":client_secret} 
          res = requests.get(naver_open_api, headers= header_params)
          if res.status_code==200:
              data = res.json()
              for item in data['items']:
                  text = item['description']
                  ftext = re.sub('(<([^>]+)>)',' ',text)
                  if ftext not in content:
                      content.append(ftext)
                      index.append(in_num) 
                      in_num +=1
                      links.append(link.split('search/')[1].split('?')[0])
          else:
              continue
      naver_df = pd.DataFrame({'출처':links,'index': index, '내용':content})
      naver_DB = pd.concat([naver_DB,naver_df])

  return naver_DB

async def brunch_crawl(keyword):
  from selenium import webdriver
  from selenium.webdriver.common.keys import Keys
  from selenium.webdriver.common.by import By
  from selenium.webdriver.chrome.service import Service as ChromeService
  from webdriver_manager.chrome import ChromeDriverManager

  import pandas as pd
  import time

  def scroll():
    last_height = driver.execute_script('return document.documentElement.scrollHeight')
    cnt=1
    while cnt<2000:
      cnt+=1
      driver.execute_script('window.scrollTo(0,document.documentElement.scrollHeight);')
      time.sleep(3)
      new_height = driver.execute_script('return document.documentElement.scrollHeight')
      if new_height == last_height:
        break
      else:
        last_height = new_height

  content =[] ; index = [] ; in_num = 1

  headlessoptions = webdriver.ChromeOptions()
  headlessoptions.add_argument('--headless')

  driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), chrome_options = headlessoptions)

  driver.get("https://brunch.co.kr/search")
  search_bar = driver.find_element(By.XPATH,'//*[@id="txt_search"]')
  search_bar.send_keys(keyword)
  search_bar.send_keys(Keys.RETURN)

  scroll()
  datas = driver.find_elements(By.XPATH,'//*[@id="resultArticle"]/div/div[1]/div[2]/ul//a/div[1]/div/span')
  for data in datas:
    text = data.text
    content.append(text)
    index.append(in_num)
    in_num+=1

  brunch_DB = pd.DataFrame({'출처':'brunch','index': index, '내용':content})
  driver.close()

  return brunch_DB

async def instiz_crawl(keyword):
  from selenium import webdriver
  from selenium.webdriver.common.by import By
  from selenium.webdriver.chrome.service import Service as ChromeService
  from webdriver_manager.chrome import ChromeDriverManager

  import pandas as pd
  import time
  content = [] ; index = [] ; in_num=1

  headlessoptions = webdriver.ChromeOptions()
  headlessoptions.add_argument('--headless')
  driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), chrome_options = headlessoptions)
  

  for i in range(1,11):
    driver.get(f"https://www.instiz.net/popup_search.htm#gsc.tab=0&gsc.q={keyword}.page="+str(i))
    time.sleep(3)
    search_bar = driver.find_elements(By.XPATH,'//*[@id="___gcse_0"]/div/div/div/div[6]/div[2]/div[2]/div/div[1]//div[1]/div[3]/div/div[2]')
    for data in search_bar:
        text = data.text
        index.append(in_num)
        in_num+=1
        content.append(text)

  instiz_DB = pd.DataFrame({'출처':'instiz','index': index, '내용':content})
  return instiz_DB

async def newsletter(keyword):
  import requests
  from bs4 import BeautifulSoup
  import pandas as pd
  mobbi_df = pd.DataFrame(columns=['출처', 'index', '내용'])
  content = [] ; index = []; in_num=1 ; links = []
  for num in range(1,8):
    if num==1:
      res = requests.get('https://www.mobiinside.co.kr/?s='+keyword)
    else:
      res = requests.get('https://www.mobiinside.co.kr/page/'+str(num)+'/?s='+keyword)
    soup = BeautifulSoup(res.content,'html.parser')

    data = soup.select('#td-outer-wrap > div.td-main-content-wrap.td-container-wrap > div > div.td-pb-row > div.td-pb-span8.td-main-content > div  div.item-details > div.td-excerpt > span')
    for item in data:
      content.append(item.get_text())
      index.append(in_num)
      in_num +=1
      links.append('mobiinside')
    
  mobbi_df = pd.DataFrame({'출처':links,'index': index, '내용':content})
  return mobbi_df

async def ppompu_crawl(keyword):
  import requests
  from bs4 import BeautifulSoup
  import pandas as pd

  ppomppu_df = pd.DataFrame(columns=['출처', 'index', '내용'])
  content = [] ; index = []; in_num=1 ; links = []
  for num in range(1,33):
    res = requests.get('https://www.ppomppu.co.kr/search_bbs.php?search_type=sub_memo&page_no='+str(num)+'&keyword='+keyword+'&page_size=20&bbs_id=&order_type=date&bbs_cate=2')
    soup = BeautifulSoup(res.content,'html.parser')

    data = soup.select('body > div > div.contents > div.container > div > form > div div > p:nth-child(2) > a')
    for item in data:
      write = item.get_text()
      if keyword in write:
        content.append(item.get_text().replace('\n', ''))
        index.append(in_num)
        in_num +=1
        links.append('ppomppu')
        
  ppomppu_df = pd.DataFrame({'출처':links,'index': index, '내용':content})
  return ppomppu_df

async def clien_crawl(keyword):
  import requests
  from bs4 import BeautifulSoup
  import pandas as pd

  clien_df = pd.DataFrame(columns=['출처', 'index', '내용'])
  content = [] ; index = []; in_num=1 ; links = [] 
  for num in range(0,44):
    res = requests.get('https://www.clien.net/service/search?q='+keyword+'&sort=recency&p='+str(num)+'&boardCd=&isBoard=false')
    soup = BeautifulSoup(res.content,'html.parser')

    data = soup.select('#div_content > div.contents_jirum div.list_title.oneline > div > span')
    for item in data:
      write = item.get_text()
      if keyword in write:
        content.append(item.get_text().replace('\n', ''))
        index.append(in_num)
        in_num +=1
        links.append('clien')
        
  clien_df = pd.DataFrame({'출처':links,'index': index, '내용':content})
  return clien_df