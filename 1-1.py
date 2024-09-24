import requests
import re
import time
import pandas as pd
from bs4 import BeautifulSoup

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
#50店舗分のデータを収集。
itemSum=50
#macOSでchromeブラウザを使用。
userAgent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
#名駅近くの和食の店を指定。
firstUrl="https://r.gnavi.co.jp/area/aream4102/japanese/rs/"

#while文(itemNum<=itemSum)とfor文(url in urls)で実装。pageNumはfor文外側、itemNumはfor文内側で更新。
#UserAgentをリクエストヘッダーに設定する準備。
headers={"User-Agent": userAgent}
itemNum=1
pageNum=1
while itemNum<=itemSum :
  secondUrl=firstUrl+"?p="+str(pageNum)
  time.sleep(3)
  response=requests.get(secondUrl,headers=headers)
  fixedResponse=BeautifulSoup(response.content,"html.parser")
  urls=fixedResponse.find_all("a", class_="style_titleLink__oiHVJ")
  #各店舗のURLから、それぞれの店舗情報を取得。
  for url in urls :
    URL=url["href"]
    time.sleep(3)
    response2=requests.get(URL,headers=headers)
    fixedResponse2=BeautifulSoup(response2.content,"html.parser")
    #店舗名、電話番号を取得。
    shopName=fixedResponse2.find("p",id="info-name").text
    shopPhone=fixedResponse2.find("span",class_="number").text
    #URL、SSL、メールアドレスを取得。
    #1-2ではURLとSSLは埋められる。
    #メールアドレスは1-1、1-2ともに存在しない。あればHTMLを読んで見つけたタグやクラスを引数にfindメソッドを用いて取得。
    shopUrl=""
    shopSsl=""
    shopMail=""
     #住所を取得して分割。
    shopAddress=fixedResponse2.find("span",class_="region").text
     #正規表現の適用。
    pattern=r"(東京都|北海道|大阪府|京都府|.{2,3}県)(.+?[^0-9])([0-9].*)$"
    pat=re.compile(pattern)
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
      shopBuilding=fixedResponse2.find("span",class_="locality").text
    except Exception :
      shopBuilding=""
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

#文字化けに気を付けつつcsvに変換。
df.to_csv("1-1.csv",index=False,encoding="utf-8-sig")
