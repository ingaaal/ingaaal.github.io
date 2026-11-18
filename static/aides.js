/* Fin de Mois : test « Quelles aides pour toi ? », une question à la fois.
   Les montants et conditions viennent des articles du site (vérifiés sur les sources officielles).
   Si un article change un montant utilisé ici, mettre ce fichier à jour en même temps. */
(function () {
  "use strict";
  var boite = document.getElementById("test");
  if (!boite) return;

  var QUESTIONS = [
    { k: "age", q: "Tu as quel âge ?", r: [["moins18", "17 ans ou moins"], ["18-25", "Entre 18 et 25 ans"], ["26-29", "Entre 26 et 29 ans"], ["30plus", "30 ans ou plus"]] },
    { k: "statut", q: "Cette année, tu es…", r: [["etudiant", "Étudiant"], ["apprenti", "En alternance (apprentissage)"], ["pro", "En alternance (contrat de professionnalisation)"]] },
    { k: "bourse", q: "Tu as une bourse du Crous ?", r: [["oui", "Oui"], ["non", "Non"]] },
    { k: "mention", si: function (r) { return r.bourse === "oui"; }, q: "Tu as eu la mention très bien au bac ?",
      p: "En entrant dans le supérieur ou l'année d'avant, sans avoir redoublé depuis.", r: [["oui", "Oui"], ["non", "Non"]] },
    { k: "logement", q: "Où tu vis ?", r: [["parents", "Chez mes parents"], ["loue", "Dans un logement que je loue"], ["cherche", "Je cherche un logement"]] },
    { k: "revenus", q: "Tu gagnes combien par mois en travaillant ?", p: "Ton salaire net d'un job ou de l'alternance. Ne compte pas la gratification de stage.",
      r: [["0", "Rien, je ne travaille pas"], ["moins850", "Moins de 850 €"], ["850-1144", "Entre 850 € et 1 144 €"], ["plus1144", "Plus de 1 144 €"]] },
    { k: "stage", q: "Tu fais un stage de plus de 2 mois cette année ?", r: [["oui", "Oui"], ["non", "Non"]] },
    { k: "galere", q: "En ce moment, c'est dur de finir le mois ?", p: "Loyer en retard, job perdu, grosse dépense imprévue…", r: [["oui", "Oui"], ["non", "Non"]] },
    { k: "permis", q: "Tu veux passer le permis de conduire ?", r: [["oui", "Oui"], ["non", "Non"]] }
  ];

  var rep = {}, chemin = [], occupe = false;

  function suivantes() { return QUESTIONS.filter(function (x) { return !x.si || x.si(rep); }); }

  function aides(r) {
    var dem = [], ver = [];
    var jeune = r.age === "moins18" || r.age === "18-25";
    var majeur = r.age !== "moins18";
    var alternant = r.statut === "apprenti" || r.statut === "pro";
    var loge = r.logement === "loue" || r.logement === "cherche";

    if (r.bourse === "oui") {
      dem.push(["Frais d'inscription et CVEC", "0 €", "Boursier, tu ne paies ni l'inscription à l'université (178 € en licence) ni la CVEC (105 €). Demande quand même ton attestation d'exonération CVEC.", "frais-inscription-universite-2026-2027"]);
      if (r.mention === "oui") {
        if (r.age === "26-29") ver.push(["Aide au mérite", "900 € par an", "En principe jusqu'à 28 ans. 90 € par mois en plus de ta bourse, pendant 3 ans maximum.", "aide-au-merite-etudiant-mention-tres-bien"]);
        else if (r.age !== "30plus") dem.push(["Aide au mérite", "900 € par an", "90 € par mois en plus de ta bourse, pendant 3 ans maximum. Rien à demander : vérifie qu'elle figure sur ta notification de bourse.", "aide-au-merite-etudiant-mention-tres-bien"]);
      }
    } else if (r.statut === "etudiant") {
      ver.push(["Bourse du Crous", "145 à 633 € par mois", "Ça dépend des revenus de tes parents. Si tu n'as pas fait ta demande cette année, fais-la : même à l'échelon 0, tu ne paies ni l'inscription ni la CVEC.", "montant-bourse-crous-2026-2027"]);
    }

    if (loge) {
      dem.push(["APL (aide au logement)", "100 à 250 € par mois", "C'est ce que touche en général un étudiant qui loue. Demande-la sur caf.fr dès que tu emménages : les mois d'avant sont perdus.", "apl-etudiant-2026"]);
    }
    if (r.logement === "cherche" && r.age !== "30plus") {
      dem.push(["Garantie Visale", "Un garant gratuit", "Pas de garant ? Action Logement se porte garant auprès du propriétaire, sans condition de salaire, jusqu'à 30 ans.", "garantie-visale-etudiant"]);
    }
    if (alternant && loge && r.age !== "30plus") {
      ver.push(["Aide Mobili-Jeune", "Jusqu'à 100 € par mois", "Pour les alternants qui ont déménagé à plus de 70 km (ou 40 minutes) ou qui paient deux loyers. À demander au plus tard 5 mois après le début du contrat.", "aide-mobili-jeune-alternant"]);
    }

    if (r.revenus === "plus1144" && majeur) {
      dem.push(["Prime d'activité", "Versée chaque mois", "Tu gagnes plus de 1 144,21 € par mois : tu passes le seuil. Le montant dépend de ta situation, fais la simulation sur caf.fr.", "prime-activite-etudiant-2026"]);
    }
    if (r.stage === "oui") {
      dem.push(["Gratification de stage", "Au moins 4,50 € de l'heure", "Obligatoire quand le stage dure plus de 2 mois : environ 630 à 690 € par mois à temps plein.", "gratification-stage-2026-montant"]);
    }

    if (r.galere === "oui" && r.statut !== "pro") {
      if (r.age === "30plus") ver.push(["Aide d'urgence du Crous", "Jusqu'à 3 071 €", "Réservée aux moins de 35 ans, boursiers ou non. Appelle le 09 72 59 65 65 pour être orienté.", "aide-urgence-crous-etudiant"]);
      else dem.push(["Aide d'urgence du Crous", "Jusqu'à 3 071 €", "Boursier ou non. Appelle le 09 72 59 65 65 (du lundi au vendredi, 9 h - 17 h) ou prends rendez-vous avec l'assistant social de ton Crous.", "aide-urgence-crous-etudiant"]);
    }

    var seul = r.logement !== "parents" || r.age === "26-29" || r.age === "30plus";
    if (seul && (r.revenus === "0" || r.revenus === "moins850" || r.revenus === "850-1144")) {
      ver.push(["Complémentaire santé solidaire", r.revenus === "850-1144" ? "Mutuelle gratuite ou presque" : "Mutuelle gratuite",
        "Si toutes tes ressources des 12 derniers mois restent sous le plafond (10 421 € pour la version gratuite)." + (jeune ? " Avant 25 ans, il ne faut pas être sur la déclaration d'impôts de tes parents." : ""),
        "complementaire-sante-solidaire-etudiant"]);
    }

    if (r.permis === "oui" && jeune) {
      ver.push(["Permis à 1 € par jour", "Prêt de 600 à 1 200 €", "Sans intérêts : tu rembourses 30 € par mois. Il faut une auto-école partenaire et l'accord d'une banque.", "aide-permis-de-conduire-etudiant-2026"]);
    }
    if (r.galere === "oui" && (r.age === "18-25" || r.age === "26-29")) {
      ver.push(["Prêt étudiant garanti par l'État", "Jusqu'à 20 000 €", "Sans caution, " + (r.age === "26-29" ? "avant 28 ans. " : "") + "mais c'est un crédit à rembourser avec intérêts. À garder en dernier recours.", "pret-etudiant-garanti-etat"]);
    }

    dem.push(["Repas Crous à 1 €", "1 € le repas", "Pour tous les étudiants et alternants, sans condition. Il te faut juste un compte Izly.", "repas-crous-1-euro-tous-les-etudiants"]);
    return { dem: dem, ver: ver };
  }

  function esc(t) { return String(t).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }

  function haut(i, n) {
    return '<div class="barre"><i style="width:' + Math.round(i / n * 100) + '%"></i></div><div class="etape-haut">' +
      (chemin.length ? '<button type="button" class="retour-q" data-action="retour">← Retour</button>' : "<span></span>") +
      "<span>" + (i < n ? "Question " + (i + 1) + " sur " + n : "Terminé") + "</span></div>";
  }

  function afficherQuestion(x) {
    var liste = suivantes(), i = liste.indexOf(x);
    boite.innerHTML = haut(i, liste.length) +
      '<h2 class="question" tabindex="-1">' + esc(x.q) + "</h2>" + (x.p ? '<p class="precision">' + esc(x.p) + "</p>" : "") +
      '<div class="reponses">' + x.r.map(function (o) {
        return '<button type="button" class="rep" data-v="' + o[0] + '" aria-pressed="' + (rep[x.k] === o[0]) + '">' + esc(o[1]) + "</button>";
      }).join("") + "</div>";
    boite.dataset.k = x.k;
  }

  function carte(a, v) {
    return '<li class="res' + (v ? " res-v" : "") + '"><div class="res-haut"><h3>' + esc(a[0]) + '</h3><span class="badge' + (v ? " badge-v" : "") + '">' +
      (v ? "À vérifier" : "À demander") + '</span></div><span class="res-montant">' + esc(a[1]) + "</span><p>" + esc(a[2]) +
      '</p><a href="/' + a[3] + '/">Comment l\'obtenir →</a></li>';
  }

  function afficherResultat() {
    var x = aides(rep), n = x.dem.length + x.ver.length;
    boite.innerHTML = haut(1, 1) +
      '<h2 class="res-titre question" tabindex="-1">Tu as peut-être droit à ' + n + " aide" + (n > 1 ? "s" : "") + "</h2>" +
      '<p class="res-sous">' + x.dem.length + " à demander" + (x.ver.length ? ", " + x.ver.length + " à vérifier selon ta situation" : "") + ".</p>" +
      '<ul class="res-liste">' + x.dem.map(function (a) { return carte(a, false); }).join("") + x.ver.map(function (a) { return carte(a, true); }).join("") + "</ul>" +
      '<div class="res-actions"><button type="button" class="btn btn-2" data-action="refaire">Refaire le test</button></div>';
    boite.dataset.k = "";
  }

  function aller(x, focus) {
    if (x) afficherQuestion(x); else afficherResultat();
    if (focus) {
      var h = boite.querySelector(".question");
      if (h) h.focus({ preventScroll: true });
      var y = boite.getBoundingClientRect().top + window.scrollY - 80;
      if (window.scrollY > y) window.scrollTo({ top: y, behavior: "smooth" });
    }
  }

  function prochaine() {
    var liste = suivantes();
    for (var i = 0; i < liste.length; i++) if (!(liste[i].k in rep)) return liste[i];
    return null;
  }

  boite.addEventListener("click", function (e) {
    var b = e.target.closest("button");
    if (!b) return;
    if (b.dataset.action === "retour") {
      var k = chemin.pop();
      delete rep[k];
      QUESTIONS.forEach(function (q) { if (q.si && !q.si(rep)) delete rep[q.k]; });
      aller(QUESTIONS.filter(function (q) { return q.k === k; })[0], true);
    } else if (b.dataset.action === "refaire") {
      rep = {}; chemin = [];
      aller(QUESTIONS[0], true);
    } else if (b.dataset.v && !occupe) {
      occupe = true;
      var cle = boite.dataset.k;
      rep[cle] = b.dataset.v;
      chemin.push(cle);
      QUESTIONS.forEach(function (q) { if (q.si && !q.si(rep)) delete rep[q.k]; });
      b.setAttribute("aria-pressed", "true");
      setTimeout(function () { occupe = false; aller(prochaine(), true); }, 120);
    }
  });

  aller(QUESTIONS[0], false);
})();
