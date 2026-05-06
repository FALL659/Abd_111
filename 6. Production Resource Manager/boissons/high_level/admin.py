# Register your models here.
from django.contrib import admin

from .models import (
    MatierePremiere,
    ApprovisionnementMatierePremiere,
    UtilisationMatierePremiere,
    Metier,
    RessourceHumaine,
    Machine,
    Fabrication,
    Produit,
    Local,
    DebitEnergie,
    Energie,
    Localisation,
)

# Simple registration: use admin.site.register for each model.
admin.site.register(
    [
        MatierePremiere,
        ApprovisionnementMatierePremiere,
        UtilisationMatierePremiere,
        Metier,
        RessourceHumaine,
        Machine,
        Fabrication,
        Produit,
        Local,
        DebitEnergie,
        Energie,
        Localisation,
    ]
)
