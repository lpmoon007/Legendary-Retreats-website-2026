// Per-page Open Graph / Twitter share image.
// Maps a generated page key (see keyFor() in scripts/generate.mjs) to a source
// photo under public/assets. scripts/og-images.mjs renders each into a 1200x630
// JPG at /assets/og/<name>.jpg; scripts/generate.mjs rewrites that page's
// og:image + twitter:image to point at it and declares the dimensions.
// Pages NOT listed here keep the branded default (assets/brand/og-default.png) —
// e.g. /contact. Several pages intentionally share a source image.
export const OG_MAP = {
  // Landing / section pages
  'home': 'field/team-desert-tea',
  'destinations__colorado': 'site-photos/telluride-ferrata',
  'destinations__vail-colorado': 'field/snow-cave-inside',
  'destinations__utah': 'field/new-img-5612',
  'destinations__alaska': 'field/remote-lodge-aerial',
  'destinations__alula-saudi-arabia': 'field/alula-lunch',
  'destinations__british-virgin-islands': 'sailing/day-sail',
  'destinations__arizona': 'dest-sedona',
  'executive-immersion__las-vegas': 'offroad/las-vegas/lv-vista',
  'ways-to-work-together': 'field/luxury-lodge-sunset',
  'about': 'field/james-carter',
  'experience': 'field/g-img1494',
  'executive-retreat-planners': 'sailing/regatta',
  'board-retreat': 'destinations/napa-calistoga',
  'strategic-planning-retreat': 'field/g-img1357',
  'retreat-cost-estimator': 'offroad/phoenix/phx-vista',
  'procurement': 'sailing/offshore-passage',

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
  'formats__winter-survival': 'field/w-img12322',
  'formats__wilderness-expedition': 'field/raft-img0003',
  'for-executive-assistants': 'destinations/napa-alila',
  'offsite-vs-executive-retreat': 'field/sierra-peaks',
  'offsite-vs-team-building': 'field/new-fire-with-team',

  'formats': 'field/rubicon-rockcrawl',
  'executive-off-road-immersion': 'field/rubicon-rockcrawl',
  'sailing-team-building': 'destinations/sailing-schooner',
  'luxury-executive-retreat': 'field/luxury-lodge-sunset',
  'executive-immersion': 'field/redrock-jeep',
  'corporate-retreat-ideas': 'field/rover-desert-joy',
  'executive-offsite-ideas': 'field/rubicon-summit-group',
  'leadership-retreat-ideas': 'field/g-img1361',
  'retreat-planning-kit': 'field/new-fire-with-team',

  // Planning guides
  'how-to-plan-a-leadership-retreat': 'field/g-img1950',
  'how-to-plan-an-executive-offsite': 'offroad/los-angeles/la-hungry-valley',
  'leadership-offsite-agenda': 'field/luxury-lodge-sunset',
  'why-leadership-offsites-dont-stick': 'field/snow-hiking',
  'leadership-team-offsite-facilitator': 'field/james-carter',

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
  'field-notes__executive-retreat-cost': 'field/sierra-lodge-night',
  'field-notes__newly-formed-post-merger-leadership-team': 'field/new-fire-with-team',
  'field-notes__signature-vs-bespoke-retreat': 'field/sierra-lodge-night',
};
