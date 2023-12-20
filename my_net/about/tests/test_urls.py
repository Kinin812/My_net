from http import HTTPStatus

from django.test import TestCase, Client
from django.urls import reverse

from posts.models import User


class AboutURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='NoName')
        cls.author_url = reverse('about:author')
        cls.tech_url = reverse('about:tech')

    def test_open_pages(self):
        """Доступность страниц"""
        page_url_names_quest = [
            self.author_url,
            self.tech_url,
        ]
        for template in page_url_names_quest:
            with self.subTest(template=template):
                response = Client().get(template)
                self.assertEqual(response.status_code, HTTPStatus.OK)
