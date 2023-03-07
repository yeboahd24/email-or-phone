from django import forms
from django.contrib.auth import get_user_model
import phonenumbers
from .models import MyModel
from django_countries.fields import CountryField

# from .models import Recipe, Cookbook
from .models import FormStep1, FormStep2
from django_countries.widgets import CountrySelectWidget

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


# class RecipeForm(forms.ModelForm):
#     class Meta:
#         model = Recipe
#         fields = [
#             "name",
#             "ingredients",
#             "instructions",
#             "servings",
#             "prep_time",
#             "cook_time",
#             "difficulty",
#         ]
#         widgets = {
#             "ingredients": forms.Textarea(attrs={"rows": 10}),
#             "instructions": forms.Textarea(attrs={"rows": 10}),
#         }


# class CookbookForm(forms.ModelForm):
#     class Meta:
#         model = Cookbook
#         fields = ['cover_image', 'color_scheme', 'recipes']


class SignUpForm(forms.ModelForm):
    username = forms.CharField(max_length=30, required=True, label="Email")
    # first_name = forms.CharField(max_length=30, required=False)
    # last_name = forms.CharField(max_length=30, required=False)
    # email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')
    password = forms.CharField(widget=forms.PasswordInput, label="Password")
    # password2 = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")

    class Meta:
        model = User
        fields = ("username", "password")

    # def clean_password2(self):
    #     cd = self.cleaned_data
    #     if cd["password"] != cd["password2"]:
    #         raise forms.ValidationError("Passwords don't match.")
    #     return cd["password2"]

    def clean_username(self):
        username = self.cleaned_data["username"]
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError('Username "%s" is already in use.' % username)

    # def clean_email(self):
    #     email = self.cleaned_data['email']
    #     try:
    #         User.objects.get(email=email)
    #     except User.DoesNotExist:
    #         return email
    #     raise forms.ValidationError('Email "%s" is already in use.' % email)

    def save(self, commit=True):
        user = super(SignUpForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class LoginForm2(forms.Form):
    username = forms.CharField()

    class Meta:
        model = User
        fields = ("username",)

    def clean(self):
        try:
            user = User.objects.get(username__iexact=self.cleaned_data["username"])
        except User.DoesNotExist:
            raise forms.ValidationError("Invalid username, please try again.")

        return self.cleaned_data


# forms.py


class Page1Form(forms.Form):
    email = forms.EmailField()
    full_name = forms.CharField(max_length=100)


class Page2Form(forms.Form):
    country = forms.CharField(max_length=100)
    phone_number = forms.CharField(max_length=20)


class Page3Form(forms.Form):
    GENDER_CHOICES = [
        ("male", "Male"),
        ("female", "Female"),
    ]
    gender = forms.ChoiceField(choices=GENDER_CHOICES)
    occupation = forms.CharField(max_length=100)


class MoveForm(forms.Form):
    row = forms.IntegerField()
    col = forms.IntegerField()

    def __init__(self, *args, **kwargs):
        board = kwargs.pop("board")
        super().__init__(*args, **kwargs)
        self.board = board

    def clean(self):
        cleaned_data = super().clean()
        row = cleaned_data.get("row")
        col = cleaned_data.get("col")

        if row is not None and col is not None:
            if not (0 <= row < 3 and 0 <= col < 3):
                raise forms.ValidationError("Invalid move")
            if self.board[row][col] is not None:
                raise forms.ValidationError("Cell already occupied")


class SignUpForm(forms.Form):
    username = forms.CharField(max_length=100)
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Password", "id": "password"}
        )
    )

    def clean_password(self):
        password = self.cleaned_data.get("password")
        if len(password) < 8:
            raise forms.ValidationError("Password must be at least 8 characters long.")
        return password


class CodeForm(forms.Form):
    code_text = forms.CharField(widget=forms.Textarea, required=False)
    code_file = forms.FileField(required=False)


class FormStep1(forms.ModelForm):
    class Meta:
        model = FormStep1
        fields = "__all__"


class FormStep2(forms.ModelForm):
    class Meta:
        model = FormStep2
        fields = "__all__"


# from .models import MyModel


class MyForm(forms.Form):
    choices = forms.ModelMultipleChoiceField(queryset=MyModel.objects.all())


class ContactForm(forms.Form):
    name = forms.CharField(max_length=100)
    email = forms.EmailField()
    # country = CountryField(attrs={"class": "form-control"}).formfield()
    phone = forms.CharField()
    country = CountryField(blank_label="(select country)").formfield(
        required=False,
        widget=CountrySelectWidget(attrs={"class": "custom-select d-block w-100"}),
    )

    def clean_phone(self):
        phone = self.cleaned_data["phone"]
        country = self.cleaned_data["country"]
        parsed_phone = phonenumbers.parse(phone, country.code)
        if not phonenumbers.is_valid_number(parsed_phone):
            raise forms.ValidationError("Please enter a valid phone number.")
        return phonenumbers.format_number(
            parsed_phone, phonenumbers.PhoneNumberFormat.E164
        )


from django.contrib.auth.forms import AuthenticationForm

class RememberMeAuthenticationForm(AuthenticationForm):
    remember_me = forms.BooleanField(required=False, initial=True, widget=forms.CheckboxInput)



class PasswordForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'id': 'password', 'name': 'password', 'placeholder': 'Enter password'}))
    


from django.contrib.auth import get_user_model

User = get_user_model()

class SignUpForm1(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'email')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('A user with that email address already exists.')
        return email





class SignUpForm2(forms.Form):
    phone = forms.CharField(max_length=20)
    password1 = forms.CharField(widget=forms.PasswordInput())
    password2 = forms.CharField(widget=forms.PasswordInput())

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2
