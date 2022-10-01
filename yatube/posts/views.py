
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from .utilits import get_page
from .forms import PostForm
from .models import Group, User, Post


def index(request):
    posts = Post.objects.all()
    page_obj = get_page(request, posts)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.all()
    page_obj = get_page(request, posts)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    page_obj = get_page(request, posts)
    context = {
        'page_obj': page_obj,
        'author': author
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    post_amount = post.get_author_post
    context = {
        'post': post,
        'post_amount': post_amount
    }
    return render(request, 'posts/post_details.html', context)


@login_required
def create_post(request):
    form = PostForm(request.POST or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect("posts:profile", username=post.author)
    context = {
        "form": form,
        'is_edit': False
    }
    return render(request, "posts/create_post.html", context)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = PostForm(request.POST or None, instance=post)
    if request.user != post.author:
        return redirect("posts:post_detail", post_id)
    if form .is_valid():
        form.save()
        return redirect("posts:post_detail", post_id)
    context = {
        'form': form,
        'is_edit': True
    }
    return render(request, 'posts/create_post.html', context)
