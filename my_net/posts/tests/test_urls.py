# posts/tests/test_urls.py
from http import HTTPStatus

from django.test import TestCase, Client
from django.urls import reverse

from ..models import Post, Group, User

HOME = '/'
CREATE_POST = '/create/'


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.author = User.objects.create_user(username='test_author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_group',
            description='Тестовое описание группы'
        )
        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=cls.user
        )
        cls.post_1 = Post.objects.create(
            text='Тестовый пост 1',
            author=cls.author
        )

        cls.group_list = reverse('posts:group',
                                 kwargs={'slug': cls.group.slug})
        cls.post_by_user = reverse('posts:profile',
                                   kwargs={'username': cls.user.username})
        cls.post_detail = reverse('posts:post_detail',
                                  kwargs={'post_id': cls.post.pk})
        cls.group_url = f'/group/{cls.group.slug}/'
        cls.profile_url = f'/profile/{cls.user}/'
        cls.post_url = f'/posts/{cls.post.pk}/'
        cls.post_edit_url = f'/posts/{cls.post.pk}/edit/'
        cls.post_edit_1_url = f'/posts/{cls.post_1.pk}/edit/'

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_author = Client()
        self.authorized_author.force_login(self.author)

    def test_open_different_pages(self):
        """Доступность страниц"""
        # проверка для неавторизованных юзеров
        page_url_names_quest = [
            HOME,
            self.group_list,
            self.post_by_user,
            self.post_detail,
        ]

        for template in page_url_names_quest:
            with self.subTest(template=template):
                response = self.guest_client.get(template)
                self.assertEqual(response.status_code, HTTPStatus.OK)

        # только авторизованным
        response = self.authorized_client.get(CREATE_POST)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        # только автору
        response = self.authorized_author.get(self.post_edit_1_url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_unexisting_page_404(self):
        """Страница не существует."""
        response = self.guest_client.get(None)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_urls_posts_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            HOME: 'posts/index.html',
            CREATE_POST: 'posts/create_post.html',
            self.group_url: 'posts/group_list.html',
            self.profile_url: 'posts/profile.html',
            self.post_url: 'posts/post_detail.html',
            self.post_edit_url: 'posts/create_post.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
