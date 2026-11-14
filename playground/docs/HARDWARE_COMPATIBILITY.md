# Hardware compatibility record

| Target | v1 implementation strategy | Validation status |
| --- | --- | --- |
| Android | Responsive installable PWA plus local Node API (Termux setup documented). | No device smoke test claimed. |
| Chromebook / Crostini | Chromium browser plus Node local API in Crostini. | No Chromebook smoke test claimed. |
| Desktop browser | Responsive browser/PWA plus local Node API. | Production build validated; no installation flow smoke test claimed. |
| Windows Phone 8.x / Windows 10 Mobile | Research-only feasibility study. | No hardware, OS build, SDK, signing, TLS or network validation has been performed. |

Windows Phone claims require a named handset and OS build, supported SDK/toolchain, app package and signing path, developer unlock availability, TLS compatibility, and successful connection to the local API. The modern PWA is not presumed to install on legacy Windows Phone browsers. No simulation controls connect to physical equipment.
