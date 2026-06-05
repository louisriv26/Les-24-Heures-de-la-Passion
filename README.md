# Les 24 Heures de la Passion — Luisa Piccarreta

Application dévotionnelle pour la méditation des 24 Heures de la Passion.

## Structure des fichiers

```
index.html              ← point d'entrée (redirige automatiquement)
luisa_24_heures.html    ← application complète
version.json            ← version actuelle (vérifiée au chargement)
icon-180.png            ← icône écran d'accueil iPhone/iPad
icon-192.png            ← icône Android / Chrome
icon-512.png            ← icône haute résolution
manifest.json           ← configuration application web
.nojekyll               ← désactive le traitement Jekyll de GitHub
```

## Déploiement sur GitHub Pages

### 1. Créer le dépôt

- Sur GitHub, créez un nouveau dépôt (public)
- Copiez tous ces fichiers à la racine du dépôt

### 2. Activer GitHub Pages

**Settings → Pages → Source : Deploy from a branch → main → / (root) → Save**

GitHub publie le site en 60 secondes environ.

### 3. URL de l'application

```
https://[votre-nom].github.io/[nom-du-depot]/
```

Partagez cette URL depuis WhatsApp, iMessage, e-mail, etc.

### 4. Ajouter à l'écran d'accueil (iPhone / iPad)

1. Ouvrez l'URL dans **Safari**
2. Bouton **Partager** → **Sur l'écran d'accueil**
3. Confirmez

L'application s'ouvre en plein écran, sans barre d'adresse.

### 5. Mises à jour

Pour mettre à jour l'application :
1. Remplacez `luisa_24_heures.html` dans le dépôt
2. Incrémentez le champ `version` dans `version.json`

Les utilisateurs voient un bandeau de mise à jour au prochain chargement
et peuvent appuyer pour actualiser — la mise à jour n'est jamais forcée.

## Fonctionnalités

- 24 heures de méditation avec prières et compléments
- Mode Prier (lecture épurée) / Mode Étude (outils d'analyse)
- Surlignage de texte en 5 couleurs
- Favoris et progression de lecture
- Paroles directes de Jésus (334 passages) et de Marie (25 passages) annotées
- Section Promesses et bienfaits avec 23 références LDC annotées
- Suivi quotidien des méditations — suggestion de l'heure du lendemain
- Recherche plein texte avec filtres (méditations, réflexions, prières, compléments)
- Recherche avec normalisation des ligatures (cœur/coeur, œuvres/oeuvres)
- Export / Import des données personnelles (favoris, surlignages, progression)
- Guide d'utilisation intégré
- Mode sombre, taille de texte ajustable (5 niveaux)
- Icône dédiée pour l'écran d'accueil

## Note sur l'usage hors ligne

Cette version est une application web. Elle nécessite une connexion lors du
premier chargement. L'usage hors ligne complet n'est pas encore garanti ;
une couche service worker sera ajoutée dans une prochaine version.

## Version

prototype-32 — Build 2026-06-04
Corpus GE / Lumen Luminis 2021 — validé structurellement.
Annotation des paroles directes : 334 Jésus · 25 Marie.
Annotation technique vérifiée — revue éditoriale en cours.
