from bs4 import BeautifulSoup
import json
import requests
import requests_cache
from flask import Flask, render_template, request

requests_cache.install_cache("roboguru",expire_after=120)
class RoboguruForum:

    def __init__(self, data):
        self.data = BeautifulSoup(data, 'html.parser')
        self._parse()

    def _parse(self):
        next_dat = self.data.find_all("script", attrs={"id":"__NEXT_DATA__"})[0]

        self.raw = json.loads(next_dat.text)
        json.dump(self.raw,open("form_data","w"),ensure_ascii=False)
    def thread(self):
        thread_ = self.raw.get('props').get("pageProps").get(
            "forumDetail").get("thread")
        content = thread_.get("content")
        likes = thread_.get("likeCount")
        username = thread_.get("username")
        cleanContent = self.raw.get('props').get("pageProps").get("cleanContent")
        gname = self.raw.get('props').get("pageProps").get("forumDetail").get(
            "structure").get("gradeName")
        subjectName = thread_.get("subjectDisplayName")
        classname = thread_.get("className")
        viewCount = thread_.get("viewCount")
        status = thread_.get("status")
        assets = thread_.get("attachments")

        items = []
        items = self.raw.get('props').get("pageProps").get(
            "forumDetail").get("items")
        return {
            "content": content,
            "assets": assets,
            "likes": likes,
            "username": username,
            "gradename": gname,
            "cleanContent": cleanContent,
            "subjectname": subjectName,
            "classname": classname,
            "viewer": viewCount,
            "status": status,
            "items": items,
        }


class RoboguruQuestion(RoboguruForum):
    def __init__(self, data):
        super().__init__(data)
    def thread(self):
        thread_ = self.raw.get("props").get("pageProps")
        question_def = thread_.get("question")

        content = question_def.get("contents")
        contentDef = question_def.get("contentDefinition").replace("»",">").replace("«","<")
        cleanContent = thread_.get("cleanContent")
        comments = thread_.get("comments")
        attachments = question_def.get("attachments")
        createdByUser = question_def["createdByUser"]
        title = thread_.get("cleanShortContents")
        return {
                "title":title,
                "content": content,
                "contentDef": contentDef,
                "cleanContent": cleanContent,
                "comments": comments,
                "attachments": attachments,
                "answerby": createdByUser,
                }
app = Flask(__name__)
@app.route('/')
def index():
    #return "oke"
    return render_template("index.html")

@app.route("/question/<page>")
def question(page):
    if(not page):
        return 404
    resp = requests.get(f"https://roboguru.ruangguru.com/question/{page}",headers={"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/600.8.9 (KHTML, like Gecko) Version/8.0.8 Safari/600.8.1"})
    print("[REQ] Read %s from cache: %s" % (page,resp.from_cache))
    thrd = RoboguruQuestion(resp.text).thread()
    return render_template("rgquestion.html",
                           title=thrd.get("cleanShortContents"),
                           thread_q=thrd.get("content"),
                           contentDef=thrd.get("contentDef"),
                           assets=thrd.get("attachments"),
                           comments=thrd.get("comments"),
                           answerby=thrd.get("answerby")
                           )

@app.route("/forum/<page>", endpoint="forum")
def forum(page):
    if(not page):
        return 404
    resp = requests.get(f"https://roboguru.ruangguru.com/forum/{page}", headers={"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/600.8.9 (KHTML, like Gecko) Version/8.0.8 Safari/600.8.1"})
    print("[REQ] Read %s from cache: %s" % (page,resp.from_cache))
    thrd = RoboguruForum(resp.text).thread()
    return render_template("rgforum.html",
                           title=thrd.get("cleanContent"),
                           grade=thrd.get("gradename"),
                           subjectname=thrd.get("subjectname"),
                           thread_q=thrd.get("content"),
                           threads=thrd.get("items"),
                           ditanya_oleh=thrd.get("username"),
                           assets=thrd.get("assets")
                           )
