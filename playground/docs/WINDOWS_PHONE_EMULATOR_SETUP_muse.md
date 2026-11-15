# Windows Phone emulator setup

A practical guide to running Microsoft's period Windows Phone emulators —
Windows 10 Mobile first, Windows Phone 8.1 second — so the Metro behaviour
this project imitates can be studied on the real thing: the genuine Start
screen, live tiles, pivot and panorama navigation, and a period browser
(Microsoft Edge on Windows 10 Mobile, Internet Explorer 11 Mobile on 8.1).

This guide supports the research-only Windows Phone entry in
[HARDWARE_COMPATIBILITY.md](HARDWARE_COMPATIBILITY.md). Nothing here changes
that status: an emulator session is research evidence, not device validation.

Researched and written November 2026. Download availability was verified at
that time; legacy Microsoft links rot, so if a link below is dead, the
"if a download is gone" notes say what to do instead.

## What this is for

- Experiencing period-correct Metro software while designing the Metro
  playground and the ZeroCloud-OS concepts — how tiles, pivots, the app bar
  and Edge Mobile actually behaved, at real phone screen sizes.
- Loading locally served pages in a period browser to record what a
  2015–2017 browser does with them.
- It is **not** a promise that the modern playground runs there. The
  playground is React 19 built with Vite 6 for current browsers, and the
  hardware record already states that the modern PWA is not presumed to
  install or run on legacy Windows Phone browsers. Treat whatever the
  emulator's browser does with the playground — including a blank page —
  as a research result to write down, not as a setup failure.

## Step zero: know your host

The emulators are Hyper-V virtual machines. Everything depends on the host
PC passing three checks: a Pro-class Windows edition, a CPU with
hardware virtualisation and SLAT (Second Level Address Translation), and
virtualisation switched on in the firmware.

Branden's Windows PC runs Windows **Pro**, which clears the edition check:
Hyper-V is a feature of Windows 10/11 Pro, Education and Enterprise, and is
absent from Home. The remaining checks take five minutes:

1. **Edition (already known: Pro).** For the record: `winver`, or
   Settings → System → About, shows the edition. Microsoft's emulator
   requirements ask for Windows 10 or later, 64-bit, Pro edition or later.
2. **Virtualisation state.** Open Task Manager → Performance → CPU and look
   at **Virtualisation:** in the bottom-right. You want **Enabled**.
3. **Full Hyper-V requirements.** Run `systeminfo` in a command prompt and
   read the **Hyper-V Requirements** section at the end. You want four
   "Yes" lines: VM Monitor Mode Extensions, Virtualisation Enabled In
   Firmware, Second Level Address Translation, and Data Execution
   Prevention Available. (If it instead says "A hypervisor has been
   detected", Hyper-V is already running and you are done checking.)
4. **If anything says No:** the usual cause is virtualisation disabled in
   the UEFI/BIOS setup — enable **Intel VT-x** (Intel) or **SVM Mode**
   (AMD), save, and reboot. For a definitive SLAT answer, Microsoft's
   Sysinternals **Coreinfo** tool (`coreinfo64.exe -v`, from
   live.sysinternals.com) prints `*` beside the features present, including
   Intel EPT / AMD NPT, which are SLAT.

Outcomes:

- **All checks pass** → follow the main route below.
- **Virtualisation cannot be enabled / no SLAT** → the official emulators
  cannot run on that machine at all. Skip to "Alternatives" (period Lumia
  hardware, or the PWA-in-a-viewport route). There is no software workaround:
  without SLAT, Hyper-V refuses to start the emulator VM.
- **Windows Home (not Branden's case, noted for completeness)** → Home has
  no Hyper-V, and *both* phone emulators need Hyper-V, so neither works.
  The routes that remain are the same alternatives; upgrading the Windows
  licence is a purchase and therefore Branden's call, never a step in this
  guide.

### Other hosts, briefly

| Host | Official emulators? | Why |
| --- | --- | --- |
| Windows PC, Pro/Education/Enterprise, SLAT CPU | **Yes — the route in this guide** | Native Hyper-V. |
| Windows PC, Home edition | No | No Hyper-V in Home. |
| Intel Mac | Possible, not recommended | Boot Camp installs real Windows on Intel Macs, where Hyper-V behaves as on a PC. Parallels on Intel with nested virtualisation was used historically with caveats (secondary sources). No Intel Mac is in the current household inventory. |
| Apple Silicon Mac (Mac mini, M4) | **No** | Three independent walls: Apple Silicon Macs run only Windows on ARM in a VM (no Boot Camp); Parallels' own documentation lists Hyper-V as unavailable inside Windows 11 ARM VMs on Apple Silicon, and VMware Fusion on Apple Silicon runs ARM64 guests only; and the emulator images are x86 Hyper-V machines — Hyper-V never emulates a foreign CPU architecture, and Windows on ARM's x86 support covers user-mode apps, not hypervisor guests. UTM/QEMU can emulate a whole x86 PC in software, but it cannot provide the SLAT-backed Hyper-V the emulator requires, and performance would be unusable. |
| Chromebook (Acer Chromebook Plus 516) | **No** | No Hyper-V exists for ChromeOS; Crostini is a Linux container and cannot host Hyper-V VMs. The Chromebook's role in this project is as a PWA target (see HARDWARE_COMPATIBILITY.md), not as an emulator host. |
| iPhone / Pixel 10a | No | Phones cannot host desktop Hyper-V. The Pixel is already a PWA test target. |

## The main route: Windows 10 Mobile emulator on the Windows PC

The Windows 10 Mobile emulator is the primary target: it is the final form
of the platform (Fall Creators Update, build 10.0.15254.x), it carries the
Edge browser, and its Metro dialect is the one closest to the ZeroCloud-OS
concepts.

### 1. Enable Hyper-V

1. Control Panel → Programs → **Turn Windows features on or off**.
2. Tick **Hyper-V** (both the platform and the management tools), click OK,
   and restart when prompted.

   Equivalent, from an elevated PowerShell:
   `Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V -All`

3. After the restart, `systeminfo` should report "A hypervisor has been
   detected", confirming Hyper-V is live.

### 2. Install the emulator

The emulator's last release is **Microsoft Emulator for Windows 10 Mobile
10.0.15254.1** (Fall Creators Update images). Two honest facts about getting
it in 2026:

- The Microsoft Download Center **catalogue page for the emulator has been
  deleted** — searching Microsoft's site lands on a dead end. The installer
  file itself is still served from download.microsoft.com: a direct check
  in November 2026 returned HTTP 200 for the EmulatorSetup.exe files below.
- Current Visual Studio releases (2019 and later, including VS 2022/2026)
  no longer offer the phone emulator in their installers. The period route
  was Visual Studio 2015/2017 with the Windows 10 SDK; the standalone setup
  below avoids that entirely for our purpose.

**Recommended install (standalone):**

1. Download the emulator setup for build 10.0.15254:
   `https://download.microsoft.com/download/E/3/4/E347E8C5-BD79-49AF-941C-D08893A45268/emulator/EmulatorSetup.exe`
2. Run it as administrator and follow the prompts. It installs the XDE
   emulator host and the phone images.
3. You do **not** need Visual Studio to boot the phone and use its browser.
   Visual Studio 2015 or later is required only to deploy and debug apps
   into the emulator (Microsoft's stated requirement). Launching the OS
   without Visual Studio is done through XDE directly — see step 3.
4. If the 15254 link ever dies, the Anniversary Update build (10.0.14393.0)
   installer was likewise still served at the time of writing:
   `https://download.microsoft.com/download/F/0/7/F0738768-AE4F-473F-B37E-6DB641D97588/emulator/EmulatorSetup.exe`
   The Legacy Update project's Download Center archive
   (legacyupdate.net) preserves the deleted catalogue pages and their file
   hashes if a link needs cross-checking.

### 3. Launch the phone

- **With Visual Studio 2015/2017:** open any UWP project and choose an
  emulator from the run dropdown.
- **Without Visual Studio** (secondary-source procedure, widely used):
  launch XDE with the image's name and VHD, e.g.

  ```text
  "C:\Program Files (x86)\Microsoft XDE\10.0.15254.0\XDE.exe" /name "Emulator 10.0.15254.0 WVGA 4 inch 512MB" /vhd "C:\Program Files (x86)\Windows Kits\10\Emulation\Mobile\10.0.15254.0\flash.vhd"
  ```

  Adjust the build folder to the version you installed, and run
  `XDE.exe /?` for its full switch list. If XDE complains that your account
  is not in the Hyper-V Administrators group, accept its offer to add you
  (or add yourself in Computer Management → Local Users and Groups) and
  sign out and back in.
- First boot takes a while — the image expands and Windows 10 Mobile runs
  its first-start sequence. Skip the Microsoft account sign-in; the phone
  is fully usable for local browsing without one.
- Useful keys in the emulator window: **F4** toggles your PC keyboard into
  the phone; **F12** twice is the power button (lock screen). The toolbar's
  Additional Tools (>>) holds screen-size/zoom, sensors and network tabs.

### Screen sizes you get

The 10.0.15254 images span the Lumia-era range (exact catalogue is listed
in Visual Studio's run dropdown after install):

| Class | Resolution | Typical memory |
| --- | --- | --- |
| WVGA 4 inch | 480 × 854 | 512 MB / 1 GB |
| 720p 4.7 inch | 720 × 1280 | 1 GB |
| 1080p 5.2 inch | 1080 × 1920 | 2 GB |
| QHD 5.7 inch | 1440 × 2560 | 2 GB |

For design study, the WVGA 512 MB image is the period's worst case and the
1080p image approximates a Lumia 950-class device.

### If it will not start (the known failure modes)

These are 2016–2017 Hyper-V images on a modern host; the classic faults,
in the order worth trying (fixes from community sources, marked as such):

1. **Stuck at "Loading OS" / VM will not start** — delete the emulator's
   virtual machines in Hyper-V Manager and let XDE recreate them, or run
   the `XdeCleanup.exe` utility that ships beside XDE, which removes the
   VMs, differencing disks and emulator switches.
2. **Virtual switch trouble** — the emulator creates its own Hyper-V
   virtual switch and adapter. If networking or startup broke after other
   Hyper-V/WSL/VPN changes, removing the emulator's switch in Hyper-V
   Virtual Switch Manager and relaunching XDE lets it rebuild. (Microsoft
   notes the adapter is not removed automatically on uninstall.)
3. **Windows 11 hosts** — community reports flag Virtualisation-Based
   Security / Memory Integrity (Settings → Windows Security → Device
   security → Core isolation) as a blocker for these legacy images on some
   machines; toggling it off is a diagnostic step, and a security
   trade-off to make knowingly, not a default recommendation.

## Optional: the Windows Phone 8.1 emulators

Worth adding only if the earlier Metro dialect (Windows Phone 8.1, IE 11
Mobile) is specifically wanted. It is a heavier lift than 10 Mobile:

- Requirements (Microsoft): a host running Windows 8.1 (x64) Professional
  or higher — the Update package also lists Windows 10 as a supported
  host — with Client Hyper-V and SLAT, and **Visual Studio 2015, or Visual
  Studio 2013 Update 2 or later, already installed**: the 8.1 emulators
  are an add-on to Visual Studio, not a standalone install. Period Visual
  Studio versions are obtained from Microsoft's older-downloads page,
  which requires signing in with a Microsoft account.
- The **Windows Phone 8.1 Update and Emulators** package (version
  8.10.14141.167) is still listed on the Microsoft Download Center
  (details page id 43719; republished 15 July 2024), as a 940.6 MB ISO or a
  small web installer.
- Images it adds, per Microsoft's own listing: WVGA 4 inch, WVGA 4 inch
  512MB, WXGA 4.5 inch (768 × 1280), qHD 5 inch (960 × 540), 720p 4.7 inch,
  1080p 5.5 inch and 1080p 6 inch. The base 8.1 set (via the Visual Studio
  install) covers WVGA 480 × 800, WXGA and 720p classes.

## Connecting the emulator to the locally served playground

The playground is served from the Windows PC (or any machine on the same
network) like this, from the repo's own scripts:

- `npm run dev:stack` starts both halves: the Vite dev server
  (`npm run dev`, default port **5173**) and the simulation API
  (`npm run simulator`, port **4174**). Vite proxies `/api` calls to the
  API, so the browser only ever talks to the Vite port.

Three things must line up, all consequences of the emulator being a
separate Hyper-V machine:

1. **Do not use `localhost` inside the emulator.** To the phone,
   `localhost`/`127.0.0.1` is the phone itself. You must browse to the
   host PC's address instead (this is the single most common gotcha;
   period Microsoft guidance says the same).
2. **Make the dev server listen beyond loopback.** The repo's `dev`
   script deliberately binds Vite to 127.0.0.1, which the emulator cannot
   reach. Start it on all interfaces instead:

   ```text
   npx vite --host 0.0.0.0 --port 5173
   ```

   (with `npm run simulator` running alongside as usual; the API can stay
   on loopback because Vite proxies to it server-side.)
3. **Find the address the phone can see, and let it through the firewall.**
   Run `ipconfig` on the host and note the IPv4 address of the
   **vEthernet** adapter belonging to the emulator's internal switch
   (a link-local 169.254.x.x address in period setups); the host's ordinary
   LAN address (e.g. 192.168.x.x) also works when the emulator's switch is
   bridged to the LAN. On first run, accept the Windows Firewall prompt
   for Node.js, or add an inbound rule for TCP 5173. Then, in the
   emulator's Edge browser:

   ```text
   http://<host-address>:5173
   ```

Expectations, restated: Edge Mobile is an EdgeHTML-era browser. Simple
pages and period web content will render; the React 19 playground is
expected to fail in whole or part, and recording exactly how it fails is
the research value. Do not "fix" the playground for EdgeHTML on the basis
of an emulator session without a separate decision — that is a design
question for Branden, not a setup step.

## You're set up when you can…

- [ ] Run `systeminfo` and see "A hypervisor has been detected" (or four
      Yes lines under Hyper-V Requirements).
- [ ] Launch a Windows 10 Mobile image and reach its Start screen with
      live tiles animating.
- [ ] Open Edge in the emulator and load a public web page.
- [ ] Serve the playground on the host, browse to
      `http://<host-address>:5173` from the emulator, and record what
      renders (a faithful record of a failure counts).
- [ ] Switch between the WVGA 512 MB and 1080p images and note the layout
      differences you observe.

## Honest limits

- **The emulator is not a phone.** Microsoft's own list of things that can
  only be tested on a physical device includes the compass, gyroscope,
  vibration and real brightness behaviour; high-resolution video is
  unreliable, especially on 512 MB images. Touch feel, scrolling physics
  under a real finger, performance on phone silicon, cellular/Wi-Fi
  radios, GPS and battery behaviour are likewise unproven by any emulator
  session.
- **x86, not ARM.** The emulator runs the x86 build of Windows 10 Mobile;
  every real Lumia ran ARM. Behaviour can differ; Microsoft noted ARM
  testing requires a physical device.
- **Dead services stay dead.** The Windows Store for these platforms, the
  WP8.1 developer-registration service and other period backends are gone;
  the emulator cannot resurrect them, and anything depending on them will
  fail for reasons unrelated to your setup.
- **Status in this repo is unchanged.** Windows Phone remains
  **research-only** in HARDWARE_COMPATIBILITY.md: no named handset, OS
  build validation, signing path, TLS or network validation is claimed.
  A successful emulator run upgrades our knowledge, not the claim.

## Alternatives

### Period Lumia hardware (the only route to ground truth)

If a real device is wanted, prefer a Windows 10 Mobile handset — Lumia
950/950 XL (the flagship pair, final build 15254.x), Lumia 650, or a
640/640 XL that has taken the official Windows 10 Mobile upgrade:

- Windows 10 Mobile has a built-in **Developer mode** toggle
  (Settings → Update & security → For developers) — no account and no
  registration service involved — and a **Device Portal** that serves a
  web UI from the phone itself for inspection and app deployment.
- Windows Phone 8.1 devices, by contrast, depended on Microsoft's
  developer-registration tool and service for unlocking, which no longer
  reliably exists; an 8.1-only handset is a poorer research tool in 2026.
- Buying notes (general, high level): confirm the exact model and that it
  reaches OS build 15254.x; expect tired batteries in 950-series units
  (they are user-replaceable, which helps); a factory reset via the
  Windows Device Recovery Tool is still the standard way to reach a known
  state. Community bootloader/interop unlock tools exist (e.g.
  WPInternals) but are unnecessary for browser and PWA research and are
  out of scope here.

### The PWA in a phone-sized viewport (no period browser)

For layout questions only, the playground already has a cheaper answer:
its Playwright suite runs desktop and Pixel 7 viewports, and any desktop
browser's device toolbar can emulate the Lumia-era sizes in the table
above. This proves responsive behaviour in a modern engine. It proves
nothing about EdgeHTML, IE 11 Mobile or period Metro behaviour — which is
the whole reason the emulator route exists.

### Community emulators

There is no maintained community emulator that boots Windows Phone 8.x or
Windows 10 Mobile. The Emulation General Wiki's cellphone survey (checked
November 2026) lists only Microsoft's own SDK emulators for these
platforms, all inactive since 2017. The one active adjacent project, WPR
(Windows Phone Runner), runs selected Windows Phone 7/8 XNA games without
booting the OS — useful for games preservation, not for Metro or browser
research, and it must not be described as a Windows Phone emulator.

## Sources

- Microsoft Learn — *Test with the Microsoft Emulator for Windows 10
  Mobile* (system requirements, features that require a physical device,
  networking notes): https://learn.microsoft.com/es-es/windows/uwp/debug-test-perf/test-with-the-emulator
- Microsoft Download Center — *Windows Phone 8.1 Update and Emulators*,
  details id 43719 (live at time of writing; image list and host
  requirements): https://www.microsoft.com/en-za/download/details.aspx?id=43719
- Microsoft — *Visual Studio 2013 System Requirements* (Windows Phone
  emulator host requirements: Windows 8.1 x64 Pro+, Client Hyper-V, SLAT):
  https://learn.microsoft.com/en-us/visualstudio/releases/2013/vs2013-sysrequirements-vs?source=recommendations
- Legacy Update — *Microsoft Emulator for Windows 10 Mobile Anniversary
  Update*, Download Center archive (catalogue page deleted from
  microsoft.com; file hash record): https://legacyupdate.net/download-center/download/53424/microsoft-emulator-for-windows-10-mobile-anniversary-update
- Windows SDK and emulator archive (direct EmulatorSetup.exe links for
  builds 10.0.14393.0 / 10.0.15063 / 10.0.15254.1; the 15254 and 14393
  files were re-verified as served by download.microsoft.com in November
  2026): http://www.output.to/sideway/default.aspx?qno=220300027
- MS-Labrats — *Use Windows Phone Emulator without Visual Studio* (XDE
  command-line launch; secondary source): https://www.ms-labrats.de/2016/05/use-windows-phone-emulator-without.html
- Damir's Corner — *Connecting to Local IIS Express Server from WP8
  Emulator* (host IP via the vEthernet internal switch, firewall rule;
  secondary source, period): https://www.damirscorner.com/blog/posts/20140113-ConnectingToLocalIisExpressServerFromWp8Emulator.html
- Emulation General Wiki — *Cellphone emulators* (Windows Phone 8.x /
  Windows 10 Mobile emulator survey; WPR scope): https://emulation.gametechwiki.com/index.php/Cellphone_emulators
- *Windows on ARM on a Mac: What Works, What Doesn't* (Parallels lists
  Hyper-V as unavailable in Windows 11 ARM VMs on Apple Silicon; secondary
  source): https://machow2.com/windows-on-arm-on-mac/
- W10M Revival Hub — *Sideload & unlock guide* (Windows 10 Mobile
  Developer Mode toggle and Device Portal; community source):
  https://windowsphonehub.neocities.org/w10m
