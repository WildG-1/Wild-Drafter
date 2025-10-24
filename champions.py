# ================================================================
#  champions.py — Données locales des champions (version simplifiée)
#  Utilisé uniquement en secours ou pour réimporter des données.
# ================================================================

# Chaque clé = nom du champion
# Chaque valeur = dictionnaire d’attributs booléens (True/False)
# Ces attributs doivent correspondre aux clés listées dans app.py (QUESTIONS).

CHAMPIONS = {
    "Bel'Veth": {
        "heavy_ad": False, "heavy_ap": False, "need_engage": False, "need_cc": False,
        "early_game": True, "scaling": True, "invade": True, "frontline": False,
        "peeling": False, "ally_melee": False, "hp_tanks": False, "aa_heavy": False,
        "enchanter_adc": False, "lock_target": False, "range_heavy": True
    },
    "Diana": {
        "heavy_ad": False, "heavy_ap": True, "need_engage": True, "need_cc": False,
        "early_game": False, "scaling": True, "invade": False, "frontline": False,
        "peeling": False, "ally_melee": False, "hp_tanks": False, "aa_heavy": False,
        "enchanter_adc": False, "lock_target": False, "range_heavy": False
    },
    "Ekko": {
        "heavy_ad": False, "heavy_ap": False, "need_engage": True, "need_cc": True,
        "early_game": False, "scaling": True, "invade": False, "frontline": False,
        "peeling": False, "ally_melee": False, "hp_tanks": False, "aa_heavy": False,
        "enchanter_adc": False, "lock_target": False, "range_heavy": False
    },
    "Graves": {
        "heavy_ad": True, "heavy_ap": True, "need_engage": False, "need_cc": False,
        "early_game": True, "scaling": True, "invade": True, "frontline": False,
        "peeling": False, "ally_melee": False, "hp_tanks": False, "aa_heavy": False,
        "enchanter_adc": False, "lock_target": False, "range_heavy": False
    },
    "Ivern": {
        "heavy_ad": False, "heavy_ap": False, "need_engage": False, "need_cc": True,
        "early_game": False, "scaling": False, "invade": False, "frontline": False,
        "peeling": True, "ally_melee": False, "hp_tanks": False, "aa_heavy": False,
        "enchanter_adc": True, "lock_target": False, "range_heavy": False
    },
    "Jarvan IV": {
        "heavy_ad": False, "heavy_ap": False, "need_engage": True, "need_cc": True,
        "early_game": False, "scaling": False, "invade": False, "frontline": True,
        "peeling": True, "ally_melee": False, "hp_tanks": False, "aa_heavy": False,
        "enchanter_adc": False, "lock_target": False, "range_heavy": False
    },
    "Jax": {
        "heavy_ad": True, "heavy_ap": False, "need_engage": False, "need_cc": True,
        "early_game": False, "scaling": True, "invade": False, "frontline": False,
        "peeling": True, "ally_melee": False, "hp_tanks": False, "aa_heavy": True,
        "enchanter_adc": False, "lock_target": True, "range_heavy": False
    },
    "Kayn": {
        "heavy_ad": False, "heavy_ap": True, "need_engage": False, "need_cc": True,
        "early_game": False, "scaling": True, "invade": False, "frontline": True,
        "peeling": False, "ally_melee": False, "hp_tanks": True, "aa_heavy": False,
        "enchanter_adc": False, "lock_target": True, "range_heavy": False
    },
    "Sejuani": {
        "heavy_ad": False, "heavy_ap": False, "need_engage": True, "need_cc": True,
        "early_game": False, "scaling": False, "invade": False, "frontline": True,
        "peeling": True, "ally_melee": True, "hp_tanks": False, "aa_heavy": False,
        "enchanter_adc": False, "lock_target": True, "range_heavy": False
    },
    "Skarner": {
        "heavy_ad": False, "heavy_ap": False, "need_engage": True, "need_cc": True,
        "early_game": False, "scaling": False, "invade": False, "frontline": True,
        "peeling": True, "ally_melee": False, "hp_tanks": False, "aa_heavy": False,
        "enchanter_adc": False, "lock_target": True, "range_heavy": False
    },
    "Vi": {
        "heavy_ad": False, "heavy_ap": False, "need_engage": True, "need_cc": False,
        "early_game": False, "scaling": True, "invade": False, "frontline": False,
        "peeling": True, "ally_melee": False, "hp_tanks": False, "aa_heavy": False,
        "enchanter_adc": False, "lock_target": True, "range_heavy": False
    },
    "Viego": {
        "heavy_ad": False, "heavy_ap": False, "need_engage": False, "need_cc": False,
        "early_game": False, "scaling": True, "invade": False, "frontline": False,
        "peeling": False, "ally_melee": False, "hp_tanks": True, "aa_heavy": False,
        "enchanter_adc": False, "lock_target": False, "range_heavy": False
    },
    "Volibear": {
        "heavy_ad": False, "heavy_ap": False, "need_engage": True, "need_cc": True,
        "early_game": True, "scaling": False, "invade": False, "frontline": True,
        "peeling": False, "ally_melee": False, "hp_tanks": True, "aa_heavy": False,
        "enchanter_adc": False, "lock_target": False, "range_heavy": False
    },
    "Wukong": {
        "heavy_ad": True, "heavy_ap": False, "need_engage": True, "need_cc": False,
        "early_game": False, "scaling": True, "invade": False, "frontline": False,
        "peeling": False, "ally_melee": False, "hp_tanks": False, "aa_heavy": False,
        "enchanter_adc": False, "lock_target": False, "range_heavy": False
    },
    "Xin Zhao": {
        "heavy_ad": False, "heavy_ap": False, "need_engage": False, "need_cc": False,
        "early_game": True, "scaling": False, "invade": True, "frontline": False,
        "peeling": False, "ally_melee": False, "hp_tanks": False, "aa_heavy": False,
        "enchanter_adc": False, "lock_target": True, "range_heavy": True
    },
    "Zac": {
        "heavy_ad": False, "heavy_ap": True, "need_engage": True, "need_cc": True,
        "early_game": False, "scaling": False, "invade": False, "frontline": True,
        "peeling": False, "ally_melee": False, "hp_tanks": False, "aa_heavy": False,
        "enchanter_adc": False, "lock_target": False, "range_heavy": False
    }
}

# ================================================================
#  💡 NOTE :
#  Ce fichier n’est plus utilisé par défaut.
#  Wild Drafter lit directement champions.json (et la DB) via app.py.
#  Tu peux l’utiliser pour réinitialiser la base si besoin :
#  → importer CHAMPIONS dans un script et les insérer dans la DB.
# ================================================================
