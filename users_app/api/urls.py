# Third-party
from django.urls import path

# Local
from users_app.api.views import LoginView, RegistrationView

urlpatterns = [
    path('registration/', RegistrationView.as_view(), name='registration'),
    path('login/', LoginView.as_view(), name='login'),
]
