 # AWA Trail Counter System

*Last updated: 2026-05-10*

## Background

Many outdoor recreation regions consist of a broad landscape subdivided into distinct management areas — wilderness areas, wild forests, canoe areas, primitive areas, private nature reserves, and public land easements — each with its own character, rules, and responsible steward. Trailheads are typically located at the edges of these areas, serving as the entry points where visitors begin their trips. Trail use varies enormously: some trailheads see hundreds of visitors on a summer weekend while others remain quiet for days at a time. Seasonal patterns, weather, and proximity to population centers all shape usage in ways that are difficult to understand without data.

Land managers responsible for these areas make decisions about trail maintenance, staffing, closures, and stewardship programs largely without reliable visitor counts. A trail counter system addresses this gap by placing small, low-power devices at trailheads that automatically detect and record passing visitors, then transmit the data wirelessly to a central platform where it can be viewed as a dashboard. The result is an accurate, continuous record of how each trailhead is used over time — data that supports better management decisions across the region. The same data may also be valuable to the general public for trip planning, particularly for understanding which trailheads are likely to be busy on a given day or season.

The initial pilot of this system is focused on the Adirondack Park in northern New York State — a protected area larger than many US states, and unique in that its "forever wild" status is enshrined in the state constitution rather than ordinary legislation. Human recreation is permitted where it is compatible with preservation, and the park contains a rich mix of management area types across both public and private land. In recent years the region has experienced a significant increase in backcountry recreation, putting growing pressure on ecosystems and trail infrastructure that were not designed for current visitation levels. Understanding where that pressure is concentrated, how it varies by season and day of week, and how it responds to events and conditions is essential to managing the park responsibly. Adirondack Wilderness Advocates (AWA) is sponsoring this pilot as a contribution to that effort.

---

## Definitions

**Trailhead** — The point where visitors access the backcountry, typically where a road ends and a trail begins. Trailheads are where counter devices are installed; all visitor counts in this system are recorded at the trailhead level. ^trailhead

**Trail** — A route through the backcountry. A single trailhead may be the starting point for one or more trails. This system counts visitors at the trailhead, not along the trail itself. ^trail

**Area** — A named management zone grouping related trailheads, corresponding to a land management designation (wilderness area, wild forest, primitive area, etc.) or an operational grouping defined by the organization. Areas are the primary unit of aggregation for regional analysis and filtering. ^area

---

## Roles

| Role                   | Responsibility                                                                                 |
| ---------------------- | ---------------------------------------------------------------------------------------------- |
| **Stewardship Manager** | Land manager or resource steward who uses data to make policy and operational decisions about the trail network; defines what "pressure" and "busyness" mean for this organization |
| **Stewardship Operations**   | Configures and maintains the system: trail and area catalog, device installation and assignment, user account management |
| **Public Viewer**       | Member of the public planning backcountry trips                                                |
| **Owner**               | Strategic accountability; funding; access governance; definition of problem and prioritization |
| **Device Engineer**     | Designs and builds the counter hardware: electronics, firmware, and mechanical packaging       |
| **SW Engineer**         | Builds, deploys, and maintains the platform                                                    |
| **System Tester**       | Validates system correctness before and after deployments                                      |

## System Components

| Component          | Description                                                                           |
| ------------------ | ------------------------------------------------------------------------------------- |
| **Counter Device**      | Physical unit deployed at a trailhead — detects, logs, and transmits visitor data     |
| **Software Platform**   | Cloud-hosted backend and web dashboard — receives device uploads, stores visitor records, and serves the viewer and management interfaces |

---

## Stewardship Manager

The stewardship manager (SM) is the primary intended user — a professional or volunteer responsible for managing backcountry trail networks or the frontcountry infrastructure that supports them (parking, staffing, road capacity). The stewardship manager works to balance recreational needs with ecological concerns.  The stewardship manager needs reliable, current visitor data to understand where pressure is concentrated, prioritize maintenance resources, and make informed decisions about closures, seasonal restrictions, or dispersal of use.  The stewardship manager is also the authority on how visitor data is interpreted — defining what "busyness" and "pressure" mean for this organization and trail network.

**SM-01a** #priority/high #status/open As a stewardship manager, I want the map to be my default view when I open the platform, so that spatial context is immediate and I do not have to navigate to it.
- Map loads on login without requiring any selection or configuration
- The usage map and the device management map are the same map — role-appropriate overlays, not two separate experiences

**SM-01b** #priority/high #status/open As a stewardship manager, I want a heatmap overlay showing where visitor activity is concentrated across the park, so that I can immediately see which locations are under pressure without clicking into individual areas.
- Heat intensity derived from the active pressure algorithm (SM-01i); default is most recent week of visitor counts per [[#^trailhead|trailhead]]
- Rendered as a continuous spatial field — hotspots emerge naturally where trailheads are close together and busy, such as the High Peaks cluster
- Heatmap is the primary data signal at regional scale; it fades as the user zooms in and individual [[#^trailhead|trailhead]] markers take over (SM-01e)
- *→ see also SM-01e (individual markers at closer zoom)*
- *→ see also SM-01i (intensity metric selection — controls which algorithm drives the heatmap)*

**SM-01c** #priority/high #status/open As a stewardship manager, I want management [[#^area|areas]] shown as labeled zones at regional scale, so that I can orient myself across the landscape and select an area to explore before zooming in.
- Zones rendered as a subtle reference layer — neutral fill, visible boundary, not visually dominant
- Selecting a zone — whether by clicking it on the map or choosing it from the area menu — highlights it and zooms to its extent
- No individual trailhead markers at this scale — the zone is the unit of navigation
- Area boundaries sourced from the APA Land Classification layer (apa.ny.gov/gis), which defines wilderness areas, wild forests, primitive areas, and other management designations

**SM-01d** #priority/high #status/open As a stewardship manager, I want selecting an [[#^area|area]] to highlight it on the map, zoom to its extent, and filter the graph to that area, so that I can move fluidly from spatial overview to data detail.
- Area highlight is subtle — distinguishable from the active state but not distracting
- Graph view automatically reflects the area selection; no additional configuration needed
- Deselecting returns to the full regional view

**SM-01e** #priority/high #status/open As a stewardship manager, I want individual [[#^trailhead|trailhead]] markers to appear when I zoom in, each colored by recent busyness relative to its own baseline, so that I can compare locations within an area.
- Marker color reflects recent activity relative to that trailhead's own typical level — not an absolute scale
- Clicking a trailhead selects it; switching to graph view shows that trailhead already loaded
- Zoom threshold for switching from area zones to individual markers is configurable

**SM-01f** #priority/medium #status/open As a stewardship manager, I want [[#^trailhead|trailheads]] in the catalog with no assigned device shown as distinct muted markers, so that I can see monitoring gaps without cross-referencing a separate list.
- Unmonitored trailheads are visually present but clearly differentiated from actively monitored ones
- Consistent appearance across both the usage map (SV) and the device management map (SM) — same marker style, same meaning

**SM-01g** #priority/medium #status/open As a stewardship manager, I want the map and graph to share selection state, so that switching between views never loses my current focus.
- Selecting a trailhead or area on the map carries into the graph automatically
- Selecting a trailhead in the graph highlights it on the map
- Navigation between views feels like one tool, not two

**SM-01h** #priority/high #status/open As a stewardship manager, I want the map to open at an extent that encompasses the entire Adirondack Park and to show the park boundary as a visual reference layer, so that I can immediately orient myself within the park and understand the geographic scope of the monitoring network.
- Initial map extent fits the Adirondack Park "Blueline" boundary
- Park boundary displayed as a subtle reference layer — present but not visually dominant
- Source: Adirondack Park Agency GIS, Adirondack Park Boundary Polygon (apa.ny.gov/gis)

**SM-01i** #priority/medium #status/open As a stewardship manager, I want to select which intensity metric the heatmap uses — such as recent activity or long-term average — so that I can explore the data from different perspectives and develop my own understanding of what signals are most meaningful.
- A control on the map allows switching among available algorithms without leaving the map view
- Default is the simplest useful option (most recent week's counts) — the map is immediately meaningful without any configuration
- At minimum, two views: *recent* (most recent week) and *long-term* (rolling average over full available history or a configurable window)
- Switching the metric updates the heatmap in place; the interface does not change
- Additional algorithms can be added over time without changing the interface contract
- The active metric is clearly labeled on the map so the SM always knows which view they are looking at
- *→ see also SM-15 (configuring busyness calculation across the platform)*

Note: the right metric for "pressure" is not yet known. Making the algorithm selectable preserves the ability to learn and refine rather than committing to a choice that may not serve all management contexts.

**SM-02** #priority/high #status/open As a stewardship manager, I want to see a line graph of visitor counts for one or more [[#^trailhead|trailheads]] over a selectable date range, so that I can understand usage patterns over time.
- Separate colored lines per trailhead
- X axis is date, Y axis is visitor count

**SM-03** #priority/medium #status/done As a stewardship manager, I want the graph to open with a sensible default view (current year, all [[#^trailhead|trailheads]] selected, weekly granularity), so that I see meaningful data immediately without having to configure anything.
- Start date defaults to January 1 of the current year
- Trailhead selector defaults to "All Trailheads" — not an empty field
- Granularity defaults to weekly

> **V1.2:** Implemented. Default start date, all-trailheads auto-select, and weekly granularity all in place.

**SM-04** #priority/high #status/open As a stewardship manager, I want to select one or more specific [[#^trailhead|trailheads]] to display, so that I can focus on the locations I am responsible for.
- Multi-select; clears chart when selection is cleared
- Search within the dropdown for large trailhead lists

**SM-05** #priority/medium #status/open As a stewardship manager, I want to filter [[#^trailhead|trailheads]] by [[#^area|area]], so that I can quickly see all trailheads within my management jurisdiction without selecting them one by one.
- Selecting an area auto-selects all trailheads in that area
- Chart title reflects the selected area name

**SM-06** #priority/medium #status/open As a stewardship manager, I want to choose the data granularity (hourly, daily, weekly, monthly, yearly), so that I can zoom in on a specific event or smooth out noise when looking at long-term trends.
- Granularity options adjust automatically based on the selected date span
- Manual override always available

**SM-07** #priority/medium #status/done As a stewardship manager, I want to aggregate all selected [[#^trailhead|trailheads]] into a single combined line, so that I can see total pressure on an [[#^area|area]] without visual clutter from individual trailhead lines.
- Toggle on the graph view
- Summed across all selected trailheads per time bucket

> **V1.2:** Aggregate toggle implemented.

**SM-08** #priority/high #status/done As a stewardship manager, I want to see a clear error message if data fails to load, so that I know the view is empty because of a problem — not because there is no data.
- A visible error message explains what went wrong
- Never a silently empty chart or map

> **V1.2:** Red error banner displayed on failed trail data fetch.

**SM-09** #priority/medium #status/open As a stewardship manager, I want to export [[#^trailhead|trailhead]] visit data to a standard open format, so that I can analyze it in other tools — GIS platforms, spreadsheets, or reporting systems — without being limited to what the built-in dashboard provides.
- Export covers the currently selected trailheads and date range
- Format is open and widely compatible (e.g. CSV or GeoJSON)
- No developer involvement required to perform an export

**SM-10** #priority/low #status/open As a stewardship manager, I want to see average visitor counts by day of week, so that I can understand the typical weekly pattern and identify which days consistently see the most use.
- Shows relative use across Monday through Sunday, averaged over the selected date range and [[#^trailhead|trailhead]] selection
- Complements the trend graph — same controls, different lens

**SM-11** #priority/low #status/open As a stewardship manager, I want to see average visitor counts by week or month of year, so that I can understand the full seasonal pattern and compare any specific period against the typical baseline.
- Full calendar-year view averaged across all years in the selected date range
- Immediately shows the shape of the season: when it starts, peaks, and tapers

**SM-12** #priority/low #status/open As a stewardship manager, I want to overlay multiple years on the same January–December axis, so that I can see whether this year's visitor levels are higher, lower, or consistent with prior seasons.
- Each year plotted as a separate line on a common weekly or monthly axis
- Reveals whether current trends are within historical norms or represent a departure

**SM-13** #priority/low #status/open As a stewardship manager, I want to see a heatmap of visitor counts by day and week, so that I can identify concentrated peaks that a line graph would smooth over.
- Rows represent days of the week; columns represent weeks or months in the selected range
- Color intensity represents relative visitor volume
- Useful for spotting holiday spikes, event-driven surges, and consistent weekend patterns

**SM-14** #priority/low #status/open As a stewardship manager, I want historical percentile bands shown alongside the main trend graph, so that I can immediately see whether current counts are within the normal range or represent an unusual event.
- Shaded band shows the historical 25th–75th percentile range for each time bucket
- Current period's line visible against this baseline context
- Turns a raw count into a signal: normal, high, or unusually low

**SM-15** #priority/medium #status/open As a stewardship manager, I want to configure how "busyness" is calculated for the map and summary views — whether that is absolute visitor count, rank among trailheads, deviation from seasonal norm, or pressure relative to the backcountry area served — so that the display reflects my organization's definition of what warrants attention rather than a hardcoded assumption.
- The busyness algorithm is a server-side concern; the display layer accepts a normalized score and renders it without knowing how the score was produced
- Default algorithm (absolute weekly count) is useful immediately; refinement is possible without changing the visualization
- The active algorithm and its parameters are visible and adjustable by the stewardship manager without developer involvement

**SM-16** #priority/medium #status/open As a stewardship manager, I want to record the approximate scale of the backcountry area each trailhead accesses — trail-miles, number of named destinations, or a capacity tier — so that visitor counts can be contextualized by the dispersal capacity of the area served.
- A trailhead serving a single summit reads differently than one that is the gateway to a large wilderness with many destinations and miles of trail
- This field informs the busyness algorithm (SM-15) but is also independently useful for catalog completeness
- Editable alongside name, area, and GPS coordinates (SO-09)

---

## Public Viewer

The public viewer is a hiker or backcountry recreationist making decisions about where and when to go. The public viewer wants to understand how busy a trailhead is likely to be and how use varies by season and day of week — enough to choose a destination or avoid peak crowds. The public viewer has no professional stake in the data and should not need an account to access basic usage information.

**PV-01** #priority/high #status/open As a public viewer, I want the map to be my primary entry point — showing how busy each part of the region is at a glance, and letting me drill into a [[#^trailhead|trailhead]] to see what I need for trip planning, so that I can find what I'm looking for without navigating a dashboard built for professionals.
- No login required
- At regional scale, [[#^area|areas]] appear as shaded zones (quiet / moderate / busy) — simple and interpretable without domain knowledge
- Zooming in reveals individual trailhead markers with the same simple busyness indication; trailheads with no active monitoring are not shown or are clearly marked as not currently monitored
- Clicking a trailhead opens a compact summary: name, area, recent activity, and typical patterns by day of week and season — not a full graph interface
- The public view does not expose administrative controls, device information, or exact visitor counts unless the organization chooses to make them public

**PV-02** #priority/medium #status/open As a public viewer, I want the [[#^trailhead|trailhead]] summary to show both recent activity and typical patterns, so that I can judge whether a trailhead is unusually busy right now versus normally busy at this time of year.
- Recent activity: last 7–30 days, displayed simply without granularity controls
- Typical patterns: relative busyness by day of week and season
- No login required for either

---

## Stewardship Operations

The stewardship operations role is responsible for configuring and maintaining the system so that the stewardship manager always has accurate, current data to work with. This covers the trail catalog — which trailheads exist, how they are named and grouped, and their field context — and the device network: installation, commissioning, and user account management. In a small organization the stewardship manager and stewardship operations may be the same person, but the responsibilities are distinct — one interprets data and sets policy, the other keeps the system correctly configured.

**SO-01** #priority/high #status/open As a [[#^trailhead|trailhead]] manager, I want to add a new trailhead to the system, so that it appears in the platform and can be assigned to a device.
- Trailhead name required; ID assigned automatically
- Optionally assign to an [[#^area|area]] at creation time

**SO-02** #priority/medium #status/open As a [[#^trailhead|trailhead]] manager, I want to rename an existing trailhead, so that the name stays accurate as land use or signage changes.
- All historical data remains associated with the trailhead after rename
- Device associations are preserved

**SO-03** #priority/low #status/open As a [[#^trailhead|trailhead]] manager, I want to mark a trailhead that has been closed.  This would keep any historical data for the closed trail, but by default it wouldn't show up in graph or map views.  In some cases, I will want to fully delete a trailhead, but in practice this is very rare and the system should force permission to delete aggressively so no accidental deletes happen.
- Cascading delete: removes all historical log data and device associations for that trailhead
- Confirmation required before deletion

**SO-04** #priority/high #status/open As a [[#^trailhead|trailhead]] manager, I want to create a named [[#^area|area]] and assign trailheads to it, so that viewers can filter by region.
- Area name required; trailhead membership defined at creation
- Trailheads can only belong to one area at a time

**SO-05** #priority/medium #status/open As a [[#^trailhead|trailhead]] manager, I want to rename an [[#^area|area]], so that the area name matches official or common usage.
- All area memberships are preserved under the new name

**SO-06** #priority/medium #status/open As a [[#^trailhead|trailhead]] manager, I want to add or remove trailheads from an existing [[#^area|area]], so that the area membership stays accurate as the monitoring network grows.
- Moving a trailhead to a new area removes it from its current area

**SO-07** #priority/medium #status/done As a [[#^trailhead|trailhead]] manager, I want all [[#^area|area]]-related labels to say "area" consistently throughout the platform, so that the terminology matches how I think about the monitoring network.

> **V1.2:** Terminology corrected throughout — buttons, modals, dropdowns, and checkboxes all use "area" rather than the earlier "group."

**SO-08** #priority/high #status/open As a [[#^trailhead|trailhead]] manager, I want historical trailhead data to be retained indefinitely, so that year-over-year comparisons remain possible as the system accumulates multiple seasons of data.
- No automatic expiration or archiving of visit log records
- Full history available for any date range query

**SO-09** #priority/high #status/open As a [[#^trailhead|trailhead]] manager, I want to record GPS coordinates for each trailhead, so that it appears correctly on the map and can be located accurately in the field.
- Coordinates stored as part of the trailhead record, editable alongside name and [[#^area|area]]
- Trailheads without coordinates are visually flagged on the map as incomplete catalog entries

**SO-10** #priority/low #status/open As a [[#^trailhead|trailhead]] manager, I want to import historical visit records from external sources — prior counter systems, scanned paper logs, or data collected before the current platform was deployed — so that the platform holds the complete visitor history for a trailhead, not just data since installation.
- Import accepts a documented, open format
- Imported records are associated with the correct trailhead
- The source of imported records is distinguishable from device-generated records

---

### Device and IT operations

**SO-11** #priority/high #status/done As stewardship operations, I want to see an overview of all counters and their current status, so that I can assess the health of the entire device fleet at a glance.
- Each device shows its associated [[#^trailhead|trailhead]], recent visitor activity, key health indicators, and when it last called in

> **V1.2:** Implemented as a table ("Device View") with columns: Device ID, Associated Trailhead, Weekly Count, Firmware Version, Battery %, Last Call-in.

**SO-12** #priority/high #status/done As stewardship operations, I want newly installed devices that have not yet been assigned to a [[#^trailhead|trailhead]] to be immediately visible and actionable, so that I can commission them promptly after installation.
- Unassociated devices are easy to find without searching
- Assignment can be initiated directly from the device overview

> **V1.2:** Unassociated devices sort to the top of the Device View with an inline "Assign Trailhead" button.

**SO-13** #priority/high #status/done As stewardship operations, I want to assign a [[#^trailhead|trailhead]] to a device quickly from the device overview, so that commissioning new hardware requires minimal steps.
- Assignment can be completed without navigating to a separate screen
- Only trailheads not already assigned to another device are available for selection

> **V1.2:** An inline dropdown and Save button appear in the same table row. No modal is required.

**SO-14** #priority/high #status/done As stewardship operations, I want the system to prevent me from assigning a [[#^trailhead|trailhead]] that is already monitored by another device, so that conflicting associations are impossible.
- The system enforces one active device per trailhead
- When reassigning a device, its own current trailhead remains available as an option

> **V1.2:** The assignment dropdown excludes trailheads already associated with another device.

**SO-15** #priority/medium #status/done As stewardship operations, I want to reassign a device to a different [[#^trailhead|trailhead]], so that I can redeploy hardware between locations without losing the device's history.
- Reassignment replaces the current association; it does not create a duplicate
- The device's call-in history is preserved under its device ID regardless of trailhead changes

> **V1.2:** A pencil (✎) edit button on each associated row opens the inline assignment dropdown.

**SO-16** #priority/medium #status/done As stewardship operations, I want to unassign a device from a [[#^trailhead|trailhead]], so that I can take a device offline or redeploy it without it appearing as a data gap at the trailhead.
- After unassignment the device returns to the pool of unassociated devices
- The trailhead becomes available for assignment to a different device

> **V1.2:** A red "Unassign" button appears within the inline edit row when editing an associated device.

**SO-17** #priority/medium #status/done As stewardship operations, I want to find a specific device quickly even as the fleet grows, so that managing a large number of devices does not become cumbersome.
- The device list is searchable or filterable without requiring a separate page

> **V1.2:** A text filter input above the Device View table filters rows by device ID as you type.

**SO-18** #priority/high #status/done As stewardship operations, I want to see the recent call-in history for a specific device, so that I can diagnose one that has gone silent or is reporting anomalous values.
- History shows health indicators per call-in: battery level, signal strength, firmware version, and record count
- Accessible from the device overview without losing context

> **V1.2:** Clicking a device ID opens a modal showing the last 5 call-ins with date/time, firmware version, battery %, RSSI, RSRP, RSRQ, and record count.

**SO-19** #priority/high #status/done As stewardship operations, I want each device call-in to record key health indicators regardless of whether visitor detections were included, so that I can track trends and plan maintenance visits even on quiet days.
- Health data captured on every call-in
- Both the most recent status and a historical trend should be accessible

> **V1.2:** Battery, firmware version, RSSI, RSRP, and RSRQ are written to DeviceCallLog on every call-in. The device overview shows the most recent entry; the detail view shows history.

**SO-20** #priority/high #status/done As stewardship operations, I want a newly installed device to appear in the system automatically as soon as it makes its first call-in, so that I can verify it is working and assign it to a [[#^trailhead|trailhead]] without any pre-registration step.
- Device is visible with its reported health status from the moment of first contact
- No administrative action is required before the device's first transmission

> **V1.2:** A POST to /devices is sufficient — no separate pre-registration call is needed. The device appears in Device View unassociated with telemetry populated.

**SO-21** #priority/high #status/done As stewardship operations, I want the system to accept a call-in from a device that has no visitor detections to report, so that a device checking in on a quiet day does not generate an error I have to investigate.
- A call-in with no detections is valid and is recorded as a health event
- The device's presence in the system is confirmed regardless of traffic

> **V1.2:** POST /devices with an empty `"data": []` array returns 200. The call-in is written to DeviceCallLog.

**SO-22** #priority/medium #status/open As stewardship operations, I want to be notified when the system stops receiving data from a device, so that I can investigate before the monitoring gap becomes significant.

**SO-23** #priority/medium #status/open As stewardship operations, I want to be notified when the system itself is unhealthy, so that problems surface before users discover them.

**SO-24** #priority/high #status/open As stewardship operations, I want to manage dashboard user accounts — provisioning new users and revoking access for departing staff — so that the owner's access policy is enforced and access remains current as the organization changes.
- Users can be added and removed without developer involvement
- Revoking access takes effect immediately, including terminating any active sessions

**SO-25** #priority/high #status/open As stewardship operations, I want the device management map to use the same map, markers, and interaction model as the usage map that viewers see, so that the system feels like one coherent tool rather than a viewer application and a separate admin application.
- Same base map, same zoom levels, same [[#^trailhead|trailhead]] and [[#^area|area]] marker positions and styles
- Management mode adds a device health overlay and provisioning controls on top of the shared foundation — it does not replace or duplicate the usage map
- Unmonitored trailhead markers look the same in both contexts (SM-01f and SO-25 share the same visual convention)

**SO-26** #priority/medium #status/open As stewardship operations, I want the map to show device health indicators on each [[#^trailhead|trailhead]] marker, so that I can assess fleet status spatially without switching to the device table.
- Healthy device: marker matches the usage map style with busyness color
- Device not heard from recently: marker shows a warning state
- Unmonitored trailhead (no device assigned): muted/outlined marker, consistent with usage map
- The device table and the map show the same information — the map is a spatial entry point to the same data

**SO-27** #priority/medium #status/open As stewardship operations, I want to import visit records collected manually from a device that was not connected to the network, so that data from locations without wireless coverage can still enter the platform record.
- Import accepts the same record format as wireless uploads
- Records are attributed to the correct [[#^trailhead|trailhead]] and device
- The source of manually imported records is distinguishable from wirelessly uploaded records
- *→ see also SO-37 (device retrieval side)*

**SO-28** #priority/high #status/partial As stewardship operations, I want to configure a device for its deployment site before I leave for the [[#^trailhead|trailhead]], so that the device is ready to operate autonomously on first power-up without requiring a laptop in the field.
- Upload endpoint and schedule configurable via a plain text file (`config.txt`) on the SD card — no software required, can be prepared at a desk before heading out
- All field-adjustable parameters (`domain`, `api_endpoint`, `upload_time`) settable without reflashing
- Cellular carrier credentials (APN) and the HTTPS root certificate must be loaded into the modem before assembly using XCTU — this is a one-time step per device, not a per-deployment task
- The device's mTLS client certificate must be generated, signed, and installed before the device leaves the bench — this is also a one-time per-device step performed at the same time as APN configuration (SO-40)
- *→ see also SO-34 (device upload behavior), SO-35 (cellular connectivity), SO-40 (certificate provisioning workflow)*

> **V1.2:** `domain`, `api_endpoint`, and `upload_time` configurable via `config.txt`. Cellular APN and SSL certificate require XCTU before assembly (Windows PC required, not field-configurable). API key not yet in `config.txt` — requires reflash (see DE-04).

**SO-29** #priority/high #status/done As stewardship operations, I want to confirm that a newly installed device has successfully registered on the network and is ready to operate, so that I can verify the installation before leaving the site and avoid a return trip to diagnose a silent failure.
- Device provides an unambiguous local indication of its state — no laptop, no phone app, no signal metrics to interpret
- Success is visually clear: I know the device is operational before I close the lid and walk away
- If there is an error, the device identifies what kind of error so I can act on it rather than just knowing something is wrong
- *→ see also SO-35 (cellular connectivity), SO-30 (platform confirmation)*

> **V1.2:** LED protocol implemented. Green LED double-flashes every few seconds while attempting to connect. When the green LED stops flashing for 30+ seconds with no red LED, the device has registered on the cellular network, fetched the current time, and confirmed connectivity to the server. If the red LED flashes, the number of flashes indicates the error: 1 = modem registration failed, 2 = server connection failed, 3 = sensor error, 4 = SD card error, 5 = other. Bluetooth-based status readable from a phone is not yet implemented.

**SO-30** #priority/medium #status/open As stewardship operations, I want to confirm that a newly installed device has appeared in the dashboard after its first contact, so that I know the full data path from device to platform is working correctly before I leave the area.
- Device appears in the device overview with health indicators populated
- Confirmation possible on a phone within minutes of a successful first boot, not requiring a return visit the next day
- Any failure to appear is surfaced as a visible alert rather than a silent absence

**SO-31** #priority/medium #status/open As stewardship operations, I want to assign a newly installed device to a [[#^trailhead|trailhead]] directly from the map, so that I can complete provisioning in the spatial context where I am working without switching to a device table.
- Clicking an unmonitored trailhead marker opens a provisioning panel listing available unassociated devices
- Selecting a device from the list associates it with that trailhead immediately
- The trailhead marker updates to reflect the assigned device's status — the map confirms the action visually
- The map-based assignment is equivalent to the table-based assignment in Device View; both reach the same result

**SO-32** #priority/high #status/done As stewardship operations, I want the counter device to detect each visitor passing the sensor and record it accurately, so that the counts reaching the platform reflect actual trailhead use.
- Each individual passing recorded as a distinct event
- Detection robust to slow walkers, groups, and normal environmental variation
- False positives (wildlife, vegetation movement) minimized

> **V1.2:** Implemented via STHS34PF80 IR presence sensor (I2C).

**SO-33** #priority/high #status/done As stewardship operations, I want the device to accumulate detection records locally between upload windows, so that data is not lost if the network is unavailable at the time of detection.
- Local storage sufficient for at least 30 days of accumulation at expected traffic volumes
- Data persists across power cycles and restarts

> **V1.2:** Records stored on SD card. Untransmitted files retained until confirmed upload.

**SO-34** #priority/high #status/done As stewardship operations, I want the device to upload accumulated data on a configurable schedule, so that the platform receives a regular, predictable stream of records without requiring a persistent connection.
- Upload schedule configurable without reflashing
- If a scheduled upload fails, the device retries and includes missed records in the next successful upload
- *→ see also SO-28 (configuration mechanism)*

> **V1.2:** Upload time configurable via `upload_time` in `config.txt` (minutes from midnight UTC).

**SO-35** #priority/high #status/partial As stewardship operations, I want the device to transmit data via cellular network where coverage is available, so that the most common deployment scenario — remote [[#^trailhead|trailheads]] accessible by car but without WiFi — is handled automatically.
- Supports LTE-M or NB-IoT for low-power wide-[[#^area|area]] coverage
- APN and carrier profile configurable before deployment
- *→ see also SO-28 (pre-deployment configuration), SO-29 (installation verification)*

> **V1.2:** Cellular upload implemented via LTE-M (Digi XBee 3 modem). APN configurable in modem flash via XCTU; not yet via `config.txt`.

**SO-36** #priority/medium #status/gap As stewardship operations, I want the device to transmit data via WiFi where it is available, so that [[#^trailhead|trailheads]] near WiFi infrastructure — ranger stations, visitor centers, parking lot kiosks — can upload without cellular dependency.
- Network credentials configurable
- Same payload format and platform endpoint as cellular

> **V1.2 gap:** WiFi upload not yet implemented.

**SO-37** #priority/medium #status/gap As stewardship operations, I want to retrieve data manually from a device at a location without wireless coverage, so that truly remote [[#^trailhead|trailheads]] are not excluded from the monitoring network.
- Bluetooth is the preferred retrieval interface — a field crew member retrieves data on a phone or tablet without opening the enclosure
- SD card extraction is an acceptable fallback
- Retrieved data enters the platform via the manual import workflow (SO-27)
- *→ see also SO-27 (platform import side)*

> **V1.2 gap:** Bluetooth retrieval not yet implemented. SD card data can be manually imported.

**SO-38** #priority/high #status/open As stewardship operations, I want the device to operate for more than one year on battery power under normal deployment conditions, so that field visits for battery maintenance are infrequent and predictable.
- Power budget accounts for continuous sensor polling, local logging, and scheduled uploads
- Battery level reported with every upload so replacement can be planned before failure

**SO-39** #priority/high #status/done As stewardship operations, I want the device to upload its full backlog of detection records when it resumes contact after a missed upload window, so that gaps in connectivity do not create permanent gaps in the data record.
- Device sends records in bounded batches; multiple sequential batches if the backlog exceeds one batch
- Platform accepts any number of sequential batches without truncation

> **V1.2:** Firmware sends batches of up to 250 detection records. Backend accepts without truncation.

**SO-40** #priority/high #status/open As stewardship operations, I want a defined workflow for generating and installing a unique client certificate on each device before it leaves the bench, so that the device can authenticate with the platform from its first call-in without any additional enrollment step in the field.
- Each device receives its own certificate — a compromise of one device's credentials does not affect the rest of the fleet
- Each device's certificate and private key are stored in a location the firmware can read at boot — the SD card is the preferred mechanism, so that cert installation requires no specialized tooling beyond a laptop
- Certificate generation is integrated into the standard device preparation process alongside APN configuration (SO-28); it is a one-time bench step, not a per-deployment task
- Certificate validity period must be set to match expected device hardware lifetime (approximately five years), so that field rotation is not required during normal operation
- The certificate's embedded device identity maps to the device ID used throughout the platform — the platform can identify which device is calling in from the certificate alone
- The certificate is registered in the platform at provisioning time so that an authenticated connection can be associated with a device record immediately
- *→ see also SO-28 (pre-deployment configuration), SO-41 (expiry monitoring), SO-42 (revocation)*

**SO-41** #priority/medium #status/open As stewardship operations, I want the device health view to surface devices whose certificates are approaching expiry, so that I can plan renewal before a device silently stops authenticating.
- Certificate expiry date is shown in the device detail view alongside battery, firmware, and signal health indicators
- Devices with certificates expiring within a configurable warning window (default: 90 days) are flagged visibly in the device overview (SO-11)
- A device rejected because its certificate has expired is distinguished from a device that is simply offline — the status label indicates the nature of the problem rather than showing a generic "not heard from" state
- *→ see also SO-11 (device overview), SO-22 (offline notification)*

Note: if certificate validity is set to match device hardware lifetime (SO-40), expiry warnings will rarely trigger in practice. This story becomes important in the event of a fleet deployed before the five-year convention was established, or if the CA was configured with a shorter default.

**SO-42** #priority/high #status/open As stewardship operations, I want to revoke a device's credentials from the platform when a device is lost, stolen, or decommissioned, so that a compromised device cannot continue to authenticate and post data.
- Revocation is initiated through the platform dashboard — no direct CA access required
- Subsequent connection attempts from a revoked device are rejected at the authentication layer; no data from a revoked device is stored
- Revocation is logged with a timestamp and the identity of the operator who initiated it
- Revocation does not delete the device's historical data — the record is preserved under the device ID for continuity
- *→ see also SO-16 (unassign device), SO-24 (account management), SO-40 (certificate provisioning)*

---

## Owner

The owner (sometimes known as the sponsor) is the person who funds the system and is accountable for whether it serves the organization's mission. The owner needs confidence that the investment is producing actionable information for land management decisions, that infrastructure costs are predictable as the network grows, and that access to the platform is properly governed.

**OW-01** #priority/medium #status/open As the owner, I want visibility into the operating cost of the platform, so that I can plan the budget and understand the cost impact of adding more [[#^trailhead|trailheads]] or devices.

**OW-02** #priority/high #status/open As the owner, I want the system's security to be reliable by design — with access control, credential management, and data integrity enforced systematically — so that protecting the platform does not depend on manual vigilance or individual judgment calls.
- Access to data and administrative functions is controlled at the system level, not through informal trust
- Credential and access management follows repeatable, auditable practices that make problems rare rather than just recoverable

**OW-03** #priority/high #status/open As the owner, I want the system's infrastructure costs to grow proportionally with the size of the monitoring network, so that the economics of expanding from a pilot to a regional deployment are predictable and the system remains viable at any scale.
- Adding [[#^trailhead|trailheads]] and devices should not trigger step-function cost increases
- Off-season and low-traffic periods should cost materially less than peak season

**OW-04** #priority/high #status/open As the owner, I want to control who has access to the platform and what they can do, so that the data is shared only with authorized organizations and individuals.
- Users can be provisioned and revoked without developer involvement
- Access policy is enforced at the system level, not through informal trust

**OW-05** #priority/high #status/open As the owner, I want to view the system operating in a realistic pre-production environment before full deployment, so that I can assess whether the investment is producing the intended capability and make informed decisions about go-live readiness.
- A working environment populated with representative data is accessible without developer involvement
- Reflects the actual system — same interfaces, same data flows — not a mockup or slideshow
- Available at any point during development, not only at formal milestones
- *→ see also TE-07 (formal certification of pre-production state)*

---

## Device Engineer

The device engineer designs and builds the counter hardware — the embedded system that detects, logs, and transmits visitor data. DE is responsible for the full hardware stack: sensor selection and integration, microcontroller firmware, power system, radio and modem interface, and mechanical packaging. DE's goals are accurate detection, multi-year battery life, and a unit cost low enough to deploy at scale. The DE team works with the SW team to ensure that both systems work together seamlessly and have a common data model and architecture.

**DE-01** #priority/high #status/partial As a device engineer, I want a documented, stable API contract for the device upload endpoint, so that firmware can evolve independently of backend changes without coordination on every release.
- Payload schema (field names, types, required vs. optional) is documented
- Breaking changes are versioned; prior versions remain supported for a migration window

> **V1.2:** API contract documented in `API_DOCUMENTATION.md`. No formal versioning yet — firmware and backend have been developed in close coordination.

**DE-02** #priority/medium #status/open As a device engineer, I want the platform to return clear, structured error responses when it rejects an upload, so that firmware can implement appropriate retry or fallback behavior without guessing at the cause.
- HTTP status codes used correctly and consistently
- Error response body describes the rejection reason in a machine-readable form

**DE-03** #priority/high #status/done As a device engineer, I want to test a firmware build end-to-end against a staging environment before deploying to field hardware, so that I can validate the full upload and reporting flow without risk to production data.
- Staging environment accepts the identical payload format as production
- Device can be redirected to staging without reflashing (via SO-28)

> **V1.2:** Staging environment available. Endpoint configurable via `config.txt`.

**DE-04** #priority/high #status/gap As a device engineer, I want the API key manageable without a firmware reflash of every deployed device, so that credential rotation is an administrative operation rather than a field expedition.

> **V1.2 gap:** API key compiled into firmware via `secrets.h`. Cannot be updated via `config.txt` without a reflash. Most significant firmware-side gap against NFR-S4 (see also SO-28).

---

## SW Engineer

The SW engineer designs, builds, and evolves the platform — backend, frontend, infrastructure, and test tooling. On this project the role has been filled by successive student teams; inheriting and improving on prior work is as much a part of the job as new development. SW's measure of success is a system correct enough to trust, maintainable enough for the next team to build on, and documented enough that institutional knowledge survives the handoff.  The SW team works with the DE team to ensure that both systems work together seamlessly and have a common data model and architecture.

**SW-01** #priority/high #status/done As a SW engineer, I want a staging environment that mirrors production, so that I can test backend and frontend changes before promoting them to production.
- All resource names prefixed (e.g. `tst-TrailDeviceLogs`)
- Separate Terraform workspace holds isolated state
- Frontend pointed at staging API via `.env`

**SW-02** #priority/medium #status/done As a SW engineer, I want [[#^trailhead|trailhead]] and [[#^area|area]] setup to be fully API-driven (not seeded by Terraform), so that Terraform does not undo manual changes on every `terraform apply`.
- No `aws_dynamodb_table_item` resources in Terraform
- Setup scripts use the same API endpoints as the dashboard

**SW-03** #priority/high #status/done As a SW engineer, I want database queries to apply date range filters at the query level, so that Lambda functions don't fetch unbounded data and hit response size limits.
- `start`/`end` applied as a key condition, not post-fetch filter
- No practical date-range query should hit the API response size limit

> **V1.2:** `start`/`end` applied as `KeyConditionExpression` in DynamoDB. Fixes the earlier pattern of fetching all records for a trail and filtering in Python.

**SW-04** #priority/high #status/done As a SW engineer, I want all database queries to handle multi-page results transparently, so that data is never silently truncated at the underlying page limit.
- All query paths loop until all pages are retrieved

> **V1.2:** All Lambda functions loop on `LastEvaluatedKey` until exhausted.

**SW-05** #priority/high #status/done As a SW engineer, I want function timeouts set to match realistic query durations, so that slow queries fail with a clear error rather than a silent timeout.
- Timeouts configured based on measured query durations, not framework defaults
- Timeout errors surface as visible errors, not silent empty results

> **V1.2:** All Lambda functions set to 30s timeout (was 3s default, causing silent failures on larger queries).

**SW-06** #priority/medium #status/done As a SW engineer, I want infrastructure tooling to detect code changes and redeploy automatically, so that the standard deploy command is the complete deploy — no manual steps.
- Code changes detected by hash; deploy triggered automatically
- Frontend build and sync included in the same deploy

> **V1.2:** `source_code_hash` on Lambda resources; React build and S3 sync triggered by source file hash.

**SW-07** #priority/high #status/done As a SW engineer, I want API credentials stored as sensitive variables in the infrastructure configuration, so that they are never visible in plan output, state files, or logs.
- `sensitive = true` on credential variables
- Staging and production use separate credential values in separate gitignored files

**SW-08** #priority/high #status/partial As a SW engineer, I want upload metadata — battery level, signal quality, firmware version, record count — stored in a dedicated per-call-in table separate from detection records, so that visit data is clean and telemetry history is preserved without inflating the detection table.
- Detection records (`TrailDeviceLogs`) contain only what was detected: trail, detection time, device
- Upload metadata belongs in a separate table, written once per call-in regardless of how many detections were in the batch
- Full call-in history retained; no overwriting

> **V1.2:** `DeviceCallLog` table introduced. Fixes two V1.1 problems: (1) battery was the only telemetry captured, and it was stored redundantly on every detection row in `TrailDeviceLogs` rather than once per upload — a side effect of having no dedicated metadata table; (2) all other telemetry (signal strength, firmware version) was not stored at all. `DeviceCallLog` captures battery, RSSI, RSRP, RSRQ, firmware version, and record count once per call-in. The `battery` field remains in `TrailDeviceLogs` as a legacy artifact; removing it is deferred to V2.

**SW-09** #priority/medium #status/gap As a SW engineer, I want the device metadata table to hold only identity and association data (device ID, current [[#^trailhead|trailhead]]), so that there is a single authoritative source for each kind of information.
- Health telemetry fields removed from the device record; no ambiguity about which table is authoritative

> **V1.2 gap:** `DeviceMetadata.battery` is still written on every call-in alongside `DeviceCallLog`. Removing the redundant field is deferred to V2.

**SW-10** #priority/medium #status/done As a SW engineer, I want a historical data population tool with realistic traffic patterns, so that the platform shows meaningful data during development and demos.
- Seasonality (summer peak, winter trough), day-of-week variation, weather events
- Per-[[#^trailhead|trailhead]] `fixed_seed` option for reproducible datasets
- Per-trailhead `zero_day_probability` for simulating days with no traffic

---

## System Tester

The system tester is responsible for validating that the system works correctly end-to-end and documenting its state relative to the user stories. The system tester understands the needs of all user roles and provides the owner with an unbiased assessment of what has been delivered and what gaps remain — a quality perspective independent of the teams building the device and platform.

**TE-01** #priority/high #status/done As a system tester, I want to establish a clean, known starting state for each test cycle, so that results are not affected by prior runs or leftover data.
- Staging environment purgeable to a blank slate and rebuildable from a configuration file
- Full [[#^trailhead|trailhead]] and [[#^area|area]] catalog and device associations restored without manual UI work
- Destructive operations refuse to run against production without an explicit override

> **V1.2:** Single command purges all staging tables. Catalog rebuilt from `config.yaml` using the same API endpoints as the dashboard.

**TE-02** #priority/high #status/done As a system tester, I want to exercise the complete data path from device upload through to dashboard display without requiring physical hardware, so that I can validate end-to-end behavior independently and repeatedly.
- Device call-ins simulatable with realistic payloads: visitor detections, health telemetry, and empty uploads
- Historical data populatable at configurable volumes and date ranges for dashboard validation
- New-device onboarding workflow exercisable without a physical device

> **V1.2:** `simulate.py` generates device call-ins with configurable firmware version, battery, signal, and detection counts. `populate.py` seeds historical data with seasonality and day-of-week variation. Simulated devices appear in Device View unassociated, ready to assign.

**TE-03** #priority/medium #status/done As a system tester, I want test runs to produce the same results given the same inputs, so that I can reliably detect regressions by comparing results before and after a change.
- Detection records and environmental variation derived deterministically from a seed value
- Per-[[#^trailhead|trailhead]] seed option for stable, named datasets

> **V1.2:** `fixed_seed` per trailhead produces identical detection sequences on every run. Weather and zero-day events also seeded deterministically.

**TE-04** #priority/medium #status/partial As a system tester, I want to confirm that boundary conditions and failure modes are handled correctly, so that edge cases are verified before a release rather than discovered in production.
- Empty upload accepted as a valid health check-in with no phantom detections recorded
- Large backlog batch processed without truncation
- System failures surface as visible errors, not silent empty results

> **V1.2:** Empty `"data": []` returns 200. Batch of 250 records accepted without truncation. Error banner displayed on failed data fetch.

**TE-05** #priority/high #status/open As a system tester, I want to produce a status report mapping each user story to its test outcome, so that the owner has an accurate, unambiguous picture of what has been delivered and what gaps remain.
- Each story assessed as passing, partial, gap, or not yet testable
- Report suitable for sharing with the owner without requiring technical context to interpret

**TE-06** #priority/high #status/open As a system tester, I want a standard verification sequence I can run after any production deployment, so that I can confirm the release succeeded before closing out the change.
- Uploads a known set of records, queries them back, asserts the count matches, and cleans up
- Produces a clear pass/fail result without manual inspection

**TE-07** #priority/high #status/open As a system tester, I want to certify the complete system in a pre-production environment before any production deployment, so that correctness is formally documented rather than assumed.
- All system components exercised together: device upload, data storage, dashboard display, and device management
- Certification produces a documented pass/fail result against explicit acceptance criteria
- *→ see also OW-05 (owner visibility into pre-production state), SW-01 (staging environment), TE-06 (post-deploy verification)*

---

## Non-Functional Requirements

These requirements apply across the system and are not tied to any single role. They constrain how the system must behave, not just what it must do.

### Cost

**NFR-C1** #priority/high #status/open The system's operating cost must scale with usage — proportional to the number of devices, trailheads, and queries — so that a small pilot is economically viable and growth to a regional network does not require a cost renegotiation.

**NFR-C2** #priority/high #status/done Infrastructure must favor consumption-based pricing (pay-per-request, pay-per-GB) over reserved capacity, so that idle periods (winter, off-season) do not incur the same cost as peak season.

**NFR-C3** #priority/high #status/open The marginal cost of adding one additional trailhead device to the network must be predictable before installation and must not require architectural changes to accommodate.

**NFR-C4** #priority/medium #status/done Service selection must avoid tiers or features that carry a fixed monthly floor charge disproportionate to expected usage at pilot scale.

### Security

**NFR-S1** #priority/high #status/done All device-to-platform communication must be authenticated. Unauthenticated or unrecognized submissions must be rejected before any data is stored.

**NFR-S2** #priority/high #status/done Platform access must require authentication for all write operations and for any data not explicitly designated as public. Unauthenticated read access is permitted only for deliberately configured public endpoints.

**NFR-S3** #priority/high #status/done API credentials and infrastructure access keys must never be committed to source control. Credentials must be injected at build or deploy time from files that are excluded from version control.

**NFR-S4** #priority/high #status/gap The system must support rotating any credential without requiring physical access to every deployed device.

> **mTLS tradeoff:** Device client certificates installed before deployment (SO-28, SO-40) are an intentional exception to this requirement — rotating them requires physical access to the device. This tradeoff is acceptable because: (1) mTLS provides stronger per-device authentication than shared API keys; (2) certificate validity set to approximately five years matches expected device hardware lifetime, so rotation during normal operation is not required; and (3) devices already require an annual field visit for battery replacement, providing a natural window for any unplanned cert intervention. All other credential types — server certificates, management API keys, infrastructure access keys — must remain remotely rotatable. This exception must be documented in the deployment guide so it is not discovered as a surprise during an incident.

**NFR-S5** #priority/high #status/open Each device must authenticate using its own unique certificate — a shared client certificate across the fleet is not acceptable — so that a compromised device's credentials can be individually revoked without affecting any other device.
- Per-device certificates are provisioned at the bench before deployment (SO-40)
- The platform enforces that each certificate maps to exactly one device identity

### Performance

**NFR-P1** #priority/high #status/done A typical query — current year, all trailheads for one area — must return and render within 10 seconds under normal load.

**NFR-P2** #priority/high #status/done Data must never be silently truncated. If a query cannot be fully satisfied, the platform must display a visible error rather than a partial or empty result.

**NFR-P3** #priority/medium #status/open The system must remain performant as the network scales to hundreds of devices and years of historical data without requiring a schema redesign or architectural change.

**NFR-P4** #priority/medium #status/open The map view must perform acceptably at full network scale. Busyness data for the map must be derived from pre-aggregated or cached summaries — not from loading individual detection records into the client.

### Maintainability

**NFR-M1** #priority/high #status/done All cloud infrastructure must be defined as code. No manual console configuration that is not reflected in the repository.

**NFR-M2** #priority/high #status/partial The device upload API contract must be documented and stable. Breaking changes must be versioned so that firmware and backend can be developed on independent schedules.

**NFR-M3** #priority/high #status/done A complete staging environment must be deployable from the repository without undocumented manual steps.

**NFR-M4** #priority/medium #status/open The system must be operable by a small team (2–3 people, part-time) and must not depend on knowledge held only by the original developers.
