%define vtag 1.2.1
%define version 1.2.1
%define date 2023-08-10T08:11:09.780
%define release %autorelease
%define source *
%define checksum *

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
just rootdir=%{buildroot} install

%files
%license LICENSE
%doc README.md
%{_bindir}/pop-launcher
%{_prefix}/lib/pop-launcher/*

%changelog
