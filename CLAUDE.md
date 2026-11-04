# Fin de Mois — consignes pour la publication automatique

Site : https://ingaaal.github.io/site-auto/ (GitHub Pages, servi depuis `docs/` sur `main`).
Sujet : le budget étudiant en France (aides, bourses, logement, démarches, bons plans, économies, jobs étudiants, banque).
Public : étudiants de 17 à 25 ans. On tutoie le lecteur.

## Publier un article

1. Lire `articles/` pour connaître les sujets déjà traités. Ne jamais publier deux articles sur la même intention de recherche.
2. Choisir UN sujet que les étudiants cherchent vraiment sur Google (question concrète, montant, démarche, comparaison). Privilégier les requêtes précises (« aide au permis étudiant 2026 », « job étudiant combien d'heures par semaine ») plutôt que les sujets vagues.
3. Rechercher sur le web. Sources officielles d'abord : service-public.fr, caf.fr, lescrous.fr, etudiant.gouv.fr, legifrance.gouv.fr, sites des régions ou de la ville. Vérifier chaque montant et chaque date sur au moins une source officielle ou deux sources sérieuses récentes. Si une info n'est pas confirmée, ne pas l'écrire.
4. Écrire `articles/<slug>.md` (slug en minuscules, mots séparés par des tirets) avec l'en-tête :
   ```
   ---
   title: ...
   description: une phrase de 140 à 160 caractères
   date: AAAA-MM-JJ
   category: Aides | Logement | Bons plans | Banque | Jobs | Démarches
   ---
   ```
5. Style : la réponse à la question dès le premier paragraphe, avec le chiffre clé en **gras**. Puis des sections `##` courtes, des listes, un tableau quand il y a des montants. 600 à 1 200 mots. Phrases simples, pas de remplissage, pas de formules creuses (« dans cet article », « il est important de noter »). Ne jamais copier de phrases des sources : tout réécrire.
6. Finir par le bloc sources :
   ```
   <div class="sources"><h2>Sources</h2>
   Liste des sources, séparées par des points-virgules.
   </div>
   ```
7. Lancer `python3 build.py` (installer `markdown` avec `pip install --break-system-packages markdown` si besoin), vérifier qu'il n'y a pas d'erreur.
8. Commit sur `main` avec un message clair (« Article : ... ») puis push.

## Mettre à jour

Si un article existant contient un montant ou une règle qui a changé, le corriger et ajouter `updated: AAAA-MM-JJ` dans son en-tête plutôt que d'écrire un nouvel article.

## Interdits

- Inventer un chiffre, une date ou une citation.
- Donner un conseil financier personnalisé. Pour la banque ou l'argent : présenter les faits et rappeler de vérifier sur le site officiel.
- Publier plus d'un article par exécution.
