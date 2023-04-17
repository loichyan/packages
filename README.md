# 🌰 RPM Packages

My personal packages used on Fedora.

You can find the RPM packages in the DNF repository at
<https://copr.fedorainfracloud.org/coprs/loichyan/packages/>.

| Package           | Status                                                                 |
| ----------------- | ---------------------------------------------------------------------- |
| wezterm           | [![Copr build status][wezterm_badge]][wezterm_url]                     |
| symbols-nerd-font | [![Copr build status][symbols_nerd_font_badge]][symbols_nerd_font_url] |

[wezterm_url]:
  https://copr.fedorainfracloud.org/coprs/loichyan/packages/package/wezterm/
[wezterm_badge]:
  https://copr.fedorainfracloud.org/coprs/loichyan/packages/package/wezterm/status_image/last_build.png
[symbols_nerd_font_url]:
  https://copr.fedorainfracloud.org/coprs/loichyan/packages/package/symbols-nerd-font/
[symbols_nerd_font_badge]:
  https://copr.fedorainfracloud.org/coprs/loichyan/packages/package/symbols-nerd-font/status_image/last_build.png

## ⚙️ Installation

```sh
sudo dnf copr enable loichyan/packages
# Or download manually
source /etc/os-release && \
  curl "https://copr.fedorainfracloud.org/coprs/loichyan/packages/repo/$ID-$VERSION_ID/dnf.repo" | \
  sudo tee /etc/yum.repos.d/_copr:copr.fedorainfracloud.org:loichyan:packages.repo
```

## ⚖️ License

Licensed under either of

- Apache License, Version 2.0 ([LICENSE-APACHE](LICENSE-APACHE) or
  <http://www.apache.org/licenses/LICENSE-2.0>)
- MIT license ([LICENSE-MIT](LICENSE-MIT) or
  <http://opensource.org/licenses/MIT>)

at your option.
