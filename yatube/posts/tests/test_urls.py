from django.contrib.auth import get_user_model
from django.test import TestCase, Client

from ..models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='leo',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='HasNoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_urls_uses_correct_template(self):

        templates_url_names = {
            '/': 200,
            f'/group/{self.group.slug}/': 200,
            f'/profile/{self.user}/': 200,
            f'/posts/{self.post.id}/': 200,
            '/create/': 302,
            '/unexisting_page/': 404
        }
        for address, status in templates_url_names.items():
            with self.subTest(address=address):

                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, status)