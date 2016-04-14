# killpls.me

An unofficial mobile client for http://killpls.me.

**App Store** https://itunes.apple.com/app/id1103203591

**iOS source code** https://github.com/vasialionia/killpls.me-ios

**Backend source code** https://github.com/vasialionia/killpls.me-api

# API

#### GET /api/article?offset=:offset&limit=:limit
Returns an array of articles. Response format:

```
[
    {    
        "content": "...",
        "posted_at": "14 апреля 2016, 05:00",
        "likes_count": ​1072,
        "id": ​17768,
        "tags": "разное"
    },
    ...
]
```

#### GET /api/article/tag/:tag
Returns an array of articles having the tag specified.

#### POST /api/article/:article_id/vote/:decision
Votes the article. Decistion can be "yes" or "no".

# Installation

```sh
git clone https://github.com/vasialionia/killpls.me-api.git killpls.me
cd killpls.me
python -c 'from app import db; db.create_all()'
python app.py
```
