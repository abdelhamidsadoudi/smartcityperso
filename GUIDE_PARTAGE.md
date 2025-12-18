# Guide de Partage - Smart City

## Pour VOUS (créateur du projet)

### Comment préparer le projet pour le partage

1. **Nettoyer le projet**
   ```bash
   # Supprimer les fichiers temporaires
   cd frontend
   rm -rf node_modules
   cd ..
   ```

2. **Créer une archive**
   - Sélectionner le dossier `SMART`
   - Faire un clic droit → "Envoyer vers" → "Dossier compressé"
   - Ou utiliser la commande : `zip -r SMART.zip SMART -x "*/node_modules/*" "*.db"`

3. **Partager l'archive**
   - Via Google Drive, Dropbox, WeTransfer, etc.
   - Ou via GitHub (créer un dépôt)

---

## Pour VOS AMIS (utilisateurs finaux)

### Prérequis à installer (OBLIGATOIRE)

#### Windows

1. **Python 3.12**
   - Télécharger : https://www.python.org/downloads/
   - ⚠️ IMPORTANT : Cocher "Add Python to PATH" lors de l'installation
   - Vérifier : Ouvrir cmd et taper `python --version`

2. **Node.js 18+**
   - Télécharger : https://nodejs.org/
   - Choisir la version LTS (Long Term Support)
   - Vérifier : Ouvrir cmd et taper `node --version`

#### Mac

```bash
# Installer Homebrew si pas déjà installé
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Installer Python et Node
brew install python@3.12 node
```

#### Linux (Ubuntu/Debian)

```bash
# Python
sudo apt update
sudo apt install python3.12 python3-pip

# Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
```

---

### Installation du projet

#### Étape 1 : Extraire le fichier

1. Télécharger le fichier `SMART.zip`
2. Extraire le contenu dans un dossier (ex: Documents)
3. Ouvrir un terminal/cmd dans le dossier SMART

#### Étape 2 : Installer les dépendances Python

**Windows (PowerShell ou cmd) :**
```cmd
cd backend
pip install -r requirements.txt
cd ..
```

**Mac/Linux :**
```bash
cd backend
pip3 install -r requirements.txt
cd ..
```

**En cas d'erreur "pip n'est pas reconnu" :**
```cmd
python -m pip install -r requirements.txt
```

#### Étape 3 : Installer les dépendances Node.js

```bash
cd frontend
npm install
cd ..
```

**⏱️ Patience :** L'installation peut prendre 2-5 minutes selon votre connexion.

#### Étape 4 : Lancer l'application

**Windows :**
- Double-cliquer sur `start.bat`
- 3 fenêtres noires vont s'ouvrir (NORMAL)

**Mac/Linux :**
Ouvrir 3 terminaux :

```bash
# Terminal 1 - Backend
cd backend
python3 api_backend.py

# Terminal 2 - Collecteur
cd backend
python3 Collecte_donnees.py

# Terminal 3 - Frontend
cd frontend
npm run dev
```

#### Étape 5 : Utiliser l'application

1. Ouvrir votre navigateur (Chrome, Firefox, Edge)
2. Aller sur : **http://localhost:5173**
3. Se connecter avec :
   - Email : `marie.dubois@smartcity.com`
   - Mot de passe : `password123`

---

## Problèmes courants

### ❌ "Python n'est pas reconnu"

**Solution :**
1. Réinstaller Python depuis https://www.python.org/
2. ⚠️ **COCHER "Add Python to PATH"**
3. Redémarrer le terminal/cmd

### ❌ "npm n'est pas reconnu"

**Solution :**
1. Réinstaller Node.js depuis https://nodejs.org/
2. Redémarrer le terminal/cmd

### ❌ "Port 5000 already in use"

**Windows :**
```cmd
netstat -ano | findstr :5000
taskkill /PID [numero_du_processus] /F
```

**Mac/Linux :**
```bash
lsof -ti:5000 | xargs kill -9
```

### ❌ L'application affiche "Aucune donnée"

**Solution :**
Attendre 1-2 minutes que le collecteur remplisse la base de données.
Vérifier que `Collecte_donnees.py` tourne bien.

### ❌ "npm ERR! code ENOENT"

**Solution :**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### ❌ Erreur PostCSS

**Solution :**
```bash
cd frontend
npm cache clean --force
rm -rf node_modules
npm install
```

---

## FAQ

**Q : Combien de temps faut-il pour l'installation ?**
R : Environ 5-10 minutes (téléchargement + installation des dépendances)

**Q : L'application marche hors ligne ?**
R : Non, elle a besoin d'Internet pour récupérer les données de pollution en temps réel.

**Q : Puis-je fermer les fenêtres noires ?**
R : Non, elles sont nécessaires pour faire tourner l'application. Les fermer = arrêter l'application.

**Q : Comment arrêter l'application ?**
R : Fermer les 3 fenêtres noires (Windows) ou faire Ctrl+C dans chaque terminal (Mac/Linux)

**Q : L'application fonctionne sur mobile ?**
R : Oui, dans le navigateur mobile, mais c'est optimisé pour ordinateur.

**Q : Puis-je changer la ville surveillée ?**
R : Oui, éditer `backend/Collecte_donnees.py` ligne 23 (variable `CITY`)

---

## Support

Si vous rencontrez un problème :

1. Vérifier que Python et Node.js sont bien installés (`python --version` et `node --version`)
2. Vérifier que les 3 composants tournent (backend, collecteur, frontend)
3. Regarder les messages d'erreur dans les terminaux
4. Redémarrer l'application

**Bon usage ! 🌍**
