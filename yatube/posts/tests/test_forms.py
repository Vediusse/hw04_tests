from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from ..forms import PostForm
from ..models import Group, Post

User = get_user_model()


class TestCreateForm(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.group = Group.objects.create(
            title='Лев Толстой',
            slug='tolstoy',
            description='Группа Льва Толстого',
        )

        cls.author = User.objects.create_user(
            username='test_user',
            first_name='test',
            last_name='test',
            email='testuser@yatube.ru'
        )
        cls.user = User.objects.create_user(username='Vedius')

        cls.form = PostForm()

    def setUp(self):
        self.guest_client = Client()

        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_form_create(self):
        post_count = Post.objects.count()
        form_data = {
            'group': self.group.id,
            'text': 'Send',
        }
        response = self.authorized_client.post(reverse('posts:create'),
                                               data=form_data,
                                               follow=True)

        self.assertRedirects(response, reverse('posts:profile',
                                               args=[self.user.username]))
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(Post.objects.filter(
            text=form_data['text'],
            group=TestCreateForm.group).exists())

    def test_form_update(self):
        post = Post.objects.create(
            group=TestCreateForm.group,
            text="text",
            author=User.objects.get(username='Vedius'),
        )

        self.authorized_client.force_login(self.author)
        url = reverse('posts:edit', args=[post.id])
        self.authorized_client.get(url)
        form_data = {
            'group': self.group.id,
            'text': 'text',
        }
        self.authorized_client.post(
            reverse('posts:edit', args=[post.id]),
            data=form_data, follow=True)
        post.refresh_from_db()
        self.assertEqual(str(post), form_data['text'])
        self.assertEqual(post.group, self.group)
        self.assertEqual(post.author, self.user)
