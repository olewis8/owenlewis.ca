from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import RedirectView
from django.utils.decorators import method_decorator

from .models import Profile

from blog.models import BlogPost


def login_page(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.success(request, 'username and password don\'t match')
            return redirect('login')

    else:
        template_name = 'authenticate/login.html'
        context = {'title': 'log in'}

        return render(request, template_name, context)


@login_required
def logout_page(request):
    template_name = 'authenticate/logout.html'
    context = {'title': 'log out'}

    if request.method == 'POST':
        logout(request)
        return redirect('home')

    return render(request, template_name, context)


def register_page(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()

            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']

            user = authenticate(request, username=username, password=password)
            login(request, user)

            return redirect('home')
    else:
        form = UserCreationForm()

    template_name = 'authenticate/register.html'
    context = {'title': 'create account',
               'form': form}

    return render(request, template_name, context)


def profile_page(request, username):
    template_name = 'pages/profile.html'

    return render(request, template_name)


def follows_page(request, username):
    template_name = 'pages/follows.html'

    return render(request, template_name)


def retrieve_bio_data(request, username):
    user = get_object_or_404(User, username=username)
    profile = get_object_or_404(Profile, user=user)
    data = profile.serialize()

    return JsonResponse(data)


@method_decorator(csrf_exempt, name='dispatch')
class toggle_follow(RedirectView):
    def get_redirect_url(self, *args, **kwargs):

        user = get_object_or_404(User, username=self.request.user)
        target_user = get_object_or_404(User, username=kwargs.get('username'))

        profile = get_object_or_404(Profile, user=user)
        target_profile = get_object_or_404(Profile, user=target_user)

        url_ = Profile.objects.get(user=target_user).get_profile_url()

        if user.is_authenticated:
            if profile in target_profile.followers.all():
                target_profile.followers.remove(profile)
                user.profile.following.remove(target_profile)
            else:
                target_profile.followers.add(profile)
                user.profile.following.add(target_profile)

        return url_


def retrieve_user_followers(request, username):
    user = get_object_or_404(User, username=username)
    qs = user.profile.followers.all()
    response = [x.serialize() for x in qs]
    data = {'response': response}

    return JsonResponse(data)


def retrieve_user_following(request, username):
    user = get_object_or_404(User, username=username)
    qs = user.profile.following.all()
    response = [x.serialize() for x in qs]
    data = {'response': response}

    return JsonResponse(data)
