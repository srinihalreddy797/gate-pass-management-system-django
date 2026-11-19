from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.utils import timezone

from .models import Log, Pass, User


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={"class": "w-full", "placeholder": "Username"})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "w-full", "placeholder": "Password"})
    )


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("first_name", "last_name", "username", "email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "w-full")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.role = User.Roles.USER
        if commit:
            user.save()
        return user


class PassForm(forms.ModelForm):
    out_time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"})
    )
    return_time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"})
    )

    class Meta:
        model = Pass
        fields = ["purpose", "department", "out_time", "return_time"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "w-full")

    def clean(self):
        cleaned_data = super().clean()
        out_time = cleaned_data.get("out_time")
        return_time = cleaned_data.get("return_time")

        if out_time and out_time < timezone.now():
            self.add_error("out_time", "Out time cannot be in the past.")
        if out_time and return_time and return_time <= out_time:
            self.add_error("return_time", "Return time must be later than out time.")
        return cleaned_data


class PassFilterForm(forms.Form):
    search = forms.CharField(required=False)
    date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    status = forms.ChoiceField(
        required=False,
        choices=[("", "All Statuses"), *Pass.Status.choices],
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "w-full")
        self.fields["search"].widget.attrs.setdefault("placeholder", "Search by Pass ID")
        self.fields["date"].widget.attrs.setdefault("placeholder", "Date")


class SecurityVerificationForm(forms.Form):
    pass_id = forms.CharField(max_length=10, label="Pass ID")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["pass_id"].widget.attrs.update(
            {"class": "w-full uppercase", "placeholder": "Enter Pass ID"}
        )


class LogActionForm(forms.ModelForm):
    class Meta:
        model = Log
        fields = []
