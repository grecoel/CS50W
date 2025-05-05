from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.core.paginator import Paginator
import json
from django.db.models import Count
from django.views.decorators.csrf import csrf_exempt
from .models import User, Post, Follow, Like


def add_like(request, post_id):
    user = request.user
    post = Post.objects.get(pk=post_id)
    Like.objects.create(user=user, post=post)
    like_count = Like.objects.filter(post=post).count()
    return JsonResponse({"message": "Like added!", "like_count": like_count})

def remove_like(request, post_id):
    user = request.user
    post = Post.objects.get(pk=post_id)
    Like.objects.filter(user=user, post=post).delete()
    like_count = Like.objects.filter(post=post).count()
    return JsonResponse({"message": "Like removed!", "like_count": like_count})


@csrf_exempt
def edit(request, post_id):
    if request.method == "POST" and request.user.is_authenticated:  # Ensure method matches frontend
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data."}, status=400)

        # Get post and verify ownership
        post = get_object_or_404(Post, pk=post_id, user=request.user)

        # Validate content
        content = data.get("content", "").strip()
        if not content:
            return JsonResponse({"error": "Content cannot be empty."}, status=400)

        # Update and save the post
        post.content = content
        post.save()
        return JsonResponse({"message": "Change successful", "data": post.content}, status=200)

    return JsonResponse({"error": "Invalid request or user not authenticated."}, status=400)


def index(request):
    # Annotate each post with its like count
    all_posts = Post.objects.annotate(like_count=Count('post_like')).order_by("-date")

    # Pagination
    paginator = Paginator(all_posts, 10)  # Display 10 posts per page
    page_number = request.GET.get('page')
    posts_of_the_page = paginator.get_page(page_number)

    # Track posts the user has liked (if authenticated)
    who_you_liked = []
    if request.user.is_authenticated:
        who_you_liked = Like.objects.filter(user=request.user).values_list('post__id', flat=True)

    return render(request, "network/index.html", {
        "posts_of_the_page": posts_of_the_page,
        "whoYouLiked": who_you_liked
    })

def new_post(request):
    if request.method == "POST" and request.user.is_authenticated:
        content = request.POST.get('content', '').strip()
        if content:
            Post.objects.create(content=content, user=request.user)
            return HttpResponseRedirect(reverse("index"))
        return render(request, "network/index.html", {"message": "Post content cannot be empty."})
    return JsonResponse({"error": "Invalid request."}, status=400)


def profile(request, user_id):
    user_profile = get_object_or_404(User, pk=user_id)
    all_posts = Post.objects.filter(user=user_profile).order_by("-id")

    following = Follow.objects.filter(user=user_profile).count()
    followers = Follow.objects.filter(user_follower=user_profile).count()

    is_following = False
    if request.user.is_authenticated:
        is_following = Follow.objects.filter(user=request.user, user_follower=user_profile).exists()

    # Pagination
    paginator = Paginator(all_posts, 10)
    page_number = request.GET.get('page')
    posts_of_the_page = paginator.get_page(page_number)

    return render(request, "network/profile.html", {
        "posts_of_the_page": posts_of_the_page,
        "username": user_profile.username,
        "following": following,
        "followers": followers,
        "isFollowing": is_following,
        "user_profile": user_profile
    })


def following(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))

    following_people = Follow.objects.filter(user=request.user).values_list('user_follower', flat=True)
    following_posts = Post.objects.filter(user__in=following_people).order_by("-id")

    # Pagination
    paginator = Paginator(following_posts, 10)
    page_number = request.GET.get('page')
    posts_of_the_page = paginator.get_page(page_number)

    return render(request, "network/following.html", {
        "posts_of_the_page": posts_of_the_page
    })


def follow(request):
    if request.method == "POST" and request.user.is_authenticated:
        userfollow = request.POST.get('userfollow')
        user_to_follow = get_object_or_404(User, username=userfollow)
        if not Follow.objects.filter(user=request.user, user_follower=user_to_follow).exists():
            Follow.objects.create(user=request.user, user_follower=user_to_follow)
        return HttpResponseRedirect(reverse(profile, kwargs={'user_id': user_to_follow.id}))
    return JsonResponse({"error": "Invalid request."}, status=400)


def unfollow(request):
    if request.method == "POST" and request.user.is_authenticated:
        userfollow = request.POST.get('userfollow')
        user_to_unfollow = get_object_or_404(User, username=userfollow)
        follow = Follow.objects.filter(user=request.user, user_follower=user_to_unfollow)
        if follow.exists():
            follow.delete()
        return HttpResponseRedirect(reverse(profile, kwargs={'user_id': user_to_unfollow.id}))
    return JsonResponse({"error": "Invalid request."}, status=400)


def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        return render(request, "network/login.html", {"message": "Invalid username and/or password."})
    return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {"message": "Passwords must match."})

        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {"message": "Username already taken."})
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    return render(request, "network/register.html")
