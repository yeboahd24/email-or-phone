# from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
# from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from datetime import datetime



User = get_user_model()

class LockoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # Create a dictionary to store the number of failed login attempts for each user
        self.failed_attempts = {}

    def __call__(self, request):
        # If the request is a POST request to the login endpoint, check if the user has exceeded the failed login attempts limit
        if request.method == 'POST' and request.path == '/login/':
            # Get the username from the request data
            username = request.POST.get('username')
            # If the username exists in the failed attempts dictionary, increment the counter
            if username in self.failed_attempts:
                self.failed_attempts[username] += 1
            # If the username does not exist in the dictionary, add it with a value of 1
            else:
                self.failed_attempts[username] = 1

            # If the user has exceeded the failed login attempts limit (3 attempts in this case), lock the user account by setting the `is_active` flag to `False`
            if self.failed_attempts[username] >= 3:
                user = User.objects.get(username=username)
                user.is_active = False
                # Set the current datetime to the `date_locked` field of the user
                user.date_locked = datetime.now()
                user.save()
                # Return a message indicating that the user account has been locked
                return JsonResponse({'message': 'Your account has been locked due to excessive failed login attempts. Please try again in 5 minutes.'}, status=status.HTTP_429_TOO_MANY_REQUESTS)

        response = self.get_response(request)
        return response
