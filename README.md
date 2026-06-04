# Les 24 Heures de la Passion — Luisa Piccarreta

Application dévotionnelle pour la méditation des 24 Heures de la Passion.

## Structure des fichiers

```
index.html              ← point d'entrée (redirige automatiquement)
luisa_24_heures.html    ← application complète
icon-180.png            ← icône écran d'accueil iPhone/iPad
icon-192.png            ← icône Android / Chrome
icon-512.png            ← icône haute résolution (PWA)
manifest.json           ← configuration application web
.nojekyll               ← désactive le traitement Jekyll de GitHub
```

## Déploiement sur GitHub Pages

### 1. Créer le dépôt

- Sur GitHub, créez un nouveau dépôt (public)
- Copiez tous ces fichiers à la racine du dépôt

### 2. Activer GitHub Pages

Dans les paramètres du dépôt :
**Settings → Pages → Source : Deploy from a branch → main → / (root) → Save**

GitHub publie le site en environ 60 secondes.

### 3. URL de l'application

```
https://[votre-nom].github.io/[nom-du-depot]/
```

Cette URL redirige automatiquement vers l'application.
Partagez cette URL — elle fonctionne depuis WhatsApp, iMessage, e-mail, etc.

### 4. Ajouter à l'écran d'accueil (iPhone / iPad)

1. Ouvrez l'URL dans **Safari**
2. Bouton **Partager** → **Sur l'écran d'accueil**
3. Confirmez

L'application s'ouvre en plein écran, sans barre d'adresse.

### 5. Mises à jour

Pour mettre à jour l'application, remplacez `luisa_24_heures.html` dans le dépôt.
Tous les utilisateurs reçoivent la mise à jour automatiquement à la prochaine ouverture.

## Fonctionnalités

- 24 heures de méditation avec prières et compléments
- Mode Prier (lecture épurée) / Mode Étude (outils d'analyse)
- Surlignage de texte en 5 couleurs
- Favoris et progression de lecture
- Paroles directes de Jésus et de Marie annotées
- Recherche avec filtres par type de contenu
- Export / Import des données personnelles
- Mode sombre, taille de texte ajustable (5 niveaux)
- Guide d'utilisation intégré (bouton ?)
- Fonctionne hors ligne après le premier chargement

## Version

prototype-26 — Corpus GE/Lumen Luminis 2021, validé structurellement.
