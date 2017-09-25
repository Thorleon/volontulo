# -*- coding: utf-8 -*-

"""
.. module:: auth
"""

from django.contrib import auth
from django.contrib import messages
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db.utils import IntegrityError
from django.shortcuts import redirect
from django.shortcuts import render
from django.utils.http import is_safe_url
from django.views.generic import View

from apps.volontulo.forms import UserForm
from apps.volontulo.lib.email import FROM_ADDRESS
from apps.volontulo.lib.email import send_mail
from apps.volontulo.models import UserProfile


def login(request):
    """Login view.

    :param request: WSGIRequest instance
    """
    if request.user.is_authenticated():
        messages.success(
            request,
            'Jesteś już zalogowany.'
        )
        return redirect('homepage')

    redirect_to = request.POST.get('next', request.GET.get('next', 'homepage'))
    user_form = UserForm()

    if request.method == 'POST':
        username = request.POST.get('email')
        password = request.POST.get('password')
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                auth.login(request, user)
                messages.success(
                    request,
                    'Poprawnie zalogowano'
                )

                # Ensure the user-originating redirection url is safe.
                if not is_safe_url(url=redirect_to, host=request.get_host()):
                    redirect_to = reverse('homepage')

                return redirect(redirect_to)
            else:
                messages.info(
                    request,
                    'Konto jest nieaktywne, skontaktuj się z administratorem.'
                )
        else:
            messages.error(
                request,
                'Nieprawidłowy email lub hasło!'
            )
    return render(
        request,
        'auth/login.html',
        {
            'user_form': user_form,
            'next': redirect_to,
        }
    )


@login_required
def logout(request):
    """Logout view.

    :param request: WSGIRequest instance
    """
    auth.logout(request)
    messages.info(
        request,
        "Użytkownik został wylogowany!"
    )
    return redirect('homepage')


class Register(View):
    """View responsible for registering new users."""

    @staticmethod
    def get(request, user_form=None):
        """Simple view to render register form.

        :param request: WSGIRequest instance
        :param user_form: UserForm instance
        """
        if request.user.is_authenticated():
            messages.success(
                request,
                'Jesteś już zalogowany.'
            )
            return redirect('homepage')

        return render(
            request,
            'auth/login.html',
            {
                'user_form': UserForm() if user_form is None else user_form,
            }
        )

    @classmethod
    def post(cls, request):
        """Method handles creation of new user.

        :param request: WSGIRequest instance
        """
        # validation of register form:
        user_form = UserForm(request.POST)
        if not user_form.is_valid():
            messages.error(
                request,
                'Wprowadzono nieprawidłowy email, hasło lub nie wyrażono '
                'zgody na przetwarzanie danych osobowych.'
            )
            return cls.get(request, user_form)

        username = request.POST.get('email')
        password = request.POST.get('password')

        ctx = {}

        # attempt of new user creation:
        try:
            user = User.objects.create_user(
                username=username,
                email=username,
                password=password,
            )
            user.is_active = False
            user.save()
            profile = UserProfile(user=user)
            ctx['uuid'] = profile.uuid
            profile.save()
        except IntegrityError:
            # if attempt failed, because user already exists we need show
            # error message:
            messages.info(
                request,
                'Użytkownik o podanym emailu już istnieje'
            )
            return cls.get(request, user_form)

        # sending email to user:
        send_mail(request, 'registration', [user.email], context=ctx)

        # automatically login new user:
        user = auth.authenticate(username=username, password=password)
        auth.login(request, user)

        # show info about successful creation of new user and redirect to
        # homepage:
        messages.success(
            request,
            'Rejestracja przebiegła pomyślnie'
        )
        messages.info(
            request,
            'Na podany przy rejestracji email został wysłany link '
            'aktywacyjny. Aby w pełni wykorzystać konto należy je aktywować '
            'poprzez kliknięcie linku lub wklejenie go w przeglądarce.'
        )
        return redirect('homepage')


def activate(request, uuid):
    """View responsible for activating user account."""
    try:
        profile = UserProfile.objects.get(uuid=uuid)
        profile.user.is_active = True
        profile.user.save()
        messages.success(
            request,
            """Pomyślnie aktywowałeś użytkownika."""
        )
    except UserProfile.DoesNotExist:
        messages.error(
            request,
            """Brak użytkownika spełniającego wymagane kryteria."""
        )
    return redirect('homepage')


def password_reset(request):
    """View responsible for password reset."""
    return auth_views.password_reset(
        request,
        template_name='auth/password_reset.html',
        post_reset_redirect='login',
        from_email=FROM_ADDRESS,
        subject_template_name='emails/password_reset.subject',
        email_template_name='emails/password_reset.txt',
        html_email_template_name='emails/password_reset.html',
    )


def password_reset_confirm(request, uidb64, token):
    """Landing page for password reset."""
    return auth_views.password_reset_confirm(
        request,
        uidb64,
        token,
        template_name='auth/password_reset_confirm.html',
        post_reset_redirect='login',
    )
