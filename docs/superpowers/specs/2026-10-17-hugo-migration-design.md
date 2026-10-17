# Design : Migration WordPress → Hugo — Le Lavardin

**Date :** 2026-10-17
**Statut :** approuvé

---

## Contexte

Site vitrine d'un gîte (Le Lavardin), actuellement sous WordPress dans Kubernetes. Régulièrement compromis malgré les mises à jour. Migration vers un site statique Hugo pour éliminer la surface d'attaque, simplifier la maintenance et réduire les coûts d'infrastructure.

---

## Objectifs

- Zéro PHP, zéro base de données, zéro surface d'attaque WordPress
- Site bilingue français / anglais
- Domaine perso `le-lavardin.com` + `www.le-lavardin.com`
- TLS automatique
- Formulaire de contact fonctionnel
- Déploiement automatique sur push

---

## Architecture

### Repo GitHub

Repo dédié `le-lavardin` (public, requis pour GitHub Pages gratuit avec domaine perso).

### Générateur

Hugo Extended (requis par Congo pour la compilation SCSS).

### Thème

Congo — moderne, support multilingue natif, grandes images hero, personnalisation CSS accessible.
Installation en git submodule : `themes/congo`.

### Hébergement

GitHub Pages, branche `gh-pages`, domaine `le-lavardin.com`.

### TLS

Let's Encrypt provisionné automatiquement par GitHub Pages. Aucune gestion manuelle.

### CI/CD

GitHub Actions : push sur `main` → `hugo --minify` → deploy sur `gh-pages`.

---

## Structure du repo

```
le-lavardin/
├── .github/
│   └── workflows/
│       └── deploy.yml
├── content/
│   ├── fr/
│   │   ├── _index.md
│   │   ├── chambres/
│   │   │   └── _index.md
│   │   ├── tarifs.md
│   │   ├── acces.md
│   │   └── contact.md
│   └── en/
│       ├── _index.md
│       ├── rooms/
│       │   └── _index.md
│       ├── rates.md
│       ├── how-to-get-here.md
│       └── contact.md
├── static/
│   ├── images/
│   └── CNAME                    # le-lavardin.com
├── layouts/
│   └── shortcodes/
│       └── contact-form.html
├── assets/
│   └── css/
│       └── custom.css
├── i18n/
│   ├── fr.yaml
│   └── en.yaml
└── hugo.toml
```

---

## Configuration Hugo (`hugo.toml`)

```toml
baseURL = "https://le-lavardin.com/"
title = "Le Lavardin"
theme = "congo"

defaultContentLanguage = "fr"
defaultContentLanguageInSubdir = false

[languages]
  [languages.fr]
    contentDir = "content/fr"
    languageName = "Français"
    weight = 1
  [languages.en]
    contentDir = "content/en"
    languageName = "English"
    weight = 2

[params]
  web3forms_key = "PLACEHOLDER"
```

---

## Multilingue

- Français sur `/`, anglais sur `/en/`
- Chaînes UI dans `i18n/fr.yaml` et `i18n/en.yaml`
- Sélecteur de langue dans le header via `$.Page.Translations` (natif Congo)
- Contenu recréé manuellement dans les deux langues (site peu volumineux)

---

## Formulaire de contact

Service : **Web3Forms** (250 soumissions/mois gratuites).

- Shortcode Hugo `contact-form.html` réutilisé sur les pages `contact.md` FR et EN
- Clé publique Web3Forms dans `hugo.toml` sous `params.web3forms_key`
- Labels du formulaire externalisés dans `i18n/*.yaml` pour les deux langues
- Pas de secret à gérer (clé Web3Forms est publique par design)

---

## Migration du contenu

Approche : **recréation manuelle** (site peu volumineux, ~6 pages).

Pages à recréer :

| Page FR | Page EN |
|---|---|
| Accueil | Home |
| Chambres | Rooms |
| Tarifs | Rates |
| Comment venir | How to get here |
| Contact | Contact |

Médias : photos exportées depuis WordPress (`wp-content/uploads/`) et placées dans `static/images/`.

---

## DNS

```dns
le-lavardin.com.      A    185.199.108.153
le-lavardin.com.      A    185.199.109.153
le-lavardin.com.      A    185.199.110.153
le-lavardin.com.      A    185.199.111.153
le-lavardin.com.      AAAA 2606:50c0:8000::153
le-lavardin.com.      AAAA 2606:50c0:8001::153
le-lavardin.com.      AAAA 2606:50c0:8002::153
le-lavardin.com.      AAAA 2606:50c0:8003::153
www.le-lavardin.com.  CNAME shtouff.github.io.
```

`static/CNAME` contient `le-lavardin.com`.
GitHub Pages settings : Custom domain → `le-lavardin.com`, Enforce HTTPS ✓.

---

## GitHub Actions (`deploy.yml`)

```yaml
name: Deploy Hugo site

on:
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: pages
  cancel-in-progress: false

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
      with:
        submodules: recursive
    - name: Setup Hugo
      uses: peaceiris/actions-hugo@v3
      with:
        hugo-version: latest
        extended: true
    - name: Build
      run: hugo --minify
    - name: Upload artifact
      uses: actions/upload-pages-artifact@v3
      with:
        path: ./public

  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
    - name: Deploy to GitHub Pages
      id: deployment
      uses: actions/deploy-pages@v4
```

---

## Ce qui n'est pas couvert

- Système de réservation en ligne (hors scope — lien vers booking.com ou email direct)
- Analytics (peut être ajouté via Plausible ou Fathom, sans cookies)
- Sitemap / robots.txt (générés automatiquement par Hugo)
