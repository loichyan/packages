%define vtag v0.1.1
%define version 0.1.1
%define release %autorelease
%define source xxx
%define checksum yyy

Name:          nix-mount
Version:       %{version}
Release:       %{release}
Packager:      Loi Chyan <loichyan@foxmail.com>
License:       MIT OR Apache-2.0
URL:           https://github.com/dnkmmr69420/nix-installer-scripts
Summary:       Mount /nix.
BuildArch:     noarch
BuildRequires: systemd-rpm-macros
#!RemoteAsset: %{checksum}
Source:        %{source}

%description
Mount /nix for single user nix installation.

%prep
%autosetup -c

%build

%install
install -Dm644 nix.mount %{name}.service -t %{buildroot}%{_unitdir}

%files
%{_unitdir}/%{name}.service
%{_unitdir}/nix.mount

%changelog

