from django.urls import path, include


from .views import email_list_signup


app_name="marketing"

urlpatterns = [

    path('subscribe', email_list_signup, name='subscribe'),


]


