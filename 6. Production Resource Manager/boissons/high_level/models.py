# Create your models here.
from django.db import models


class QuantiteMatierePremiere(models.Model):
    quantite = models.IntegerField()
    matiere_premiere = models.ForeignKey(
        "MatierePremiere",
        on_delete=models.PROTECT,
    )

    class Meta:
        abstract = True


class UtilisationMatierePremiere(QuantiteMatierePremiere):
    pass


class ApprovisionnementMatierePremiere(QuantiteMatierePremiere):
    localisation = models.ForeignKey(
        "Localisation",
        on_delete=models.PROTECT,
    )
    prix_unitaire = models.IntegerField()
    delai = models.IntegerField()

    def __str__(self):
        return f"{self.matiere_premiere} ({self.quantite})"

    def cost(self):
        return self.prix_unitaire * self.quantite

    def json(self):
        return {
            "quantite": self.quantite,
            "prix_unitaire": self.prix_unitaire,
            "delai": self.delai,
        }

    def json_extended(self):
        data = self.json()
        data["matiere_premiere"] = self.matiere_premiere.json()
        data["localisation"] = self.localisation.json()
        return data


class MatierePremiere(models.Model):
    nom = models.CharField(max_length=100)
    # stock = models.IntegerField()
    emprise = models.IntegerField()

    def __str__(self):
        return f"{self.nom})"

    def json(self):
        return {
            "nom": self.nom,
            "emprise": self.emprise,
        }

    def json_extended(self):
        data = self.json()
        return data


class Energie(models.Model):
    nom = models.CharField(max_length=100)
    prix = models.IntegerField()

    def __str__(self):
        return f"{self.nom} ({self.prix} €/kWh)"

    def json(self):
        return {
            "nom": self.nom,
            "prix": self.prix,
        }

    def json_extended(self):
        data = self.json()
        return data


class Localisation(models.Model):
    nom = models.CharField(max_length=100)
    Taxe = models.IntegerField()
    prix_m2 = models.IntegerField()

    def __str__(self):
        return f"{self.nom} ({self.prix_m2} €/m2)"

    def json(self):
        return {
            "nom": self.nom,
            "Taxe": self.Taxe,
            "prix_m2": self.prix_m2,
        }

    def json_extended(self):
        data = self.json()
        return data


class DebitEnergie(models.Model):
    debit = models.IntegerField()
    energie = models.ForeignKey(
        "Energie",
        on_delete=models.PROTECT,
    )

    def __str__(self):
        return f"{self.debit} kWh/h d'Energie ID {self.energie}"

    def cost(self):
        return self.debit * self.energie.prix

    def json(self):
        return {
            "debit": self.debit,
            "energie": self.energie.nom,
        }

    def json_extended(self):
        data = self.json()
        data["energie_prix"] = self.energie.json()
        return data


class Produit(models.Model):
    nom = models.CharField(max_length=100)
    prix_vente = models.IntegerField()
    quantite = models.IntegerField()
    emprise = models.IntegerField()
    local = models.ForeignKey(
        "Local",
        on_delete=models.PROTECT,
    )

    def __str__(self):
        return f"{self.nom} ({self.quantite})"

    def json(self):
        return {
            "nom": self.nom,
            "prix_vente": self.prix_vente,
            "quantite": self.quantite,
            "emprise": self.emprise,
        }

    def json_extended(self):
        data = self.json()
        data["local"] = self.local.json()
        return data


class Local(models.Model):
    nom = models.CharField(max_length=100)
    localisation = models.ForeignKey(
        "Localisation",
        on_delete=models.PROTECT,
    )
    surface = models.IntegerField()

    def __str__(self):
        return f"{self.nom} ({self.surface} m2)"

    def costs(self):
        cout_localisation = self.surface * self.localisation.prix_m2

        cout_machines = sum(m.cost() for m in self.machine_set.all())

        cout_stocks = sum(
            app.cost()
            for app in self.localisation.approvisionnementmatierepremiere_set.all()
        )

        return cout_localisation + cout_machines + cout_stocks

    def json(self):
        return {
            "nom": self.nom,
            "localisation": self.localisation.nom,
            "surface": self.surface,
        }

    def json_extended(self):
        data = self.json()
        data["localisation"] = self.localisation.json()
        return data


class Metier(models.Model):
    nom = models.CharField(max_length=100)
    renumeration = models.IntegerField()

    def __str__(self):
        return f"{self.nom} ({self.renumeration} €/h)"

    def json(self):
        return {
            "nom": self.nom,
            "renumeration": self.renumeration,
        }

    def json_extended(self):
        data = self.json()
        return data


class RessourceHumaine(models.Model):
    metier = models.ForeignKey(
        "Metier",
        on_delete=models.PROTECT,
    )
    quantite = models.IntegerField()

    def __str__(self):
        return f"{self.metier} ({self.quantite})"

    def cost(self):
        return self.quantite * self.metier.renumeration

    def json(self):
        return {
            "metier": self.metier.nom,
            "quantite": self.quantite,
        }

    def json_extended(self):
        data = self.json()
        data["metier"] = self.metier.json()
        return data


class Machine(models.Model):
    nom = models.CharField(max_length=100)
    prix_achat = models.IntegerField()
    cout_maintenance = models.IntegerField()
    operateurs = models.ManyToManyField(
        "RessourceHumaine",
    )
    debit = models.IntegerField()
    surface = models.IntegerField()
    debit_energie = models.IntegerField()
    taux_utilisation = models.IntegerField()
    local = models.ForeignKey(
        "Local",
        on_delete=models.PROTECT,
    )

    def __str__(self):
        return f"{self.nom} ({self.prix_achat} €)"

    def cost(self):
        return self.prix_achat + self.cout_maintenance

    def json(self):
        return {
            "nom": self.nom,
            "prix_achat": self.prix_achat,
            "cout_maintenance": self.cout_maintenance,
            "debit": self.debit,
            "surface": self.surface,
            "debit_energie": self.debit_energie,
            "taux_utilisation": self.taux_utilisation,
            "local": self.local.nom,
        }

    def json_extended(self):
        data = self.json()
        data["local"] = self.local.json()
        data["operateurs"] = [op.json() for op in self.operateurs.all()]
        return data


class Fabrication(models.Model):
    produit = models.ForeignKey(
        "Produit",
        on_delete=models.PROTECT,
    )
    utilisation_matiere_premiere = models.ManyToManyField(
        "UtilisationMatierePremiere",
    )
    machines = models.ManyToManyField(
        "Machine",
    )
    ressources_humaines = models.ManyToManyField(
        "RessourceHumaine",
    )

    def __str__(self):
        return f"Fabrication de {self.produit}"

    def json(self):
        return {
            "produit": self.produit.nom,
            "utilisation_matiere_premiere": [
                ump.json() for ump in self.utilisation_matiere_premiere.all()
            ],
            "machines": [machine.json() for machine in self.machines.all()],
            "ressources_humaines": [rh.json() for rh in self.ressources_humaines.all()],
        }

    def json_extended(self):
        data = self.json()
        data["produit"] = self.produit.json()
        data["utilisation_matiere_premiere"] = [
            ump.json_extended() for ump in self.utilisation_matiere_premiere.all()
        ]
        data["machines"] = [machine.json_extended() for machine in self.machines.all()]
        data["ressources_humaines"] = [
            rh.json_extended() for rh in self.ressources_humaines.all()
        ]
        return data
