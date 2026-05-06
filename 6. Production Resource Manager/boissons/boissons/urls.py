"""
URL configuration for boissons project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from high_level.views import (
    LocalDetailView,
    MetierDetailView,
    RessourceHumaineDetailView,
    MachineDetailView,
    FabricationDetailView,
    MatierePremiereDetailView,
    ApprovisionnementMatierePremiereDetailView,
    ProduitDetailView,
    EnergieDetailView,
    DebitEnergieDetailView,
    LocalisationDetailView,
    ApiLocalView,
    ApiMetierView,
    ApiRessourceHumaineView,
    ApiMachineView,
    ApiFabricationView,
    ApiMatierePremiereView,
    ApiApprovisionnementMatierePremiereView,
    ApiProduitView,
    ApiEnergieView,
    ApiDebitEnergieView,
    ApiLocalisationView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("local/<int:pk>/", LocalDetailView.as_view(), name="local-detail"),
    path("metier/<int:pk>/", MetierDetailView.as_view(), name="metier-detail"),
    path(
        "ressourcehumaine/<int:pk>/",
        RessourceHumaineDetailView.as_view(),
        name="ressourcehumaine-detail",
    ),
    path("machine/<int:pk>/", MachineDetailView.as_view(), name="machine-detail"),
    path(
        "fabrication/<int:pk>/",
        FabricationDetailView.as_view(),
        name="fabrication-detail",
    ),
    path(
        "matierepremiere/<int:pk>/",
        MatierePremiereDetailView.as_view(),
        name="matierepremiere-detail",
    ),
    path(
        "approvisionnementmatierepremiere/<int:pk>/",
        ApprovisionnementMatierePremiereDetailView.as_view(),
        name="approvisionnementmatierepremiere-detail",
    ),
    path("produit/<int:pk>/", ProduitDetailView.as_view(), name="produit-detail"),
    path("energie/<int:pk>/", EnergieDetailView.as_view(), name="energie-detail"),
    path(
        "debiteenergie/<int:pk>/",
        DebitEnergieDetailView.as_view(),
        name="debiteenergie-detail",
    ),
    path(
        "localisation/<int:pk>/",
        LocalisationDetailView.as_view(),
        name="localisation-detail",
    ),
    path("api/local/<int:pk>/", ApiLocalView.as_view(), name="api-local"),
    path("api/metier/<int:pk>/", ApiMetierView.as_view(), name="api-metier"),
    path(
        "api/ressourcehumaine/<int:pk>/",
        ApiRessourceHumaineView.as_view(),
        name="api-ressourcehumaine",
    ),
    path("api/machine/<int:pk>/", ApiMachineView.as_view(), name="api-machine"),
    path(
        "api/fabrication/<int:pk>/",
        ApiFabricationView.as_view(),
        name="api-fabrication",
    ),
    path(
        "api/matierepremiere/<int:pk>/",
        ApiMatierePremiereView.as_view(),
        name="api-matierepremiere",
    ),
    path(
        "api/approvisionnementmatierepremiere/<int:pk>/",
        ApiApprovisionnementMatierePremiereView.as_view(),
        name="api-approvisionnementmatierepremiere",
    ),
    path("api/produit/<int:pk>/", ApiProduitView.as_view(), name="api-produit"),
    path("api/energie/<int:pk>/", ApiEnergieView.as_view(), name="api-energie"),
    path(
        "api/debiteenergie/<int:pk>/",
        ApiDebitEnergieView.as_view(),
        name="api-debiteenergie",
    ),
    path(
        "api/localisation/<int:pk>/",
        ApiLocalisationView.as_view(),
        name="api-localisation",
    ),
]
