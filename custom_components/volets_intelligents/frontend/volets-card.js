/*
 * Volets Intelligents — carte Lovelace (custom element
 * `volets-intelligents-card`).
 *
 * Contrat de données : docs/API.md. JavaScript pur, module ES, sans
 * dépendance. Le DOM est construit avec createElement/textContent : aucune
 * donnée dynamique n'est interprétée comme du HTML.
 */

const WS = "volets_intelligents/";

/* Traductions (fr complet, en complet ; langue = hass.language, repli fr). */
const I18N = {
  fr: {
    "card.loading": "Chargement…",
    "card.unavailable": "Statut indisponible",
    "card.retry": "Réessayer",
    "card.interrupted": "Abonnement interrompu : {error}",
    "card.noCovers": "Aucun volet configuré.",
    "card.cmdFailed": "Commande impossible : {error}",
    "card.badTitle": "Le paramètre « title » doit être une chaîne de caractères.",
    "card.description": "Mode, scénario et état des volets gérés par Volets Intelligents.",
    "card.pause": "Pause",
    "card.resume": "Reprendre",
    "card.pauseAria": "Mettre en pause {name}",
    "card.resumeAria": "Reprendre {name}",
    "err.notInstalled": "L'intégration « Volets Intelligents » n'est pas installée ou n'est pas démarrée.",
    "err.unknown": "Erreur inconnue.",
    "err.unauthorized": "Vous n'avez pas le droit d'effectuer cette action",
    "mode.group": "Mode global",
    "mode.auto": "Auto",
    "mode.manual": "Manuel",
    "mode.off": "Arrêt",
    "scenario.group": "Scénario",
    "scenario.summer": "Été",
    "scenario.winter": "Hiver",
    "scenario.vacation": "Vacances",
    "scenario.off": "Désactivé",
    "status.disabled": "Désactivé",
    "status.mode_manual": "Mode manuel",
    "status.mode_off": "Arrêté",
    "status.scenario_off": "Scénario désactivé",
    "status.grace": "Démarrage",
    "status.outside_window": "Hors plage",
    "status.no_data": "Données manquantes",
    "status.paused": "En pause",
    "status.window_open": "Fenêtre ouverte",
    "status.wind_protected": "Protégé du vent",
    "status.shaded": "Protégé du soleil",
    "status.watching": "Surveillance",
    "status.cooldown": "Anti-usure",
    "status.unavailable": "Indisponible",
  },
  en: {
    "card.loading": "Loading…",
    "card.unavailable": "Status unavailable",
    "card.retry": "Retry",
    "card.interrupted": "Subscription interrupted: {error}",
    "card.noCovers": "No shutters configured.",
    "card.cmdFailed": "Command failed: {error}",
    "card.badTitle": "The “title” parameter must be a string.",
    "card.description": "Mode, scenario and state of the shutters managed by Volets Intelligents.",
    "card.pause": "Pause",
    "card.resume": "Resume",
    "card.pauseAria": "Pause {name}",
    "card.resumeAria": "Resume {name}",
    "err.notInstalled": "The “Volets Intelligents” integration is not installed or not running.",
    "err.unknown": "Unknown error.",
    "err.unauthorized": "You are not allowed to perform this action",
    "mode.group": "Global mode",
    "mode.auto": "Auto",
    "mode.manual": "Manual",
    "mode.off": "Off",
    "scenario.group": "Scenario",
    "scenario.summer": "Summer",
    "scenario.winter": "Winter",
    "scenario.vacation": "Vacation",
    "scenario.off": "Disabled",
    "status.disabled": "Disabled",
    "status.mode_manual": "Manual mode",
    "status.mode_off": "Stopped",
    "status.scenario_off": "Scenario disabled",
    "status.grace": "Starting up",
    "status.outside_window": "Outside active hours",
    "status.no_data": "Missing data",
    "status.paused": "Paused",
    "status.window_open": "Window open",
    "status.wind_protected": "Wind protection",
    "status.shaded": "Sun protection",
    "status.watching": "Watching",
    "status.cooldown": "Wear protection",
    "status.unavailable": "Unavailable",
  },
};

/** Traduit une clé dans la langue donnée (repli fr, puis la clé elle-même). */
function translate(lang, key, vars) {
  const text = (I18N[lang] || I18N.fr)[key] ?? I18N.fr[key] ?? key;
  return vars ? text.replace(/\{(\w+)\}/g, (m, k) => (k in vars ? String(vars[k]) : m)) : text;
}

const MODE_IDS = ["auto", "manual", "off"];
// Clés fixes des scénarios (contrat §1), utilisées si le statut ne fournit pas `scenarios`.
const SCENARIO_IDS = ["summer", "winter", "vacation", "off"];

// Code de statut -> couleur (contrat §3).
const STATUS_COLORS = {
  disabled: "grey", mode_manual: "grey", mode_off: "grey", scenario_off: "grey",
  grace: "grey", outside_window: "grey", no_data: "red", paused: "blue",
  window_open: "purple", wind_protected: "purple", shaded: "orange",
  watching: "green", cooldown: "grey", unavailable: "red",
};

/** Crée un élément DOM sans jamais interpréter de HTML (textContent uniquement). */
function el(tag, props = {}, ...children) {
  const node = document.createElement(tag);
  for (const [key, val] of Object.entries(props)) {
    if (val === undefined || val === null || val === false) continue;
    if (key === "class") node.className = val;
    else if (key === "text") node.textContent = val;
    else if (key.startsWith("on")) node.addEventListener(key.slice(2), val);
    else if (key === "disabled" || key === "hidden") node[key] = val;
    else node.setAttribute(key, val === true ? "" : String(val));
  }
  const append = (child) => {
    if (child === null || child === undefined || child === false) return;
    if (Array.isArray(child)) child.forEach(append);
    else node.append(child instanceof Node ? child : document.createTextNode(String(child)));
  };
  children.forEach(append);
  return node;
}

/** Appelle une fonction de désabonnement sans laisser fuiter d'erreur. */
function safeUnsub(unsub) {
  try {
    const result = unsub();
    if (result && typeof result.catch === "function") result.catch(() => {});
  } catch (_err) {
    /* connexion déjà fermée : rien à faire */
  }
}

const isPaused = (c) => c.status === "paused" || Boolean(c.paused_until);

const CSS = `
:host { display: block; --c: var(--disabled-color, #9e9e9e); }
* { box-sizing: border-box; }
[hidden] { display: none !important; }
button { font: inherit; }
.card {
  background: var(--ha-card-background, var(--card-background-color, #fff));
  color: var(--primary-text-color, #212121);
  border: 1px solid var(--ha-card-border-color, var(--divider-color, #e0e0e0));
  border-radius: var(--ha-card-border-radius, 12px);
  box-shadow: var(--ha-card-box-shadow, none);
  padding: 16px; display: flex; flex-direction: column; gap: 12px;
  font-family: var(--paper-font-body1_-_font-family, Roboto, "Segoe UI", sans-serif);
  font-size: 14px; line-height: 1.4;
}
h2 { margin: 0; font-size: 18px; font-weight: 500; }
.muted { color: var(--secondary-text-color, #727272); }
.small { font-size: 12px; }
.c-orange { --c: var(--warning-color, #ffa600); }
.c-green { --c: var(--success-color, #43a047); }
.c-blue { --c: var(--info-color, #039be5); }
.c-purple { --c: var(--purple-color, #8e24aa); }
.c-red { --c: var(--error-color, #db4437); }
.c-grey { --c: var(--disabled-color, #9e9e9e); }

.seg { display: flex; border: 1px solid var(--primary-color, #03a9f4); border-radius: 8px; overflow: hidden; }
.seg-btn {
  flex: 1 1 0; min-width: 0; min-height: 44px; padding: 0 6px; border: 0;
  background: transparent; color: var(--primary-text-color, #212121); cursor: pointer;
}
.seg-btn + .seg-btn { border-left: 1px solid var(--primary-color, #03a9f4); }
.seg-btn.on { background: var(--primary-color, #03a9f4); color: var(--text-primary-color, #fff); }
.seg-btn:disabled, .btn:disabled { opacity: .5; cursor: default; }
button:focus-visible { outline: 2px solid var(--primary-color, #03a9f4); outline-offset: 2px; }

.row { display: flex; align-items: center; gap: 10px; min-height: 48px; border-top: 1px solid var(--divider-color, #e0e0e0); padding-top: 4px; }
.row:first-of-type { border-top: 0; }
.dot { width: 14px; height: 14px; border-radius: 50%; background: var(--c); flex: none; }
.name { flex: 1; min-width: 0; display: flex; flex-direction: column; }
.name > span { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.pos { white-space: nowrap; }
.btn {
  min-height: 44px; min-width: 44px; padding: 0 12px; border-radius: 8px; cursor: pointer;
  border: 1px solid var(--divider-color, #ccc);
  background: transparent; color: var(--primary-text-color, #212121);
}
.notice { border: 1px solid var(--c); border-radius: 8px; padding: 12px; display: flex; flex-direction: column; gap: 8px; align-items: flex-start; }
.err { color: var(--error-color, #db4437); }
`;

class VoletsIntelligentsCard extends HTMLElement {
  constructor() {
    super();
    this._hass = null;
    this._lang = "fr";
    this._config = { title: "Volets Intelligents" };
    this._status = null;
    this._error = null; // erreur d'abonnement
    this._cmdError = null; // erreur de la dernière commande
    this._busy = false;
    this._unsub = null;
    this._subGen = 0;
    this._started = false;
    this.attachShadow({ mode: "open" });
    this.shadowRoot.append(el("style", { text: CSS }), (this._root = el("div")));
    this._render();
  }

  _t(key, vars) {
    return translate(this._lang, key, vars);
  }

  /** Message d'erreur lisible à partir d'une erreur WebSocket de HA. */
  _describeError(err) {
    if (err && err.code === "unauthorized") return this._t("err.unauthorized");
    if (err && err.code === "unknown_command") return this._t("err.notInstalled");
    if (err && typeof err.message === "string" && err.message) return err.message;
    return this._t("err.unknown");
  }

  /** Configuration Lovelace : seule `title` (optionnelle) est reconnue. */
  setConfig(config) {
    if (config && config.title !== undefined && typeof config.title !== "string") {
      throw new Error(this._t("card.badTitle"));
    }
    this._config = { title: "Volets Intelligents", ...(config || {}) };
    this._render();
  }

  getCardSize() {
    const covers = this._status && this._status.covers ? this._status.covers.length : 2;
    return 3 + covers;
  }

  static getStubConfig() {
    return {};
  }

  set hass(hass) {
    this._hass = hass;
    const lang = String((hass && hass.language) || "fr").slice(0, 2).toLowerCase();
    const next = lang in I18N ? lang : "fr";
    if (next !== this._lang) {
      this._lang = next;
      this._render();
    }
    this._start();
  }
  get hass() {
    return this._hass;
  }

  connectedCallback() {
    this._start();
  }

  disconnectedCallback() {
    this._started = false;
    this._subGen++; // invalide un abonnement encore en cours d'établissement
    if (this._unsub) {
      safeUnsub(this._unsub);
      this._unsub = null;
    }
  }

  _start() {
    if (this._started || !this.isConnected || !this._hass) return;
    this._started = true;
    this._subscribe();
  }

  async _subscribe() {
    const gen = ++this._subGen;
    if (this._unsub) {
      safeUnsub(this._unsub);
      this._unsub = null;
    }
    this._error = null;
    try {
      const unsub = await this._hass.connection.subscribeMessage(
        (status) => this._onStatus(status),
        { type: `${WS}subscribe_status` }
      );
      if (gen !== this._subGen) {
        safeUnsub(unsub);
        return;
      }
      this._unsub = unsub;
    } catch (err) {
      if (gen !== this._subGen) return;
      this._error = this._describeError(err);
      this._render();
    }
  }

  /**
   * Nouveau statut : le DOM n'est reconstruit que si une donnée affichée a changé
   * (sinon le focus clavier serait perdu à chaque évaluation).
   */
  _onStatus(status) {
    const changed = this._viewKey(status) !== this._viewKey(this._status) || this._error !== null;
    this._status = status;
    this._error = null;
    if (changed) this._render();
  }

  /** Signature des seules données affichées par la carte. */
  _viewKey(st) {
    if (!st) return "";
    return JSON.stringify([st.mode, st.scenario, st.scenarios || null,
      (st.covers || []).map((c) => [c.entity_id, c.name, c.status, c.reason, c.position, c.enabled, c.paused_until])]);
  }

  async _command(payload) {
    if (this._busy) return;
    this._busy = true;
    this._cmdError = null;
    this._render();
    try {
      await this._hass.callWS({ type: `${WS}command`, ...payload });
    } catch (err) {
      this._cmdError = this._t("card.cmdFailed", { error: this._describeError(err) });
    } finally {
      this._busy = false;
      this._render();
    }
  }

  /* ---------- Rendu ---------- */

  _render() {
    const card = el("div", { class: "card" }, el("h2", { text: this._config.title }));
    const st = this._status;
    const retry = el("button", { class: "btn", type: "button", text: this._t("card.retry"), onclick: () => this._subscribe() });
    if (!st) {
      card.append(this._error
        ? el("div", { class: "notice c-red", role: "alert" },
          el("strong", { text: this._t("card.unavailable") }),
          el("span", { text: this._error }), retry)
        : el("span", { class: "muted", text: this._t("card.loading") }));
      this._root.replaceChildren(card);
      return;
    }

    // Libellés des scénarios fournis par le statut (clé -> libellé), y compris personnalisés.
    const labels = st.scenarios || {};
    const keys = Object.keys(labels).length ? Object.keys(labels) : SCENARIO_IDS.slice();
    if (!keys.includes(st.scenario)) keys.push(st.scenario);
    const scenarios = keys.map((key) => [
      key, labels[key] || (SCENARIO_IDS.includes(key) ? this._t(`scenario.${key}`) : key),
    ]);

    card.append(
      this._error ? el("div", { class: "notice c-red", role: "alert" },
        el("span", { text: this._t("card.interrupted", { error: this._error }) }), retry) : null,
      this._segmented(MODE_IDS.map((m) => [m, this._t(`mode.${m}`)]), st.mode, this._t("mode.group"),
        (v) => this._command({ command: "set_mode", value: v })),
      this._segmented(scenarios, st.scenario, this._t("scenario.group"),
        (v) => this._command({ command: "set_scenario", value: v })),
      this._cmdError ? el("span", { class: "err", role: "alert", text: this._cmdError }) : null,
      el("div", {}, (st.covers || []).map((c) => this._row(c))),
      (st.covers || []).length ? null : el("span", { class: "muted", text: this._t("card.noCovers") }));
    this._root.replaceChildren(card);
  }

  _segmented(options, active, label, onPick) {
    return el("div", { class: "seg", role: "group", "aria-label": label },
      options.map(([value, text]) => el("button", {
        class: `seg-btn${value === active ? " on" : ""}`, type: "button", text,
        "aria-pressed": String(value === active), disabled: this._busy,
        onclick: () => onPick(value),
      })));
  }

  _row(c) {
    const known = c.status in STATUS_COLORS;
    const label = known ? this._t(`status.${c.status}`) : String(c.status);
    const color = known ? STATUS_COLORS[c.status] : "grey";
    const paused = isPaused(c);
    const name = c.name || c.entity_id;
    return el("div", { class: "row" },
      el("span", { class: `dot c-${color}`, title: label, role: "img", "aria-label": label }),
      el("div", { class: "name" },
        el("span", { text: name }),
        el("span", { class: "muted small", title: c.reason || "", text: label })),
      el("span", { class: "pos muted", text: typeof c.position === "number" ? `${c.position}\u00a0%` : "—" }),
      el("button", {
        class: "btn", type: "button", text: paused ? this._t("card.resume") : this._t("card.pause"),
        disabled: this._busy || c.enabled === false,
        "aria-label": this._t(paused ? "card.resumeAria" : "card.pauseAria", { name }),
        onclick: () => this._command({ command: paused ? "resume" : "pause", entity_id: c.entity_id }),
      }));
  }
}

if (!customElements.get("volets-intelligents-card")) {
  customElements.define("volets-intelligents-card", VoletsIntelligentsCard);
}

window.customCards = window.customCards || [];
window.customCards.push({
  type: "volets-intelligents-card",
  name: "Volets Intelligents",
  description: translate("fr", "card.description") + " / " + translate("en", "card.description"),
});
