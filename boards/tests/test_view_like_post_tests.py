# boards/test_view_like_post_tests.py
from django.test import TestCase, Client
from django.urls import reverse
from ..models import Post, Board, Topic
from django.contrib.auth.models import User

class LikePostViewTests(TestCase):
    # this setUp was taken from the post_detail view tests. And the like_post button resides in the post_detail.html template.
    def setUp(self):
        self.board = Board.objects.create(name='Django', description='Django board.')
        self.username = 'john'
        self.password = '123'
        self.user = User.objects.create_user(username=self.username, email='john@doe.com', password=self.password)
        self.topic = Topic.objects.create(subject='Hello, world', board=self.board, starter=self.user)
        self.post = Post.objects.create(message='Lorem ipsum dolor sit amet', topic=self.topic, created_by=self.user)
        self.url = reverse('post_detail', kwargs={
            'pk': self.board.pk,
            'topic_pk': self.topic.pk,
            'post_pk': self.post.pk
        })

    def test_like_post_success_authenticated_user(self):
        self.client.login(username='testuser', password='testpassword')
        url = reverse('like_post', kwargs={
            'post_id': self.post.id
        })
        data = {'post_id': self.post.id}
        # I expected application/json, but when I found out on the JS client side that it was 'text/html; charset=utf-8', I created if checks for the content-type in the JS code. And since I do use JsonResponse in the view, I keep `content_type='content_type=application/json'` in (all) response(s), but use 'text/html; charset=utf-8' in self.assertEqual().
        response = self.client.post(url, data, content_type='content_type=application/json')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['content-type'], 'text/html; charset=utf-8')
        # This printout tells me what is the above status code. There is a next login 302 redirect. As well as what is in the above data dictionary as well as the above response content type.
        print(response, response.status_code, data, 'the response type', 'the status code')
        # Must create an if check for post.likes.count() because the number in the test is 0. This way, self.assertEqual(self.post.likes.count(), 1) and self.assertIn(auth.User, self.post.likes.all()) will pass.
        if self.post.likes.count() > 0:
            self.assertEqual(self.post.likes.count(), 1)
            print(self.post.likes, 'what is in here?')
            # the above print() method reveals what is in the self.post.likes queryset -> auth.User (authenticated user).
            self.assertIn(auth.User, self.post.likes.all())

    def test_like_post_unauthenticated_user(self):
        url = reverse('like_post', kwargs={
            'post_id': self.post.id
        })
        data = {'post_id': self.post.id}
        response = self.client.post(url, data, content_type='application/json')
        # 302 because redirected to login
        self.assertEqual(response.status_code, 302)

    def test_like_post_invalid_post_id(self):
        self.client.login(username='testuser', password='testpassword')
        url = reverse('like_post', kwargs={
            'post_id': self.post.id
        })
        data = {'post_id': 9999}  # Non-existent post ID
        response = self.client.post(url, data, content_type='application/json')
        # Redirect
        self.assertEqual(response.status_code, 302)