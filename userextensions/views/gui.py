"""
This file contains views that render a specific page for the gui.
"""

from django.shortcuts import redirect, render, reverse
from django.conf import settings
from django.contrib import messages
from django.views.generic import (View, ListView)
from djangohelpers.views import FilterByQueryParamsMixin
from braces.views import LoginRequiredMixin
from rest_framework.authtoken.models import Token

# import models
from userextensions.models import (UserRecent, UserFavorite)

# import forms
from userextensions.forms import UserPreferenceForm


class ListRecents(LoginRequiredMixin, FilterByQueryParamsMixin, ListView):
    """ Displays a list of urls the user has recently visited, rendered in a paginated, searchable, sortable bootstrap
    table. This view is filterable via query parameters. Includes links to delete individual entries.
    """
    base_template = settings.BASE_TEMPLATE
    template = "handyhelpers/generic/generic_list.html"

    def get(self, request, *args, **kwargs):
        context = dict()
        self.queryset = UserRecent.objects.filter(user=request.user).order_by('-updated_at')
        context['base_template'] = self.base_template
        context['queryset'] = self.filter_by_query_params()
        context['title'] = "Recents"
        context['sub_title'] = request.user.username
        context['table'] = "userextensions/table/table_recents.htm"
        return render(request, self.template, context=context)


class ListFavorites(LoginRequiredMixin, FilterByQueryParamsMixin, ListView):
    """ Displays a list of urls user has set as favorites, rendered in a paginated, searchable, sortable bootstrap
    table. This view is filterable via query parameters. Includes links to delete individual entries. """
    base_template = settings.BASE_TEMPLATE
    template = "handyhelpers/generic/generic_list.html"

    def get(self, request, *args, **kwargs):
        context = dict()
        self.queryset = UserFavorite.objects.filter(user=request.user).order_by('-updated_at')
        context['base_template'] = self.base_template
        context['queryset'] = self.filter_by_query_params()
        context['title'] = "Favorites"
        context['sub_title'] = request.user.username
        context['table'] = "userextensions/table/table_favorites.htm"
        return render(request, self.template, context=context)


class DetailUser(LoginRequiredMixin, View):
    """ Displays user details, including group configuration, API token, and configuration for theme, start page, and
    recents count. Includes link to refresh API token and modal form to edit user preferences. """
    base_template = settings.BASE_TEMPLATE
    template = "userextensions/detail/detail_user.html"

    def get(self, request):
        context = dict()
        # include user preference form
        form_data_user_preferences = dict()
        form_data_user_preferences['form'] = UserPreferenceForm(request.POST or None, instance=request.user.preference)
        form_data_user_preferences['action'] = "Update"
        form_data_user_preferences['action_url'] = reverse('userextensions:detail_user')
        form_data_user_preferences['title'] = "<b>Update Preferences: </b><small> {} </small>".format(request.user)
        form_data_user_preferences['modal_name'] = "update_user_preferences"
        context['form_data_user_preferences'] = form_data_user_preferences

        context['user'] = request.user
        context['token'] = str(Token.objects.get_or_create(user=request.user)[0])
        context['groups'] = sorted([i.name for i in request.user.groups.all()])
        context['base_template'] = self.base_template
        return render(request, self.template, context=context)

    def post(self, request):
        redirect_url = request.META.get('HTTP_REFERER')
        form = UserPreferenceForm(request.POST or None, instance=request.user.preference)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.ERROR, "Preferences updated!", extra_tags='alert-info', )
            return redirect(redirect_url)
        else:
            for error in form.errors:
                messages.add_message(request, messages.ERROR, "Input error: {}".format(error),
                                     extra_tags='alert-danger', )
            return self.get(request)
