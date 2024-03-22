%define vtag nightly
%define version nightly
%define date 2024-03-22T12:20:04.333
%define release %autorelease
%define source *
%define checksum *

Name:          rio
Version:       %{version}
Release:       %{release}
Packager:      Loi Chyan <loichyan@foxmail.com>
License:       MIT
URL:           https://raphamorim.io/rio/
Summary:       A hardware-accelerated GPU terminal emulator.
Requires:      %{name}-terminfo = %{version}-%{release}
BuildRequires: cargo >= 1.75
BuildRequires: cmake
BuildRequires: fontconfig-devel
BuildRequires: freetype-devel
BuildRequires: g++
BuildRequires: libxcb-devel
BuildRequires: libxkbcommon-devel
BuildRequires: ncurses
#!RemoteAsset: %{checksum}
Source:        %{source}


%description
Rio is a terminal built to run everywhere, as a native desktop applications by
Rust or even in the browser powered by WebAssembly.

%package terminfo
Summary:   The terminfo file for %{name}.
BuildArch: noarch
Requires:  ncurses-base

%description terminfo
The terminfo file for %{name}.

%prep
%autosetup -c

%build
# https://github.com/raphamorim/rio/issues/380
cargo build --frozen --offline --release -p rioterm --no-default-features --features=x11

%install
# install-main
install -Dsm755 target/release/rio -t %{buildroot}%{_bindir}
# install-assets
install -Dm644 misc/rio.desktop %{buildroot}%{_datadir}/applications/rio.desktop
install -Dm644 misc/logo.svg %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/rio.svg
# install-terminfo
install -dm755 %{buildroot}%{_datadir}/terminfo
tic -x -o %{buildroot}%{_datadir}/terminfo misc/rio.terminfo

%files
%license LICENSE
%doc README.md
%{_bindir}/rio
%{_datadir}/icons/*
%{_datadir}/applications/*

%files terminfo
%license LICENSE
%{_datadir}/terminfo

%changelog
%autochangelog
