from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.db import IntegrityError
from .models import UserProfile , Post , Reply , Mood , Journal , Report, Block
from django.contrib.auth import authenticate, login
from datetime import date
import random
from .models import UserProfile, generate_anonymous_username
def home(request):
    return render(request, "index.html")


def login_page(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "")

        user = authenticate(
            request,
            username=email,
            password=password
        )

        if user is not None:
            login(request, user)
            return redirect("dashboard")

        messages.error(request, "Invalid email or password.")

    return render(request, "login.html")


def register_page(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")
        dob = request.POST.get("date_of_birth", "").strip()
        confirm_dob = request.POST.get("confirm_date_of_birth", "").strip()
        username = generate_anonymous_username()
        if not all([
            email, password, confirm_password,
            dob, confirm_dob, 
        ]):
            messages.error(request, "Please fill in all fields.")
            return redirect("register")

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect("register")

        if dob != confirm_dob:
            messages.error(request, "Dates of birth do not match.")
            return redirect("register")

        try:
            date_of_birth = date.fromisoformat(dob)
            today = date.today()

            if date_of_birth > today:
                raise ValueError

            if date_of_birth < date(1900, 1, 1):
                raise ValueError

            age = today.year - date_of_birth.year

            if (today.month, today.day) < (
                date_of_birth.month, date_of_birth.day
            ):
                age -= 1

            if not 1 <= age <= 120:
                raise ValueError

        except ValueError:
            messages.error(
                request,
                "Please enter a valid date of birth."
            )
            return redirect("register")

        if User.objects.filter(username=email).exists():
            messages.error(
                request,
                "This email is already registered."
            )
            return redirect("register")

        
        user = None
        try:
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password
            )

            avatars = [
                "girl1",
                "boy1",
                "girl2",
                "boy2",
                "neutral1",
                "neutral2"
            ]

            if age <= 17:
                community = "Teen Community"
            elif age <= 24:
                community = "Young Adults Community"
            else:
                community = "Adults Community"

            selected_avatar = random.choice(avatars)

            UserProfile.objects.create(
                email=email,
                age=age,
                date_of_birth=date_of_birth,
                anonymous_username=username,
                avatar=selected_avatar,
                community=community
            )

        except IntegrityError:
            if user is not None:
                user.delete()

            messages.error(
                request,
                "Registration failed. Please try again."
            )
            return redirect("register")

        messages.success(
            request,
            "Account created successfully! Please log in."
        )
        return redirect("login")

    return render(request, "register.html")



def community_page(request):
    if not request.user.is_authenticated:
        return redirect("login")

    profile = UserProfile.objects.get(email=request.user.email)

    if request.method == "POST":
        action = request.POST.get("action", "")

        # REPORT A POST
        if action == "report":
            post_id = request.POST.get("post_id")
            reason = request.POST.get("reason", "").strip()

            post = Post.objects.filter(
                id=post_id,
                community=profile.community
            ).first()

            if post and post.author != profile and reason:
                Report.objects.get_or_create(
                    reporter=profile,
                    post=post,
                    defaults={"reason": reason}
                )
                messages.success(
                    request,
                    "Thank you. Your report has been recorded."
                )
            else:
                messages.error(
                    request,
                    "Unable to submit this report."
                )

            return redirect("community")

        # BLOCK A USER
        elif action == "block":
            post_id = request.POST.get("post_id")

            post = Post.objects.filter(
                id=post_id,
                community=profile.community
            ).first()

            if post and post.author != profile:
                Block.objects.get_or_create(
                    blocker=profile,
                    blocked=post.author
                )
                messages.success(
                    request,
                    "This user has been blocked."
                )
            else:
                messages.error(
                    request,
                    "You cannot block this user."
                )

            return redirect("community")

        # REPLY TO A POST
        reply_content = request.POST.get(
            "reply_content", ""
        ).strip()
        post_id = request.POST.get("post_id")

        if reply_content and post_id:
            post = Post.objects.filter(
                id=post_id,
                community=profile.community
            ).first()

            blocked_users = Block.objects.filter(
                blocker=profile
            ).values_list("blocked_id", flat=True)

            if (
                post
                and post.author_id not in blocked_users
                and post.author != profile
            ):
                Reply.objects.create(
                    post=post,
                    author=profile,
                    content=reply_content
                )

        # CREATE A NEW POST
        else:
            content = request.POST.get("content", "").strip()

            if content:
                Post.objects.create(
                    author=profile,
                    content=content,
                    community=profile.community
                )

        return redirect("community")

    # Hide posts from users this person has blocked
    blocked_users = Block.objects.filter(
        blocker=profile
    ).values_list("blocked_id", flat=True)

    posts = Post.objects.filter(
        community=profile.community
    ).exclude(
        author_id__in=blocked_users
    ).order_by("-created_at")

    return render(
        request,
        "community.html",
        {
            "profile": profile,
            "posts": posts
        }
    )



def dashboard_page(request):

    if request.user.is_authenticated:
        profile = UserProfile.objects.get(email=request.user.email)
        return render(request, "dashboard.html", {"profile": profile})

    return redirect("login")


def mood_page(request):
    if not request.user.is_authenticated:
        return redirect("login")

    profile = UserProfile.objects.get(email=request.user.email)

    if request.method == "POST":
        selected_mood = request.POST.get("mood")

        if selected_mood in ["Happy", "Okay", "Sad", "Angry", "Anxious"]:
            Mood.objects.create(
                user=profile,
                mood=selected_mood
            )
            messages.success(request, "Your mood has been saved!")
            return redirect("mood")

        messages.error(request, "Please select a valid mood.")

    return render(request, "mood.html")


def journal_page(request):
    if not request.user.is_authenticated:
        return redirect("login")

    profile = UserProfile.objects.get(email=request.user.email)

    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        mood = request.POST.get("mood", "").strip()
        content = request.POST.get("content", "").strip()

        if not content:
            messages.error(request, "Please write your thoughts first.")
            return redirect("journal")

        Journal.objects.create(
            user=profile,
            title=title,
            mood=mood,
            content=content
        )

        messages.success(request, "Your journal entry has been saved!")
        return redirect("journal")

    return render(request, "journal.html")
