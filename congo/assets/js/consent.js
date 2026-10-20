// Cookie consent with vanilla-cookieconsent v3 and Google Consent Mode v2.
// GTM is only loaded once the visitor has accepted analytics or marketing.
(function () {
  const gtmId = document.currentScript && document.currentScript.dataset.gtmId;
  let gtmLoaded = false;

  function gtag() {
    window.dataLayer.push(arguments);
  }

  function loadGtm() {
    if (gtmLoaded || !gtmId) return;
    gtmLoaded = true;
    window.dataLayer.push({ "gtm.start": new Date().getTime(), event: "gtm.js" });
    const script = document.createElement("script");
    script.async = true;
    script.src = "https://www.googletagmanager.com/gtm.js?id=" + encodeURIComponent(gtmId);
    document.head.appendChild(script);
  }

  function applyConsent() {
    const analytics = CookieConsent.acceptedCategory("analytics");
    const marketing = CookieConsent.acceptedCategory("marketing");
    gtag("consent", "update", {
      analytics_storage: analytics ? "granted" : "denied",
      ad_storage: marketing ? "granted" : "denied",
      ad_user_data: marketing ? "granted" : "denied",
      ad_personalization: marketing ? "granted" : "denied",
    });
    if (analytics || marketing) loadGtm();
  }

  // Follow Blowfish's light/dark appearance (it toggles the "dark" class on <html>)
  function syncDarkMode() {
    document.documentElement.classList.toggle(
      "cc--darkmode",
      document.documentElement.classList.contains("dark")
    );
  }
  syncDarkMode();
  new MutationObserver(syncDarkMode).observe(document.documentElement, {
    attributes: true,
    attributeFilter: ["class"],
  });

  CookieConsent.run({
    guiOptions: {
      consentModal: { layout: "box", position: "bottom right", equalWeightButtons: true },
      preferencesModal: { layout: "box", equalWeightButtons: true },
    },
    categories: {
      necessary: { enabled: true, readOnly: true },
      analytics: {
        autoClear: { cookies: [{ name: /^_ga/ }, { name: "_gid" }] },
      },
      marketing: {
        autoClear: { cookies: [{ name: /^_gcl/ }, { name: /^_fbp/ }] },
      },
    },
    onConsent: applyConsent,
    onChange: applyConsent,
    language: {
      default: "da",
      autoDetect: "document",
      translations: {
        da: {
          consentModal: {
            title: "Vi bruger cookies 🍪",
            description:
              "Vi vil gerne bruge cookies til at måle, hvordan sitet bruges, og til markedsføring. Det sker kun, hvis du siger ja. Du kan altid ændre dit valg.",
            acceptAllBtn: "Accepter alle",
            acceptNecessaryBtn: "Kun nødvendige",
            showPreferencesBtn: "Vælg selv",
          },
          preferencesModal: {
            title: "Cookie-indstillinger",
            acceptAllBtn: "Accepter alle",
            acceptNecessaryBtn: "Kun nødvendige",
            savePreferencesBtn: "Gem valg",
            closeIconLabel: "Luk",
            sections: [
              {
                title: "Dine valg",
                description:
                  "Her kan du vælge, hvilke typer cookies vi må bruge. Dit valg gemmes i en cookie i 6 måneder.",
              },
              {
                title: "Nødvendige",
                description: "Gør at sitet fungerer, fx at dit cookievalg huskes. Kan ikke slås fra.",
                linkedCategory: "necessary",
              },
              {
                title: "Statistik",
                description: "Hjælper os med at forstå, hvordan sitet bruges (Google Analytics via Google Tag Manager).",
                linkedCategory: "analytics",
              },
              {
                title: "Markedsføring",
                description: "Bruges til at måle og målrette annoncer (fx Google Ads).",
                linkedCategory: "marketing",
              },
            ],
          },
        },
        en: {
          consentModal: {
            title: "We use cookies 🍪",
            description:
              "We would like to use cookies to measure how the site is used and for marketing. This only happens if you say yes. You can change your choice at any time.",
            acceptAllBtn: "Accept all",
            acceptNecessaryBtn: "Necessary only",
            showPreferencesBtn: "Let me choose",
          },
          preferencesModal: {
            title: "Cookie settings",
            acceptAllBtn: "Accept all",
            acceptNecessaryBtn: "Necessary only",
            savePreferencesBtn: "Save choices",
            closeIconLabel: "Close",
            sections: [
              {
                title: "Your choices",
                description:
                  "Choose which types of cookies we may use. Your choice is stored in a cookie for 6 months.",
              },
              {
                title: "Necessary",
                description: "Make the site work, e.g. remembering your cookie choice. Cannot be turned off.",
                linkedCategory: "necessary",
              },
              {
                title: "Statistics",
                description: "Help us understand how the site is used (Google Analytics via Google Tag Manager).",
                linkedCategory: "analytics",
              },
              {
                title: "Marketing",
                description: "Used to measure and target ads (e.g. Google Ads).",
                linkedCategory: "marketing",
              },
            ],
          },
        },
      },
    },
    cookie: { expiresAfterDays: 182 },
  });
})();
