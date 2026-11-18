/* Fin de Mois : test « Quelles aides pour toi ? »
   Les montants et conditions viennent des articles du site (vérifiés sur les sources officielles).
   Si un article change un montant utilisé ici, mettre ce fichier à jour en même temps. */
(function () {
  "use strict";
  var form = document.getElementById("quiz");
  var sortie = document.getElementById("resultats");
  if (!form || !sortie) return;

  var SEUIL_PRIME = 1144.21;   // prime d'activité étudiant/apprenti, revenu d'activité mensuel
  var C2S_GRATUITE = 10421;    // C2S, personne seule, ressources sur 12 mois
  var C2S_PARTICIPATION = 14069;

  function euros(n) {
    return n.toLocaleString("fr-FR", { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + " €";
  }

  function lire() {
    var d = new FormData(form), r = {};
    ["statut", "bourse", "mention", "logement", "stage", "galere", "permis"].forEach(function (k) { r[k] = d.get(k) || ""; });
    var age = parseInt(d.get("age"), 10);
    r.age = age >= 15 && age <= 70 ? age : null;
    var rev = String(d.get("revenus") || "").replace(",", ".").trim();
    r.revenus = rev === "" ? null : Math.max(0, parseFloat(rev) || 0);
    return r;
  }

  function calculer(r) {
    var dem = [], ver = [], non = [];
    var etudiantOuApprenti = r.statut === "etudiant" || r.statut === "apprenti";
    var alternant = r.statut === "apprenti" || r.statut === "pro";
    var loge = r.logement === "loue" || r.logement === "cherche";

    // Bourse et ce qu'elle débloque
    if (r.statut === "etudiant" && r.bourse === "jamais") {
      ver.push({ t: "Bourse Crous", m: "145 à 633 € / mois", s: "montant-bourse-crous-2026-2027",
        d: "Tout dépend des revenus de tes parents, du nombre d'enfants à charge et de la distance avec ton lieu d'études. Fais ta demande dans ton dossier social étudiant (en général entre janvier et mai), même si tu n'es pas sûr : même l'échelon 0, sans argent versé, te fait économiser les frais d'inscription et la CVEC." });
    }
    if (r.bourse === "non") {
      non.push({ t: "Bourse refusée", s: "montant-bourse-crous-2026-2027",
        d: "Si les revenus de ta famille ont baissé depuis (chômage, divorce, décès), tu peux demander un réexamen au Crous sans attendre l'an prochain." });
    }
    if (r.bourse === "oui") {
      dem.push({ t: "Frais d'inscription et CVEC", m: "0 €", s: "frais-inscription-universite-2026-2027",
        d: "Boursier, tu ne paies ni les droits d'inscription à l'université (178 € en licence, 255 € en master) ni la CVEC (105 €). Pour la CVEC, demande quand même ton attestation d'exonération sur cvec.etudiant.gouv.fr." });
      if (r.mention === "oui") {
        var merite = { t: "Aide au mérite", m: "900 € / an", s: "aide-au-merite-etudiant-mention-tres-bien",
          d: "90 € par mois de septembre à juin, en plus de ta bourse, pendant 3 ans maximum. Pas de dossier en plus : vérifie qu'elle apparaît sur ta notification de bourse, sinon contacte ton Crous avec ton relevé de notes du bac." };
        if (r.age !== null && r.age > 28) {
          merite.d = "Service-public indique un âge maximum de 28 ans, sauf exceptions : vérifie ta situation auprès de ton Crous. " + merite.d;
          ver.push(merite);
        } else dem.push(merite);
      }
    }

    // Logement
    if (r.logement === "loue" || r.logement === "cherche") {
      dem.push({ t: "APL (aide au logement)", m: "100 à 250 € / mois", s: "apl-etudiant-2026",
        d: (r.logement === "cherche" ? "Simule-la sur caf.fr avant de signer ton bail, puis fais la demande la semaine où tu emménages. " : "Si ce n'est pas déjà fait, demande-la tout de suite sur caf.fr. ") +
           "C'est la fourchette habituelle pour un étudiant : le montant dépend de ton loyer, de ta ville et de tes ressources. Les mois passés avant ta demande ne sont jamais rattrapés." });
    }
    if (r.logement === "cherche" && r.age !== null && r.age <= 30) {
      dem.push({ t: "Garantie Visale", m: "Garant gratuit", s: "garantie-visale-etudiant",
        d: "Pas de garant ? Action Logement se porte caution auprès de ton propriétaire jusqu'à tes 31 ans, sans condition de salaire. Fais ta demande sur visale.fr avant les visites. Attention : un loyer impayé couvert par Visale reste à rembourser." });
    }
    if (alternant && loge && r.age !== null && r.age < 30) {
      ver.push({ t: "Aide Mobili-Jeune", m: "Jusqu'à 100 € / mois", s: "aide-mobili-jeune-alternant",
        d: "Action Logement rembourse une partie de ton loyer après APL, jusqu'à 1 100 € par an. Il faut que ton logement soit à plus de 70 km (ou 40 minutes) de ton ancienne adresse, ou que tu paies deux loyers, et gagner au plus 120 % du Smic brut. Demande-la dans les 3 mois avant ou les 5 mois après le début de ton contrat : après, c'est trop tard pour l'année." });
    }

    // Travail
    if (r.revenus !== null && r.age !== null) {
      if (r.age >= 18 && r.revenus > SEUIL_PRIME) {
        dem.push({ t: "Prime d'activité", m: "Chaque mois, non imposable", s: "prime-activite-etudiant-2026",
          d: "Tu gagnes plus de 1 144,21 € par mois, le seuil fixé pour les étudiants et les apprentis. Le montant dépend de ton foyer et de tes ressources : fais la simulation sur caf.fr, puis la demande en ligne. Elle n'est jamais versée automatiquement." });
      } else if (r.revenus > 0) {
        non.push({ t: "Prime d'activité", s: "prime-activite-etudiant-2026",
          d: r.age < 18 ? "Il faut avoir au moins 18 ans."
            : "Il faut gagner plus de 1 144,21 € par mois en travaillant. Il te manque " + euros(SEUIL_PRIME - r.revenus + 0.01) + " par mois." });
      }
    }
    if (r.stage === "oui") {
      dem.push({ t: "Gratification de stage", m: "4,50 € / heure minimum", s: "gratification-stage-2026-montant",
        d: "Obligatoire dès le premier jour si ton stage dépasse 2 mois (44 jours à 7 h) ou 308 heures dans le même organisme. À temps plein, ça fait environ 630 à 690 € par mois." +
           (r.revenus !== null && r.revenus <= SEUIL_PRIME ? " Attention : elle ne compte pas pour la prime d'activité." : "") });
    }

    // Coup dur
    if (r.galere === "oui") {
      if (etudiantOuApprenti && r.age !== null && r.age < 35) {
        dem.push({ t: "Aide d'urgence du Crous", m: "Jusqu'à 3 071 €", s: "aide-urgence-crous-etudiant",
          d: "Ouverte aux boursiers comme aux non-boursiers, étudiée au cas par cas. Appelle le 09 72 59 65 65 (du lundi au vendredi, 9 h - 17 h) ou prends rendez-vous avec le service social de ton Crous, avec tes justificatifs. Si c'est très urgent, un versement anticipé jusqu'à 500 € est possible." });
      }
    }

    // Santé : Complémentaire santé solidaire
    if (r.revenus !== null && r.age !== null && r.age <= 49 && r.logement) {
      var seul = r.age > 25 || r.logement !== "parents";
      var annuel = r.revenus * 12;
      if (seul && annuel <= C2S_PARTICIPATION) {
        ver.push({ t: "Complémentaire santé solidaire", s: "complementaire-sante-solidaire-etudiant",
          m: annuel <= C2S_GRATUITE ? "Mutuelle à 0 €" : (r.age <= 29 ? "Mutuelle à 8 € / mois" : "Mutuelle à 14 € / mois"),
          d: "Avec tes revenus du travail, tu resterais sous le plafond pour une personne seule (" + (annuel <= C2S_GRATUITE ? "10 421 €" : "14 069 €") + " sur 12 mois). Mais toutes tes ressources comptent" +
             (r.age <= 25 ? ", et avant 25 ans tu ne peux faire ta demande seul que si tu n'es pas sur l'avis d'imposition de tes parents et qu'ils ne déduisent pas de pension pour toi" : "") + ". Vérifie sur ameli.fr." });
      }
    }

    // Permis
    if (r.permis === "oui" && r.age !== null) {
      if (r.age <= 25) {
        ver.push({ t: "Permis à 1 € par jour", m: "Prêt de 600 à 1 200 € à 0 %", s: "aide-permis-de-conduire-etudiant-2026",
          d: "Tu rembourses 30 € par mois et l'État paie les intérêts. Il faut une auto-école labellisée et l'accord de la banque. Ce n'est pas un don : le remboursement commence le mois suivant, permis en poche ou non." });
      } else {
        non.push({ t: "Permis à 1 € par jour", s: "aide-permis-de-conduire-etudiant-2026", d: "Réservé aux 15-25 ans. Regarde du côté des aides locales de ta mairie, ton département ou ta région." });
      }
      if (r.statut === "apprenti") {
        non.push({ t: "Aide de 500 € au permis des apprentis", s: "aide-permis-de-conduire-etudiant-2026", d: "Elle a été supprimée le 21 février 2026." });
      }
    }

    // En dernier recours
    if (r.galere === "oui") {
      if (r.age !== null && r.age < 28) {
        ver.push({ t: "Prêt étudiant garanti par l'État", m: "Jusqu'à 20 000 €", s: "pret-etudiant-garanti-etat",
          d: "Sans caution et sans condition de revenus, mais c'est un crédit : tu rembourses tout, avec des intérêts fixés par la banque. À garder en dernier recours, après les aides qui ne se remboursent pas." });
      }
    }

    // Pour tout le monde
    if (r.statut) {
      dem.push({ t: "Repas Crous à 1 €", m: "1 € le repas", s: "repas-crous-1-euro-tous-les-etudiants",
        d: "Pour tous les étudiants, alternants compris, sans condition de revenus. Il te faut juste un compte Izly actif. 20 déjeuners par mois te coûtent environ 20 €." });
    }
    return { dem: dem, ver: ver, non: non };
  }

  function esc(t) {
    return String(t).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; });
  }

  function carte(a, genre) {
    return '<li class="res res-' + genre + '"><div class="res-haut"><h3>' + esc(a.t) + "</h3>" +
      (a.m ? '<span class="res-montant">' + esc(a.m) + "</span>" : "") + "</div><p>" + esc(a.d) +
      '</p><a href="/' + a.s + '/">Tout comprendre →</a></li>';
  }

  function groupe(titre, intro, liste, genre) {
    if (!liste.length) return "";
    return '<div class="res-groupe"><h2>' + titre + "</h2>" + (intro ? '<p class="res-intro">' + intro + "</p>" : "") +
      '<ul class="res-liste">' + liste.map(function (a) { return carte(a, genre); }).join("") + "</ul></div>";
  }

  function afficher() {
    var r = lire();
    // questions conditionnelles
    form.querySelectorAll("[data-si]").forEach(function (el) {
      var p = el.getAttribute("data-si").split("=");
      var ok = r[p[0]] === p[1];
      el.hidden = !ok;
      if (!ok) el.querySelectorAll("input").forEach(function (i) { i.checked = false; });
    });
    r = lire();
    var rep = ["statut", "bourse", "logement", "stage", "galere", "permis"].filter(function (k) { return r[k]; }).length +
              (r.age !== null ? 1 : 0) + (r.revenus !== null ? 1 : 0);
    if (!rep) {
      sortie.innerHTML = '<p class="res-vide">Tes résultats apparaîtront ici dès ta première réponse.</p>';
      return;
    }
    var x = calculer(r);
    var resume = x.dem.length + " aide" + (x.dem.length > 1 ? "s" : "") + " à demander" +
      (x.ver.length ? " et " + x.ver.length + " à vérifier" : "");
    var manque = 8 - rep;
    sortie.innerHTML = '<p class="res-resume"><strong>' + resume + "</strong>" +
      (manque > 0 ? "<span>Encore " + manque + " question" + (manque > 1 ? "s" : "") + " pour un résultat complet.</span>" : "<span>Résultat complet.</span>") + "</p>" +
      groupe("À demander", "", x.dem, "dem") +
      groupe("À vérifier", "Tu pourrais y avoir droit, mais une condition ne se vérifie pas ici.", x.ver, "ver") +
      groupe("Pas pour toi pour l'instant", "", x.non, "non");
  }

  form.addEventListener("input", afficher);
  form.addEventListener("change", afficher);
  form.addEventListener("reset", function () { setTimeout(afficher, 0); });
  afficher();
})();
