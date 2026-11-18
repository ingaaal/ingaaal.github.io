/* Fin de Mois : mode sombre, partage, filtres de l'accueil */
(function () {
  "use strict";
  var racine = document.documentElement;

  /* Mode clair / sombre */
  var bouton = document.querySelector(".theme");
  if (bouton) {
    var sombreSysteme = window.matchMedia ? window.matchMedia("(prefers-color-scheme: dark)") : null;
    var actuel = function () { return racine.dataset.theme || (sombreSysteme && sombreSysteme.matches ? "dark" : "light"); };
    var maj = function () {
      var s = actuel() === "dark";
      bouton.setAttribute("aria-label", s ? "Passer en mode clair" : "Passer en mode sombre");
      bouton.setAttribute("aria-pressed", s ? "true" : "false");
    };
    bouton.hidden = false;
    maj();
    bouton.addEventListener("click", function () {
      var t = actuel() === "dark" ? "light" : "dark";
      racine.dataset.theme = t;
      try { localStorage.setItem("theme", t); } catch (e) {}
      maj();
    });
    if (sombreSysteme && sombreSysteme.addEventListener) sombreSysteme.addEventListener("change", maj);
  }

  /* Partage */
  function copier(texte) {
    if (navigator.clipboard && window.isSecureContext) return navigator.clipboard.writeText(texte);
    return new Promise(function (ok, ko) {
      var t = document.createElement("textarea");
      t.value = texte; t.setAttribute("readonly", ""); t.style.position = "fixed"; t.style.opacity = "0";
      document.body.appendChild(t); t.select();
      try { document.execCommand("copy") ? ok() : ko(); } catch (e) { ko(); }
      document.body.removeChild(t);
    });
  }
  document.querySelectorAll(".partage").forEach(function (bloc) {
    var url = bloc.dataset.url, titre = bloc.dataset.titre;
    var natif = bloc.querySelector(".p-natif"), bouton = bloc.querySelector(".p-copier");
    if (navigator.share && natif) {
      natif.hidden = false;
      natif.addEventListener("click", function () { navigator.share({ title: titre, url: url }).catch(function () {}); });
    }
    if (bouton) {
      var libelle = bouton.querySelector("span");
      bouton.addEventListener("click", function () {
        copier(url).then(function () {
          libelle.textContent = "Lien copié !"; bouton.classList.add("ok");
          setTimeout(function () { libelle.textContent = "Copier le lien"; bouton.classList.remove("ok"); }, 2000);
        }, function () { window.prompt("Copie ce lien :", url); });
      });
    }
  });

  /* Accueil : filtres et « voir plus » */
  var grille = document.getElementById("grille");
  if (!grille) return;
  var cartes = Array.prototype.slice.call(grille.querySelectorAll(".art"));
  var une = document.querySelector(".une-bloc");
  var info = document.querySelector(".filtre-info");
  var titre = document.getElementById("liste-titre");
  var plus = document.querySelector(".plus");
  var filtres = Array.prototype.slice.call(document.querySelectorAll("[data-filtre]"));
  var LIMITE = 6, deplie = false, courant = "tout";

  function appliquer(f, defiler) {
    courant = f;
    var p = f.split(":"), n = 0, visibles = 0;
    cartes.forEach(function (c) {
      var ok = f === "tout" ? !c.hasAttribute("data-une")
        : p[0] === "cat" ? c.dataset.cat === p[1]
        : (" " + c.dataset.sit + " ").indexOf(" " + p[1] + " ") >= 0;
      if (ok) n++;
      var montre = ok && (f !== "tout" || deplie || n <= LIMITE);
      c.hidden = !montre;
      if (montre) visibles++;
    });
    if (une) une.hidden = f !== "tout";
    var reste = f === "tout" ? n - visibles : 0;
    plus.hidden = reste <= 0;
    plus.textContent = "Voir les " + reste + " autres articles";
    filtres.forEach(function (b) { b.setAttribute("aria-pressed", b.dataset.filtre === f ? "true" : "false"); });
    var lien = document.querySelector('[data-filtre="' + f + '"]');
    if (f === "tout") { titre.textContent = "Tous les articles"; info.textContent = ""; }
    else {
      titre.textContent = lien.classList.contains("sit") ? lien.querySelector("span").textContent : lien.firstChild.textContent.trim();
      info.innerHTML = n + " article" + (n > 1 ? "s" : "") + ' · <a href="#articles" data-filtre-raz>Voir tous les articles</a>';
    }
    if (defiler) document.getElementById("articles").scrollIntoView({ behavior: "smooth", block: "start" });
  }

  filtres.forEach(function (b) {
    b.addEventListener("click", function (e) {
      e.preventDefault();
      var f = b.dataset.filtre;
      appliquer(f === courant && f !== "tout" ? "tout" : f, b.classList.contains("sit"));
    });
  });
  info.addEventListener("click", function (e) {
    if (e.target.hasAttribute("data-filtre-raz")) { e.preventDefault(); appliquer("tout", false); }
  });
  plus.addEventListener("click", function () { deplie = true; appliquer("tout", false); });
  appliquer("tout", false);
})();
