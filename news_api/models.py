from django.contrib.auth.models import User
from django.db import models


# Create your models here.
class Source(models.Model):
    name = models.CharField(
        verbose_name=u'Название', max_length=100, unique=True)
    trust = models.IntegerField(verbose_name=u'Уровень доверия')

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)
        verbose_name = u'Источник'
        verbose_name_plural = u'Источники'


class News(models.Model):
    title = models.CharField(verbose_name=u'Название', max_length=255)
    url = models.CharField(
        verbose_name=u'Ссылка', max_length=255, unique=True)
    version = models.IntegerField()
    document_type = models.CharField(verbose_name=u'Тип новости', max_length=10)
    pub_date = models.DateField(verbose_name=u'Дата публикации')
    modified_date = models.DateField(verbose_name=u'Дата изменения')
    source = models.ForeignKey(
        Source, verbose_name=u'Источник', related_name='sources'
    )

    def __str__(self):
        return self.title

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = u'Новость'
        verbose_name_plural = u'Новости'
