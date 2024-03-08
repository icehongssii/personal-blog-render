from flask import Flask
import requests as req
import json
import base64
import markdown2 as md2
import os
import re

URL = ""

app = Flask(__name__)


def get_list(u) -> str:
    res = req.get(u)
    data = res.json()
    content = data['content']
    decoded_content = base64.b64decode(content).decode('utf-8')
    return decoded_content

def convert_md_to_HTML(decoded_content: str) -> str:
    html = md2.markdown(decoded_content, extras=["metadata", "highlightjs-lang",
                                                    "spoiler",
                                                    'fenced-code-blocks',
                                                    "admonitions"
                                                    ])

    return html
    
    
@app.route("/d", methods=["GET"])
def returnMd():
    ddd = get_list(URL)    
    md = convert_md_to_HTML(ddd)
    return md



@app.route('/')
def show_markdown():
    print("hi")

