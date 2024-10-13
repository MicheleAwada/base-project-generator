def get_base_url(base_urls_pattern=[]):
    base_urls_pattern = [f"    {i}" for i in base_urls_pattern]
    seperator = ",\n"
    return \
f"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
{seperator.join(base_urls_pattern)}
]"""
