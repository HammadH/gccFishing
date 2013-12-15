from __future__ import unicode_literals

from django import forms, VERSION as DJANGO_VERSION
from django.contrib.auth.forms import ReadOnlyPasswordHashField, ReadOnlyPasswordHashWidget
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import identify_hasher
from django.utils.translation import ugettext_lazy as _, ugettext
from django.utils.html import format_html



User = get_user_model()


def is_password_usable(pw):
    # like Django's is_password_usable, but only checks for unusable
    # passwords, not invalidly encoded passwords too.
    try:
        # 1.5
        from django.contrib.auth.hashers import UNUSABLE_PASSWORD
        return pw != UNUSABLE_PASSWORD
    except ImportError:
        # 1.6
        from django.contrib.auth.hashers import UNUSABLE_PASSWORD_PREFIX
        return not pw.startswith(UNUSABLE_PASSWORD_PREFIX)


class BetterReadOnlyPasswordHashWidget(ReadOnlyPasswordHashWidget):
    """
    A ReadOnlyPasswordHashWidget that has a less intimidating output.
    """
    def render(self, name, value, attrs):
        from django.forms.util import flatatt
        final_attrs = flatatt(self.build_attrs(attrs))

        if not value or not is_password_usable(value):
            summary = ugettext("No password set.")
        else:
            try:
                identify_hasher(value)
            except ValueError:
                summary = ugettext("Invalid password format or unknown"
                                   " hashing algorithm.")
            else:
                summary = ugettext('*************')

        return format_html('<div{attrs}><strong>{summary}</strong></div>',
                           attrs=final_attrs, summary=summary)


class UserCreationForm(forms.ModelForm):
    
	pass


class UserChangeForm(forms.ModelForm):
    """
    A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField(label=_("Password"),
        widget=BetterReadOnlyPasswordHashWidget)

    class Meta:
        model = User
        if DJANGO_VERSION >= (1, 6):
            fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(UserChangeForm, self).__init__(*args, **kwargs)
        f = self.fields.get('user_permissions', None)
        if f is not None:
            f.queryset = f.queryset.select_related('content_type')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


class AdminUserChangeForm(UserChangeForm):
    def __init__(self, *args, **kwargs):
        super(AdminUserChangeForm, self).__init__(*args, **kwargs)
        if not self.fields['password'].help_text:
            self.fields['password'].help_text = _(
                "Raw passwords are not stored, so there is no way to see this"
                " user's password, but you can change the password using"
                " <a href=\"password/\">this form</a>.")
