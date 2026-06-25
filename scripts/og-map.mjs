// Per-page Open Graph / Twitter share image.
// Maps a generated page key (see keyFor() in scripts/generate.mjs) to a source
// photo under public/assets. scripts/og-images.mjs renders each into a 1200x630
// JPG at /assets/og/<name>.jpg; scripts/generate.mjs rewrites that page's
// og:image + twitter:image to point at it and declares the dimensions.
// Pages NOT listed here keep the branded default (assets/brand/og-default.png) —
// e.g. /contact. Several pages intentionally share a source image.
export const OG_MAP = {
  // Landing / section pages
  'home': 'field/new-fire-with-team',
  'leadership-retreats': 'field/g-img1361',
  'ways-to-work-together': 'field/luxury-lodge-sunset',
  'framework': 'field/james-portrait',
  'is-this-your-team': 'field/new-fire-with-team',
  'about': 'field/james-carter',
  'experience': 'field/g-img1494',

  // Destinations
  'destinations': 'field/sierra-peaks',
  'destinations__moab-utah': 'field/redrock-jeep',
  'destinations__san-juan-mountains-colorado': 'field/g-img1361',
  'destinations__sierra-nevada': 'field/sierra-peaks',
  'destinations__great-basin-desert': 'field/rovers-pyramid-lake',
  'destinations__death-valley': 'field/dest-deathvalley-titus',
  'destinations__sedona-arizona': 'destinations/sedona-offroad',
  'destinations__napa-valley': 'destinations/napa-alila',
  'destinations__lake-tahoe': 'destinations/tahoe-lodge',
  'destinations__jackson-hole-wyoming': 'destinations/jackson-jenny-lake',
  'destinations__montana': 'destinations/montana-rock-creek',

  // Signature formats
  'formats__cabin-fever': 'field/mining-lodge',
  'formats__off-road-immersion': 'field/rubicon-rockcrawl',
  'formats__winter-survival': 'field/w-img12322',
  'formats__wilderness-expedition': 'field/raft-img0003',
  'sailing-offsites': 'destinations/sailing-schooner',
  'executive-offsites': 'field/rubicon-summit-group',
  'executive-offsite-facilitator': 'field/james-carter',

  // Case studies (text pages — images chosen to match each engagement)
  'case-studies': 'field/rover-desert-joy',
  'case-studies__alaska-executive-vulnerability': 'field/overlook-alaska',
  'case-studies__san-juan-mountains-work-ethic': 'field/snow-cave-build',
  'case-studies__online-auto-retailer-leadership-team': 'field/rover-desert-joy',
  'case-studies__everglades-abundance-mindset': 'field/raft-img0003',
  'case-studies__federal-fiscal-leadership-team': 'field/new-fire-with-team',

  // Field Notes (essays — images chosen to match each topic)
  'field-notes': 'field/rubicon-summit-group',
  'field-notes__do-leadership-retreats-work': 'field/rubicon-summit-group',
  'field-notes__two-questions-leadership-retreat': 'field/james-portrait',
  'field-notes__align-leadership-team': 'field/team-desert-tea',
  'field-notes__questions-before-executive-retreat': 'field/new-fire-with-team',
  'field-notes__30-day-reinforcement': 'field/snow-hiking',
  'field-notes__what-is-an-experiential-leadership-retreat': 'field/kayak-fjord',
  'field-notes__executive-retreat-cost': 'field/luxury-lodge-sunset',
  'field-notes__newly-formed-post-merger-leadership-team': 'field/new-fire-with-team',
  'field-notes__signature-vs-bespoke-retreat': 'field/sierra-lodge-night',
};
