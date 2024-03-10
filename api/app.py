import requests as req
import json
import base64
import markdown2 as md2
import os
import re
from bs4 import BeautifulSoup as bs, element

from flask import Flask, render_template
URL = "https://api.github.com/repos/icehongssii/tech-blog-obsidian/contents/tech-blog/posts/blogs/"
META_URL = "https://api.github.com/repos/icehongssii/tech-blog-obsidian/contents/tech-blog/posts/html/blog-meta.md"

app = Flask(__name__,
            static_folder='../static',  # Set the correct path to the 'static' folder.
            template_folder='../templates'
            )



@app.route("/tags")
def getTags():
    res = req.get(META_URL)
    data = res.json()
    post = data['content']
    decodedPost = base64.b64decode(post).decode('utf-8')
    html = convert_md_to_HTML(decodedPost)
    htmlObj = bs(html, "lxml")
    data_dict = {}
    
    for row in htmlObj.tbody.find_all("tr"):    
        cells = row.find_all("td")
        key = cells[0].text.strip()
        values = [li.text.strip() for li in cells[1].find("ul").find_all("li")]
        data_dict[key] = values
        
    return render_template('tags.html', tags = data_dict)


            
@app.route("/posts/<title>", methods=["GET"])
def postDetail(title):
    res = req.get(URL+f"{title}")    
    data = res.json()
    post = data['content']
    decodedPost = base64.b64decode(post).decode('utf-8')
    html = convert_md_to_HTML(decodedPost)
    html.metadata['last_updated']=html.metadata['last-updated']
    return render_template('post.html', meta = html.metadata, html = html)
    

@app.route("/")
def index():
    res = req.get(URL)
    postList = res.json()    
    postCnt = len(postList)
    postList = [ {"url":p['url'].split(URL)[1], "name":p['name']} for p in postList]
    return render_template('index.html', posts=postList, cnt=postCnt)

def convert_md_to_HTML(decoded_content: str) -> str:
    html = md2.markdown(decoded_content, extras=["metadata", "highlightjs-lang",
                                                    "spoiler","tables",
                                                    'fenced-code-blocks',
                                                    "admonitions"
                                                    ])

    return html
