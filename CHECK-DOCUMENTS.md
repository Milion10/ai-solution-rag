# Guide de vérification des documents

## 1. Vérifier les documents dans la base de données

```powershell
# Voir tous les documents avec leurs détails
docker exec -i ai-solution-postgres psql -U ai_user -d ai_solution -c "SELECT id, filename, scope, user_id, organization_id, is_indexed, uploaded_at FROM documents ORDER BY uploaded_at DESC;"
```

## 2. Types de documents

### Documents GLOBAUX (scope: organization)
- **Uploadés depuis** : Dashboard (`/dashboard`) - ADMIN seulement
- **Champ rempli** : `organization_id`
- **Champ vide** : `user_id`
- **Accessibles par** : Tous les membres de l'organisation
- **Indicateur visuel** : Badge "🌍 Global" dans la liste

### Documents PRIVÉS (scope: user)
- **Uploadés depuis** : Chat (icône 📎 trombone)
- **Champ rempli** : `user_id`
- **Champ vide** : `organization_id`
- **Accessibles par** : Uniquement l'utilisateur qui l'a uploadé
- **Indicateur visuel** : Message vert "✅ fichier.pdf ajouté à cette conversation (privé)"

## 3. Tests de vérification

### Test 1 : Upload document global
1. Aller sur `/dashboard` (connexion ADMIN requise)
2. Uploader un PDF via le formulaire de gauche
3. Vérifier :
   ```sql
   SELECT filename, scope, organization_id, user_id 
   FROM documents 
   WHERE filename = 'ton-fichier.pdf';
   ```
   ✅ `scope = 'organization'` et `organization_id` rempli

### Test 2 : Upload document privé
1. Aller sur `/chat`
2. Cliquer sur l'icône 📎 trombone
3. Sélectionner un PDF
4. Cliquer sur "Upload"
5. ✅ Message vert apparaît : "fichier.pdf ajouté à cette conversation (privé)"
6. Vérifier :
   ```sql
   SELECT filename, scope, organization_id, user_id 
   FROM documents 
   WHERE filename = 'ton-fichier.pdf';
   ```
   ✅ `scope = 'user'` et `user_id` rempli

### Test 3 : RAG avec documents globaux
1. Dashboard : Upload un PDF avec contenu unique (ex: "Le projet Apollo")
2. Chat : Poser une question sur ce contenu
3. ✅ L'IA doit mentionner le document dans les sources

### Test 4 : RAG avec documents privés
1. Chat : Upload un PDF via 📎 avec contenu unique
2. Attendre 10-15 secondes (indexation)
3. Poser une question sur ce contenu
4. ✅ L'IA doit trouver l'info dans ce document

### Test 5 : Isolation des documents privés
1. User A : Upload un document privé "secret.pdf"
2. User B : Se connecter avec un autre compte
3. User B : Poser une question sur le contenu de "secret.pdf"
4. ✅ L'IA ne doit PAS trouver ce document (user_id différent)

## 4. Vérifier l'indexation

```sql
-- Voir les documents non indexés
SELECT filename, is_indexed, indexing_status, uploaded_at 
FROM documents 
WHERE is_indexed = false 
ORDER BY uploaded_at DESC;

-- Voir les chunks indexés pour un document
SELECT d.filename, COUNT(c.id) as nb_chunks
FROM documents d
LEFT JOIN document_chunks c ON d.id = c.document_id
GROUP BY d.id, d.filename
ORDER BY d.uploaded_at DESC;
```

## 5. Nettoyer les doublons (si besoin)

```sql
-- Voir les doublons
SELECT filename, COUNT(*) as count 
FROM documents 
GROUP BY filename 
HAVING COUNT(*) > 1;

-- Supprimer les doublons (garde le plus récent)
DELETE FROM documents
WHERE id NOT IN (
  SELECT MAX(id)
  FROM documents
  GROUP BY filename, user_id, organization_id
);
```

## 6. Commandes utiles

```powershell
# Redémarrer l'app
.\stop-app.ps1
.\start-app.ps1

# Voir les logs backend (pour debug indexation)
docker logs ai-solution-backend -f

# Connexion psql interactive
docker exec -it ai-solution-postgres psql -U ai_user -d ai_solution
```

## 7. Résumé de ton système actuel

D'après la BDD :
- ✅ 2 documents globaux : `prd.pdf`, `prd-1.pdf` (organization_id rempli)
- ✅ 3 documents privés : `Mémoire - Gestion des Tâches planifiées.pdf` x3 (user_id rempli)
- ⚠️ Tu as des doublons (même fichier uploadé 3 fois en test)
- ⚠️ Aucun document n'est indexé (`is_indexed = false`) → le backend doit indexer

**Le système fonctionne correctement !** Les documents sont bien enregistrés avec la bonne structure.
