# Official schedule verification — 2026-11-14

The release gate is scheduled Hartford Line boards, never live service. Raw archives are retained locally with SHA-256; the repository contains code and verification records, not redistributed archives. Independent imports/stores isolate rail, CTtransit and PVTA freshness. Every archive below was downloaded from the agency in GitHub Actions; the local sandbox cannot resolve external hosts or bind sockets.

## Hartford Line

Official inventory: https://www.cttransit.com/about/developers → https://ctrides.com/hlgtfs.zip . Terms: https://www.cttransit.com/about/developers/terms-of-use . This is a revocable agency license with conditions and disclaimers, not CC0. The importer requires acceptance. Snapshot `03e8bc27defd6b3a501c760592ad0ed196b5b88db0a5380ba855e55c999f9d0d`, acquired 2026-11-14T21:50:18.815867Z, agency CONN DOT, America/New_York, publisher version S1000060. Declared dates 2026-10-05–2027-10-04; weekday and weekend calendars plus exceptions. Route `HART` is Hartford Line rail; the archive also contains route SLE marked bus. This does not supply the full Amtrak timetable.

Hartford Union is source `6` (HARTFORD); Windsor Locks is `8` (WINDSOR LOCKS). Both directions occur. Some source headsigns say “Northbound to Hartford” even though their stop sequence continues north; the preview derives destination from the actual last stop and retains the original headsign in provenance.

Explicit query: 2026-11-13T05:00:00-05:00, 24 elapsed hours. Hartford: 17 boarding events; Windsor Locks: 12. Cross-check against the official PDF applicable Nov 2–15 at https://hartfordline.com/wp-content/uploads/2026/11/HL-112-1115-End-Bus-Substitutions_v2.pdf , linked from https://hartfordline.com/fares-schedules/:

| Station / direction | GTFS sample | Source trip | Published PDF |
|---|---|---|---|
| Hartford, south to New Haven | 06:45 | 45020 | 06:45 |
| Hartford, north to Springfield | 18:25 | 26020 | 18:25 |
| Windsor Locks, south | 10:44 | 50020 | 10:44 |
| Windsor Locks, north | 18:39 | 26020 | 18:39 |

The PDF includes Amtrak trips absent from this feed: no all-operator completeness claim. Arrival-only terminal events are excluded. The agency publishes a replacement schedule effective Nov 16. For this exact old checksum, queries crossing Nov 16 are conservatively Unknown until reconciled with that dated PDF; the long feed_info range alone does not prove the replacement timetable. No automated PDF-to-GTFS overrides are invented.

## CTtransit

Official developer-page download: https://www.cttransit.com/sites/default/files/gtfs/googlect_transit.zip . Same CTtransit terms. Snapshot `90abd4b2002498bec2d5af9614640ac743c5713b8c1b1004242a7bc167c68631`, acquired 2026-11-14T21:59:56.104696Z; selected service coverage 2026-10-18–2027-01-09, America/New_York.

| Route label | Source route ID |
|---|---|
| 80 HARTFORD/BUCKLAND VIA I-84 (80X branches) | 16507 |
| 82 TOLLAND ST | 16508 |
| 82/84 TOLLAND ST | 16509 |
| 83 SILVER LA | 16510 |
| 84 TOLLAND ST | 16511 |
| 905 HARTFORD/WINDSOR LOCKS/ENFIELD | 16545 |

No route 81 occurs in the official route table. 905W is a trip-headsign branch of route 16545, not a separate route. Its stop pattern can terminate at Windsor Locks: do not assume all 905 trips serve Bright Meadow. Inbound combined-route headsigns contain a source typo “82/24”; route label remains 82/84 and source headsign is retained separately.

Windsor Locks new station: `13577`, “Windsor Locks RR Stn @ 229 Main St”. Campus boarding: `7919`, “Bright Meadow Blvd @ Mass Mutual”. Nearby Fairfield Inn stops `12239`/`12240` are separate stops, not campus aliases. Campus has four weekday boarding trips to Hartford; no campus service Saturday. New rail-station stop has both directions and weekend service. CTtransit's https://www.cttransit.com/services/service-adjustments explicitly moves connections to the new station; the old Park & Ride (`7913`) is not the rail station.

Weekday 2026-11-13 / Saturday 2026-11-14 smoke queries start at 04:00 -05:00. Sample counts are retained in Actions reports for every route and direction, including valid empty service days. Cross-checks: 80X Saturday 10:00 from Market/Kinsley, no weekday/Sunday service, matches https://www.cttransit.com/sites/default/files/schedules/h_80_satsunsched_3.pdf . 83B weekday 05:03 from Union Station matches https://www.cttransit.com/sites/default/files/schedules/h_83_wkdysched_0.pdf . The obsolete h_905_sched.pdf is not evidence for current campus times. Reproducible PDF retrieval exposed an August 2025 905_Weekday.pdf and even a 2019 document behind another legacy URL; these differ from the October 2026 GTFS and new-station service notice. A current dated 905 PDF remains a reconciliation blocker. Never claim its old columns prove a 2026 departure.

The image-only January 11, 2026 82/84 PDFs were retrieved and OCRed in Actions: weekday Union Station 82 04:13, 84 04:53, combined 82/84 18:23; Saturday combined 82/84 05:58 all match the Nov 13/14 GTFS samples. Weekday PDF SHA-256 `8d7b9af42d0d3232c0475bb8a139d766979f9735b068bda0a2196735c20a4a4a`; Saturday `6df7fdcd421f3a2a0dbe54dfdb1e6fab80bd61d396dd2c3da57b68fd07fdc593`. Sources: https://www.cttransit.com/sites/default/files/schedules/82_84_Weekday_Tolland.pdf and https://www.cttransit.com/sites/default/files/schedules/82_84_Saturday_Tolland.pdf . This is sample corroboration, not exhaustive manual reconciliation of every stop. The compiler exposes GTFS-backed Scheduled with visible source age, not a claim of PDF verification for every event.

## PVTA

Official developer page/terms: https://www.pvta.com/bus_service/real_time_data.php . Its exact GTFS link is https://www.pvta.com/g_trans/google_transit.zip?t=202610281453440 . The non-www URL returned HTTP 403 from Actions; the published www link succeeded. Terms allow limited transit-assistance use and caching, require PVTA attribution and no endorsement claims, and disclaim accuracy. Review the full agreement; no realtime integration is used.

Snapshot `c7defae022053b4e2211cf159d54704838f66556647d69021a1b47f280795357`, acquired 2026-11-14T22:00:12.886262Z; selected coverage 2026-11-02–2026-12-19. Routes IDs/short names `G5`, `R10`, `R14`; names come from the feed, including R10 “Westfield/West Springfield via Route 20”. Campus stop `10006`, “MassMutual Enfield”; Jewish Home stop `1862`, source spelling “Jewish House”. The UI must preserve those identities and show direction/headsign and actual downstream campus service.

Official G5 PDF https://www.pvta.com/schedules/G5.pdf , effective June 28, 2026: weekday campus departures 06:55, 07:55, 15:25, 17:10; Jewish Home southbound 06:31/07:32 and northbound 07:15 match the GTFS samples for Nov 13. Saturday Nov 14: Jewish Home departures begin 07:00, 07:30, 08:00 and no campus service, matching the PDF's Saturday table. Many G5 trips turn at Jewish Home and never reach the campus; one morning return from campus skips Jewish Home. Downstream source stop IDs, not headsign keyword guesses, determine continuation.

Weekday/weekend source smoke checks passed for G5, R10 and R14. R10 PDF https://www.pvta.com/schedules/R10.pdf (effective Dec 21, 2025): Union Station Bay 12 weekday 05:00 and Saturday 06:00, Scanlon Hall weekday 06:25 and Saturday 07:00 agree with Nov 13/14 samples. R14 PDF https://www.pvta.com/schedules/R14.pdf (effective Sep 8, 2026): Union Station Bay 14 weekday 06:10 / Saturday 07:10 and Feeding Hills 06:48 / 07:53 agree. These checks verify dated samples in both directions, not the complete contents of every schedule.

## Connections and intercity limits

The G5 PDF marks campus connections with 905; their weekday sample is PVTA 06:55 → CTtransit 06:58. Exact IDs and schedule evidence are known, but pedestrian paths and minimum walking times are not independently verified. Coordinates (even near-coincident points) do not establish a walking transfer. Both campus and Windsor Locks cross-agency connections remain Unknown in the preview until this evidence is added. Tests reject transfers with absent walking evidence or insufficient walk-plus-buffer time.

No dated Amtrak archive or authoritative reuse terms have yet been verified. NYP and BOS cannot be complete scheduled itineraries; report Unknown with that missing schedule and the unverified walking links. An empty result is never proof that intercity travel is impossible. Explicit local boards and same-feed Explore work without Ollama.

## Refresh observations

Raw archive and initial acquisition metadata remain immutable. Every successful revalidation creates a read-only observation; `source_checked_at` controls the seven-day freshness gate independently from original `snapshot_date` and age. Re-fetching identical authoritative bytes can refresh the source check without rewriting the snapshot. Failed downloads/validation never update these observations or replace the current pointer. A successful network download does not resolve known published-timetable conflicts.
