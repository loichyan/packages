%define vtag 1.2.1
%define version 1.2.1
%define date 2023-08-10T08:11:09.780
%define release %autorelease
%define source https://github.com/loichyan/packages/releases/download/nightly/pop-launcher-1.2.1-source.tar.xz
%define checksum sha256:d4afa2921a51257202c0f8c509e62e1de11df39459cd659ab81f7aa576db80ef

Name:          pop-launcher
Version:       %{version}
Release:       %{release}
Packager:      Loi Chyan <loichyan@foxmail.com>
License:       MPL-2.0
URL:           https://github.com/pop-os/launcher/
Summary:       Library for writing plugins and frontends for pop-launcher
BuildRequires: cargo, just
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
