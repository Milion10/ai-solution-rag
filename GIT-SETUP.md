# Configuration Git Remote

## Option 1 : GitHub

1. Créer un repo sur GitHub : https://github.com/new
   - Nom : `ai-solution-rag`
   - Description : "Solution IA on-premise avec RAG pour entreprises"
   - ❌ Ne pas cocher "Initialize with README"

2. Ajouter le remote et pousser :

```bash
git remote add origin https://github.com/VOTRE-USERNAME/ai-solution-rag.git
git branch -M main
git push -u origin main
```

## Option 2 : GitLab

1. Créer un projet sur GitLab : https://gitlab.com/projects/new
   - Project name : `ai-solution-rag`
   - Visibility : Private

2. Ajouter le remote et pousser :

```bash
git remote add origin https://gitlab.com/VOTRE-USERNAME/ai-solution-rag.git
git branch -M main
git push -u origin main
```

## Option 3 : Azure DevOps

```bash
git remote add origin https://dev.azure.com/ORGANIZATION/PROJECT/_git/ai-solution-rag
git push -u origin --all
```

## Vérifier le remote

```bash
git remote -v
```

## Futurs commits

Après avoir fait des modifications :

```bash
# Voir les changements
git status

# Ajouter les fichiers modifiés
git add .

# Commiter avec un message
git commit -m "feat: ajouter fonctionnalité X"

# Pousser vers le remote
git push
```

## Conventions de commit (optionnel)

- `feat:` nouvelle fonctionnalité
- `fix:` correction de bug
- `docs:` documentation
- `refactor:` refactorisation sans changement de comportement
- `perf:` amélioration de performance
- `test:` ajout/modification de tests
- `chore:` tâches de maintenance

Exemples :
```bash
git commit -m "feat: support DOCX uploads"
git commit -m "fix: documents not showing for MEMBER users"
git commit -m "docs: update README with deployment instructions"
```
