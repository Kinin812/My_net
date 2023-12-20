from django.test import TestCase, Client
from django.urls import reverse


class AboutURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author_url = reverse('about:author')
        cls.tech_url = reverse('about:tech')

    def test_urls_posts_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            self.author_url: 'about/author.html',
            self.tech_url: 'about/tech.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = Client().get(address)
                self.assertTemplateUsed(response, template)
