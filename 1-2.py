import time
import re
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

#chromedriver
options=Options()
options.add_argument('user-agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"')
driver=webdriver.Chrome(options=options)
#データの形を準備。
firstData={
    "店舗名":[],
    "電話番号":[],
    "メールアドレス":[],
    "都道府県":[],
    "市区町村":[],
    "番地":[],
    "建物名":[],
    "URL":[],
    "SSL":[]}
df=pd.DataFrame(firstData)
#50店舗分
itemSum=50
itemNum=1
pageNum=1
#名駅近くの和食の店を指定。
firstUrl="https://r.gnavi.co.jp/area/aream4102/japanese/rs/"
#正規表現の準備。
pattern=r"(東京都|北海道|大阪府|京都府|.{2,3}県)(.+?[^0-9])([0-9].*)$"
pat=re.compile(pattern)

#外側に50店舗までのページごとのwhile文、内側に50店舗までの店舗ごとのfor文。
while itemNum<=itemSum:
     secondUrl=firstUrl+"?p="+str(pageNum)
     driver.get(secondUrl)
     time.sleep(2)
     link_elements= driver.find_elements(By.CLASS_NAME, "style_titleLink__oiHVJ")
     links=[]
     for link_element in link_elements:
         links.append(link_element.get_attribute("href"))
     for link in links:
         driver.get(link)
         time.sleep(2)
         #店舗名と電話番号
         shopName=driver.find_element(By.ID,"info-name").text
         shopPhone=driver.find_element(By.CLASS_NAME,"number").text
         #メールアドレス
         shopMail=""
         
         #住所
         shopAddress = driver.find_element(By.CLASS_NAME, "region").text
         #正規表現の適用。
         matches=pat.match(shopAddress)
         if matches :
             shopPrefecture=matches.group(1)
             shopCity=matches.group(2)
             shopStreet=matches.group(3)
         else:
             shopPrefecture=shopAddress
             shopCity=""
             shopStreet=""
         #localityクラスの有無で分岐。
         try:
             shopBuilding=driver.find_element(By.CLASS_NAME,"locality").text
         except Exception :
             shopBuilding=""
             
         #urlとssl
         shopUrl=""
         shopSsl=""
         try:
            shopUrl_element=driver.find_element(By.CLASS_NAME,"sv-of.double")
         except Exception:
             continue
         shopUrl=shopUrl_element.get_attribute("href")
         shopSsl= "TRUE" if shopUrl.startswith("https") else "FALSE"
         
         #店ひとつ分のデータを追加する。
         newData={
            "店舗名":[shopName],
            "電話番号":[shopPhone],
            "メールアドレス":[shopMail],
            "都道府県":[shopPrefecture],
            "市区町村":[shopCity],
            "番地":[shopStreet],
            "建物名":[shopBuilding],
            "URL":[shopUrl],
            "SSL":[shopSsl]}
         miniDf=pd.DataFrame(newData)
         df=pd.concat([df,miniDf],ignore_index=True)
         #for文末尾で店の数を更新。ここで51になればfor文を抜けて、while文が終了。
         itemNum+=1
         if itemNum>itemSum:
            break
     #while文末尾でページ更新
     pageNum+=1

driver.quit()

#文字化けに気を付けつつcsvに変換。
df.to_csv("1-2.csv",index=False,encoding="utf-8-sig")
