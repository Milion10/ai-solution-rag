# Partager le projet avec un collaborateur

## 🎯 Option 1 : GitHub/GitLab (Recommandé)

### Sur GitHub

1. **Pousser votre code** (si pas encore fait) :
```bash
cd C:\Users\axelm\OneDrive\Documents\Code\Projet-ia\ai-solution
git remote add origin https://github.com/VOTRE-USERNAME/ai-solution-rag.git
git branch -M main
git push -u origin main
```

2. **Ajouter votre ami comme collaborateur** :
   - Aller sur : `https://github.com/VOTRE-USERNAME/ai-solution-rag/settings/access`
   - Cliquer sur "Add people"
   - Entrer son username GitHub ou email
   - Choisir le rôle : `Write` (peut push) ou `Admin` (contrôle total)

3. **Votre ami clone le repo** :
```bash
git clone https://github.com/VOTRE-USERNAME/ai-solution-rag.git
cd ai-solution-rag
```

### Sur GitLab

1. **Pousser votre code** :
```bash
git remote add origin https://gitlab.com/VOTRE-USERNAME/ai-solution-rag.git
git push -u origin main
```

2. **Ajouter votre ami comme membre** :
   - Aller sur : `Project > Members > Invite members`
   - Entrer son username GitLab
   - Choisir le rôle : `Developer` ou `Maintainer`

---

## 📦 Option 2 : Fichier ZIP (Rapide mais pas de sync)

**Créer un export sans git :**

```powershell
cd C:\Users\axelm\OneDrive\Documents\Code\Projet-ia

# Créer un zip excluant les dossiers sensibles
Compress-Archive -Path "ai-solution\*" -DestinationPath "ai-solution-export.zip" -CompressionLevel Optimal
```

**⚠️ Avant d'envoyer, supprimer manuellement du zip :**
- `node_modules/`
- `.next/`
- `__pycache__/`
- `backend/uploads/*.pdf` (documents users)
- Fichiers `.env` (contiennent des secrets)

**Votre ami devra :**
1. Dézipper
2. Installer les dépendances : `npm install` et `pip install -r requirements.txt`
3. Créer ses propres fichiers `.env`

---

## 🔐 Option 3 : Repo Privé Partagé (Meilleure sécurité)

### GitHub Private Repo

1. **Créer un repo PRIVÉ** sur GitHub
2. Suivre les étapes de l'Option 1
3. Seuls les collaborateurs invités peuvent voir le code

### GitLab Private Repo

Par défaut, les repos GitLab sont privés. Suivre les étapes de l'Option 1.

---

## 🚀 Option 4 : Fork + Pull Requests (Workflow pro)

**Si vous voulez que votre ami contribue proprement :**

1. **Vous** : Créez un repo public sur GitHub
2. **Votre ami** : 
   - Fork le repo (bouton "Fork" sur GitHub)
   - Clone son fork : `git clone https://github.com/SON-USERNAME/ai-solution-rag.git`
   - Crée une branche : `git checkout -b feature/nouvelle-fonctionnalite`
   - Fait des modifications et commit
   - Pousse sur son fork : `git push origin feature/nouvelle-fonctionnalite`
   - Ouvre une Pull Request vers votre repo

3. **Vous** : Reviewez et mergez la PR

---

## 📋 Instructions pour votre ami (après clone)

**1. Prérequis**
- Node.js 18+
- Python 3.14+
- Docker
- Ollama + Mistral 7B

**2. Setup**

```bash
# Cloner le repo
git clone <URL-DU-REPO>
cd ai-solution-rag

# PostgreSQL
cd docker
docker compose up -d
cd ..

# Backend
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
pip install -r requirements.txt

# Créer .env (copier .env.example)
# DATABASE_URL=postgresql://ai_user:ai_password@localhost:5432/ai_solution
# OLLAMA_BASE_URL=http://localhost:11434

python -m backend.main  # Démarrer sur port 8000
cd ..

# Frontend
cd frontend
npm install
npx prisma generate
npx prisma db push

# Créer .env (copier .env.example)
# DATABASE_URL=postgresql://ai_user:ai_password@localhost:5432/ai_solution
# NEXTAUTH_SECRET=<générer avec: openssl rand -base64 32>
# NEXTAUTH_URL=http://localhost:3000

npm run dev  # Démarrer sur port 3000
```

**3. Ollama**
```bash
ollama pull mistral
```

**4. Tester**
- Aller sur http://localhost:3000
- Créer un compte (devient ADMIN)
- Uploader un PDF
- Poser une question

---

## 🤝 Workflow collaboratif recommandé

**Pour travailler ensemble efficacement :**

1. **Créer des branches pour chaque feature**
```bash
git checkout -b feature/nom-de-la-feature
# ... faire des modifications ...
git add .
git commit -m "feat: description"
git push origin feature/nom-de-la-feature
```

2. **Fusionner via Pull Request** (review de code)

3. **Garder main propre** (seulement du code qui fonctionne)

4. **Communiquer** :
   - Utiliser les Issues GitHub pour les bugs/idées
   - Faire des commits clairs
   - Documenter les changements importants

---

## ⚡ Résumé rapide

**Si vous êtes pressés :**

1. Créer repo sur GitHub (privé ou public)
2. Pousser le code :
   ```bash
   git remote add origin https://github.com/VOUS/ai-solution-rag.git
   git push -u origin main
   ```
3. Inviter votre ami comme collaborateur
4. Il clone et suit les instructions du README.md

**Lien à partager avec votre ami :**
`https://github.com/VOTRE-USERNAME/ai-solution-rag`
