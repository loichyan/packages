%define vtag 1.2.1
%define version 1.2.1
%define date 2023-08-24T12:23:08.000
%define release %autorelease -b 2
%define source https://github.com/loichyan/packages/releases/download/nightly/pop-launcher-1.2.1.src.tar.xz
%define checksum sha256:960c83d69ed678754fb22f97ddc8ded841df87f7358122c64073357d7f418d64

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
