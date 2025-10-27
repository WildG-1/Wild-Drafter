# Code Review de Wild Drafter

## Problèmes Identifiés

1. **API d'administration sans protection**  
   Les routes `/admin`, `/api/champions` et `/api/champions` (POST) ne disposent d'aucun mécanisme d'authentification ou de protection CSRF. Toute personne ayant accès à l'application peut lire ou écraser l'intégralité de la base de données de champions, ce qui constitue une vulnérabilité majeure.  
   Références : `app.py`, lignes 90-114.

2. **Suppression totale avant insertion sans validation**  
   La route POST `/api/champions` supprime toutes les entrées via `Champion.query.delete()` puis réinsère les données reçues sans validation ou gestion d'erreur. En cas de payload invalide, de rollback ou de champ manquant, l'application peut se retrouver sans données persistées. Il est recommandé d'ajouter de la validation et d'encapsuler l'opération dans une transaction sécurisée.  
   Références : `app.py`, lignes 108-114.

3. **Gestion d'erreurs côté client insuffisante**  
   Dans `static/js/questions.js`, les fonctions `getJSON` et `postJSON` ne gèrent pas les réponses HTTP non OK. La moindre erreur serveur (ex. 500) provoquerait une exception non interceptée côté client et une interface bloquée.  
   Références : `static/js/questions.js`, lignes 15-24.

4. **Absence de fallback pour les icônes**  
   Lorsqu'aucune URL d'icône valide n'est fournie, la réponse JSON renvoie `icon: null`. Le front affiche alors `<img src="null">`, produisant une image cassée. Il faudrait prévoir une image par défaut côté backend ou frontend.  
   Références : `app.py`, lignes 68-83 et `static/js/questions.js`, lignes 65-83.

## Recommandations Générales

- Ajouter une couche d'authentification/autorisation pour les routes d'administration.
- Valider et journaliser les payloads reçus avant de manipuler la base.
- Gérer les erreurs réseau/serveur côté client pour garantir une meilleure expérience utilisateur.
- Prévoir un asset par défaut pour les icônes manquantes afin d'éviter les images cassées.

