from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import include, path

from ninja import NinjaAPI

from project.api.router import router as common_router
from project.api.admin.router import router as admin_router
from project.api.advertisements.router import router as advertisements_router
from project.api.categories.router import router as categories_router
from project.api.consultations.router import router as consultations_router
from project.api.districts.router import router as districts_router
from project.api.portfolio.router import router as portfolio_router

api = NinjaAPI(title="HD Realty API", version="1.0.0")
api.add_router("/", common_router)
api.add_router("/", admin_router)
api.add_router("/", advertisements_router)
api.add_router("/", categories_router)
api.add_router("/", consultations_router)
api.add_router("/", districts_router)
api.add_router("/", portfolio_router)


@api.get("/health")
def health(request):
    return {"status": "ok"}


urlpatterns = [
    path("", lambda r: HttpResponseRedirect("/api/docs")),
    path("admin/", lambda r: HttpResponseRedirect("/ru/admin/")),
    path("api/", api.urls),
    path("i18n/", include("django.conf.urls.i18n")),
] + i18n_patterns(
    path("admin/", admin.site.urls),
    prefix_default_language=True,
)
