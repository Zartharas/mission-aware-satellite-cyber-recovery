# Legal, Ethical, and Responsible-Research Boundary

This document is a research control record, not legal advice.

## Green-zone activities

- Software-only simulation
- Researcher-owned computers
- Publicly licensed software and datasets
- Synthetic identities, keys, commands, telemetry, and mission states
- Host-only virtual networks
- Software-emulated delay, loss, corruption, and contact windows
- Defensive testing under a written lab Rules of Engagement
- Publication of sanitized methods and aggregate results

## Amber-zone activities requiring review

- Reanalysis of original interview transcripts
- Human operator evaluation
- Proprietary telemetry or commercial partner systems
- Spacecraft hardware or flight-like components
- SDR hardware, even when cabled
- International sharing of potentially controlled technical data
- Modified NASA software redistribution
- Public release of detailed event-injection code

Required review may include:
- IRB/HRPP determination
- Export-control review
- Data-use agreement
- Software-license review
- Institutional counsel
- Asset-owner written authorization
- Responsible-disclosure review

## Red-zone activities excluded

- Operational satellite or ground-station access
- Unauthorized scanning, testing, or exploitation
- Live RF transmission toward satellite services
- Jamming or spoofing
- Use of stolen credentials
- Interception of non-public communications
- Classified or export-controlled technical data
- Publication of partner-sensitive vulnerabilities without coordinated disclosure

## Human subjects

The first phase should use no human participants. Public or synthetic machine data generally avoids human-subject collection, but the institution should make the formal determination if the study reuses interview data or later measures operator behavior.

## Export control

Use public software and publishable fundamental research. Do not assume that all spacecraft hardware, technical data, encryption implementations, or international collaborations are outside export controls. Escalate any move beyond public software and synthetic data.

## Radio-frequency boundary

Do not use antennas or intentional radiators in the first study. RF impairment must be modeled in software. Private property or a Faraday enclosure does not independently authorize otherwise prohibited interference.

## Security testing authorization

Maintain a written Rules of Engagement covering:
- Assets and owner
- Network scope
- Permitted events
- Prohibited actions
- Test dates
- Emergency shutdown
- Data handling
- Incident handling
- Publication and disclosure boundaries

## Repository release control

Keep the repository private until:
- License audit is complete
- Secrets scan passes
- Dataset redistribution review passes
- Event-injection code is reviewed for misuse risk
- Participant-derived content is absent or approved
- Export-control review is complete where applicable
