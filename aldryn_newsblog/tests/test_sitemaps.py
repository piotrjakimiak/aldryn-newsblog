# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from . import NewsBlogTestCase
from aldryn_newsblog.sitemaps import NewsBlogSitemap

from django.contrib.sites.models import get_current_site
from django.utils.translation import override

class TestSitemaps(NewsBlogTestCase):

    def _sitemap_urls(self, sitemap):
        urls_info = sitemap.get_urls()
        urls = [url_info['location'] for url_info in urls_info]
        return urls

    def _article_urls(self, articles):
        host = 'http://' + get_current_site(self.request).domain
        return [host + article.get_absolute_url() for article in articles]

    def assertArticlesIn(self, articles, sitemap):
        urls = self._sitemap_urls(sitemap)
        article_urls = self._article_urls(articles)

        for url in article_urls:
            self.assertIn(url, urls)

    def assertArticlesNotIn(self, articles, sitemap):
        urls = self._sitemap_urls(sitemap)
        article_urls = self._article_urls(articles)

        for url in article_urls:
            self.assertNotIn(url, urls)

    def test_listening_all_instances(self):
        articles = [self.create_article() for _ in range(11)]
        unpublished_article = articles[0]
        unpublished_article.is_published = False
        unpublished_article.save()
        sitemap = NewsBlogSitemap()
        self.assertArticlesIn(articles[1:], sitemap)
        self.assertArticlesNotIn([unpublished_article], sitemap)

    def test_listening_namespace(self):
        articles = [self.create_article() for _ in range(11)]
        unpublished_article = articles[0]
        unpublished_article.is_published = False
        unpublished_article.save()
        sitemap = NewsBlogSitemap(namespace=self.app_config.namespace)
        self.assertArticlesIn(articles[1:], sitemap)
        self.assertArticlesNotIn([unpublished_article], sitemap)

    def test_listening_unexisting_namespace(self):
        articles = [self.create_article() for _ in range(11)]
        unpublished_article = articles[0]
        unpublished_article.is_published = False
        unpublished_article.save()
        sitemap = NewsBlogSitemap(
            namespace='not exists')
        self.assertFalse(sitemap.items())
        self.assertArticlesNotIn(articles, sitemap)

    def test_languages_support(self):
        with override('en'):
            multilanguage_article = self.create_article()
            en_article = self.create_article()

        multilanguage_article.create_translation('de', title='DE title')
        with override('de'):
            de_article = self.create_article()

        multilingual_sitemap = NewsBlogSitemap()
        self.assertArticlesIn([multilanguage_article, en_article, de_article], multilingual_sitemap)

        en_sitemap = NewsBlogSitemap(language='en')
        self.assertArticlesIn([multilanguage_article, en_article], en_sitemap)
        self.assertArticlesNotIn([de_article], en_sitemap)

        de_sitemap = NewsBlogSitemap(language='de')
        self.assertArticlesIn([multilanguage_article, de_article], de_sitemap)
        self.assertArticlesNotIn([en_article], de_sitemap)