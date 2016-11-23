from django.core.cache import cache
from django.db.models import Count
from rest_framework.decorators import api_view, throttle_classes
from rest_framework.exceptions import ValidationError
from rest_framework.throttling import UserRateThrottle
from rest_framework.response import Response

from news_api.serializers import NewsSerializer, SourceSerializer
from news_api.models import News, Source

import re


# Create your views here.
@api_view(['GET'])
@throttle_classes([UserRateThrottle])
def source_list(request):
    try:
        start_date = request.GET['start_date']
    except LookupError:
        raise ValidationError('Not params start_date')
    try:
        end_date = request.GET['end_date']
    except LookupError:
        raise ValidationError('Not params end_date')

    if not (re.match('^\d{4}-\d{2}-\d{2}$', start_date) and
        re.match('^\d{4}-\d{2}-\d{2}$', end_date)):
        raise ValidationError('Format date Y-m-d')

    key = 'source_list_{}_{}'.format(start_date, end_date)
    sources = cache.get(key)
    if not sources:
        count_news = News.objects.count()
        sources = News.objects.filter(pub_date__range=(start_date, end_date)) \
                        .values('source__name', 'source_id') \
                        .annotate(count_ref=Count('source_id')) \
                        .order_by('-count_ref')

        for item in sources:
            item['name'] = item['source__name']
            item['ratio'] = item['count_ref']/count_news

        cache.set(key, sources, 60 * 10)

    serializer = SourceSerializer(sources, many=True)
    return Response({'detail': serializer.data})


@api_view(['GET'])
@throttle_classes([UserRateThrottle])
def news_list(request):
    try:
        source = request.GET['source']
    except LookupError:
        raise ValidationError('Not params source')
    try:
        start_date = request.GET['start_date']
    except LookupError:
        raise ValidationError('Not params start_date')
    try:
        end_date = request.GET['end_date']
    except LookupError:
        raise ValidationError('Not params end_date')

    if not source:
        raise ValidationError('Source empty')
    if not (re.match('^\d{4}-\d{2}-\d{2}$', start_date) and
        re.match('^\d{4}-\d{2}-\d{2}$', end_date)):
        raise ValidationError('Format date Y-m-d')

    key = 'news_list_{}_{}_{}'.format(source, start_date, end_date)
    news = cache.get(key)
    if not news:
        news = News.objects.filter(source__name = source, \
            pub_date__range=(start_date, end_date)) \
            .values('title', 'url', 'pub_date')
        cache.set(key, news, 60 * 10)

    serializer = NewsSerializer(news, many=True)
    return Response({'detail': serializer.data})
