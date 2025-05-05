from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MaxLengthValidator


class User(AbstractUser):
    """
    Inherits from Django's AbstractUser. No additional fields are added for now.
    """
    pass


class Post(models.Model):
    """
    Represents a user's post with a content limit of 140 characters.
    """
    content = models.CharField(
        max_length=140,

        validators=[MaxLengthValidator(140)],
        help_text="Maximum 140 characters."
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="author",
        help_text="The user who created this post."
    )
    date = models.DateTimeField(auto_now_add=True, help_text="Date and time the post was created.")

    def __str__(self):
        return f"Post {self.id} made by {self.user} on {self.date.strftime('%d %b %Y %H:%M:%S')}"

    class Meta:
        ordering = ["-date"]
        verbose_name = "Post"
        verbose_name_plural = "Posts"


class Follow(models.Model):
    """
    Represents a follow relationship where a user follows another user.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="user_who_is_following",
        help_text="The user who is following someone."
    )
    user_follower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="user_who_is_being_followed",
        help_text="The user being followed."
    )

    def __str__(self):
        return f"{self.user} is following {self.user_follower}"

    class Meta:
        verbose_name = "Follow"
        verbose_name_plural = "Follows"
        unique_together = ("user", "user_follower")  # Ensure one follow relationship per user pair.


class Like(models.Model):
    """
    Represents a 'like' relationship where a user likes a post.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="user_like",
        help_text="The user who liked the post."
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="post_like",
        help_text="The post that was liked."
    )

    def __str__(self):
        return f"{self.user} liked {self.post}"

    class Meta:
        verbose_name = "Like"
        verbose_name_plural = "Likes"
        unique_together = ("user", "post")  # Ensure a user can only like a post once.
