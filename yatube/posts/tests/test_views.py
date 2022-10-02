from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Post, Group
from django.conf import settings

User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        User.objects.create(username="Bazz")
        cls.user = User.objects.get(username="Bazz")
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="test-slug",
        )
        post_objs = [
            Post(
                text=f"Пост №{i+1}",
                author=User.objects.get(username="Bazz"),
                group=Group.objects.get(slug="test-slug"),
            )
            for i in range(settings.POST_PAGE_AMOUNT)
        ]
        Post.objects.bulk_create(post_objs)

        cls.last_post_id = Post.objects.latest("pub_date").id

        cls.templates_pages_names = {
            reverse("posts:index"): "posts/index.html",
            reverse(
                "posts:group_list", kwargs={"slug": "test-slug"}
            ): "posts/group_list.html",
            reverse("posts:create"): "posts/create_post.html",
            reverse(
                "posts:post_detail",
                kwargs={"post_id": PostPagesTests.last_post_id},
            ): "posts/post_details.html",
            reverse(
                "posts:edit",
                kwargs={"post_id": PostPagesTests.last_post_id},
            ): "posts/create_post.html",
            reverse(
                "posts:profile",
                kwargs={"username": "Bazz"},
            ): "posts/profile.html",
        }

    def setUp(self):

        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.group = Group.objects.get(slug="test-slug")

    def test_pages_uses_correct_template(self):
        for (
            reverse_name,
            template,
        ) in PostPagesTests.templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_paginator_and_sorting_by_pubdate(self):
        FIELDS = (
            PostPagesTests.last_post_id,
            f"Пост №{PostPagesTests.last_post_id}",
            self.user,
            self.group,
        )
        view_funcs = {
            reverse("posts:index"): "?page=2",
            reverse(
                "posts:group_list", kwargs={"slug": "test-slug"}
            ): "?page=2",
            reverse("posts:profile", kwargs={"username": "Bazz"}): "?page=2",
        }

        for reverse_name, page_number in view_funcs.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.client.get(reverse_name)
                self.assertEqual(len(response.context["page_obj"]),
                                 settings.PAGE_AMOUNT)
                response = self.client.get(reverse_name + page_number)
                self.assertEqual(len(response.context["page_obj"]),
                                 settings.POST_PAGE_AMOUNT
                                 - settings.PAGE_AMOUNT)
                response = self.authorized_client.get(reverse_name)
                first_object = response.context["page_obj"][0]
                self.assertEqual(first_object.id, FIELDS[0])
                self.assertEqual(first_object.text, FIELDS[1])
                self.assertEqual(first_object.author, FIELDS[2])
                self.assertEqual(first_object.group, FIELDS[3])

    def test_forms_pages(self):
        view_funcs = {
            reverse("posts:create"): forms.ModelForm,
            reverse(
                "posts:edit", kwargs={"post_id": 10}
            ): forms.ModelForm,
        }
        for reverse_name, clss in view_funcs.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                form_obj = response.context["form"]
                self.assertIsInstance(form_obj, clss)

    def test_post_detail(self):
        response = self.client.get(
            reverse(
                "posts:post_detail",
                kwargs={"post_id": PostPagesTests.last_post_id},
            )
        )
        obj = response.context["post"]
        fields = {
            obj.id: PostPagesTests.last_post_id,
            obj.text: f"Пост №{PostPagesTests.last_post_id}",
            obj.author: self.user,
            obj.group: self.group,
        }
        for field, correct_field in fields.items():
            self.assertEqual(field, correct_field)

    def test_form_post_creation(self):
        fields = [
            "Test post creation",
            self.user,
            self.group,
        ]
        Post.objects.create(text=fields[0], author=fields[1], group=fields[2])
        view_funcs = [
            reverse("posts:index"),
            reverse("posts:group_list", kwargs={"slug": self.group.slug}),
            reverse("posts:profile", kwargs={"username": self.user.username}),
        ]
        for reverse_name in view_funcs:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                first_object = response.context["page_obj"][0]
                self.assertEqual(first_object.text, fields[0])
                self.assertEqual(first_object.author, fields[1])
                self.assertEqual(first_object.group, fields[2])
