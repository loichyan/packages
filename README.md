# 🌰 RPM Packages

My personal packages used on Fedora.

You can find the RPM packages in the DNF repository at
<https://build.opensuse.org/project/show/home:loichyan>.

## 📊 Status

| Package               | Status                                                  |
| --------------------- | ------------------------------------------------------- |
| [nix-mount]           | [![nix-mount-badge]][nix-mount-pkg]                     |
| [sarasa-gothic-fonts] | [![sarasa-gothic-fonts-badge]][sarasa-gothic-fonts-pkg] |
| [symbols-nerd-fonts]  | [![symbols-nerd-fonts-badge]][symbols-nerd-fonts-pkg]   |
| [wezterm]             | [![wezterm-badge]][wezterm-pkg]                         |

[nix-mount]: nix-mount
[nix-mount-pkg]: https://build.opensuse.org/package/show/home:loichyan/nix-mount
[nix-mount-badge]:
  https://build.opensuse.org/projects/home:loichyan/packages/nix-mount/badge.svg?type=percent
[symbols-nerd-fonts]: https://www.nerdfonts.com
[symbols-nerd-fonts-pkg]: https://build.opensuse.org/package/show/home:loichyan/symbols-nerd-fonts
[symbols-nerd-fonts-badge]:
  https://build.opensuse.org/projects/home:loichyan/packages/symbols-nerd-fonts/badge.svg?type=percent
[wezterm]: https://wezfurlong.org/wezterm
[wezterm-pkg]: https://build.opensuse.org/package/show/home:loichyan/wezterm
[wezterm-badge]:
  https://build.opensuse.org/projects/home:loichyan/packages/wezterm/badge.svg?type=percent
[sarasa-gothic-fonts]: https://github.com/be5invis/Sarasa-Gothic
[sarasa-gothic-fonts-pkg]: https://build.opensuse.org/package/show/home:loichyan/sarasa-gothic-fonts
[sarasa-gothic-fonts-badge]:
  https://build.opensuse.org/projects/home:loichyan/packages/sarasa-gothic-fonts/badge.svg?type=percent

## ⚙️ Installation

```sh
sudo dnf copr enable loichyan/packages
# Or download manually
source /etc/os-release &&
  curl "https://copr.fedorainfracloud.org/coprs/loichyan/packages/repo/$ID-$VERSION_ID/dnf.repo" |
  sudo tee /etc/yum.repos.d/_copr:copr.fedorainfracloud.org:loichyan:packages.repo
```

## ⚖️ License

Licensed under either of

- Apache License, Version 2.0 ([LICENSE-APACHE](LICENSE-APACHE) or
  <http://www.apache.org/licenses/LICENSE-2.0>)
- MIT license ([LICENSE-MIT](LICENSE-MIT) or <http://opensource.org/licenses/MIT>)

at your option.
