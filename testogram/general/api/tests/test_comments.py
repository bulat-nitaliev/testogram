from rest_framework.test import APITestCase
from rest_framework import status
from general.factories import PostFactory, UserFactory,  CommentFactory
from general.models import Comment
from django.utils.timezone import make_naive


class CommentsTestCase(APITestCase):
    def setUp(self):
        self.user = UserFactory()
        self.client.force_authenticate(user=self.user)
        self.post = PostFactory()
        self.url = "/api/comments/"
        print(self)

    def test_create_comment(self):
        data = {
            "post": self.post.pk,
            "body": "new comment"
        }
        response = self.client.post(path=self.url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        comment = Comment.objects.last()
        self.assertEqual(comment.post.id, data["post"])
        self.assertEqual(comment.body, data["body"])
        self.assertEqual(self.user, comment.author)
        self.assertIsNotNone(comment.created_at)

    def test_pass_incorrect_post_id(self):
        data = {
            "post": self.post.pk + 1,
            "body": "new comment"
        }
        response = self.client.post(path=self.url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_own_comment(self):
        comment = CommentFactory(author=self.user)
        response = self.client.delete(path=f"{self.url}{comment.pk}/", format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Comment.objects.all().count(), 0)


    def test_delete_other_comment(self):
        comment = CommentFactory()
        response = self.client.delete(path=f"{self.url}{comment.pk}/", format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Comment.objects.all().count(), 1)
        self.assertEqual(response.data["detail"], "Вы не являетесь автором этого комментария.") 

    def test_comment_list_filtered_by_post_id(self):
        comments = CommentFactory.create_batch(5, post=self.post)
        CommentFactory.create_batch(5)
        url = f"{self.url}?post__id={self.post.pk}"
        response = self.client.get(path=url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]),5)

        comment_ids = {comment.id for comment in comments}
        for comment in response.data["results"]:
            self.assertTrue(comment["id"] in comment_ids)

    def test_comment_data_structure(self):
        CommentFactory(post=self.post)
        url = f"{self.url}?post__id={self.post.pk}"
        response = self.client.get(path=url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        comment = Comment.objects.last()
        expected_data = {
            "id": comment.pk,
            "author":{
                "id": comment.author.id, 
                "first_name": comment.author.first_name, 
                "last_name": comment.author.last_name
            },
            "post": comment.post.id,
            "body": comment.body,
            "created_at": make_naive(comment.created_at).strftime("%Y-%m-%dT%H:%M:%S"),
        }
        self.assertDictEqual(response.data["results"][0], expected_data)

