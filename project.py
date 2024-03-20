import requests
from bs4 import BeautifulSoup
from flask import Flask
import json
import re
import math

def backend(page_id): 
    flag=0
    try:
        url = f"https://www.ceneo.pl/{page_id}/opinii-1"
        res=requests.get(url)
        soup = BeautifulSoup(res.content, 'html.parser')
        count=(soup.find("div",class_="score-extend__review")).text
    except Exception as e:
        print("No such page or no comments to extract")
        flag=1
    if flag==1:
        return False
    reviews={}
    author_names=[]
    ratings=[]
    likes={}
    review_dict={}
    comment_date={}
    comments={}
    date={}
    trust={}
    publish_arr=[]
    usage_arr=[]
    def find_review(id,page,dif,amount_of_comment,recommend,advantages):
        url = f"https://www.ceneo.pl/{id}/opinie-{page}"
        res=  requests.get(url)
        print(url)
        soup =  BeautifulSoup(res.content, 'html.parser')
        post = soup.find('div', class_= 'js_product-reviews js_reviews-hook js_product-reviews-container')  
        i=0
        len_comment=0
        while i<=9+amount_of_comment-dif:
            post_date_find(post,i,dif,page)
            comment_find(post,i,dif,comment_date)
            counter=text_find(post,i,id_find(post,i,amount_of_comment),amount_of_comment,len_comment)
            if counter=="comment":
                amount_of_comment+=1
            likes_find(post,i,dif)
            advantage_find(post,i,amount_of_comment,advantages)
            recommend_find(post,i,amount_of_comment,recommend)    
            trust_find(post,i,dif,amount_of_comment)
            rating_find(post,i,dif)
            i+=1
    def advantage_find(post,i,amount_of_comments,advantages):
        zalety=[]
        wady=[]
        users=post.find_all("div",class_="user-post user-post__card js_product-review")[i-amount_of_comments]
        for columns in users.find_all("div",class_="review-feature__col"):
            if columns.find("div",class_="review-feature__title review-feature__title--positives") is not None:
                for  label in columns.find_all("div",class_="review-feature__item"):
                    zalety.append(label.text)
            elif columns.find("div",class_="review-feature__title review-feature__title--negatives") is not None:
                for  label in columns.find_all("div",class_="review-feature__item"):
                    wady.append(label.text)
        advantages[users["data-entry-id"]]={"Advantages":zalety,"Disadvantages":wady}
    def recommend_find(post,i,amount_of_comments,recommend):
        users=post.find_all("div",class_="user-post user-post__card js_product-review")[i-amount_of_comments]
        recommend[users["data-entry-id"]]=[users.find("span",class_="user-post__author-recomendation").text if users.find("span",class_="user-post__author-recomendation") is not None else " "]
    def id_find(post,i,amount_of_comments):
        return [item["data-entry-id"] for item in post.find_all("div",class_="user-post user-post__card js_product-review") if "data-entry-id" in item.attrs][i-amount_of_comments]
    def comment_find(post,i,dif,comment_date):
        if i<=9-dif:
            comment_arr=[]
            author_Comment=[]
            class_text=""
            if i==0:
                comment_id=(re.split("-",((post.findChildren("div",class_="js_product-review-comments js_product-review-hook js_product-review-comments-list"))[i])["id"])[3])
            else:
                comment_id=(re.split("-",((post.findChildren("div",class_="js_product-review-comments js_product-review-hook js_product-review-comments-list hidden"))[i-1])["id"])[3])
                class_text=" hidden"
            if post.findChildren("div",class_=f"js_product-review-comments js_product-review-hook js_product-review-comments-list{class_text}")[i if i==0 else i-1].text is not None:
                for comment_text in post.findChildren("div",class_=f"js_product-review-comments js_product-review-hook js_product-review-comments-list{class_text}")[i if i==0 else i-1].findChildren("div",class_="user-post__text"):
                    comment_arr.append(comment_text.text)
                for author_text in post.findChildren("div",class_=f"js_product-review-comments js_product-review-hook js_product-review-comments-list{class_text}")[i if i==0 else i-1].findChildren("span",class_="user-post__author-name"):
                    author_Comment.append(author_text.text)
                comments[f"{comment_id}"]={f"text":comment_arr,"Authors":author_Comment, "Date":comment_date[comment_id]}
            else:
                comments[f"{comment_id}"]=[f"{i}","none"]
    def likes_find(post,i,dif):
        if i<=9-dif:
            like_arr=[]
            like_arr.append((post.findChildren("button", class_= "vote-yes js_product-review-vote js_vote-yes")[i]).text)
            like_arr.append((post.findChildren("button", class_= "vote-no js_product-review-vote js_vote-no")[i]).text)
            likes[f"{i}"]={"likes":like_arr[0],"dislikes":like_arr[1]}
    def trust_find(post,i,dif,amount_of_comments):
        if i<=(9-dif):
            users=post.find_all("div",class_="user-post user-post__card js_product-review")[i]
            trust[users["data-entry-id"]]=(users.find("div",class_="review-pz"))["data-hint"] if (users.find("div",class_="review-pz")) is not None else "None"
    def text_find(post,i,id,amount_of_comment,len_comment):
        flag=1
        for item,names in comments.items():
            for texts in names["text"]:
                if amount_of_comment==0:
                    if texts==(post.findChildren("div", class_= "user-post__text")[i]).text :
                        flag=0
                else:
                    if texts==(post.findChildren("div", class_= "user-post__text")[i]).text :
                        flag=0
        if flag==1:
            if amount_of_comment==0:
                if i>=amount_of_comment+1 or i==0:
                    reviews[i-amount_of_comment]={"text":(post.findChildren("div", class_= "user-post__text")[i+amount_of_comment]).text,"id":f"{id}"}
                    author_find(post,i,amount_of_comment)
                    return "none"
            else:
                if i>=amount_of_comment+1 or i==0 and i+amount_of_comment!=2:
                    reviews[i-amount_of_comment]={"text":(post.findChildren("div", class_= "user-post__text")[i]).text,"id":f"{id}"}
                    author_find(post,i,amount_of_comment)
                    return "none"
        else:
            len_comment+= len(names["text"])-1
            if len_comment!=amount_of_comment:
                return "comment"
    def post_date_find(post,i,dif,cycle):
        comment_data=[]
        if i<10-dif:
            j=0
            users=post.find_all("div",class_="user-post user-post__card js_product-review")[i]
            for time in users.findChildren("time"):
                if time.text[0:2]!="po" and j==0:
                    publish_arr.append(time.text)
                    j+=1
                elif j==1 and time.text[0:2]=="po":
                    usage_arr.append(time.text)
                    j+=1
                else:
                    comment_data.append(time.text)
            if j==1:
                usage_arr.append("None")
            comment_date[users["data-entry-id"]]=comment_data
            date[users["data-entry-id"]]={"Published":publish_arr[i+(cycle-1)*10],"Usage":usage_arr[i+(cycle-1)*10]}
    def author_find(post,i,amount_of_comments):
        if amount_of_comments==0:
            author_names.append((post.findChildren("span", class_= "user-post__author-name")[i]).text)
        else:
            author_names.append((post.findChildren("span", class_= "user-post__author-name")[i]).text)
    def rating_find(post,i,dif):
        if i<10-dif:
            ratings.append((post.findChildren("span", class_= "user-post__score-count")[i]).text)
    def json_creation(author,review,rating,cycle,dif,recommend,advantages):
        for  i in range(10-dif):
            review_dict[f'Review{i+1+((cycle-1)*10)}']= {"Id":review[i]["id"],"Published":date[review[i]["id"]]["Published"],"Usage_time":date[review[i]["id"]]["Usage"],"Author":author[i+((cycle-1)*10)],"Text":review[i]["text"],"Rating":rating[i+((cycle-1)*10)],"Comments":[comments[review[i]["id"]] for item,name in comments.items() if  item==review[i]["id"]],"Likes":likes[f"{i}"]["likes"],"Dislikes":likes[f"{i}"]["dislikes"],"Recommend":recommend[review[i]["id"]],"Advantages":advantages[review[i]["id"]]["Advantages"],"Disadvantages":advantages[review[i]["id"]]["Disadvantages"],"Trusted_opinion":trust[review[i]["id"]]}
        return  (review_dict)
    def final_json(json1):
        return json.dumps(json1,indent=2,ensure_ascii=False).encode('utf8')
    def find_all_review(id):
        page=1
        url = f"https://www.ceneo.pl/{id}/opinii-{page}"
        res=requests.get(url)
        soup = BeautifulSoup(res.content, 'html.parser')
        count=(soup.find("div",class_="score-extend__review")).text
        count=re.split(r'\D+',count)
        for page in range(1,math.ceil(int(count[0])/10)+1):
            recommend={}
            advantages={}
            amount_of_comment=0
            if page!=math.ceil(int(count[0])/10):
                
                find_review(id,page,0,amount_of_comment,recommend,advantages)
                json_text=final_json(json_creation(author_names,reviews,ratings,page,0,recommend,advantages))
            else:
                find_review(id,page,(math.ceil(int(count[0])/10))*10-int(count[0]),amount_of_comment,recommend,advantages)
                json_text=final_json(json_creation(author_names,reviews,ratings,page,(math.ceil(int(count[0])/10))*10-int(count[0]),recommend,advantages))
        return json_text
    with open("sample.json", 'wb') as outfile:
        outfile.write(find_all_review(page_id))
    return review_dict