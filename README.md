# 🌰 RPM Packages

My personal packages used on Fedora.

You can find the RPM packages in the DNF repository at
<https://copr.fedorainfracloud.org/coprs/loichyan/packages/>.

## 📊 Status

| Package               | Status                                                  |
| --------------------- | ------------------------------------------------------- |
| [wezterm]             | [![wezterm-badge]][wezterm-pkg]                         |
| [symbols-nerd-font]   | [![symbols-nerd-font-badge]][symbols-nerd-font-pkg]     |
| [nix-mount]           | [![nix-mount-badge]][nix-mount-pkg]                     |
| [sarasa-gothic-fonts] | [![sarasa-gothic-fonts-badge]][sarasa-gothic-fonts-pkg] |

[wezterm]: https://wezfurlong.org/wezterm
[wezterm-pkg]:
  https://copr.fedorainfracloud.org/coprs/loichyan/packages/package/wezterm/
[wezterm-badge]:
  https://copr.fedorainfracloud.org/coprs/loichyan/packages/package/wezterm/status_image/last_build.png
[symbols-nerd-font]: https://www.nerdfonts.com
[symbols-nerd-font-pkg]:
  https://copr.fedorainfracloud.org/coprs/loichyan/packages/package/symbols-nerd-font/
[symbols-nerd-font-badge]:
  https://copr.fedorainfracloud.org/coprs/loichyan/packages/package/symbols-nerd-font/status_image/last_build.png
[nix-mount]: nix-mount
[nix-mount-pkg]:
  https://copr.fedorainfracloud.org/coprs/loichyan/packages/package/nix-mount/
[nix-mount-badge]:
  https://copr.fedorainfracloud.org/coprs/loichyan/packages/package/nix-mount/status_image/last_build.png
[sarasa-gothic-fonts]: https://github.com/be5invis/Sarasa-Gothic
[sarasa-gothic-fonts-pkg]:
  https://copr.fedorainfracloud.org/coprs/loichyan/packages/package/sarasa-gothic-fonts/
[sarasa-gothic-fonts-badge]:
  https://copr.fedorainfracloud.org/coprs/loichyan/packages/package/sarasa-gothic-fonts/status_image/last_build.png

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
- MIT license ([LICENSE-MIT](LICENSE-MIT) or
  <http://opensource.org/licenses/MIT>)

at your option.
