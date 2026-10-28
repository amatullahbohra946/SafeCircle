
from django.db import models
import random
import string


class UserProfile(models.Model):
    email = models.EmailField(unique=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    anonymous_username = models.CharField(max_length=50, unique=True)
    avatar = models.CharField(max_length=50, blank=True)
    community = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.anonymous_username


class Post(models.Model):
    author = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE
    )
    content = models.TextField()
    community = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.author.anonymous_username


class Reply(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="replies"
    )
    author = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE
    )
    content = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reply by {self.author.anonymous_username}"
    
class Mood(models.Model):
    MOOD_CHOICES = [
        ("Happy", "Happy"),
        ("Okay", "Okay"),
        ("Sad", "Sad"),
        ("Angry", "Angry"),
        ("Anxious", "Anxious"),
    ]

    user = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name="moods"
    )
    mood = models.CharField(
        max_length=10,
        choices=MOOD_CHOICES
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.anonymous_username} - {self.mood}"
    
class Journal(models.Model):
    user = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name="journal_entries"
    )
    title = models.CharField(max_length=100, blank=True)
    mood = models.CharField(max_length=20, blank=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title or f"Journal entry {self.id}"

class Report(models.Model):
    reporter = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name="reports_made"
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="reports"
    )
    reason = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["reporter", "post"],
                name="unique_report_per_user_post"
            )
        ]

    def __str__(self):
        return f"Report on post {self.post.id}"


class Block(models.Model):
    blocker = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name="users_blocked"
    )
    blocked = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name="blocked_by_users"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["blocker", "blocked"],
                name="unique_block_per_user"
            )
        ]

    def __str__(self):
        return f"{self.blocker} blocked {self.blocked}"
def generate_anonymous_username():
    characters = string.ascii_uppercase + string.digits

    while True:
        code = ''.join(random.choices(characters, k=5))
        username = f"SC_{code}"

        if not UserProfile.objects.filter(anonymous_username=username).exists():
            return username
