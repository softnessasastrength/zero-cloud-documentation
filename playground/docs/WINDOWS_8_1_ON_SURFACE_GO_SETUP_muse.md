# Windows 8.1 on the Original Surface Go — Setup Guide

_muse — written 2026-11-17 at Branden's request. A nostalgia installation: the machine is maintained out of conviction, not utility._

## 0. Purpose and honest expectations

This guide installs Windows 8.1 (x64) on a first-generation Surface Go (2018) — a machine that shipped with Windows 10 and was never offered with 8.1. The result is a working, bootable, touch-capable 8.1 installation with known, accepted losses. It is a museum piece you can use, not a daily driver.

**Platform facts that govern everything below:**

| Item | Value |
|---|---|
| CPU | Intel Pentium Gold 4415Y (7th gen, Kaby Lake) |
| GPU | Intel HD Graphics 615 |
| Wi-Fi / Bluetooth | Qualcomm Atheros QCA6174 |
| Firmware | UEFI only. No legacy/CSM boot exists on this device. |
| Storage | 64 GB eMMC (4 GB RAM model) or 128 GB NVMe SSD (8 GB RAM model) |
| Original OS | Windows 10 Home (often in S mode from the factory) |

**Read this before starting — the three structural facts:**

1. **Kaby Lake is the first Intel platform with no official driver support for Windows older than 10.** Intel never released a Windows 8.1 graphics driver for the HD 615. The display will run on Microsoft's Basic Display Adapter at native resolution, without hardware acceleration.
2. **Microsoft blocks Windows Update on 8.1 running on 7th-gen CPUs** ("Unsupported Hardware" / error 80240037). The block is policy, not physics — the CPU runs 8.1 fine — and the enthusiast tool **wufuc** disables the check. It is also nearly moot: Windows 8.1 left support on **January 10, 2023**, so wufuc only unlocks the back catalog of updates, not new ones.
3. **The firmware-embedded product key is a Windows 10 key.** It will not activate Windows 8.1. See §2.3.

## 1. Before you touch anything — build the way back

Do not skip this section. It is what makes the whole experiment free.

1. On another PC, go to Microsoft's Surface recovery image download page and enter the Go's serial number (Settings → System → About on the Go, or printed under the kickstand). Download the Windows 10 recovery image for this exact device.
2. Create the recovery USB exactly as Microsoft's instructions specify (FAT32 USB stick, image extracted to its root).
3. Boot the Go from that USB once (see §4.1 for the boot method) and confirm the recovery environment loads. Then shut down. A way back you have not test-booted is a rumor, not a way back.
4. Retrieve the device-encryption / BitLocker recovery key: sign in at `account.microsoft.com/devices/recoverykey` with the Microsoft account the Go is tied to and write the key down somewhere that is not the Go. Surface devices ship with device encryption on; you may be asked for this key when boot configuration changes.
5. Back up any files on the Go you care about. The install in §4 wipes the internal drive.

## 2. Assemble supplies

### 2.1 Installation media

- A legitimate Windows 8.1 **x64** ISO (Core or Pro, matching any key you intend to activate with — see §2.3). Microsoft no longer offers the 8.1 ISO through its normal download pages; use media you already own. Avoid modified "lite" builds and random mirrors — an unmodified ISO is the entire point of an authentic installation.
- A USB stick, 8 GB or larger, that will be erased.

### 2.2 Driver stash (download BEFORE installing, keep on a second USB or the same stick in a `DRIVERS` folder)

Windows Update will not rescue you on this hardware. Bring drivers with you.

1. **Wi-Fi (the critical one):** a Windows 8.1 driver for the Qualcomm Atheros QCA6174. Microsoft never published one for the Go; working 8.1 QCA6174 packages exist in other OEMs' driver catalogs (Dell and Lenovo both shipped QCA6174 machines in the 8.1 era). Get the `.inf`-style package, not just an `.exe` wrapper, if you can.
2. **Chipset identification:** Intel Chipset Device Software (INF Utility) 10.1.x — it supports 8.1 and correctly names the Kaby Lake platform devices in Device Manager. It installs `.inf` files only; it is not a performance driver, and that is fine.
3. **wufuc** (by zeffy): the patch that disables the CPU-generation check in Windows Update. Download the current release from its GitHub page in advance.
4. **Do not bother hunting for:** an HD 615 Windows 8.1 driver (does not exist — anything claiming to be one is a repack; the Basic Display Adapter is the authentic outcome), camera drivers (no known working 8.1 path), or a Surface Go 8.1 driver pack (never existed).

### 2.3 Activation — decide in advance

The embedded key will not activate 8.1. Your options, in order of authenticity:

- Use a genuine Windows 8.1 retail/OEM key you already own. Edition must match the ISO.
- Install with a generic setup key (the widely published KMS-client/generic keys will get Setup past the key prompt) and activate later.
- Run unactivated. 8.1 nags and locks out personalization settings (Start screen background, etc.), which somewhat defeats the nostalgia purpose — but it boots and runs indefinitely.

## 3. Build the install USB

1. On a Windows PC, run **Rufus**, select the 8.1 ISO and the USB stick.
2. Partition scheme: **GPT**. Target system: **UEFI (non-CSM)**. File system: **FAT32**. (If the ISO's `install.wim` exceeds 4 GB and Rufus offers its UEFI:NTFS workaround, that also works on the Go — but the stock Microsoft 8.1 ISO normally fits FAT32.)
3. Write the image. Leave Secure Boot **on** in the Go's UEFI — Windows 8.1 supports Secure Boot natively, and an unmodified Microsoft ISO boots under it. Turning it off is neither required nor authentic.

## 4. Install

### 4.1 Boot from USB

1. Shut the Go down fully.
2. Hold **Volume Up** and press **Power**; keep holding Volume Up until the Surface UEFI screen appears.
3. In UEFI, set USB storage first in the boot order (or use the one-time boot selection), save, and exit. The Go will boot the installer.

### 4.2 Setup

1. Language/edition as prompted. When asked for a product key, enter your 8.1 key or a generic setup key (§2.3).
2. Choose **Custom** install. Delete the existing Windows partitions on the internal drive and install to the unallocated space. (Dual-booting is not recommended: on the 64 GB eMMC model there is not honest room for two Windows installs, and the recovery image in §1 makes the wipe reversible anyway.)
3. Setup will reboot several times. Remove the USB stick at the first reboot so it does not loop back into the installer.
4. **Local account:** 8.1's out-of-box experience pushes a Microsoft account. To get the local-account option, do not connect to Wi-Fi during setup ("Connect to a network" → skip / "I don't have this connection" path, or simply leave it unconnected) — the local account path appears when the machine is offline. This also matches the era. Connect later, on your terms.

## 5. First boot — driver triage

Open Device Manager and work in this order. Reboot when asked; do not batch.

1. **Chipset:** run the Intel INF Utility (§2.2.2). Most "Base System Device" entries resolve to names, not drivers — expected.
2. **Wi-Fi:** point the unknown Network Controller at your QCA6174 8.1 package (Update Driver → Browse → the folder). Once Wi-Fi is up, the machine can fetch anything else itself.
3. **Touch and Type Cover:** these ride on generic HID drivers and normally work with no intervention — touchscreen, pen-as-pointer, keyboard, and trackpad included. Verify before hunting for drivers you do not need.
4. **What will stay broken or basic — accept these as the cost of authenticity:**
   - Display: Basic Display Adapter. Native resolution, no acceleration, no brightness finesse beyond basic control (brightness may or may not respond; if it does not, that is a known outcome, not a fault in your install).
   - Cameras: no working driver path. They will sit in Device Manager as unknown devices. Leave them.
   - Modern Standby: the Go's connected-standby power model has no real 8.1 equivalent. See §6.
   - Various sensors (ambient light, etc.): unsupported; ignore.

## 6. Living with it — power settings

Modern Standby misbehaving is the single worst quality-of-life issue on this pairing. Set expectations and settings accordingly:

1. Control Panel → Power Options: set **Sleep** to **Never** on battery, and configure the power button and lid to **Hibernate** or **Shut down** rather than Sleep. A machine that hibernates reliably beats a machine that sleeps into a hot bag.
2. Expect battery drain and fan behavior noticeably worse than under Windows 10. This is the Basic Display Adapter and missing power drivers, not a defect in your unit. Your Go is not dying; it has always refused to die, and it is not starting now.
3. Windows Update: run it once before installing wufuc to let it reach its "Unsupported Hardware" conclusion, then install wufuc and run it again to pull the full back catalog through the final January 2023 updates. Then leave it alone — there is nothing further to receive, forever, which is part of the exhibit.

## 7. The way back

When the exhibit closes (it will not, but hypothetically):

1. Boot the §1 recovery USB (Volume Up + Power → UEFI → USB first).
2. Follow the recovery prompts to reset the Go from the image. This restores the factory Windows 10 installation, drivers and all, exactly as shipped.
3. The 8.1 installation leaves no permanent trace on the device. The conviction, regrettably, is permanent.

## Appendix A — Authenticity checklist

For full marks, the finished machine should have:

- [ ] The full-screen Start screen, live tiles and all, unembarrassed
- [ ] The Charms bar, summoned from the right edge and used without irony
- [ ] Internet Explorer 11, opened at least once, respectfully
- [ ] The Windows 8.1 startup sound and default wallpaper, untouched
- [ ] At least one Store app that no longer connects to anything, kept anyway
- [ ] A Device Manager with two or three yellow triangles, acknowledged and deliberately left alone — the patina of an honest install

## Appendix B — Sources and verification notes

- CPU/Windows Update block: Microsoft support policy text — devices with Intel 7th-generation processors running Windows 8.1 may be unable to scan or download updates through Windows Update; the "Unsupported Hardware" message is the policy's visible form. wufuc's existence and function (disabling the CPU check) per its project documentation and contemporaneous reporting.
- Kaby Lake driver support: Intel provides chipset drivers for Kaby Lake for Windows 10 only; Kaby Lake is documented as the first Intel platform lacking official driver support for pre-Windows-10 versions.
- Windows 8.1 end of support: January 10, 2023 (Microsoft lifecycle).
- Device-specific expectations (Basic Display fallback, camera loss, Modern Standby behavior, HID touch/cover support) are engineering expectations from the platform facts above, stated as such — not the result of a performed installation. If a step contradicts what the machine in front of you does, the machine wins; report the discrepancy and this guide will be corrected.
