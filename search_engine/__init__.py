from urllib.parse import urlparse
from flask import Flask, render_template, request
from pymongo import MongoClient
from profanity import profanity 
app = Flask(__name__)
app.config.from_object('config')

client = MongoClient('localhost', 27017)
db = client['test']
col = db["Index"]


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        keyword = request.form['keyword']
        keywords = keyword.split(" ")
        keywords = [a.lower() for a in keywords]
        if profanity.contains_profanity(keyword):
            return render_template(
                'index.html',
                is_profane=True,
                query=None,
                keyword=None)
        if keyword:
            return render_template(
                'index.html',
                is_profane=False,
                query=results(keywords),
                keyword=keyword)
    return render_template('index.html')

def results(keywords):
    priority_dict = dict()
    for keyword in keywords:
        query=col.find_one({'keyword': keyword})
        if not query:
            continue
        urls = query['url']
        for url in urls:
            if url in priority_dict:
                priority_dict[url] += 1
            else:
                priority_dict[url] = 1
    sorted_pd = sorted(priority_dict.items(), key=lambda kv: kv[1]*-1)
    return [a[0] for a in sorted_pd]

