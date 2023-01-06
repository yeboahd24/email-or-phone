from django import forms
from django.contrib.auth import get_user_model
from .models import Recipe, Cookbook


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


class WordForm(forms.Form):
    input = forms.CharField(label="Enter a sentence or paragraph:")


class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = [
            "name",
            "ingredients",
            "instructions",
            "servings",
            "prep_time",
            "cook_time",
            "difficulty",
        ]
        widgets = {
            "ingredients": forms.Textarea(attrs={"rows": 10}),
            "instructions": forms.Textarea(attrs={"rows": 10}),
        }



class CookbookForm(forms.ModelForm):
    class Meta:
        model = Cookbook
        fields = ['cover_image', 'color_scheme', 'recipes']
