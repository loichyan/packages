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
BuildRequires: cargo
#!RemoteAsset: %{checksum}
Source:        %{source}
Patch0         0001-Copy-instead-of-symlink.patch
Patch1:        0001-Remove-frozen-lock.patch

%description
Library for writing plugins and frontends for pop-launcher.

%prep
%autosetup -c

%build
just build-vendored

%install
just rootdir=%{buildroot} install

%files
%license LICENSE
%doc README.md
%{_bindir}/pop-launcher
%{_prefix}/lib/pop-launcher/*

%changelog
