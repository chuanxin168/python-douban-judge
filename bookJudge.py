import requests
import csv
from bs4 import BeautifulSoup
import time


# 输入要爬取的书籍
bookName = input("请输入您感兴趣的书籍：")
outData = []
#bookName = "练习的心态"
url = 'https://book.douban.com/j/subject_suggest?q=' + bookName

#模拟浏览器标识：
header = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/536.39 (KHTML, like Gecko) Chrome/94.0.4606.60 Safari/537.38"
}
page = requests.get(url, headers=header)
page.encoding = "utf-8"
pageContent = page.json()
print("---侵入地址：",url)

realContent = {}
# 判断如果是list格式
if isinstance(pageContent, list):
    # 拿第一个，是最多评论的书籍
    realContent = pageContent[0]
# print(realContent)
titleBook = realContent['title']
urlBook = realContent['url'] + "/reviews?start=20"

print("---书评列表：",urlBook)

# 获取子页面地址的内容
childPage = requests.get(urlBook, headers=header)
childPage.encoding = "utf-8"
childContent = childPage.text

soup = BeautifulSoup(childContent, "html.parser")
pageAllPj = soup.find("div", class_="review-list").find_all("div", class_="main review-item")

page.close()
childPage.close()
for onePj in pageAllPj:
    # print("----------------------------------")
    try:
        level_title = onePj.find("span", class_="main-title-rating").attrs['title']
    except Exception as e:
        level_title = ""
    row = {
        "pj_id": onePj.get("id"),
        "user_name": onePj.find("a", class_="name").string,
        "pj_level": level_title,
        "pj_date": onePj.find("span", class_="main-meta").string,
        "pj_real_url": "https://book.douban.com/review/" + onePj.get("id") + "/",
        "pj_content": ""
    }
    outData.append(row)

# 循环调详情接口，拿到具体的评价内容
csvData = [
    [
        "评价ID",
        "评价人",
        "推荐情况",
        "评价日期",
        "评价详情地址",
        "评价内容"
    ]
]
try:
    for item in outData:
        print("----------正在侵入详评---")
        pj_content_url = item['pj_real_url']
        itemObj = requests.get(pj_content_url, headers=header)
        itemObj.encoding = "utf-8"
        item_content = itemObj.text
        itemObj.close()
        itemSoup = BeautifulSoup(item_content, "html.parser")
        lastContent = itemSoup.find("div", class_="review-content clearfix").contents
        myContent = ''
        # 将获取到的review-content clearfix的list转成string
        for realLastContent in lastContent:
            myContent += str(realLastContent)

        raw = [
            item['pj_id'],
            item['user_name'],
            item['pj_level'],
            item['pj_date'],
            item['pj_real_url'],
            myContent
        ]
        csvData.append(raw)
        # 休眠1s，防止反爬
        time.sleep(2)
        # item['pj_content'] = itemSoup.find("div", class_="review-content clearfix").find("p").string
except Exception as e:
    print("中途可能ip被发现了……",e)




f_csv = open("《" + bookName + "》--前20书评" + ".csv", mode="w", newline='', encoding='utf-8-sig')
csvWriter = csv.writer(f_csv)
csvWriter.writerows(csvData)
f_csv.close()
print(csvData)
