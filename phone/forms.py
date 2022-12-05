from django import forms
from django.contrib.auth import get_user_model


User = get_user_model()


class LoginForm(forms.ModelForm):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    remember_user = forms.BooleanField(required=False, label="Remember Me")

    def clean(self):
        try:
            user = User.objects.get(username__iexact=self.cleaned_data["username"])
        except User.DoesNotExist:
            raise forms.ValidationError("Invalid username, please try again.")

        if not user.check_password(self.cleaned_data["password"]):
            raise forms.ValidationError("Invalid password, please try again.")

        return self.cleaned_data
