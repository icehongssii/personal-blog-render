import requests as req
import base64
import markdown2 as md2
from bs4 import BeautifulSoup as bs
from flask import Flask, render_template

# Constants
URL = "https://api.github.com/repos/icehongssii/tech-blog-obsidian/contents/tech-blog/posts/blogs/"
META_URL = "https://api.github.com/repos/icehongssii/tech-blog-obsidian/contents/tech-blog/posts/html/blog-meta.md"
ABOUT_CONTENT = """


## Iceheongssii

2.9년 경력의 소프트웨어 개발자!  
컨테이너, 파이썬, AWS를 좋아하고 사용하는데 익숙합니다.


```ad-note
tl;dr
- 개발에서 관심있는 분야 : devops문화, python, 클라우드, K8S
- 개발 외에 관심있는 분야 : 블록체인, NFT, 게임, 만화, obsidian, 생산성
```

### 제가 해본 미친짓

- 코스프레 대회 1등
- 인도네시아 피칭대회 1등
- MIT 원서넣기


    
    """




app = Flask(__name__, static_folder='../static', template_folder='../templates')

# Utility Functions
def fetch_github_content(url):
    response = req.get(url)
    data = response.json()
    return base64.b64decode(data['content']).decode('utf-8')

def convert_md_to_html(markdown_content):
    return md2.markdown(markdown_content, extras=["metadata", "highlightjs-lang", "spoiler", "tables", 'fenced-code-blocks', "admonitions"])

def extract_tags_from_html(html_content):
    html_obj = bs(html_content, "lxml")
    data_dict = {}
    for row in html_obj.tbody.find_all("tr"):
        cells = row.find_all("td")
        key = cells[0].text.strip()
        values = [li.text.strip() for li in cells[1].find("ul").find_all("li")]
        data_dict[key] = values
    return data_dict

# Route Handlers
@app.route("/about")
def get_about():
    html_content = convert_md_to_html(ABOUT_CONTENT)
    return render_template('about.html', html=html_content)

@app.route("/tags")
def get_tags():
    decoded_post = fetch_github_content(META_URL)
    html_content = convert_md_to_html(decoded_post)
    tags = extract_tags_from_html(html_content)
    return render_template('tags.html', tags=tags)

@app.route("/posts/<title>", methods=["GET"])
def post_detail(title):
    post_content = fetch_github_content(URL + f"{title}")
    html = convert_md_to_html(post_content)
    html.metadata['last_updated'] = html.metadata['last-updated']
    return render_template('post.html', meta=html.metadata, html=html)

@app.route("/")
def index():
    post_list = req.get(URL).json()
    post_cnt = len(post_list)
    posts = [{"url": p['url'].split(URL)[1], "name": p['name']} for p in post_list]
    return render_template('index.html', posts=posts, cnt=post_cnt)

if __name__ == "__main__":
    app.run(debug=True)
