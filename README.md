# 🌰 RPM Packages

My personal packages used on Fedora.

You can find the RPM packages in the DNF repository at
<https://build.opensuse.org/project/show/home:loichyan>.

## 📊 Status

| Package               | Status                                                  |
| --------------------- | ------------------------------------------------------- |
| [nerd-font-symbols]   | [![nerd-font-symbols-badge]][nerd-font-symbols-pkg]     |
| [nix-mount]           | [![nix-mount-badge]][nix-mount-pkg]                     |
| [sarasa-gothic-fonts] | [![sarasa-gothic-fonts-badge]][sarasa-gothic-fonts-pkg] |
| [v2raya]              | [![v2raya-badge]][v2raya-pkg]                           |
| [wezterm]             | [![wezterm-badge]][wezterm-pkg]                         |
| [xray]                | [![xray-badge]][xray-pkg]                               |

[nerd-font-symbols]: https://www.nerdfonts.com
[nerd-font-symbols-pkg]: https://build.opensuse.org/package/show/home:loichyan/nerd-font-symbols
[nerd-font-symbols-badge]:
  https://build.opensuse.org/projects/home:loichyan/packages/nerd-font-symbols/badge.svg?type=percent
[nix-mount]: nix-mount
[nix-mount-pkg]: https://build.opensuse.org/package/show/home:loichyan/nix-mount
[nix-mount-badge]:
  https://build.opensuse.org/projects/home:loichyan/packages/nix-mount/badge.svg?type=percent
[sarasa-gothic-fonts]: https://github.com/be5invis/Sarasa-Gothic
[sarasa-gothic-fonts-pkg]: https://build.opensuse.org/package/show/home:loichyan/sarasa-gothic-fonts
[sarasa-gothic-fonts-badge]:
  https://build.opensuse.org/projects/home:loichyan/packages/sarasa-gothic-fonts/badge.svg?type=percent
[v2raya]: https://www.nerdfonts.com
[v2raya-pkg]: https://build.opensuse.org/package/show/home:loichyan/v2raya
[v2raya-badge]:
  https://build.opensuse.org/projects/home:loichyan/packages/v2raya/badge.svg?type=percent
[wezterm]: https://wezfurlong.org/wezterm
[wezterm-pkg]: https://build.opensuse.org/package/show/home:loichyan/wezterm
[wezterm-badge]:
  https://build.opensuse.org/projects/home:loichyan/packages/wezterm/badge.svg?type=percent
[xray]: https://www.nerdfonts.com
[xray-pkg]: https://build.opensuse.org/package/show/home:loichyan/xray
[xray-badge]: https://build.opensuse.org/projects/home:loichyan/packages/xray/badge.svg?type=percent

## ⚙️ Installation

```sh
source /etc/os-release &&
  dnf config-manager --add-repo https://download.opensuse.org/repositories/home:loichyan/Fedora_$VERSION_ID/home:loichyan.repo
# Or download manually
source /etc/os-release &&
  curl -fL "https://download.opensuse.org/repositories/home:loichyan/Fedora_$VERSION_ID/home:loichyan.repo" |
  sudo tee /etc/yum.repos.d/home_loichyan.repo
```

## 📦 Packaging process

A package is checked locally (via manually running or GitHub Actions):

<!--
// https://arthursonzogni.com/Diagon/#Flowchart

"START"

if ("Is %vtag the latest?")
  noop
else {
  "Update SPEC files (ci --update)"
  "Update sources (ci --update-source)"
  "Upload sources (ci --upload)"
  "Commit changes (ci --commit)"
  "Trigger rebuild (ci --rebuild)"
}

"END"
-->

```text
        ┌─────┐
        │START│
        └──┬──┘
  _________▽__________
 ╱                    ╲
╱ Is %vtag the latest? ╲___
╲                      ╱yes│
 ╲____________________╱    │
           │no             │
  ┌────────▽────────┐      │
  │Update SPEC files│      │
  │(ci --update)    │      │
  └────────┬────────┘      │
 ┌─────────▽────────┐      │
 │Update sources (ci│      │
 │--update-source)  │      │
 └─────────┬────────┘      │
   ┌───────▽──────┐        │
   │Upload sources│        │
   │(ci --upload) │        │
   └───────┬──────┘        │
   ┌───────▽──────┐        │
   │Commit changes│        │
   │(ci --commit) │        │
   └───────┬──────┘        │
   ┌───────▽───────┐       │
   │Trigger rebuild│       │
   │(ci --rebuild) │       │
   └───────┬───────┘       │
           └───┬───────────┘
             ┌─▽─┐
             │END│
             └───┘
```

When the OBS instance receive the rebuild request:

<!--
// https://arthursonzogni.com/Diagon/#Flowchart

"START"

{
  "Fetch SPEC files (obs_scm)"
  "Download sources (download_assets)"
  "Build packages"
}

"END"
-->

```text
      ┌─────┐
      │START│
      └──┬──┘
 ┌───────▽───────┐
 │Fetch SPEC     │
 │files (obs_scm)│
 └───────┬───────┘
┌────────▽────────┐
│Download sources │
│(download_assets)│
└────────┬────────┘
 ┌───────▽──────┐
 │Build packages│
 └───────┬──────┘
       ┌─▽─┐
       │END│
       └───┘
```

## ⚖️ License

Licensed under either of

- Apache License, Version 2.0 ([LICENSE-APACHE](LICENSE-APACHE) or
  <http://www.apache.org/licenses/LICENSE-2.0>)
- MIT license ([LICENSE-MIT](LICENSE-MIT) or <http://opensource.org/licenses/MIT>)

at your option.
