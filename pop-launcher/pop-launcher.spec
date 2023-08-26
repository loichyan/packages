%define vtag 1.2.1
%define version 1.2.1
%define date 2023-08-24T12:23:08.000
%define release %autorelease -b 2
%define source https://github.com/loichyan/packages/releases/download/nightly/pop-launcher-1.2.1.src.tar.xz
%define checksum sha256:647d060963c3da6be6cf9f7d3f1d881e7f1c783bdd4eb570e92a3602dc462a5d

Name:          pop-launcher
Version:       %{version}
Release:       %{release}
Packager:      Loi Chyan <loichyan@foxmail.com>
License:       MPL-2.0
URL:           https://github.com/pop-os/launcher/
Summary:       Library for writing plugins and frontends for pop-launcher
BuildRequires: cargo, just
Requires:      qalculate
#!RemoteAsset: %{checksum}
Source:        %{source}

%description
Library for writing plugins and frontends for pop-launcher.

%prep
%autosetup -c

%build
just vendor=1

%install
just rootdir=%{buildroot} install_bin
just rootdir=%{buildroot} bin_path=%{_bindir}/pop-launcher install_scripts
just rootdir=%{buildroot} bin_path=%{_bindir}/pop-launcher install_plugins

%files
%license LICENSE
%doc README.md
%{_bindir}/pop-launcher
%{_prefix}/lib/pop-launcher/plugins/*
%{_prefix}/lib/pop-launcher/scripts/*

%changelog
%autochangelog
