from rest_framework import serializers
from news_api.models import News, Source

class SourceSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    count_ref = serializers.IntegerField()
    ratio = serializers.DecimalField(max_digits=5, decimal_places=2)

class NewsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = News
        fields = ('title', 'url', 'pub_date')
