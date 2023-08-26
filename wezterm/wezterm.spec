%define vtag 20230712-072601-f4abf8fd
%define version 20230712
%define date 2023-07-12T14:26:01.000
%define release %autorelease -b 2
%define source https://github.com/loichyan/packages/releases/download/nightly/wezterm-20230712-source.tar.xz
%define checksum sha256:adafbef84dc464dfe97bf1ff970f13fd6ddca90c1fdc4751adc894de5a8fc43e

Name:          wezterm
Version:       %{version}
Release:       %{release}
Packager:      Loi Chyan <loichyan@foxmail.com>
License:       MIT
URL:           https://wezfurlong.org/wezterm/
Summary:       Wez's Terminal Emulator.
# TODO: no need requires?
Requires:      dbus, fontconfig, openssl, libxcb, libxkbcommon, libxkbcommon-x11
Requires:      libwayland-client, libwayland-egl, libwayland-cursor, mesa-libEGL
Requires:      xcb-util, xcb-util-keysyms, xcb-util-image, xcb-util-wm
Requires:      %{name}-terminfo = %{version}-%{release}
BuildRequires: cargo >= 1.65, make, gcc, gcc-c++, ncurses, fontconfig-devel, openssl-devel
BuildRequires: libxcb-devel, libxkbcommon-devel, libxkbcommon-x11-devel, wayland-devel
BuildRequires: mesa-libEGL-devel, xcb-util-devel, xcb-util-keysyms-devel
BuildRequires: xcb-util-image-devel, xcb-util-wm-devel
#!RemoteAsset: %{checksum}
Source:        %{source}


%description
wezterm is a terminal emulator with support for modern features
such as fonts with ligatures, hyperlinks, tabs and multiple
windows.

%package terminfo
Summary:   The terminfo file for wezterm.
BuildArch: noarch
Requires:  ncurses-base

%description terminfo
The terminfo file for wezterm.

%files terminfo
%license LICENSE
%{_datadir}/terminfo

%prep
%autosetup -c

%build
cargo build --frozen --offline --all --release

%install
# install-main
install -Dsm755 target/release/wezterm -t %{buildroot}%{_bindir}
install -Dsm755 target/release/wezterm-mux-server -t %{buildroot}%{_bindir}
install -Dsm755 target/release/wezterm-gui -t %{buildroot}%{_bindir}
install -Dsm755 target/release/strip-ansi-escapes -t %{buildroot}%{_bindir}
install -Dm755 assets/open-wezterm-here -t %{buildroot}%{_bindir}
install -Dm644 assets/shell-integration/* -t %{buildroot}%{_sysconfdir}/profile.d
install -Dm644 assets/shell-completion/zsh %{buildroot}%{_datadir}/zsh/site-functions/_wezterm
install -Dm644 assets/shell-completion/bash %{buildroot}%{_sysconfdir}/bash_completion.d/wezterm
install -Dm644 assets/icon/terminal.png %{buildroot}%{_datadir}/icons/hicolor/128x128/apps/org.wezfurlong.wezterm.png
install -Dm644 assets/wezterm.desktop %{buildroot}%{_datadir}/applications/org.wezfurlong.wezterm.desktop
install -Dm644 assets/wezterm.appdata.xml %{buildroot}%{_datadir}/metainfo/org.wezfurlong.wezterm.appdata.xml
install -Dm644 assets/wezterm-nautilus.py %{buildroot}%{_datadir}/nautilus-python/extensions/wezterm-nautilus.py
# install-terminfo
install -dm755 %{buildroot}%{_datadir}/terminfo
tic -x -o %{buildroot}%{_datadir}/terminfo termwiz/data/wezterm.terminfo

%files
%license LICENSE
%doc README.md
%{_bindir}/wezterm
%{_bindir}/wezterm-gui
%{_bindir}/wezterm-mux-server
%{_bindir}/strip-ansi-escapes
%{_bindir}/open-wezterm-here
%{_datadir}/zsh/site-functions/_wezterm
%{_sysconfdir}/bash_completion.d/wezterm
%{_datadir}/icons/hicolor/128x128/apps/org.wezfurlong.wezterm.png
%{_datadir}/applications/org.wezfurlong.wezterm.desktop
%{_datadir}/metainfo/org.wezfurlong.wezterm.appdata.xml
%{_datadir}/nautilus-python/extensions/wezterm-nautilus.py*
%{_sysconfdir}/profile.d/*

%files terminfo
%license LICENSE
%{_datadir}/terminfo

%changelog
%autochangelog
