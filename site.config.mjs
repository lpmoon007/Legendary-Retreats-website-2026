// Site-wide IDs read by scripts/generate.mjs. Empty = feature off (the build
// warns). legendary-retreats.com has its OWN GA4 property and Clarity project,
// separate from belegendary.org, so per-site conversion data stays clean.
export const SITE_CONFIG = {
  // GA4 measurement ID for legendary-retreats.com, e.g. 'G-XXXXXXXXXX'.
  ga4: 'G-9CEJQ87GF0',
  // Microsoft Clarity project ID for legendary-retreats.com.
  clarity: 'yzaagzb8dt',
  // HubSpot (portal 20276071, na2). The kit form already exists; the retreat
  // inquiry form GUID, once created, replaces the home page's inquiry CTA with
  // the embedded form and starts reporting `generate_lead`.
  hubspotPortal: '20276071',
  hubspotRegion: 'na2',
  kitFormGuid: 'c4bf79e3-be0f-4cdb-ac08-d3f2a146f949',
  inquiryFormGuid: 'ffc85cce-43c8-400d-94f1-cd0a5d5c8e55',
};
