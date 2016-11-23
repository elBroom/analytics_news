from celery import Celery
from news_api.models import Source, News
from datetime import datetime
import requests

app = Celery('analytics_news')


# Create your tasks here
@app.task(bind=True)
def grabber_task(page=0, per_page=50, locale='ru'):
    try:
        response = requests.get("http://meduza.io/api/v3/search", params={
            'chrono': 'news',
            'page': page,
            'per_page': per_page,
            'locale': locale
        })
        if response.status_code == requests.codes.ok:
            save_news_task.delay(response.json())
            return u"Данные получены"
        else:
            return u"Статус ответа {}".format(response.status_code)
    except Exception as detail:
        return u"Ошибка: {}".format(detail)


@app.task(bind=True)
def save_news_task(self, data):
    (new, update) = (0, 0)
    for item in data['documents'].values():
        source = None
        try:
            try:
                source = Source.objects.filter(
                    name=item['source']['name']).get()
            except Source.DoesNotExist:
                source = Source(name=item['source']['name'],
                    trust=item['source']['trust'])
                source.save()
        except KeyError:
            continue

        modified_date = datetime.fromtimestamp(item['modified_at']).strftime('%Y-%m-%d')
        news = None
        try:
            try:
                news = News.objects.filter(url=item['url']).get()
                if news.version < item['version']:
                    news.title = item['title']
                    news.version = item['version']
                    news.document_type = item['document_type']
                    news.pub_date = item['pub_date']
                    news.modified_date = modified_date
                    news.source_id = source.id
                    update += 1
            except News.DoesNotExist:
                news = News(title=item['title'], url=item['url'], 
                    version=item['version'], document_type=item['document_type'],
                    pub_date=item['pub_date'], modified_date=modified_date,
                    source_id=source.id)
                new += 1
            news.save()
        except KeyError:
            continue

    return u"Добавлено новостей: {}; Изменено новостей: {}".format(new, update)