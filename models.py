from app import db
from app import cfg
import urllib
from contextlib import closing
import BeautifulSoup

class Article(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    guid = db.Column(db.String, nullable=False, unique=True)
    content = db.Column(db.Text(4095), nullable=False)
    tags = db.Column(db.String, nullable=False)
    posted_at = db.Column(db.String, nullable=False)
    likes_count = db.Column(db.Integer, nullable=False)

    def __init__(self, article_id, guid, content, tags, posted_at, likes_count):
        self.id = article_id
        self.guid = guid
        self.content = content
        self.tags = tags
        self.posted_at = posted_at
        self.likes_count = likes_count

    def json(self):
        return {
            'id': self.id,
            'content': self.content,
            'tags': self.tags,
            'posted_at': self.posted_at,
            'likes_count': self.likes_count
        }

    @staticmethod
    def get(session=None, article_id=None, offset=0, limit=0, tag=None):
        if not session:
            session = db.session

        if article_id:
            return session.query(Article).get(article_id)
        else:
            limit = min(limit, cfg.ARTICLES_COUNT_MAX - offset)
            limit = max(limit, 0)

            query = session.query(Article)

            if tag:
                query = query.filter(Article.tags.like('%%%s%%' % tag))

            return query.order_by(Article.id.desc()).offset(offset).limit(limit).all()

    @staticmethod
    def vote(article_id, positive):
        article = Article.get(None, article_id)
        url = 'http://killpls.me/vote/%s/%s' % ('yes' if positive else 'no', article.guid)
        request = urllib.urlopen(url)
        request.close()

    @staticmethod
    def parse_articles_content(session, content):

        count = 0

        for i in range(len(content[:-2])):

            if content[i].get('class') == 'row':
                if content[i + 1].get('class') == 'row':
                    if content[i + 2].get('class') == 'row':

                        if content[i + 1].div.center:
                            if content[i + 1].div.center.a.text == '18+':
                                continue

                        count += 1

                        article_id = int(content[i].div.a.text[1:])
                        article_guid = content[i + 2].div.div.a['href'][10:]
                        article_likes_count = content[i + 2].div.div.b.text

                        existing_article = Article.get(session, article_id)
                        if existing_article:
                            existing_article.likes_count = article_likes_count
                            continue

                        article_posted_at = content[i].div.contents[3].text
                        article_tags = ','.join([tag.text for tag in content[i].contents[3].contents if type(tag) == BeautifulSoup.Tag])

                        article_content = ''
                        for item in content[i + 1].div.contents:
                            if type(item) == BeautifulSoup.NavigableString:
                                article_content += item
                            elif type(item) == BeautifulSoup.Tag:
                                if item.name == 'br':
                                    article_content += '\n'
                                else:
                                    assert False
                            else:
                                assert False
                        article_content = article_content[9:-5]

                        session.add(Article(
                            article_id,
                            article_guid,
                            article_content,
                            article_tags,
                            article_posted_at,
                            article_likes_count
                        ))

        return count

    @staticmethod
    def scrap_recent_articles():

        tags = [
            'look',
            'money',
            'friends',
            'health',
            'relations',
            'rabota',
            'other',
            'parents',
            'sex',
            'family',
            'tech',
            'stud'
        ]
        urls = ['http://killpls.me/bytag/%s' % tag for tag in tags]
        urls.append('http://killpls.me')

        for url in urls:

            print 'loading %s...' % url

            count = 0
            current_page = None
            page_path = '/page' if url == urls[-1] else ''

            while count < cfg.ARTICLES_COUNT_MAX:

                paged_url = url

                if current_page:
                    current_page -= 1
                    paged_url += '%s/%d' % (page_path, current_page)

                print ' loading %s...' % paged_url

                with closing(urllib.urlopen(paged_url)) as request:
                    xml_data = BeautifulSoup.BeautifulSoup(request.read())

                articles_container = xml_data.findAll('div', attrs={'id': 'stories'})
                articles_content = [item for item in articles_container[0].contents[5:-9] if type(item) == BeautifulSoup.Tag]

                if not current_page:
                    current_page = int(articles_content[0].div.div.span.text)

                session = db.create_scoped_session()

                count += Article.parse_articles_content(session, articles_content[4:])

                session.commit()
                session.close()

                print '  loaded %d' % count
