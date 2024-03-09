import requests as req
import json
import base64
import markdown2 as md2
import os
import re

from flask import Flask, render_template
URL = "https://api.github.com/repos/icehongssii/tech-blog-obsidian/contents/tech-blog/posts/blogs/"


app = Flask(__name__,
            static_folder='../static',  # Set the correct path to the 'static' folder.
            template_folder='../templates'
            )
            
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
