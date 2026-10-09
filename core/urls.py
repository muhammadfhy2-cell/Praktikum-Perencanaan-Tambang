from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    # ========================================================
    # ADMIN DJANGO
    # ========================================================
    path("admin/", admin.site.urls),

    # ========================================================
    # WEBSITE PRAKTIKUM PERENCANAAN TAMBANG
    # ========================================================
    path(
        "",
        include("praktikum.urls", namespace="praktikum"),
    ),
]


# ============================================================
# MEDIA FILES UNTUK DEVELOPMENT
# ============================================================
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )
