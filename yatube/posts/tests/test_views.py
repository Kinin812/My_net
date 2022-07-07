# posts/tests/test_views.py
import shutil
import tempfile
import time

from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django import forms
from django.conf import settings

from ..models import Post, Group, User, Follow

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
HOME = reverse('posts:index')
CREATE_POST = '/create/'
IMAGE_TEST = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='KumKumov')
        cls.group_1 = Group.objects.create(
            title='Тестовая группа 1',
            slug='test_group_1',
            description='Тестовое описание группы'
        )
        cls.group_2 = Group.objects.create(
            title='Тестовая группа 2',
            slug='test_group_2',
            description='Тестовое описание группы 2'
        )
        #  Пакетное создание постов
        #  создали 15 постов
        #  12 постов от первой группы
        for i in range(0, 12):
            Post.objects.create(
                author=cls.user,
                text=f'Тестовый пост {i + 1}',
                group=cls.group_1
            )
            time.sleep(1 / 1000)
        #  2 поста от второй группы
        for i in range(12, 14):
            Post.objects.create(
                author=cls.user,
                text=f'Тестовый пост {i + 1}',
                group=cls.group_2
            )
            time.sleep(1 / 1000)
        #  1 пост без группы
        Post.objects.create(
            author=cls.user,
            text='Тестовый пост 15'
        )
        cls.posts = Post.objects.all()
        cls.group_list = reverse('posts:group',
                                 kwargs={'slug': cls.group_1.slug})
        cls.profile_url = reverse('posts:profile',
                                  kwargs={'username': cls.user.username})
        cls.post_detail = reverse(
            'posts:post_detail',
            kwargs={'post_id': 1})
        cls.post_edit_url = reverse(
            'posts:post_edit',
            kwargs={'post_id': 1})
        cls.post_edit_1_url = reverse(
            'posts:group',
            kwargs={'slug': 'test_group_1'})

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            HOME: 'posts/index.html',
            self.group_list: 'posts/group_list.html',
            self.profile_url: 'posts/profile.html',
            self.post_detail: 'posts/post_detail.html',
            CREATE_POST: 'posts/create_post.html',
            self.post_edit_url: 'posts/create_post.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_post_list_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.guest_client.get(HOME + '?page=2')
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.text, 'Тестовый пост 5')
        self.assertEqual(first_object.group.title, 'Тестовая группа 1')
        self.assertEqual(first_object.author.username, 'KumKumov')

    def test_group_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом"""
        response = self.guest_client.get(self.post_edit_1_url)
        for i, post in enumerate(response.context['page_obj']):
            self.assertEqual(post.text,
                             f'Тестовый пост {len(self.posts) - i - 3}')
            self.assertEqual(post.group.title, 'Тестовая группа 1')
            self.assertEqual(post.author.username, self.user.username)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом"""
        response = self.guest_client.get(self.profile_url)
        for i, post in enumerate(response.context['page_obj']):
            self.assertEqual(post.text, f'Тестовый пост {len(self.posts) - i}')
            self.assertEqual(post.author.username, self.user.username)

    def test_post_detail_pages_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = (self.authorized_client.get(self.post_detail))
        self.assertEqual(response.context.get('post').text,
                         Post.objects.get(pk=1).text)
        self.assertEqual(response.context.get('post').group.title,
                         self.group_1.title)
        self.assertEqual(response.context.get('post').author.username,
                         self.user.username)

    def test_post_create_pages_show_correct_context(self):
        """Шаблон create_post сформирован с правильным контекстом."""
        response = (self.authorized_client.get(CREATE_POST))
        form_fields = {'text': forms.fields.CharField}
        # Проверяем, что типы полей формы в словаре context
        # соответствуют ожиданиям
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                # Проверяет, что поле формы является экземпляром
                # указанного класса
                self.assertIsInstance(form_field, expected)

    def test_post_edit_pages_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = (self.authorized_client.get(self.post_edit_url))
        form_fields = {'text': forms.fields.CharField}
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_cache_index(self):
        """Тест для проверки кеширования главной страницы index."""
        cached_object = Post.objects.order_by('id')
        cached_object = cached_object.last()
        response_before_delete = self.client.get(reverse('posts:index'))
        Post.objects.filter(pk=cached_object.pk).delete()
        response_after_deleted = self.client.get(reverse('posts:index'))
        content_deleted = response_after_deleted.content
        self.assertEqual(response_before_delete.content, content_deleted)
        cache.clear()
        response_cached = self.client.get(reverse('posts:index'))
        content_cached = response_cached.content
        self.assertNotEqual(content_deleted, content_cached)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='KumKumov')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_group',
            description='Тестовое описание группы'
        )

        #  создали 15 постов
        count_of_posts = 15
        for i in range(count_of_posts):
            Post.objects.create(
                author=cls.user,
                text=f'Тестовый пост {i + 1}',
                group=cls.group
            )
            time.sleep(1 / 1000)
        cls.group_url = reverse('posts:group',
                                kwargs={'slug': 'test_group'})
        cls.profile_url = reverse('posts:profile',
                                  kwargs={'username': cls.user.username})

    # Проверяем паджинатор
    def test_index_page_contains_15(self):
        """На страницу index выводится по 10 постов"""
        response = self.client.get(HOME)
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_index_page_contains_5(self):
        """На вторую страницу index выводится 5 постов"""
        response = self.client.get(HOME + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 5)

    def test_group_list_page_contains_15(self):
        """На страницу group_list выводится 10 постов"""
        response = self.client.get(self.group_url)
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_group_list_page_contains_2(self):
        """На вторую страницу group_list выводится 5 постов"""
        response = self.client.get(self.group_url + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 5)

    def test_profile_page_contains_15(self):
        """На страницу profile выводится 10 постов"""
        response = self.client.get(self.profile_url)
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_profile_page_contains_5(self):
        """На вторую страницу profile выводится 5 постов"""
        response = self.client.get(self.profile_url + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 5)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostIsVisibleOnTruePages(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='KumKumov')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_group',
            description='Тестовое описание группы'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=IMAGE_TEST,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
            image=cls.uploaded.name
        )
        cls.group_url = reverse('posts:group',
                                kwargs={'slug': cls.post.group.slug})
        cls.profile_url = reverse('posts:profile',
                                  kwargs={'username': cls.user.username})
        cls.post_detail = reverse('posts:post_detail',
                                  kwargs={'post_id': cls.post.pk})

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_post_in_group_on_true_page(self):
        """Пост, входящий в группу, отображается
        на требуемых страницах и в требуемой группе"""
        page_url_names = [
            HOME,
            self.group_url,
            self.profile_url
        ]
        for template in page_url_names:
            with self.subTest(template=template):
                response = self.authorized_client.get(template)
                self.assertEqual(response.context['page_obj'][0].group.slug,
                                 self.post.group.slug)

    def test_post_with_image_on_true_page(self):
        """Пост с картинкой отображается на требуемых страницах"""
        page_url_names = [
            HOME,
            self.group_url,
            self.profile_url
        ]
        for template in page_url_names:
            with self.subTest(template=template):
                response = self.authorized_client.get(template)
                self.assertEqual(response.context['page_obj'][0].image,
                                 self.post.image)

        response = self.authorized_client.get(self.post_detail)
        self.assertEqual(response.context['post'].image,
                         self.post.image)


# Тестируем подписки
class FollowTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создали юзера-подписчика
        cls.user_follower = User.objects.create_user(
            username='TestFollower'
        )
        # Создали юзера-автора
        cls.user_author = User.objects.create_user(
            username='TestAuthor'
        )
        # Создали группу
        cls.group = Group.objects.create(
            title='Название группы для теста подписки',
            slug='group_slug_follow',
            description='Описание группы для теста подписок'
        )
        # Создали пост
        cls.post = Post.objects.create(
            author=cls.user_author,
            text='Текст поста для теста подписки',
            group=cls.group
        )
        # Создали путь для подписки
        cls.profile_follow_url = reverse(
            'posts:profile_follow',
            kwargs={'username': cls.user_author.username}
        )
        # путь на страницу автора
        cls.profile_url = reverse(
            'posts:profile',
            kwargs={'username': cls.user_author.username}
        )

    def setUp(self):
        self.guest_client = Client()
        self.client_user = Client()
        self.client_user.force_login(self.user_follower)
        self.client_author = Client()
        self.client_author.force_login(self.user_author)

    def test_follow(self):
        """Авторизованный пользователь может подписываться на
        других пользователей."""
        # Посчитали количество подписок
        count_of_followes = Follow.objects.all().count()
        response = self.client_user.post(self.profile_follow_url)
        # Проверили редирект
        self.assertRedirects(response, self.profile_url)
        # Снова посчитали количество подписок
        self.assertEqual(Follow.objects.count(), count_of_followes + 1)
        # Проверили, что подписка активна
        self.assertTrue(self.user_follower, self.user_author)
