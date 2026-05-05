import numpy as np
from tabulate import tabulate
from colorama import Fore, Style


def initialise_number_ply(ply_thickness, angles=30, min_thickness=1e-3):
    """
    Initialise un stratifié symétrique avec une épaisseur minimale,
    en positionnant l'axe médian au niveau \( z = 0 \).

    Paramètres :
    -----------
    ply_thickness : float
        Épaisseur de chaque pli (en mm).
    angles : float
        Angle d'orientation des plis (symétrie imposée).
    min_thickness : float
        Épaisseur minimale totale du stratifié (par défaut 1.0 mm).

    Retour :
    -------
    ply_results : list of dict
        Liste des plis avec `z_top`, `z_bottom`, et `angles` configurés symétriquement.
    """
    # Nombre minimal de plis dans chaque moitié
    num_plies_half = int(np.ceil(min_thickness / (2 * ply_thickness)))
    total_thickness = 2 * num_plies_half * ply_thickness

    # Construction des plis symétriques
    ply_results = []
    z_top = total_thickness / 2

    for _ in range(2 * num_plies_half):
        z_bottom = z_top - ply_thickness
        ply_results.append({
            "z_top": z_top,
            "z_bottom": z_bottom,
            "thickness": ply_thickness,
            "angle": angles,
            "global_strain": 0,
            "global_stress": 0,
            "local_stress": 0,
        })
        z_top = z_bottom

    return ply_results


def calculate_Q_matrix(E_1, E_2, G_12, v_12):
    """
    Calcule la matrice de rigidité réduite Q pour un ply.
    """
    v_21 = (E_2 / E_1) * v_12
    Q_11 = E_1 / (1 - v_12 * v_21)
    Q_22 = E_2 / (1 - v_12 * v_21)
    Q_12 = v_12 * E_2 / (1 - v_12 * v_21)
    Q_66 = G_12

    return {
        'Q11': Q_11,
        'Q22': Q_22,
        'Q12': Q_12,
        'Q66': Q_66,
    }


def calculate_transformed_Q(Q_matrix, theta):
    """
    Calcule les coefficients Q_ij transformés pour un pli composite.

    Paramètres :
    -----------
    Q_matrix : dict
        Dictionnaire contenant Q_11, Q_22, Q_12, Q_66.
    theta : float
        Angle (en degrés) entre la direction de référence et l'orientation du pli.

    Retour :
    -------
    transformed_Q : dict
        Dictionnaire contenant les coefficients Q_ij' transformés.
    """
    # Convertir l'angle en radians
    theta_rad = np.radians(theta)

    # Extraire les coefficients de la matrice Q
    Q11, Q22, Q12, Q66 = Q_matrix['Q11'], Q_matrix['Q22'], Q_matrix['Q12'], Q_matrix['Q66']

    # Pré-calcul des termes trigonométriques
    c, s = np.cos(theta_rad), np.sin(theta_rad)
    c2, s2 = c**2, s**2
    c4, s4 = c2**2, s2**2
    cs, c2s2 = c * s, 2 * c2 * s2

    # Calcul des coefficients transformés
    Q11_t = Q11 * c4 + 2 * (Q12 + 2 * Q66) * c2s2 + Q22 * s4
    Q22_t = Q11 * s4 + 2 * (Q12 + 2 * Q66) * c2s2 + Q22 * c4
    Q12_t = (Q11 + Q22 - 4 * Q66) * c2s2 + Q12 * (c4 + s4)
    Q66_t = (Q11 + Q22 - 2 * Q12 - 2 * Q66) * c2s2 + Q66 * (c2 + s2)**2
    Q16_t = (Q11 - Q12 - 2 * Q66) * cs * c2 + (Q12 - Q22 + 2 * Q66) * cs * s2
    Q26_t = (Q11 - Q12 - 2 * Q66) * cs * s2 + (Q12 - Q22 + 2 * Q66) * cs * c2

    # Retourner les coefficients transformés
    return {
        'Q11': Q11_t,
        'Q22': Q22_t,
        'Q12': Q12_t,
        'Q66': Q66_t,
        'Q16': Q16_t,
        'Q26': Q26_t
    }


def calculate_laminate_matrices(ply_data, Q_matrix):
    """
    Calcule les matrices A_ij, B_ij, D_ij pour un stratifié composite.

    Paramètres :
    -----------
    ply_data : list of dict
        Liste contenant les informations pour chaque pli, sous forme de dictionnaires avec :
        - 'Q_transformed': dict avec Q11', Q22', Q12', Q66', Q16', Q26'
        - 'z_top': float, position de la surface supérieure
        - 'z_bottom': float, position de la surface inférieure
        - 'thickness': float, épaisseur du pli"""

    # Initialisation des matrices A, B et D
    A = np.zeros((3, 3))
    B = np.zeros((3, 3))
    D = np.zeros((3, 3))

    # Parcours des plis pour accumuler les contributions
    for ply in ply_data:
        angle = ply['angle']

        # Matrice Q transformée
        Q_transformed = calculate_transformed_Q(Q_matrix, angle)
        z_top, z_bottom = ply['z_top'], ply['z_bottom']
        delta_z = z_top - z_bottom

        # Construction de la matrice Q transformée
        Q_trans = np.array([
            [Q_transformed['Q11'], Q_transformed['Q12'], Q_transformed['Q16']],
            [Q_transformed['Q12'], Q_transformed['Q22'], Q_transformed['Q26']],
            [Q_transformed['Q16'], Q_transformed['Q26'], Q_transformed['Q66']]
        ])

        # Contribution aux matrices A, B et D
        A += Q_trans * delta_z
        B += Q_trans * (z_top**2 - z_bottom**2) / 2
        D += Q_trans * (z_top**3 - z_bottom**3) / 3

    return A, B, D


def calculate_stresses_laminate(A, B, D, N, M, ply, Q_matrix):
    """
    Calcule les contraintes et déformations dans un pli d'un stratifié composite.

    Paramètres :
    -----------
    A, B, D : ndarray
        Matrices de rigidité du stratifié.
    N : ndarray
        Forces normales globales [N_x, N_y, N_xy].
    M : ndarray
        Moments globaux [M_x, M_y, M_xy].
    ply : dict
        Informations sur le pli :
        - 'z_top': position supérieure,
        - 'z_bottom': position inférieure,
        - 'angle': angle d'orientation du pli (en degrés).
    Q_matrix : dict
        Matrice de rigidité réduite du matériau (ex : {'Q11': ..., 'Q12': ..., etc.}).

    Retour :
    -------
    ply : dict
        Mise à jour des informations du pli avec les déformations et contraintes calculées :
        - 'global_strain': déformations globales,
        - 'global_stress': contraintes globales,
        - 'local_stress': contraintes locales.
    """
    # Construction de la matrice globale de rigidité ABD
    ABD = np.block([
        [A, B],
        [B, D]
    ])

    # Construction du vecteur des charges
    loads = np.concatenate([N, M])  # [N_x, N_y, N_xy, M_x, M_y, M_xy]

    # Résolution pour obtenir les déformations moyennes (ε₀) et courbures (κ)
    strains_and_curvatures = np.dot(np.linalg.inv(ABD), loads)
    mid_plane_strains = strains_and_curvatures[:3]   # ε₀
    mid_plane_curvatures = strains_and_curvatures[3:]  # κ

    # Calcul des déformations globales dans le pli
    z_mid = (ply["z_top"] + ply["z_bottom"]) / 2
    global_strain = mid_plane_strains + z_mid * mid_plane_curvatures

    # Matrice Q transformée pour l'angle du pli
    angle = ply["angle"]
    Q_transformed = calculate_transformed_Q(
        Q_matrix, angle)  # Retourne un dictionnaire

    # Construction de la matrice \( Q \) transformée à partir du dictionnaire
    Q_matrice = np.array([
        [Q_transformed["Q11"], Q_transformed["Q12"], Q_transformed["Q16"]],
        [Q_transformed["Q12"], Q_transformed["Q22"], Q_transformed["Q26"]],
        [Q_transformed["Q16"], Q_transformed["Q26"], Q_transformed["Q66"]]
    ])

    # Contraintes globales dans le pli
    global_stress = np.dot(Q_matrice, global_strain)

    # Transformation des contraintes globales vers locales
    theta = np.radians(angle)
    c, s = np.cos(theta), np.sin(theta)

    # Matrice de transformation T
    T = np.array([
        [c**2, s**2, -2*c*s],
        [s**2, c**2, 2*c*s],
        [c*s, -c*s, c**2 - s**2]
    ])

    # Contraintes locales
    local_stress = np.dot(np.linalg.inv(T), global_stress)

    # Enregistrement des résultats
    ply["global_strain"] = global_strain
    ply["global_stress"] = global_stress
    ply["local_stress"] = local_stress

    return ply


def tsai_hill_criterion(local_stress, Xt, Xc, Yt, Yc, S):
    """
    Vérifie le critère de Tsai-Hill pour un matériau composite.

        Contraintes locales dans le pli (\( \sigma_x \), \( \sigma_y \), \( \tau_{xy} \)).
    Xt, Xc : float
        Résistances en traction et en compression dans la direction longitudinale.
    Yt, Yc : float
        Résistances en traction et en compression dans la direction transverse.
    S : float
        Résistance au cisaillement dans le plan.

    Retour :
    -------
    criterion : float
        Valeur du critère de Tsai-Hill (doit être <= 1 pour que le pli soit sûr).
    """
    sigma_x, sigma_y, tau_xy = local_stress

    # Choisir la résistance en fonction du signe de sigma_x
    X = Xt if sigma_x >= 0 else Xc
    # Choisir la résistance en fonction du signe de sigma_y
    Y = Yt if sigma_y >= 0 else Yc

    # Calcul du critère
    criterion = (
        (sigma_x / X) ** 2
        - (sigma_x * sigma_y) / (X ** 2)  # Utilise Xt et Xc directement ici
        + (sigma_y / Y) ** 2
        + (tau_xy / S) ** 2
    )

    return criterion


def adjust_ply_angles(ply_data, Q_matrix, N, M, limit_strength):
    """
    Ajuste les angles des plis dans un stratifié symétrique pour satisfaire le critère de Tsai-Hill.

    Paramètres :
    -----------
    ply_data : list of dict
        Liste contenant les données des plis.
    Q_matrix : ndarray
        Matrice de rigidité réduite.
    N : ndarray
        Forces normales (N_x, N_y, N_xy).
    M : ndarray
        Moments (M_x, M_y, M_xy).
    limit_strength : dict
        Limites de résistance mécanique du matériau.

    Retour :
    -------
    ply_data : list of dict
        Liste mise à jour des plis avec les angles ajustés.
    """
    angles = [0, -15, 15, -30, 30, -45, 45, -60,
              60, -75, 75, 90]  # Angles disponibles
    num_plies = len(ply_data)
    mid_index = num_plies // 2  # Indice de l'axe médian (si symétrie)

    for i in range(mid_index):
        # Initialiser les critères pour le pli i (au-dessus) et le pli j (en dessous)
        j = num_plies - i - 1  # Pli symétrique
        ply_i = ply_data[i]
        ply_j = ply_data[j]
        criteria_i = []
        criteria_j = []

        for angle in angles:
            # Ajuste l'angle du pli i et symétriquement du pli j
            ply_i['angle'] = angle
            ply_j['angle'] = angle

            # Recalculer les matrices A, B, D
            A, B, D = calculate_laminate_matrices(ply_data, Q_matrix)

            # Calculer les contraintes locales pour les plis i et j
            stresses_i = calculate_stresses_laminate(
                A, B, D, N, M, ply_i, Q_matrix)
            stresses_j = calculate_stresses_laminate(
                A, B, D, N, M, ply_j, Q_matrix)

            local_stress_i = stresses_i['local_stress']
            local_stress_j = stresses_j['local_stress']

            # Calculer les valeurs du critère de Tsai-Hill pour i et j
            criterion_i = tsai_hill_criterion(
                local_stress_i,
                limit_strength["Xt"], limit_strength["Xc"],
                limit_strength["Yt"], limit_strength["Yc"], limit_strength["S"]
            )
            criterion_j = tsai_hill_criterion(
                local_stress_j,
                limit_strength["Xt"], limit_strength["Xc"],
                limit_strength["Yt"], limit_strength["Yc"], limit_strength["S"]
            )

            # Enregistrer la pire valeur entre les deux plis pour ce choix d'angle
            criteria_i.append(max(criterion_i, criterion_j))

        # Décision pour les angles des plis i et j
        criteria_i = np.array(criteria_i)
        if np.all(criteria_i > 1):  # Aucun angle ne satisfait le critère
            closest_index = np.argmin(np.abs(criteria_i - 1))
            ply_i["angle"] = angles[closest_index]
            ply_j["angle"] = angles[closest_index]  # Symétrie
        else:  # Plusieurs angles satisfont le critère
            valid_indices = np.where(criteria_i <= 1)[0]
            min_index = valid_indices[np.argmin(criteria_i[valid_indices])]
            ply_i["angle"] = angles[min_index]
            ply_j["angle"] = angles[min_index]  # Symétrie

        # Recalculer les matrices A, B, D
        A, B, D = calculate_laminate_matrices(ply_data, Q_matrix)

        # Calculer les contraintes locales pour les plis i et j
        stresses_i = calculate_stresses_laminate(
            A, B, D, N, M, ply_i, Q_matrix)
        stresses_j = calculate_stresses_laminate(
            A, B, D, N, M, ply_j, Q_matrix)

        local_stress_i = stresses_i['local_stress']
        local_stress_j = stresses_j['local_stress']

        ply_i["global_strain"] = stresses_i["global_strain"]
        ply_i["global_stress"] = stresses_i["global_stress"]
        ply_i["local_stress"] = stresses_i["local_stress"]

        ply_j["global_strain"] = stresses_j["global_strain"]
        ply_j["global_stress"] = stresses_j["global_stress"]
        ply_j["local_stress"] = stresses_j["local_stress"]

    return ply_data


def add_ply(ply_data, thickness):
    """
    Ajoute une paire de plis symétriques pour respecter la symétrie du stratifié
    sans nécessiter de réajustement du mid-plane.

    Paramètres :
    -----------
    ply_data : list of dict
        Liste des plis existants dans le stratifié.
    thickness : float
        Épaisseur de chaque pli à ajouter.

    Retour :
    -------
    ply_data : list of dict
        Liste mise à jour des plis avec la paire ajoutée.
    """

    # Ajouter une paire symétrique par rapport à l'axe médian
    z_bottom_upper = ply_data[0]["z_top"]
    z_top_upper = z_bottom_upper + thickness

    # Ajouter le pli supérieur
    ply_data.insert(0, {
        "z_top": z_top_upper,
        "z_bottom": z_bottom_upper,
        "thickness": thickness,
        "angle": 0,
        "global_strain": np.zeros(3),
        "global_stress": np.zeros(3),
        "local_stress": np.zeros(3)
    })

    z_top_lower = ply_data[-1]["z_bottom"]
    z_bottom_lower = z_top_lower - thickness

    # Ajouter le pli inférieur
    ply_data.append({
        "z_top": z_top_lower,
        "z_bottom": z_bottom_lower,
        "thickness": thickness,
        "angle": 0,
        "global_strain": np.zeros(3),
        "global_stress": np.zeros(3),
        "local_stress": np.zeros(3)
    })

    return ply_data


def calculate_laminate_properties(A_matrix, thickness_total):
    """
    Calcule les propriétés effectives du stratifié composite.

    Paramètres :
    - A_matrix : ndarray
        Matrice de rigidité A du stratifié (issue des matrices A, B, D).
    - thickness_total : float
        Épaisseur totale du stratifié.

    Retourne :
    - properties : dict
        Dictionnaire contenant les propriétés \(E_x\), \(E_y\), \(G_{xy}\), \(\nu_{xy}\), et \(\nu_{yx}\).
    """
    # Inversion de la matrice A pour obtenir la souplesse
    compliance_matrix = np.linalg.inv(A_matrix)

    # Calcul des propriétés
    E_x = 1 / (compliance_matrix[0, 0] * thickness_total)
    E_y = 1 / (compliance_matrix[1, 1] * thickness_total)
    G_xy = 1 / (compliance_matrix[2, 2] * thickness_total)
    v_xy = -compliance_matrix[0, 1] / compliance_matrix[0, 0]
    v_yx = v_xy * (E_y / E_x)  # Relation entre v_xy et v_yx

    return {
        "E_x": E_x,
        "E_y": E_y,
        "G_xy": G_xy,
        "v_xy": v_xy,
        "v_yx": v_yx
    }


def generate_stacking_sequence(ply_data):
    """
    Génère une séquence d'empilement standardisée avec les indices inférieurs pour les plis consécutifs.

    Arguments :
    - ply_data : Liste de dictionnaires contenant l'angle des plis.

    Retourne :
    - Une chaîne de caractères représentant la séquence d'empilement.
    """
    def to_subscript(number):
        """
        Convertit un entier en indice (subscript) Unicode.
        """
        subscript_map = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")
        return str(number).translate(subscript_map)

    angles = [ply["angle"] for ply in ply_data]  # Récupération des angles
    # Partie unique (avant symétrie)
    half_sequence = angles[:len(angles) // 2 + len(angles) % 2]

    # Comptage des plis consécutifs au même angle
    sequence = []
    current_angle = half_sequence[0]
    count = 0

    for angle in half_sequence:
        if angle == current_angle:
            count += 1
        else:
            if count > 1:
                sequence.append(f"{current_angle}{to_subscript(count)}")
            else:
                sequence.append(f"{current_angle}")
            current_angle = angle
            count = 1
    if count > 1:
        sequence.append(f"{current_angle}{to_subscript(count)}")
    else:
        sequence.append(f"{current_angle}")

    # Assemblage final avec le souscrit `ₛ` pour indiquer la symétrie
    return f"[{' / '.join(sequence)}]ₛ"


def display_results(ply_data, material_properties, limit_strength):
    """
    Affiche les résultats avec validation Tsai-Hill, séquence d'empilage et propriétés des matériaux.
    """
    console_width = 100  # Largeur totale pour centrer les tableaux et titres
    separator = "=" * console_width

    # Préparer les données des plis
    results_data = []
    for idx, ply in enumerate(ply_data, start=1):
        tsai_hill = tsai_hill_criterion(
            ply["local_stress"],
            limit_strength["Xt"], limit_strength["Xc"],
            limit_strength["Yt"], limit_strength["Yc"],
            limit_strength["S"]
        )
        validation_status = f"{Fore.GREEN}OK{
            Style.RESET_ALL}" if tsai_hill <= 1 else f"{Fore.RED}NON{Style.RESET_ALL}"

        results_data.append([
            idx,
            f"{Fore.CYAN}{ply['angle']}°{Style.RESET_ALL}",
            f"{Fore.YELLOW}{ply['z_top']:.3e}{Style.RESET_ALL}",
            f"{Fore.YELLOW}{ply['z_bottom']:.3e}{Style.RESET_ALL}",
            f"{Fore.MAGENTA}{ply['local_stress'][0]:.2e}{Style.RESET_ALL}",
            f"{Fore.MAGENTA}{ply['local_stress'][1]:.2e}{Style.RESET_ALL}",
            f"{Fore.MAGENTA}{ply['local_stress'][2]:.2e}{Style.RESET_ALL}",
            f"{Fore.BLUE}{tsai_hill:.2f}{Style.RESET_ALL}",
            validation_status
        ])

    # Générer la séquence d'empilage
    stacking_sequence = generate_stacking_sequence(ply_data)
    total_plies = len(ply_data)

    # Préparer les données pour les propriétés des matériaux et résumé
    summary_data = [
        [f"{Fore.LIGHTBLUE_EX}Eₓ (Pa){Style.RESET_ALL}", f"{
            material_properties['E_x']:.2e}"],
        [f"{Fore.LIGHTBLUE_EX}Eᵧ (Pa){Style.RESET_ALL}", f"{
            material_properties['E_y']:.2e}"],
        [f"{Fore.LIGHTBLUE_EX}Gₓᵧ (Pa){Style.RESET_ALL}", f"{
            material_properties['G_xy']:.2e}"],
        [f"{Fore.LIGHTBLUE_EX}νₓᵧ{Style.RESET_ALL}",
            f"{material_properties['v_xy']:.3f}"],
        [f"{Fore.LIGHTBLUE_EX}νᵧₓ{Style.RESET_ALL}",
            f"{material_properties['v_yx']:.3f}"],
        [f"{Fore.LIGHTGREEN_EX}Nombre total de plis{
            Style.RESET_ALL}", total_plies],
        [f"{Fore.LIGHTGREEN_EX}Séquence d'empilage{
            Style.RESET_ALL}", stacking_sequence]
    ]

    # Afficher les résultats des plis
    print("\n" + Fore.YELLOW + "=" * 50)
    print("PROPRIÉTÉS DES PLI".center(50))
    print("=" * 50 + Style.RESET_ALL)

    headers = [
        "Pli", "Orientation", "z_top", "z_bottom",
        "σ₁ (Pa)", "σ₂ (Pa)", "τ₁₂ (Pa)", "Tsai-Hill", "Validation"
    ]
    print(tabulate(results_data, headers=headers,
          tablefmt="grid", numalign="center", stralign="center"))

    # Afficher le résumé global
    print("\n" + Fore.YELLOW + "=" * 50)
    print("RÉSUMÉ GLOBAL".center(50))
    print("=" * 50 + Style.RESET_ALL)

    print(tabulate(summary_data, tablefmt="grid",
          numalign="center", stralign="center", showindex=False))


composites = {
    1: {
        "name": "Composite E-Glass Fiber/Epoxy",
        "E_1": 36.5e9,  # Module d'élasticité longitudinal (Pa)
        "E_2": 15e9,   # Module d'élasticité transverse (Pa)
        "v_12": 0.24,   # Coefficient de Poisson dans la direction longitudinale
        "G_12": 6.35e9,   # Module de cisaillement (Pa)
        "thickness": 0.3e-3,  # Épaisseur d'un pli (m)
        "Xt": 1050e6,  # Résistance en traction longitudinale (Pa)
        "Xc": -938e6,  # Résistance en compression longitudinale (Pa)
        "Yt": 43e6,    # Résistance en traction transverse (Pa)
        "Yc": -106e6,    # Résistance en compression transverse (Pa)
        "S": 88e6      # Résistance au cisaillement (Pa)
    },
    2: {
        "name": "Composite Carbone Fiber/Epoxy",
        "E_1": 127.7e9,
        "E_2": 7.4e9,
        "v_12": 0.33,
        "G_12": 6.9e9,
        "thickness": 0.3e-3,
        "Xt": 1717e6,
        "Xc": -1200e6,
        "Yt": 30e6,
        "Yc": -216e6,
        "S": 33e6
    },
    3: {
        "name": "Composite SiC Aluminium/Epoxy",
        "E_1": 101e9,
        "E_2": 101e9,
        "v_12": 0.29,
        "G_12": 39e9,
        "thickness": 0.1e-3,
        "Xt": 476e6,
        "Xc": 500e6,
        "Yt": 476e6,
        "Yc": 500e6,
        "S": 303e6
    }
}

# Interface utilisateur pour choisir le matériaux composite
print("Choisissez un matériaux composite :")
for key, value in composites.items():
    print(f"{key}. {value['name']}")

while True:
    try:
        materiaux_choice = int(
            input("Votre choix de matériaux composite (1, 2, 3) : "))
        if materiaux_choice in [1, 2, 3]:
            materiaux = composites[materiaux_choice]
            break
        else:
            print("Choix invalide. Veuillez entrer 1, 2 ou 3.")
    except ValueError:
        print("Veuillez entrer un nombre valide.")

# Entrées supplémentaires
'''while True:
    try:
        fiber_volume_fraction = float(
            input("Entrez la fraction volumique de fibre (entre 0 et 1) : "))
        if 0 <= fiber_volume_fraction <= 1:
            break
        else:
            print("Veuillez entrer une valeur entre 0 et 1.")
    except ValueError:
        print("Veuillez entrer un nombre valide.")'''

# Forces normales
while True:
    try:
        N = list(
            map(float, input("Entrez les forces (N_x N_y N_s) : ").split()))
        if len(N) == 3:
            break
        else:
            print("Veuillez entrer exactement 3 valeurs.")
    except ValueError:
        print("Veuillez entrer des nombres valides (séparés par des espaces).")

# Moments
while True:
    try:
        M = list(map(float, input("Entrez les moments (M_x M_y M_s) : ").split()))
        if len(M) == 3:
            break
        else:
            print("Veuillez entrer exactement 3 valeurs.")
    except ValueError:
        print("Veuillez entrer des nombres valides (séparés par des espaces).")

E_1, E_2, v_12, G_12 = materiaux["E_1"], materiaux["E_2"], materiaux["v_12"], materiaux["G_12"]
e = materiaux["thickness"]
limit_strengh = {"Xt": materiaux["Xt"], "Xc": materiaux["Xc"],
                 "Yt": materiaux["Yt"], "Yc": materiaux["Yc"], "S": materiaux["S"]}

Q_matrix = calculate_Q_matrix(E_1, E_2, G_12, v_12)

ply_data = initialise_number_ply(e)

while True:
    ply_data = adjust_ply_angles(ply_data, Q_matrix, N, M, limit_strengh)
    if all(tsai_hill_criterion(ply["local_stress"], limit_strengh["Xt"], limit_strengh["Xc"], limit_strengh["Yt"], limit_strengh["Yc"], limit_strengh["S"]) <= 1 for ply in ply_data):
        break
    ply_data = add_ply(ply_data, e)

A, *Z = calculate_laminate_matrices(ply_data, Q_matrix)

material_properties = calculate_laminate_properties(A, e)

display_results(ply_data, material_properties, limit_strengh)
