from rest_framework.test import APITestCase
import json
from rest_framework import status
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth.hashers import check_password
from general.factories import PostFactory, UserFactory
from general.models import Post, User
from django.utils.timezone import make_naive

class PostTestCase(APITestCase):
    def setUp(self) -> None:
        self.user = UserFactory()
        self.client.force_authenticate(user=self.user)
        self.url = '/api/posts/'
        print(self)

    def test_create_post(self):
        data = {
            "title": "some post title",
            "body": "some text",
        }
        response = self.client.post(path=self.url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        post = Post.objects.last()
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.title, data["title"])
        self.assertEqual(post.body, data["body"])
        self.assertIsNotNone(post.created_at)


