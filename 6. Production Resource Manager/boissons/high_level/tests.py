# Create your tests here.
from django.test import TestCase

from .models import Machine

from .models import Localisation

from .models import Local

from .models import MatierePremiere

from .models import ApprovisionnementMatierePremiere


class LocalCostsTests(TestCase):
    def test_machine_creation(self):
        self.assertEqual(Localisation.objects.count(), 0)
        Localisation.objects.create(nom="Labège", prix_m2=2000, Taxe=5)
        self.assertEqual(Localisation.objects.count(), 1)

        self.assertEqual(Local.objects.count(), 0)
        Local.objects.create(
            nom="Local 1",
            surface=50,
            localisation=Localisation.objects.first(),
        )
        self.assertEqual(Local.objects.count(), 1)

        self.assertEqual(Machine.objects.count(), 0)
        Machine.objects.create(
            nom="Machine A",
            prix_achat=1000,
            cout_maintenance=0,
            debit_energie=0,
            local=Local.objects.first(),
            debit=0,
            surface=0,
            taux_utilisation=0,
        )
        self.assertEqual(Machine.objects.count(), 1)
        Machine.objects.create(
            nom="Machine B",
            prix_achat=2000,
            cout_maintenance=0,
            debit_energie=0,
            local=Local.objects.first(),
            debit=0,
            surface=0,
            taux_utilisation=0,
        )
        self.assertEqual(Machine.objects.count(), 2)

        self.assertEqual(MatierePremiere.objects.count(), 0)
        MatierePremiere.objects.create(nom="Sucre", emprise=0)
        self.assertEqual(MatierePremiere.objects.count(), 1)
        MatierePremiere.objects.create(nom="Eau", emprise=0)
        self.assertEqual(MatierePremiere.objects.count(), 2)

        self.assertEqual(ApprovisionnementMatierePremiere.objects.count(), 0)
        ApprovisionnementMatierePremiere.objects.create(
            matiere_premiere=MatierePremiere.objects.first(),
            quantite=1000,
            localisation=Localisation.objects.first(),
            prix_unitaire=10,
            delai=0,
        )
        self.assertEqual(ApprovisionnementMatierePremiere.objects.count(), 1)

        ApprovisionnementMatierePremiere.objects.create(
            matiere_premiere=MatierePremiere.objects.first(),
            quantite=50,
            localisation=Localisation.objects.first(),
            prix_unitaire=15,
            delai=0,
        )
        self.assertEqual(ApprovisionnementMatierePremiere.objects.count(), 2)

        self.assertEqual(Local.objects.first().costs(), 113750)
