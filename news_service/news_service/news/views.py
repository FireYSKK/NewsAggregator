from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Headline
from .serializers import HeadlineSerializer
from django.core.cache import cache

import requests
from bs4 import BeautifulSoup as BSoup
from datetime import datetime


# Define decorator to check access token in redis
def token_required(view_func):
    def wrapper(self, request, *args, **kwargs):
        access_token = request.COOKIES.get('access_token')

        if access_token is not None and cache.has_key(access_token):
            return view_func(self, request, *args, **kwargs)

        message = {"message": "Unauthorized"}
        return Response(message, status=status.HTTP_401_UNAUTHORIZED)

    return wrapper


# Define decorator to check user is manager
def manager_required(view_func):
    def wrapper(self, request, *args, **kwargs):
        access_token = request.COOKIES.get('access_token')

        if access_token is not None and cache.has_key(access_token):
            user_data = cache.get(access_token)
            if user_data["is_manager"]:
                return view_func(self, request, *args, **kwargs)

        message = {"message": "Unauthorized"}
        return Response(message, status=status.HTTP_401_UNAUTHORIZED)

    return wrapper


def scrape_rbc():
    session = requests.Session()

    url = "https://rssexport.rbc.ru/rbcnews/news/30/full.rss"
    tags = {
        "Общество": "Общество",
        "Спорт": "Спорт",
        "Политика": "Политика",
        "Экономика": "Экономика",
        "Бизнес": "Экономика",
        "Финансы": "Экономика",
        "Технологии и медиа": "Медиа"
    }

    content = session.get(url, verify=False).content
    soup = BSoup(content, "xml")
    news = soup.find_all('item')
    for article in news:
        title = article.find_all('title')[0].get_text()
        category = article.find_all('category')[0].get_text()

        # RSS лента РБК добавляет новые статьи вверх списка
        # Если обрабатываемая статья уже добавлена БД сервиса,
        # Значит все последующие также были добавлены ранее.
        if Headline.objects.filter(title__iexact=title).filter(source__iexact="rbc"):
            break

        if category not in tags:
            continue

        link = article.find_all('link')[0].get_text()
        pub_date = article.find_all('pubDate')[0].get_text()
        description = article.find_all('description')[0].get_text()

        converted_date = datetime.strptime(pub_date, '%a, %d %b %Y %H:%M:%S %z')

        new_headline = Headline()
        new_headline.title = title
        new_headline.url = link
        new_headline.pub_date = converted_date
        new_headline.description = description
        new_headline.category = tags[category]
        new_headline.source = 'rbc'
        new_headline.save()


def scrape_tass():
    session = requests.Session()

    url = "https://tass.ru/rss/anews.xml"
    tags = {
        "В стране": "Политика",
        "Политика": "Политика",
        "Армия и ОПК": "Политика",
        "Спорт": "Спорт",
        "Культура": "Общество",
        "Общество": "Общество",
        "Наука": "Медиа",
        "Происшествия": "Медиа",
        "Экономика и бизнес": "Экономика",
        "Международная панорама": "Политика"
    }

    content = session.get(url, verify=False).content
    soup = BSoup(content, "xml")
    news = soup.find_all('item')
    for article in news:
        title = article.find_all('title')[0].get_text()
        category = article.find_all('category')[0].get_text()

        # RSS лента добавляет новые статьи вверх списка
        # Если обрабатываемая статья уже добавлена БД сервиса,
        # Значит все последующие также были добавлены ранее.
        if Headline.objects.filter(title__iexact=title).filter(source__iexact="tass"):
            break

        if category not in tags:
            continue

        link = article.find_all('link')[0].get_text()
        pub_date = article.find_all('pubDate')[0].get_text()
        if article.find_all('description'):
            description = article.find_all('description')[0].get_text()
        else:
            continue

        converted_date = datetime.strptime(pub_date, '%a, %d %b %Y %H:%M:%S %z')

        new_headline = Headline()
        new_headline.title = title
        new_headline.url = link
        new_headline.pub_date = converted_date
        new_headline.description = description
        new_headline.category = tags[category]
        new_headline.source = 'tass'
        new_headline.save()


def scrape_vedomosti():
    session = requests.Session()

    url = "https://www.vedomosti.ru/rss/articles.xml"
    tags = {
        "Политика": "Политика",
        "Общество": "Общество",
        "Экономика": "Экономика",
        "Инвестиции": "Экономика",
        "Финансы": "Экономика",
        "Бизнес": "Экономика",
        "Недвижимость": "Экономика",
        "Авто": "Экономика",
        "Технологии": "Медиа"
    }

    content = session.get(url, verify=False).content
    soup = BSoup(content, "xml")
    news = soup.find_all('item')
    for article in news:
        title = article.find_all('title')[0].get_text()
        category = article.find_next('category')
        if not category:
            continue

        # RSS лента добавляет новые статьи вверх списка
        # Если обрабатываемая статья уже добавлена БД сервиса,
        # Значит все последующие также были добавлены ранее.
        if Headline.objects.filter(title__iexact=title).filter(source__iexact="vedomosti"):
            break

        if category not in tags:
            continue

        link = article.find_all('link')[0].get_text()
        pub_date = article.find_all('pubDate')[0].get_text()
        description = article.find_all('description')[0].get_text()

        converted_date = datetime.strptime(pub_date, '%a, %d %b %Y %H:%M:%S %z')

        new_headline = Headline()
        new_headline.title = title
        new_headline.url = link
        new_headline.pub_date = converted_date
        new_headline.description = description
        new_headline.category = tags[category]
        new_headline.source = 'vedomosti'
        new_headline.save()


def scrape_kommersant():
    session = requests.Session()

    url = "https://www.kommersant.ru/RSS/news.xml"
    tags = {
        "Мир": "Политика",
        "Спорт": "Спорт",
        "Культура": "Общество",
        "Общество": "Общество",
        "Бизнес": "Экономика",
        "Авто": "Экономика",
        "Происшествия": "Медиа",
        "Hi-Tech": "Медиа"
    }

    content = session.get(url, verify=False).content
    soup = BSoup(content, "xml")
    news = soup.find_all('item')
    for article in news:
        title = article.find_all('title')[0].get_text()
        category = article.find_all('category')[0].get_text()

        # RSS лента добавляет новые статьи вверх списка
        # Если обрабатываемая статья уже добавлена БД сервиса,
        # Значит все последующие также были добавлены ранее.
        if Headline.objects.filter(title__iexact=title).filter(source__iexact="kommersant"):
            break

        if category not in tags:
            continue

        link = article.find_all('link')[0].get_text()
        pub_date = article.find_all('pubDate')[0].get_text()
        description = article.find_all('description')[0].get_text()

        converted_date = datetime.strptime(pub_date, '%a, %d %b %Y %H:%M:%S %z')

        new_headline = Headline()
        new_headline.title = title
        new_headline.url = link
        new_headline.pub_date = converted_date
        new_headline.description = description
        new_headline.category = tags[category]
        new_headline.source = 'kommersant'
        new_headline.save()


def scrape_lenta():
    session = requests.Session()

    url = "https://lenta.ru/rss/articles"
    tags = {
        "Россия": "Политика",
        "Мир": "Политика",
        "Бывший СССР": "Политика",
        "Силовые структуры": "Политика",
        "Экономика": "Экономика",
        "Спорт": "Спорт",
        "Культура": "Общество",
        "Интернет и СМИ": "Медиа",
        "Путешествия": "Путешествия"
    }

    content = session.get(url, verify=False).content
    soup = BSoup(content, "xml")
    news = soup.find_all('item')
    for article in news:
        title = article.find_all('title')[0].get_text()
        category = article.find_all('category')[0].get_text()

        # RSS лента добавляет новые статьи вверх списка
        # Если обрабатываемая статья уже добавлена БД сервиса,
        # Значит все последующие также были добавлены ранее.
        if Headline.objects.filter(title__iexact=title).filter(source__iexact="lenta"):
            break

        if category not in tags:
            continue

        link = article.find_all('link')[0].get_text()
        pub_date = article.find_all('pubDate')[0].get_text()
        description = article.find_all('description')[0].get_text()

        converted_date = datetime.strptime(pub_date, '%a, %d %b %Y %H:%M:%S %z')

        new_headline = Headline()
        new_headline.title = title
        new_headline.url = link
        new_headline.pub_date = converted_date
        new_headline.description = description
        new_headline.category = tags[category]
        new_headline.source = 'lenta'
        new_headline.save()


SCRAPPERS = [scrape_rbc, scrape_tass, scrape_vedomosti, scrape_kommersant, scrape_lenta]
CATEGORIES = ["Политика", "Экономика", "Спорт", "Медиа", "Общество", "Путешествия"]
SOURCES = ["rbc", "tass", "vedomosti", "kommersant", "lenta"]


class NewsView(APIView):
    # Получить все новости
    @token_required
    def get(self, *args, **kwargs):
        queryset = Headline.objects.all().order_by('-pub_date')

        category = self.request.query_params.get('category')
        if category is not None and category in CATEGORIES:
            queryset = queryset.filter(category__iexact=category)

        source = self.request.query_params.get('source')
        if source is not None and source in SOURCES:
            queryset = queryset.filter(source__iexact=source)

        serializer = HeadlineSerializer(queryset, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    # Провести выгрузку новостей
    @manager_required
    def post(self, request):
        for scrape_func in SCRAPPERS:
            scrape_func()
        serializer = HeadlineSerializer(Headline.objects.all().last())
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class NewsDetailView(APIView):
    def get_object(self, pk):
        try:
            headline = Headline.objects.get(pk=pk)
            return headline
        except:
            return None

    # Get single article details with id
    @token_required
    def get(self, request, pk):
        headline = self.get_object(pk)
        if headline is None:
            message = {"message": "Статья не найдена"}
            return Response(message, status=status.HTTP_400_BAD_REQUEST)

        serializer = HeadlineSerializer(headline)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # Update an article with id
    @manager_required
    def patch(self, request, pk):
        headline = self.get_object(pk)
        if headline is None:
            message = {"message": "Статья не найдена"}
            return Response(message, status=status.HTTP_400_BAD_REQUEST)

        serializer = HeadlineSerializer(headline, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Delete a transaction with id
    @manager_required
    def delete(self, request, pk):
        headline = self.get_object(pk)
        if headline is None:
            message = {"message": "Статья не найдена"}
            return Response(message, status=status.HTTP_400_BAD_REQUEST)

        headline.delete()
        message = {"message": "Статья удалена"}
        return Response(message, status=status.HTTP_200_OK)

