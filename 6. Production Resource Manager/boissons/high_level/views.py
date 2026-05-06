# Create your views here.
from django.shortcuts import get_object_or_404
from django.views.generic.detail import DetailView
from django.views.generic import View
from django.http import JsonResponse
from .models import (
    Local,
    Machine,
    MatierePremiere,
    ApprovisionnementMatierePremiere,
    Metier,
    RessourceHumaine,
    Fabrication,
    Energie,
    DebitEnergie,
    Localisation,
    Produit,
)


class LocalDetailView(DetailView):
    model = Local

    def render_to_response(self, context, **response_kwargs):
        obj = self.get_object()
        return JsonResponse(obj.json(), **response_kwargs)


class ApiLocalView(View):
    def get(self, request, *args, **kwargs):
        local = get_object_or_404(Local, pk=kwargs.get("pk"))
        data = local.json_extended()
        return JsonResponse(data, safe=False)


class MetierDetailView(DetailView):
    model = Metier

    def render_to_response(self, context, **response_kwargs):
        obj = self.get_object()
        return JsonResponse(obj.json(), **response_kwargs)


class ApiMetierView(View):
    def get(self, request, *args, **kwargs):
        metier = get_object_or_404(Metier, pk=kwargs.get("pk"))
        data = metier.json_extended()
        return JsonResponse(data, safe=False)


class RessourceHumaineDetailView(DetailView):
    model = RessourceHumaine

    def render_to_response(self, context, **response_kwargs):
        obj = self.get_object()
        return JsonResponse(obj.json(), **response_kwargs)


class ApiRessourceHumaineView(View):
    def get(self, request, *args, **kwargs):
        ressourcehumaine = get_object_or_404(RessourceHumaine, pk=kwargs.get("pk"))
        data = ressourcehumaine.json_extended()
        return JsonResponse(data, safe=False)


class MachineDetailView(DetailView):
    model = Machine

    def render_to_response(self, context, **response_kwargs):
        obj = self.get_object()
        return JsonResponse(obj.json(), **response_kwargs)


class ApiMachineView(View):
    def get(self, request, *args, **kwargs):
        machine = get_object_or_404(Machine, pk=kwargs.get("pk"))
        data = machine.json_extended()
        return JsonResponse(data, safe=False)


class FabricationDetailView(DetailView):
    model = Fabrication

    def render_to_response(self, context, **response_kwargs):
        obj = self.get_object()
        return JsonResponse(obj.json(), **response_kwargs)


class ApiFabricationView(View):
    def get(self, request, *args, **kwargs):
        fabrication = get_object_or_404(Fabrication, pk=kwargs.get("pk"))
        data = fabrication.json_extended()
        return JsonResponse(data, safe=False)


class MatierePremiereDetailView(DetailView):
    model = MatierePremiere

    def render_to_response(self, context, **response_kwargs):
        obj = self.get_object()
        return JsonResponse(obj.json(), **response_kwargs)


class ApiMatierePremiereView(View):
    def get(self, request, *args, **kwargs):
        matierepremiere = get_object_or_404(MatierePremiere, pk=kwargs.get("pk"))
        data = matierepremiere.json_extended()
        return JsonResponse(data, safe=False)


class ApprovisionnementMatierePremiereDetailView(DetailView):
    model = ApprovisionnementMatierePremiere

    def render_to_response(self, context, **response_kwargs):
        obj = self.get_object()
        return JsonResponse(obj.json(), **response_kwargs)


class ApiApprovisionnementMatierePremiereView(View):
    def get(self, request, *args, **kwargs):
        approvisionnement = get_object_or_404(
            ApprovisionnementMatierePremiere, pk=kwargs.get("pk")
        )
        data = approvisionnement.json_extended()
        return JsonResponse(data, safe=False)


class ProduitDetailView(DetailView):
    model = Produit

    def render_to_response(self, context, **response_kwargs):
        obj = self.get_object()
        return JsonResponse(obj.json(), **response_kwargs)


class ApiProduitView(View):
    def get(self, request, *args, **kwargs):
        produit = get_object_or_404(Produit, pk=kwargs.get("pk"))
        data = produit.json_extended()
        return JsonResponse(data, safe=False)


class EnergieDetailView(DetailView):
    model = Energie

    def render_to_response(self, context, **response_kwargs):
        obj = self.get_object()
        return JsonResponse(obj.json(), **response_kwargs)


class ApiEnergieView(View):
    def get(self, request, *args, **kwargs):
        energie = get_object_or_404(Energie, pk=kwargs.get("pk"))
        data = energie.json_extended()
        return JsonResponse(data, safe=False)


class DebitEnergieDetailView(DetailView):
    model = DebitEnergie

    def render_to_response(self, context, **response_kwargs):
        obj = self.get_object()
        return JsonResponse(obj.json(), **response_kwargs)


class ApiDebitEnergieView(View):
    def get(self, request, *args, **kwargs):
        debiteenergie = get_object_or_404(DebitEnergie, pk=kwargs.get("pk"))
        data = debiteenergie.json_extended()
        return JsonResponse(data, safe=False)


class LocalisationDetailView(DetailView):
    model = Localisation

    def render_to_response(self, context, **response_kwargs):
        obj = self.get_object()
        return JsonResponse(obj.json(), **response_kwargs)


class ApiLocalisationView(View):
    def get(self, request, *args, **kwargs):
        localisation = get_object_or_404(Localisation, pk=kwargs.get("pk"))
        data = localisation.json_extended()
        return JsonResponse(data, safe=False)
