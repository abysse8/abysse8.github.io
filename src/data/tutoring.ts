// Tutoring page data (/cours, /tutoring). Edit rates and contact details here only.

// Phone number without braces, e.g. "06 12 34 56 78". While it is still
// "{{PHONE}}", the pages show a visible TODO and the call/SMS buttons fall back to email.
const PHONE = "07 75 85 70 82";

export const contact = {
  email: "julienabdougonzales@gmail.com",
  phone: PHONE,
  phoneIsPlaceholder: PHONE.startsWith("{{"),
  // "06 12 34 56 78" → "+33612345678" for tel:/sms: links.
  phoneHref: "+33" + PHONE.replace(/\D/g, "").replace(/^0/, ""),
};

export const zones = ["Orsay", "Bures-sur-Yvette", "Gif-sur-Yvette", "Palaiseau", "Les Ulis"];

// Net hourly rate paid via CESU. `afterCredit` is an ESTIMATE of the family's real
// hourly cost (employer contributions included, minus the 50 % tax credit).
export const rates = [
  {
    level: { fr: "Collège / lycée", en: "Middle & high school" },
    net: 15,
    afterCredit: 14,
  },
  {
    level: { fr: "Supérieur & électronique", en: "University & electronics" },
    net: 20,
    afterCredit: 19,
  },
];

export const freeTrialMinutes = 30;
export const cancelNoticeHours = 24;
export const cesuUrl = "https://www.cesu.urssaf.fr";
