from flask import Flask, render_template
import requests as req
import json
import base64
import markdown2 as md2
import os
import re

URL = "https://api.github.com/repos/icehongssii/tech-blog-obsidian/contents/tech-blog/posts/blogs"

app = Flask(__name__,
            static_folder='../static',  # Set the correct path to the 'static' folder.
            template_folder='../templates'
            )
            

@app.route("/")
def index():
    res = req.get(URL)
    postList = res.json()    
    postCnt = len(postList)
    return render_template('index.html', posts=postList, cnt=postCnt)

def convert_md_to_HTML(decoded_content: str) -> str:
    html = md2.markdown(decoded_content, extras=["metadata", "highlightjs-lang",
                                                    "spoiler",
                                                    'fenced-code-blocks',
                                                    "admonitions"
                                                    ])

    return html



