# posts/tests/tests_form.py
import shutil
import tempfile

from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

from ..forms import PostForm
from ..models import Post, Group, User, Comment

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
CREATE_POST = '/create/'
IMAGE_TEST = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='KumKumov')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_group',
            description='Тестовое описание группы'
        )

        cls.form = PostForm()
        cls.profile_url = reverse('posts:profile',
                                  kwargs={'username': cls.user.username})

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

        self.post = Post.objects.create(
            text='Тестовый текст',
            author=self.user,
            group=self.group
        )

    def test_create_post(self):
        posts_count = Post.objects.count()
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=IMAGE_TEST,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Тестовый текст',
            'author': self.user,
            'group': self.group.pk,
            'image': uploaded,
        }
        # Отправляем POST-запрос
        response = self.authorized_client.post(
            CREATE_POST,
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, self.profile_url)
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый текст',
                image='posts/small.gif'
            ).exists()
        )


class PostEditFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='KumKumov')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_group',
            description='Тестовое описание группы'
        )
        # Создаем запись в базе данных
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group,
        )
        cls.post_after_edit = {
            'text': 'Текст поста после изменения',
            'group': cls.group.pk,
        }
        # Создаем форму
        cls.form = PostForm()
        cls.post_detail_url = reverse(
            'posts:post_detail', kwargs={'post_id': cls.post.pk})

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_edit_post(self):
        response = self.authorized_client.post(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.pk}
            ),
            data=self.post_after_edit,
            follow=True
        )
        self.assertRedirects(response, self.post_detail_url)
        self.post.refresh_from_db()
        self.assertEqual(self.post.text, self.post_after_edit['text'])


class CommentCreateFormTests(TestCase):
    """комментировать посты может только авторизованный пользователь.
    после успешной отправки комментарий появляется на странице поста"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='KumKumov')

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

        self.post = Post.objects.create(
            text='Тестовый текст',
            author=self.user
        )
        self.post_detail_url = reverse(
            'posts:post_detail', kwargs={'post_id': self.post.pk})
        self.create_comment = reverse(
            'posts:add_comment', kwargs={'post_id': self.post.pk})

    def test_create_comment(self):
        posts_comments_count = Comment.objects.count()
        form_data = {
            'text': 'Тестовый коммент',
            'author': self.user,
            'post': self.post
        }
        response = self.authorized_client.post(
            self.create_comment,
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, self.post_detail_url)
        self.assertEqual(Comment.objects.count(), posts_comments_count + 1)
        self.assertTrue(
            Comment.objects.filter(
                text='Тестовый коммент',
                author=self.user,
                post=self.post
            ).exists()
        )
