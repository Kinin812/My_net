# users/tests/test_urls.py
from http import HTTPStatus

from django.test import TestCase, Client
from django.urls import reverse

from posts.models import User


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='NoName')
        cls.signup = reverse('users:signup')
        cls.login = reverse('users:login')
        cls.logout = reverse('users:logout')
        cls.password_reset_form = reverse('users:password_reset_form')
        #        cls.password_reset_down = reverse('users:password_reset_down')
        #        cls.password_reset_confirm = reverse(
        #        'users:password_reset_confirm')
        cls.password_reset_complete = reverse('users:password_reset_complete')
        cls.password_change_form = reverse('users:password_change_form')
        cls.password_change_done = reverse('users:password_change_done')

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_open_different_pages(self):
        """Доступность страниц"""
        # проверка для неавторизованных юзеров
        page_url_names_quest = [
            self.signup,
            self.login,
        ]

        for template in page_url_names_quest:
            with self.subTest(template=template):
                response = self.guest_client.get(template)
                self.assertEqual(response.status_code, HTTPStatus.OK)

        # проверка для авторизованных юзеров
        page_url_names_quest = [
            self.password_reset_form,
            #            self.password_reset_down,
            #            self.password_reset_confirm,
            self.password_reset_complete,
            self.password_change_form,
            self.password_change_done
        ]

        for template in page_url_names_quest:
            with self.subTest(template=template):
                response = self.authorized_client.get(template)
                self.assertEqual(response.status_code, HTTPStatus.OK)
