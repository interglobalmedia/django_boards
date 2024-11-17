from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView, DeleteView
from django.utils import timezone
from django.utils.decorators import method_decorator
from .forms import NewTopicForm
from .forms import PostForm
from .models import Board, Topic, Post
from accounts.models import Profile
from django.contrib.auth.models import User
import math
import nh3
from django.http import JsonResponse

@login_required
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    # Toggle the like status
    if request.user in post.likes.all():
        post.likes.remove(request.user)
        liked = False
    else:
        post.likes.add(request.user)
        liked = True

        return JsonResponse({'likes_count': post.likes.count(), 'liked': liked})

    return JsonResponse({'error': 'Invalid request'})

@method_decorator(login_required, name='dispatch')
class PostDetailView(DetailView):
    model = Post
    fields = ('message', )
    template_name = 'post_detail.html'
    pk_url_kwarg = 'post_pk'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class BoardListView(ListView):
    model = Board
    context_object_name = 'boards'
    template_name = 'index.html'

class TopicListView(ListView):
    model = Topic
    context_object_name = 'topics'
    template_name = 'topics.html'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        kwargs['board'] = self.board
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        self.board = get_object_or_404(Board, pk=self.kwargs.get('pk'))
        queryset = self.board.topics.order_by('-last_updated').annotate(replies=Count('posts') - 1)
        return queryset

@login_required
def new_topic(request, pk):
    board = get_object_or_404(Board, pk=pk)
    if request.method == 'POST':
        form = NewTopicForm(request.POST)
        if form.is_valid():
            topic = form.save(commit=False)
            topic.board = board
            topic.starter = request.user
            topic.save()
            Post.objects.create(
                message=form.cleaned_data.get('message'),
                topic=topic,
                created_by=request.user
            )
            # redirect to topic_posts view
            return redirect('topic_posts', pk=pk, topic_pk=topic.pk)
    else:
        form = NewTopicForm()
    return render(request, 'new_topic.html', {'board': board, 'form': form})

@method_decorator(login_required, name='dispatch')
class PostListView(ListView):
    model = Post
    context_object_name = 'posts'
    template_name = 'topic_posts.html'
    paginate_by = 10

    def get_context_data(self, **kwargs):

        session_key = 'viewed_topic_{}'.format(self.topic.pk)
        if not self.request.session.get(session_key, False):
            self.topic.views += 1
            self.topic.save()
            self.request.session[session_key] = True
        kwargs['topic'] = self.topic
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        self.topic = get_object_or_404(Topic, board__pk=self.kwargs.get('pk'), pk=self.kwargs.get('topic_pk'))
        queryset = list(reversed(self.topic.posts.order_by('created_at')))
        return queryset

@login_required
def reply_topic(request, pk, topic_pk):
    topic = get_object_or_404(Topic, board__pk=pk, pk=topic_pk)
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.topic = topic
            post.created_by = request.user
            post.save()
            print(post.save, 'save the replied data')
            topic.last_updated = timezone.now()
            topic.save()

            topic_url = reverse('topic_posts', kwargs={'pk': pk, 'topic_pk': topic_pk})
            topic_post_url = '{url}?page={page}#{id}'.format(
                url=topic_url,
                id=post.pk,
                page=topic.get_page_count()
            )

            return redirect(topic_post_url)
    else:
        form = PostForm()
    return render(request, 'reply_topic.html', {'topic': topic, 'form': form})

@method_decorator(login_required, name='dispatch')
class PostUpdateView(UpdateView):
    model = Post
    fields = ('message', )
    template_name = 'edit_post.html'
    pk_url_kwarg = 'post_pk'
    context_object_name = 'post'
    success_url = "/"

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(created_by=self.request.user)

    def form_valid(self, form):
        if form:
            form.instance.message = nh3.clean(form.instance.message,
                tags={
                    "a",
                    "abbr",
                    "acronym",
                    "b",
                    "blockquote",
                    "code",
                    "em",
                    "i",
                    "li",
                    "ol",
                    "strong",
                    "ul",
                    "s",
                    "sup",
                    "sub",
                },
                attributes={
                    "a": {"href"},
                    "abbr": {"title"},
                    "acronym": {"title"},
                },
                url_schemes={"https"},
                link_rel=None,)
            super().form_valid(form)
        post = form.save(commit=False)
        post.updated_by = self.request.user
        post.updated_at = timezone.now()
        post.save()
        return redirect('topic_posts', pk=post.topic.board.pk, topic_pk=post.topic.pk)

@method_decorator(login_required, name='dispatch')
class PostDeleteView(DeleteView):

    # just as for PostUpdateView, this makes sure the UnauthorizedPostDeleteViewTests status_code test passes, making sure that if the user trying to delete the post does not equal the owner of the post (set here via filter), then they cannot delete the post, and a status code of 404 is rendered instead of 200.
    def get_queryset(self): # added
        queryset = super().get_queryset()
        return queryset.filter(created_by=self.request.user)

    model = Post
    template_name = "post_confirm_delete.html"
    pk_url_kwarg = "post_pk"
    # can specify success url
    # url to redirect after successfully
    # deleting object
    success_url = "/"


