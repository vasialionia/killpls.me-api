from flask.views import MethodView
from flask import Response
from flask import abort
from flask import request
from config import config as cfg
import models
import json

def response(data=None, status=200):
    resp = json.dumps(data, ensure_ascii=False) if data is not None else None
    return Response(resp, status=status, mimetype='application/json', headers={'Cache-Control': 'no-cache'})

class ArticleView(MethodView):

    def get(self, tag=None):

        args = request.args

        offset = int(args['offset']) if args.get('offset') else 0
        limit = int(args['limit']) if args.get('limit') else cfg.ARTICLES_LIMIT_DEFAULT

        return response([article.json() for article in models.Article.get(offset=offset, limit=limit, tag=tag)])

    def post(self, article_id=None, decision=None, path=None):
        if article_id:

            if decision not in ['yes', 'no']:
                abort(401)

            models.Article.vote(article_id, decision == 'yes')

            return response()
        else:
            if path == 'scrap':
                models.Article.scrap_recent_articles()
                return response()
            else:
                abort(401)

    @classmethod
    def register(cls, app):
        article_view = cls.as_view('article_view')
        app.add_url_rule('/api/article', methods=['GET'], view_func=article_view)
        app.add_url_rule('/api/article/tag/<string:tag>', methods=['GET'], view_func=article_view)
        app.add_url_rule('/api/article/<int:article_id>/vote/<string:decision>', methods=['POST'], view_func=article_view)
        app.add_url_rule('/api/article/<string:path>', methods=['POST'], view_func=article_view)

views = [ArticleView]
