%define vtag 20230712-072601-f4abf8fd
%define version 20230712
%define date 2023-07-12T14:26:01.000
%define release %autorelease
%define source https://github.com/loichyan/packages/releases/download/nightly/wezterm-20230712.src.tar.xz
%define checksum sha256:72da065d54879c06f155e35c8da9c2fc2b9a5087ced348d6ef809ecd0937890b

Name:          wezterm
Version:       %{version}
Release:       %{release}
Packager:      Loi Chyan <loichyan@foxmail.com>
License:       MIT
URL:           https://wezfurlong.org/wezterm/
Summary:       Wez's Terminal Emulator.
Requires:      %{name}-terminfo = %{version}-%{release}
BuildRequires: cargo >= 1.65
BuildRequires: make
BuildRequires: gcc
BuildRequires: gcc-c++
BuildRequires: ncurses
BuildRequires: fontconfig-devel
BuildRequires: openssl-devel
BuildRequires: libxcb-devel
BuildRequires: libxkbcommon-devel
BuildRequires: libxkbcommon-x11-devel
BuildRequires: wayland-devel
BuildRequires: mesa-libEGL-devel
BuildRequires: xcb-util-devel
BuildRequires: xcb-util-keysyms-devel
BuildRequires: xcb-util-image-devel
BuildRequires: xcb-util-wm-devel
#!RemoteAsset: %{checksum}
Source:        %{source}


%description
wezterm is a terminal emulator with support for modern features
such as fonts with ligatures, hyperlinks, tabs and multiple
windows.

%package terminfo
Summary:   The terminfo file for %{name}.
BuildArch: noarch
Requires:  ncurses-base

%description terminfo
The terminfo file for %{name}.

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
# install-assets
install -Dm755 assets/open-wezterm-here -t %{buildroot}%{_bindir}
install -Dm644 assets/shell-integration/* -t %{buildroot}%{_sysconfdir}/profile.d
install -Dm644 assets/shell-completion/zsh %{buildroot}%{_datadir}/zsh/site-functions/_wezterm
install -Dm644 assets/shell-completion/bash %{buildroot}%{_sysconfdir}/bash_completion.d/wezterm
install -Dm644 assets/shell-completion/fish %{buildroot}%{_datadir}/fish/completions/wezterm.fish
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
%{_bindir}/wezterm*
%{_bindir}/strip-ansi-escapes
%{_bindir}/open-wezterm-here
%{_datadir}/zsh/site-functions/*
%{_sysconfdir}/bash_completion.d/*
%{_datadir}/fish/completions/*
%{_datadir}/icons/*
%{_datadir}/applications/*
%{_datadir}/metainfo/*
%{_datadir}/nautilus-python/extensions/*
%{_sysconfdir}/profile.d/*

%files terminfo
%license LICENSE
%{_datadir}/terminfo

%changelog
%autochangelog
