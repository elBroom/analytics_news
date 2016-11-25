from django.contrib.auth.models import User
from django.test import TestCase

from rest_framework.test import APIClient
from rest_framework import status
from knox.models import AuthToken

from news_api.tasks import grabber_task, save_news_task
from news_api.models import Source, News


# Create your tests here.
class GrabberTestCase(TestCase):

    def test_save_news_task(self):
        result = save_news_task({
            "documents": {
                "news/2016/11/23/v-peterburge-otkryli-pervuyu-v-rossii-prachechnuyu-dlya-bezdomnyh": {
                    "title": "В Петербурге открыли первую в России прачечную для бездомных",
                    "url": "news/2016/11/23/v-peterburge-otkryli-pervuyu-v-rossii-prachechnuyu-dlya-bezdomnyh",
                    "document_type": "news",
                    "version": 2,
                    "published_at": 1479906553,
                    "modified_at": 1479906553,
                    "pub_date": "2016-11-23",
                    "source": {
                        "name": "Meduza",
                        "trust": 3
                    },
                    "locale": "ru"
                },
                "news/2016/11/23/v-peterburge-otkryli-pervuyu-v-rossii-prachechnuyu-dlya-bezdomnyh1": {
                    "title": "В Петербурге открыли первую в России прачечную для бездомных",
                    "url": "news/2016/11/23/v-peterburge-otkryli-pervuyu-v-rossii-prachechnuyu-dlya-bezdomnyh",
                    "document_type": "news",
                    "version": 3,
                    "published_at": 1479906553,
                    "modified_at": 1479906553,
                    "pub_date": "2016-11-23",
                    "source": {
                        "name": "Meduza",
                        "trust": 3
                    },
                    "locale": "ru"
                },
                "game/2016/11/23/v-peterburge-otkryli-pervuyu-v-rossii-prachechnuyu-dlya-bezdomnyh": {
                    "title": "В Петербурге открыли первую в России прачечную для бездомных",
                    "url": "game/2016/11/23/v-peterburge-otkryli-pervuyu-v-rossii-prachechnuyu-dlya-bezdomnyh",
                    "document_type": "game",
                    "version": 3,
                    "published_at": 1479906953,
                    "modified_at": 1479906553,
                    "pub_date": "2016-11-23",
                    "locale": "ru"
                },
            }
        })
        self.assertTrue(result)
        self.assertEqual(result, u"Добавлено новостей: 1; Изменено новостей: 1")

    def test_grabber_task(self):
        result = grabber_task(page=2, per_page=30)
        self.assertEqual(result, u"Данные получены")


class NewsApiTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='test', email="test@te.com", password='password')
        self.token = AuthToken.objects.create(self.user)
        self.client = APIClient()

    def test_login(self):
        response = self.login()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_logout(self):
        (response, response_login) = self.logout()
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_double_logout(self):
        (response, response_login) = self.logout()
        response = self.with_token(response_login.data['token']).client.post('/logout/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_source_list_invalid_token(self):
        response = self.with_token(self.token[:-2]+'11').client.get('/source_list/', \
            {'start_date': '2016-11-12', 'end_date': '2016-11-23'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_source_list_logout_token(self):
        (response, response_login) = self.logout()
        response = self.with_token(response_login.data['token']).client.get('/source_list/', \
            {'start_date': '2016-11-12', 'end_date': '2016-11-23'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


    def test_source_list(self):
        response = self.with_token(self.token).client.get('/source_list/', \
            {'start_date': '2016-11-12', 'end_date': '2016-11-23'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_source_list_empty_params(self):
        response = self.with_token(self.token).client.get('/source_list/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_source_list_not_valid_date(self):
        response = self.with_token(self.token).client.get('/source_list/', \
            {'start_date': '20016-11-12', 'end_date': '2016-11-23'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, ['Format date Y-m-d'])


    def test_news_list(self):
        response = self.with_token(self.token).client.get('/news_list/', \
            {'start_date': '2016-11-12', 'end_date': '2016-11-23', 'source': 'Meduza'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_news_list_empty_params(self):
        response = self.with_token(self.token).client.get('/news_list/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_news_list_empty_source(self):
        response = self.with_token(self.token).client.get('/news_list/', \
            {'start_date': '2016-11-12', 'end_date': '2016-11-23', 'source': ''})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, ['Source empty'])

    def test_news_list_not_valid_date(self):
        response = self.with_token(self.token).client.get('/news_list/', \
            {'start_date': '20016-11-12', 'end_date': '2016-11-23', 'source': 'Meduza'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, ['Format date Y-m-d'])


    def login(self):
        self.with_token(None).client.force_authenticate(user=self.user)
        response = self.client.post('/login/')
        self.client.force_authenticate()
        return response

    def logout(self):
        response_login = self.login()
        response = self.with_token(response_login.data['token']).client.post('/logout/')
        return (response, response_login)

    def with_token(self, token=None):
        if token:
            self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        else:
            self.client.credentials(HTTP_AUTHORIZATION=None)
        return self
