from django.test import TestCase, Client

from ..models import Group, Post, User, Comment, Follow


class PostModelsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.user_commentator = User.objects.create_user(username='commentator')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая группа',
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user_commentator)
        self.comment = Comment.objects.create(
            post=self.post,
            author=self.user_commentator,
            text='Тестовый комментарий'
        )
        self.follow = Follow.objects.create(
            user=self.user_commentator,
            author=self.user
        )

    def test_model_post_have_correct_object_names(self):
        """Проверяем, что у модели Post корректно работает __str__."""
        post = self.post
        expected_object_name = post.text
        self.assertEqual(expected_object_name, str(post))

    def test_model_group_have_correct_object_names(self):
        """Проверяем, что у модели Group корректно работает __str__."""
        group = self.group
        expected_object_name = group.title
        self.assertEqual(expected_object_name, str(group))

    def test_verbose_names_post(self):
        """verbose_name в полях post совпадает с ожидаемым."""
        field_verboses = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа',
            'image': 'Картинка'
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.post._meta.get_field(field)
                        .verbose_name, expected_value)

    def test_verbose_names_group(self):
        """verbose_name в полях group совпадает с ожидаемым."""
        field_verboses = {
            'title': 'Название группы',
            'slug': 'Представление в url-е',
            'description': 'Описание группы'
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.group._meta.get_field(field)
                        .verbose_name, expected_value)

    def test_verbose_names_comment(self):
        """verbose_name в полях comment совпадает с ожидаемым."""
        field_verboses = {
            'post': 'Запись',
            'author': 'Автор комментария',
            'text': 'Текст комментария',
            'created': 'Дата публикации'
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.comment._meta.get_field(field)
                        .verbose_name, expected_value)

    def test_verbose_names_follow(self):
        """verbose_name в полях follow совпадает с ожидаемым."""
        field_verboses = {
            'user': 'Подписчик',
            'author': 'Автор'
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.follow._meta.get_field(field)
                        .verbose_name, expected_value)

    def test_help_text_post(self):
        """help_text в полях post совпадает с ожидаемым."""
        field_help_texts = {
            'text': 'Введите текст поста',
            'group': 'Выберите группу',
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.post._meta.get_field(field)
                        .help_text, expected_value)

    def test_help_text_group(self):
        """help_text в полях group совпадает с ожидаемым."""
        field_help_texts = {
            'title': 'Enter title .......',
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.group._meta.get_field(field)
                        .help_text, expected_value)

    def test_help_text_comment(self):
        """help_text в полях comment совпадает с ожидаемым."""
        field_help_texts = {
            'text': 'Введите текст комментария',
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.comment._meta.get_field(field)
                        .help_text, expected_value)
