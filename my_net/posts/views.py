from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic.edit import CreateView

from .forms import PostForm, CommentForm
from .mixins import AuthenticatedMixin
from .models import Post, Group, Comment, Follow, User


def paginator_for_all_funcs(request, post_list):
    paginator = Paginator(post_list, settings.POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj


def index(request):
    template = 'posts/index.html'
    post_list = Post.objects.all()
    context = {
        'page_obj': paginator_for_all_funcs(request, post_list),
    }
    return render(request, template, context)


def group_posts(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    post_list = group.groups.all()
    context = {
        'group': group,
        'page_obj': paginator_for_all_funcs(request, post_list),
    }
    return render(request, template, context)


def profile(request, username):
    template = 'posts/profile.html'
    user = get_object_or_404(User, username=username)
    post_list = (user.posts.select_related('author').
                 select_related('group').all())
    context = {
        'author': user,
        'page_obj': paginator_for_all_funcs(request, post_list),
        'post_list': post_list
    }
    if request.user.is_authenticated:
        authors = Follow.objects.filter(
            user=request.user
        ).values_list('author_id', flat=True)
        if user.id in authors:
            following = True
        else:
            following = False
        context.update({'following': following})
    return render(request, template, context)


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    post = Post.objects.get(id=post_id)
    authors_posts = Post.objects.filter(author=post.author)
    post_count = authors_posts.count()
    form = CommentForm()
    comments = Comment.objects.filter(post_id=post_id)
    context = {
        'post': post,
        'authors_posts': authors_posts,
        'post_count': post_count,
        'form': form,
        'comments': comments,
    }
    return render(request, template, context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


# @login_required
class PostCreate(CreateView, AuthenticatedMixin):
    form_class = PostForm
    template_name = 'posts/create_post.html'
    success_url = reverse_lazy('index')


@login_required
def post_create(request):
    template = 'posts/create_post.html'
    if request.method == 'POST':
        form = PostForm(
            request.POST or None,
            files=request.FILES or None
        )
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.pub_date = timezone.now()
            post.save()
            return redirect('posts:profile', username=request.user.username)
    else:
        form = PostForm()
    context = {
        'form': form,
        'title': 'Новая запись',
        'btn_text': 'Добавить'
    }
    return render(request, template, context)


def post_edit(request, post_id):
    template = 'posts/create_post.html'
    post = get_object_or_404(Post, id=post_id)
    if post.author == request.user:
        if request.method == 'POST':
            form = PostForm(
                request.POST or None,
                files=request.FILES or None,
                instance=post
            )
            if form.is_valid():
                post = form.save(commit=False)
                post.author = request.user
                post.pub_date = timezone.now()
                post.save()
                return redirect('posts:post_detail', post_id=post.id)
        else:
            form = PostForm(instance=post)
        context = {
            'form': form,
            'title': 'Редактировать запись',
            'btn_text': 'Сохранить'
        }
        return render(request, template, context)
    else:
        return redirect('posts:post_detail', post_id=post.id)


@login_required
def follow_index(request):
    template = 'posts/follow.html'
    follower_user = request.user
    user_following_authors = Follow.objects.filter(
        user=follower_user).values('author')
    post_list = Post.objects.filter(author__in=user_following_authors)
    context = {
        'page_obj': paginator_for_all_funcs(request, post_list),
    }
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    # Подписаться на автора
    author = get_object_or_404(User, username=username)
    user = request.user
    if author != user:
        Follow.objects.get_or_create(user=user, author=author)
        return redirect('posts:profile', username=author)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
def profile_unfollow(request, username):
    # Дизлайк, отписка
    author = get_object_or_404(User, username=username)
    user = request.user
    Follow.objects.get(user=user, author=author).delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
