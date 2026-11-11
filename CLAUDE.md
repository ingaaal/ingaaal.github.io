# Fin de Mois — consignes pour la publication automatique

Site : https://ingaaal.github.io/ (dépôt ingaaal/ingaaal.github.io, GitHub Pages servi depuis `docs/` sur `main`).
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
5. Style et structure (obligatoires) — 700 à 1 200 mots :
   - **Accroche** : la réponse dès le premier paragraphe avec le chiffre clé en **gras**, puis une phrase qui donne envie de lire la suite (un enjeu concret, un piège à éviter, ce que ça représente sur l'année).
   - Sections `##` courtes, listes, un tableau dès qu'il y a des montants.
   - **Un exemple concret chiffré** (« Tu es à l'échelon 2 et… », « Tu loues un studio à 450 €… ») construit uniquement avec des chiffres vérifiés ; si un montant est hypothétique, le présenter clairement comme un exemple.
   - **Une section « Les erreurs qui coûtent cher »** (ou équivalent) avec 3 à 4 erreurs fréquentes.
   - **Une section « Questions fréquentes »** à la fin : 3 à 4 questions telles que les gens les tapent sur Google, chaque question seule sur sa ligne en **gras**, puis une ligne vide, puis la réponse courte.
   - **2 liens internes minimum** vers d'autres articles du site quand c'est pertinent, au format `[texte](/<slug>/)`. Si un nouvel article est lié à un ancien, ajouter aussi un lien depuis l'ancien vers le nouveau.
   - Phrases simples, tutoiement, pas de remplissage, pas de formules creuses (« dans cet article », « il est important de noter »). Ne jamais copier de phrases des sources : tout réécrire.
6. Finir par le bloc sources. Chaque source est un lien Markdown vers la page réellement lue (URL exacte, jamais devinée), séparées par des points-virgules :
   ```
   <div class="sources"><h2>Sources</h2>
   [Organisme, « Titre de la page »](https://url-exacte) ; [Autre source, date](https://url-exacte).
   </div>
   ```
   Ne citer que des pages effectivement lues pendant la recherche.
7. Lancer `python3 build.py` (installer `markdown` et `Pillow` avec `pip install --break-system-packages markdown Pillow` si besoin). Le script contrôle chaque article avant de générer le site : en cas d'« ÉCHEC », rien n'est généré ; corriger chaque point listé et relancer. Les lignes « alerte » sont à corriger si c'est possible sans dégrader l'article.
8. Commit sur `main` avec un message clair (« Article : ... ») puis push. Inclure `docs/` et les images de partage créées dans `static/og/`.

## Mettre à jour

Si un article existant contient un montant ou une règle qui a changé, le corriger et ajouter `updated: AAAA-MM-JJ` dans son en-tête plutôt que d'écrire un nouvel article.

La date affichée « Infos vérifiées le » est `updated` si présent, sinon `date`. Ne modifier `updated` qu'après avoir revérifié l'article sur les sources officielles.

## Interdits

- Inventer un chiffre, une date ou une citation.
- Donner un conseil financier personnalisé. Pour la banque ou l'argent : présenter les faits et rappeler de vérifier sur le site officiel.
- Publier plus d'un article par exécution.
