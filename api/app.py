from typing import Any
import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.base import BaseHTTPMiddleware
from pathlib import Path
import redis
import requests as req
import base64
import json
import markdown2 as md2
from bs4 import BeautifulSoup as bs

app = FastAPI()


class HTTPSRedirectMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Change the scheme to https
        request.scope['scheme'] = 'https'
        response = await call_next(request)
        return response

redis_host = os.getenv("REDIS_HOST")
redis_pwd = os.getenv("REDIS_PWD")
redis_client = redis.Redis(
        host = redis_host,
        port=6379,
        password=redis_pwd,
        decode_responses=True
    )    


# 환경 변수를 체크하여 로컬 환경이 아닐 때만 HTTPSRedirectMiddleware를 적용합니다.
if os.getenv("ENV") != "local":
    app.add_middleware(HTTPSRedirectMiddleware)

BASE_DIR = Path(__file__).resolve().parent.parent  # 프로젝트 루트 디렉토리
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")


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

def fetch_github_content(url):
    # Create a unique key for storing the content in Redis.
    # This could be the URL itself or some other unique identifier.
    cache_key = f"content:{url}"
    # Try fetching the content from Redis cache first.
    try:
        cache_data = redis_client.get(cache_key)
    except redis.exceptions.ConnectionError:
    # Redis 연결 문제 처리
        print("Redis 연결에 실패했습니다.")
        cache_data = None
    if cache_data:
        # If content exists in cache, return it without making an API call.
        return cache_data
    else:
        response = req.get(url)
        data = response.text
        # Store the new content in Redis cache for future use.
        # Set an expiration time for the cache, for example, 1 hour (3600 seconds).
        redis_client.setex(cache_key, 3600, data) # json넣으면 안된다..
        return data


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

# # Route Handlers
@app.get("/about", response_class=HTMLResponse)
def get_about(request:Request):
    html_content = convert_md_to_html(ABOUT_CONTENT)
    return templates.TemplateResponse("about.html", {"request": request, "html": html_content})
    

@app.get("/tags", response_class=HTMLResponse)
def get_tags(request:Request):
    data = json.loads(fetch_github_content(META_URL))
    decoded_post = base64.b64decode(data['content']).decode('utf-8')
    html_content = convert_md_to_html(decoded_post)
    tags = extract_tags_from_html(html_content)
    return templates.TemplateResponse("tags.html", {"request": request, "tags": tags})

    

@app.get("/posts/{title}", response_class=HTMLResponse)
def post_detail(request:Request,title:str):
    data = json.loads(fetch_github_content(URL + f"{title}"))
    decoded_post = base64.b64decode(data['content']).decode('utf-8')
    html = convert_md_to_html(decoded_post)
    html.metadata['last_updated'] = html.metadata['last-updated']
    return templates.TemplateResponse("post.html", {"request": request, "meta": html.metadata, "html": html})

@app.get("/", response_class=HTMLResponse)
def index(request:Request):
    data = json.loads(fetch_github_content(URL))
    post_cnt = len(data)    
    posts = [{"url": p['url'].split(URL)[1], "name": p['name']} for p in data]
    return templates.TemplateResponse("index.html", {"request": request, "posts": posts, "cnt": post_cnt})
    


if __name__ == "__main__":
    app.run(debug=True)
