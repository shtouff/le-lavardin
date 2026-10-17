# Hugo Migration — Le Lavardin — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Migrer le site gîte Le Lavardin de WordPress vers Hugo statique, hébergé sur GitHub Pages avec domaine perso bilingue FR/EN.

**Architecture:** Hugo Extended + thème Congo en git submodule. Configuration multilingue via `config/_default/`. Déploiement automatique par GitHub Actions sur push `main` → branche `gh-pages`. Formulaire de contact via Web3Forms (API externe, clé publique).

**Tech Stack:** Hugo Extended ≥ 0.120, thème Congo (branche stable), GitHub Actions, GitHub Pages, Web3Forms

**Spec:** `docs/superpowers/specs/2026-10-17-hugo-migration-design.md`

## Global Constraints

- Hugo **Extended** obligatoire (Congo nécessite la compilation SCSS)
- Congo installé en **git submodule** branche `stable` : `themes/congo`
- Configuration Hugo via `config/_default/` (pas de `hugo.toml` racine)
- Site bilingue : français sur `/`, anglais sur `/en/`
- `baseURL = "https://le-lavardin.com/"`
- Clé Web3Forms dans `params.toml` sous `web3forms_key`
- Tous les chemins d'images relatifs à `static/` → référencés comme `/images/...`

---

## File Map

| Fichier | Rôle |
|---|---|
| `themes/congo/` | Thème Hugo (git submodule) |
| `config/_default/config.toml` | Config Hugo de base |
| `config/_default/languages.fr.toml` | Config langue FR |
| `config/_default/languages.en.toml` | Config langue EN |
| `config/_default/params.toml` | Paramètres Congo + Web3Forms |
| `config/_default/menus.fr.toml` | Navigation FR |
| `config/_default/menus.en.toml` | Navigation EN |
| `i18n/fr.yaml` | Chaînes UI en français |
| `i18n/en.yaml` | UI strings in English |
| `layouts/shortcodes/contact-form.html` | Formulaire Web3Forms réutilisable |
| `assets/css/custom.css` | Surcharges CSS Congo |
| `content/fr/_index.md` | Accueil FR |
| `content/fr/chambres/_index.md` | Chambres FR |
| `content/fr/tarifs.md` | Tarifs FR |
| `content/fr/acces.md` | Comment venir FR |
| `content/fr/contact.md` | Contact FR |
| `content/en/_index.md` | Home EN |
| `content/en/rooms/_index.md` | Rooms EN |
| `content/en/rates.md` | Rates EN |
| `content/en/how-to-get-here.md` | Directions EN |
| `content/en/contact.md` | Contact EN |
| `static/CNAME` | Domaine GitHub Pages |
| `static/images/` | Photos exportées de WordPress |
| `.github/workflows/deploy.yml` | CI/CD GitHub Actions |

---

## Task 1 : Hugo init + Congo submodule

**Files:**
- Create: `themes/congo/` (submodule)
- Create: `.gitmodules`

- [ ] **Step 1 : Vérifier Hugo Extended installé**

```bash
hugo version
# Doit afficher "hugo extended"
# Si absent : https://gohugo.io/installation/
```

- [ ] **Step 2 : Initialiser le site Hugo dans le répertoire existant**

```bash
cd /home/shtouff/github/shtouff/le-lavardin
hugo new site . --force
```

Hugo crée : `archetypes/`, `assets/`, `content/`, `layouts/`, `static/`, `hugo.toml`.

- [ ] **Step 3 : Supprimer hugo.toml racine (on utilisera config/_default/)**

```bash
rm hugo.toml
```

- [ ] **Step 4 : Ajouter Congo en git submodule**

```bash
git submodule add -b stable https://github.com/jpanther/congo.git themes/congo
```

- [ ] **Step 5 : Vérifier la présence du thème**

```bash
ls themes/congo/
# Doit lister : assets/ layouts/ etc.
```

- [ ] **Step 6 : Commit**

```bash
git add .
git commit -m "feat: init Hugo site with Congo theme submodule"
```

---

## Task 2 : Configuration Hugo multilingue (config/_default/)

**Files:**
- Create: `config/_default/config.toml`
- Create: `config/_default/languages.fr.toml`
- Create: `config/_default/languages.en.toml`
- Create: `config/_default/params.toml`
- Create: `config/_default/menus.fr.toml`
- Create: `config/_default/menus.en.toml`

- [ ] **Step 1 : Créer le répertoire de config**

```bash
mkdir -p config/_default
```

- [ ] **Step 2 : Créer config.toml**

```toml
# config/_default/config.toml
theme = "congo"
baseURL = "https://le-lavardin.com/"
defaultContentLanguage = "fr"
defaultContentLanguageInSubdir = false
enableRobotsTXT = true
```

- [ ] **Step 3 : Créer languages.fr.toml**

```toml
# config/_default/languages.fr.toml
languageCode = "fr"
languageName = "Français"
weight = 1
title = "Le Lavardin"
contentDir = "content/fr"
```

- [ ] **Step 4 : Créer languages.en.toml**

```toml
# config/_default/languages.en.toml
languageCode = "en"
languageName = "English"
weight = 2
title = "Le Lavardin"
contentDir = "content/en"
```

- [ ] **Step 5 : Créer params.toml**

```toml
# config/_default/params.toml
colorScheme = "congo"
defaultAppearance = "light"
autoSwitchAppearance = true
web3forms_key = "PLACEHOLDER"   # Remplacer par la vraie clé Web3Forms

[homepage]
  layout = "page"
  showRecent = false

[article]
  showDate = false
  showAuthor = false
  showReadingTime = false
  showTableOfContents = false
  showEdit = false

[list]
  showBreadcrumbs = true
  showSummary = false

[footer]
  showCopyright = true
  showThemeAttribution = false

customCSS = ["css/custom.css"]
```

- [ ] **Step 6 : Créer menus.fr.toml**

```toml
# config/_default/menus.fr.toml
[[main]]
  name = "Chambres"
  pageRef = "chambres"
  weight = 10

[[main]]
  name = "Tarifs"
  pageRef = "tarifs"
  weight = 20

[[main]]
  name = "Comment venir"
  pageRef = "acces"
  weight = 30

[[main]]
  name = "Contact"
  pageRef = "contact"
  weight = 40
```

- [ ] **Step 7 : Créer menus.en.toml**

```toml
# config/_default/menus.en.toml
[[main]]
  name = "Rooms"
  pageRef = "rooms"
  weight = 10

[[main]]
  name = "Rates"
  pageRef = "rates"
  weight = 20

[[main]]
  name = "Getting here"
  pageRef = "how-to-get-here"
  weight = 30

[[main]]
  name = "Contact"
  pageRef = "contact"
  weight = 40
```

- [ ] **Step 8 : Vérifier que Hugo build sans erreur**

```bash
hugo --minify
# Doit terminer sans erreur. Warnings Congo OK, errors KO.
# Le dossier public/ est généré.
```

- [ ] **Step 9 : Commit**

```bash
git add config/
git commit -m "feat: add Hugo multilingual config with Congo theme"
```

---

## Task 3 : Fichiers i18n (chaînes UI)

**Files:**
- Create: `i18n/fr.yaml`
- Create: `i18n/en.yaml`

- [ ] **Step 1 : Créer i18n/fr.yaml**

```yaml
# i18n/fr.yaml
form_name:
  other: "Nom"
form_email:
  other: "Email"
form_phone:
  other: "Téléphone"
form_message:
  other: "Message"
form_send:
  other: "Envoyer"
form_success:
  other: "Message envoyé, merci !"
form_error:
  other: "Une erreur est survenue, veuillez réessayer."
nav_language:
  other: "English"
footer_copyright:
  other: "© Le Lavardin"
```

- [ ] **Step 2 : Créer i18n/en.yaml**

```yaml
# i18n/en.yaml
form_name:
  other: "Name"
form_email:
  other: "Email"
form_phone:
  other: "Phone"
form_message:
  other: "Message"
form_send:
  other: "Send"
form_success:
  other: "Message sent, thank you!"
form_error:
  other: "An error occurred, please try again."
nav_language:
  other: "Français"
footer_copyright:
  other: "© Le Lavardin"
```

- [ ] **Step 3 : Vérifier build**

```bash
hugo --minify
# Aucune erreur
```

- [ ] **Step 4 : Commit**

```bash
git add i18n/
git commit -m "feat: add FR/EN i18n strings"
```

---

## Task 4 : Formulaire de contact + CSS custom

**Files:**
- Create: `layouts/shortcodes/contact-form.html`
- Create: `assets/css/custom.css`

- [ ] **Step 1 : Créer le répertoire shortcodes**

```bash
mkdir -p layouts/shortcodes
mkdir -p assets/css
```

- [ ] **Step 2 : Créer layouts/shortcodes/contact-form.html**

```html
<form action="https://api.web3forms.com/submit" method="POST" class="contact-form">
  <input type="hidden" name="access_key" value="{{ .Site.Params.web3forms_key }}">
  <input type="hidden" name="subject" value="Contact - Le Lavardin">
  <input type="hidden" name="from_name" value="Le Lavardin Contact">
  <input type="hidden" name="redirect" value="false">
  <input type="checkbox" name="botcheck" style="display:none;">

  <div class="form-group">
    <label for="cf-name">{{ i18n "form_name" }}</label>
    <input type="text" id="cf-name" name="name" required>
  </div>

  <div class="form-group">
    <label for="cf-email">{{ i18n "form_email" }}</label>
    <input type="email" id="cf-email" name="email" required>
  </div>

  <div class="form-group">
    <label for="cf-phone">{{ i18n "form_phone" }}</label>
    <input type="tel" id="cf-phone" name="phone">
  </div>

  <div class="form-group">
    <label for="cf-message">{{ i18n "form_message" }}</label>
    <textarea id="cf-message" name="message" rows="6" required></textarea>
  </div>

  <button type="submit">{{ i18n "form_send" }}</button>
</form>
```

- [ ] **Step 3 : Créer assets/css/custom.css**

```css
/* Contact form */
.contact-form .form-group {
  margin-bottom: 1.2rem;
}

.contact-form label {
  display: block;
  margin-bottom: 0.3rem;
  font-weight: 500;
}

.contact-form input,
.contact-form textarea {
  width: 100%;
  padding: 0.6rem 0.8rem;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  font-size: 1rem;
  font-family: inherit;
}

.contact-form button[type="submit"] {
  padding: 0.7rem 2rem;
  background-color: #1d4ed8;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
}

.contact-form button[type="submit"]:hover {
  background-color: #1e40af;
}
```

- [ ] **Step 4 : Vérifier build**

```bash
hugo --minify
```

- [ ] **Step 5 : Commit**

```bash
git add layouts/ assets/
git commit -m "feat: add contact form shortcode and custom CSS"
```

---

## Task 5 : Contenu français

**Files:**
- Create: `content/fr/_index.md`
- Create: `content/fr/chambres/_index.md`
- Create: `content/fr/tarifs.md`
- Create: `content/fr/acces.md`
- Create: `content/fr/contact.md`

> **Note :** Les corps de pages ci-dessous sont des placeholders. Remplace-les par le contenu copié depuis ton WordPress avant de committer.

- [ ] **Step 1 : Créer les répertoires**

```bash
mkdir -p content/fr/chambres
```

- [ ] **Step 2 : Créer content/fr/_index.md**

```markdown
---
title: "Bienvenue au Lavardin"
description: "Gîte de charme au cœur de la nature"
---

[COLLER ICI LE TEXTE DE LA PAGE D'ACCUEIL DEPUIS WORDPRESS]
```

- [ ] **Step 3 : Créer content/fr/chambres/_index.md**

```markdown
---
title: "Nos Chambres"
description: "Découvrez nos chambres confortables"
---

[COLLER ICI LE TEXTE DE LA PAGE CHAMBRES DEPUIS WORDPRESS]
```

- [ ] **Step 4 : Créer content/fr/tarifs.md**

```markdown
---
title: "Tarifs"
description: "Nos tarifs pour la saison"
---

[COLLER ICI LE TEXTE DE LA PAGE TARIFS DEPUIS WORDPRESS]
```

- [ ] **Step 5 : Créer content/fr/acces.md**

```markdown
---
title: "Comment venir"
description: "Itinéraire et accès au Lavardin"
---

[COLLER ICI LE TEXTE DE LA PAGE COMMENT VENIR DEPUIS WORDPRESS]
```

- [ ] **Step 6 : Créer content/fr/contact.md**

```markdown
---
title: "Contact"
description: "Contactez-nous"
---

{{< contact-form >}}
```

- [ ] **Step 7 : Vérifier localement**

```bash
hugo server -D
# Ouvrir http://localhost:1313 dans le navigateur
# Vérifier : accueil, menu FR, pages chambres/tarifs/accès/contact
```

- [ ] **Step 8 : Commit**

```bash
git add content/fr/
git commit -m "feat: add French content pages"
```

---

## Task 6 : Contenu anglais

**Files:**
- Create: `content/en/_index.md`
- Create: `content/en/rooms/_index.md`
- Create: `content/en/rates.md`
- Create: `content/en/how-to-get-here.md`
- Create: `content/en/contact.md`

> **Note :** Remplace les placeholders par la traduction anglaise de ton contenu WordPress.

- [ ] **Step 1 : Créer les répertoires**

```bash
mkdir -p content/en/rooms
```

- [ ] **Step 2 : Créer content/en/_index.md**

```markdown
---
title: "Welcome to Le Lavardin"
description: "A charming guesthouse in the heart of nature"
---

[PASTE ENGLISH HOME PAGE CONTENT HERE]
```

- [ ] **Step 3 : Créer content/en/rooms/_index.md**

```markdown
---
title: "Our Rooms"
description: "Discover our comfortable rooms"
---

[PASTE ENGLISH ROOMS PAGE CONTENT HERE]
```

- [ ] **Step 4 : Créer content/en/rates.md**

```markdown
---
title: "Rates"
description: "Our seasonal rates"
---

[PASTE ENGLISH RATES PAGE CONTENT HERE]
```

- [ ] **Step 5 : Créer content/en/how-to-get-here.md**

```markdown
---
title: "How to get here"
description: "Directions and access to Le Lavardin"
---

[PASTE ENGLISH DIRECTIONS CONTENT HERE]
```

- [ ] **Step 6 : Créer content/en/contact.md**

```markdown
---
title: "Contact"
description: "Get in touch"
---

{{< contact-form >}}
```

- [ ] **Step 7 : Vérifier le switching de langue**

```bash
hugo server -D
# Ouvrir http://localhost:1313
# Vérifier : http://localhost:1313/en/ charge en anglais
# Vérifier : le sélecteur de langue dans le header switch FR ↔ EN
# Vérifier : http://localhost:1313/en/contact affiche le formulaire
```

- [ ] **Step 8 : Commit**

```bash
git add content/en/
git commit -m "feat: add English content pages"
```

---

## Task 7 : CI/CD GitHub Actions + CNAME

**Files:**
- Create: `.github/workflows/deploy.yml`
- Create: `static/CNAME`

- [ ] **Step 1 : Créer les répertoires**

```bash
mkdir -p .github/workflows
```

- [ ] **Step 2 : Créer static/CNAME**

```
le-lavardin.com
```

- [ ] **Step 3 : Créer .github/workflows/deploy.yml**

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

> **Note :** Si `peaceiris/actions-hugo@v3` n'existe pas au moment de l'exécution, vérifier la dernière version sur https://github.com/peaceiris/actions-hugo/releases et ajuster.

- [ ] **Step 4 : Vérifier build final**

```bash
hugo --minify
# Aucune erreur. public/ généré avec les pages FR et EN.
ls public/
# Doit contenir : index.html, en/, chambres/, tarifs/, etc.
```

- [ ] **Step 5 : Commit**

```bash
git add .github/ static/CNAME
git commit -m "feat: add GitHub Actions deploy workflow and CNAME"
```

---

## Task 8 : Photos (migration depuis WordPress)

**Files:**
- Create: `static/images/` (photos copiées depuis WordPress)
- Modify: pages de contenu pour référencer les images

> **Action manuelle requise** — accès au serveur WordPress nécessaire.

- [ ] **Step 1 : Exporter les photos depuis WordPress**

Depuis le pod WordPress dans Kubernetes :
```bash
kubectl cp -n wordpress <pod-wordpress>:/var/www/html/wp-content/uploads ./wp-uploads
```

Ou via l'interface admin WordPress : Médias → Bibliothèque → sélectionner et télécharger.

- [ ] **Step 2 : Copier les images dans static/images/**

```bash
mkdir -p static/images
cp wp-uploads/**/*.jpg static/images/
cp wp-uploads/**/*.jpeg static/images/
cp wp-uploads/**/*.png static/images/
cp wp-uploads/**/*.webp static/images/
```

Renommer les fichiers avec des noms propres (sans espaces, en minuscules) :
```bash
# Exemple : "chambre bleue.jpg" → "chambre-bleue.jpg"
```

- [ ] **Step 3 : Référencer les images dans le contenu**

Dans chaque fichier de contenu, ajouter l'image hero dans le frontmatter :
```markdown
---
title: "Nos Chambres"
heroStyle: "background"
---

![La chambre principale](/images/chambre-principale.jpg)
```

Pour l'accueil, image hero Congo via frontmatter :
```markdown
---
title: "Bienvenue au Lavardin"
heroStyle: "thumbAndBackground"
---
```

- [ ] **Step 4 : Vérifier localement**

```bash
hugo server -D
# Vérifier que les images s'affichent sur toutes les pages
# Vérifier la page chambres en FR et EN
```

- [ ] **Step 5 : Commit**

```bash
git add static/images/ content/
git commit -m "feat: add photos and wire images into content pages"
```

---

## Task 9 : Création du repo GitHub et premier push

> **Prérequis :** avoir un compte GitHub `shtouff` et `gh` CLI installé.

- [ ] **Step 1 : Créer le repo GitHub**

```bash
gh repo create shtouff/le-lavardin \
  --public \
  --description "Le Lavardin — site gîte Hugo" \
  --source . \
  --remote origin \
  --push
```

- [ ] **Step 2 : Vérifier le push**

```bash
git log --oneline origin/main
# Doit lister tous les commits
```

- [ ] **Step 3 : Vérifier GitHub Actions**

```bash
gh run list --repo shtouff/le-lavardin
# Attendre que le premier run passe (status: completed / success)
gh run watch --repo shtouff/le-lavardin
```

---

## Task 10 : GitHub Pages + DNS

> **Prérequis :** accès à la gestion DNS de ton registrar.

- [ ] **Step 1 : Activer GitHub Pages dans les settings du repo**

```bash
gh api \
  --method POST \
  -H "Accept: application/vnd.github+json" \
  /repos/shtouff/le-lavardin/pages \
  -f source='{"branch":"gh-pages","path":"/"}' \
  -f build_type="workflow"
```

Ou via l'interface GitHub : Settings → Pages → Source → GitHub Actions.

- [ ] **Step 2 : Configurer le domaine custom**

```bash
gh api \
  --method PUT \
  -H "Accept: application/vnd.github+json" \
  /repos/shtouff/le-lavardin/pages \
  -f cname="le-lavardin.com"
```

Ou via l'interface : Settings → Pages → Custom domain → `le-lavardin.com`.

- [ ] **Step 3 : Configurer les DNS chez ton registrar**

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

- [ ] **Step 4 : Attendre la propagation DNS (~30 min) et vérifier**

```bash
dig le-lavardin.com +short
# Doit retourner les 4 IPs GitHub Pages

curl -I https://le-lavardin.com
# HTTP/2 200
# cert Let's Encrypt valide
```

- [ ] **Step 5 : Activer "Enforce HTTPS" dans GitHub Pages settings**

Via l'interface : Settings → Pages → Enforce HTTPS ✓

- [ ] **Step 6 : Vérifier le site en production**

```bash
# Page d'accueil FR
curl -s https://le-lavardin.com | grep "<title>"

# Page EN
curl -s https://le-lavardin.com/en/ | grep "<title>"

# Formulaire de contact
curl -s https://le-lavardin.com/contact | grep "web3forms"
```

- [ ] **Step 7 : Obtenir la clé Web3Forms et remplacer le placeholder**

1. S'inscrire sur https://web3forms.com
2. Créer un accès avec l'email de destination
3. Copier la clé publique générée
4. Remplacer `PLACEHOLDER` dans `config/_default/params.toml`

```bash
# Éditer config/_default/params.toml
# web3forms_key = "ta-vraie-clé-ici"
git add config/_default/params.toml
git commit -m "chore: set Web3Forms access key"
git push
```

- [ ] **Step 8 : Tester le formulaire de contact en production**

Remplir et soumettre le formulaire sur https://le-lavardin.com/contact.
Vérifier que l'email arrive dans la boîte de destination.
