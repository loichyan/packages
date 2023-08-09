%define vtag v0.1.1
%define version 0.1.1
%define date 2023-05-30T14:21:46.000
%define release %autorelease
%define source https://github.com/loichyan/packages/releases/download/nightly/nix-mount-0.1.1-source.tar.xz
%define checksum sha256:c7d233d651b7e88e1fa3ab01b32fd1852787072d1ada59695446d4c19736a128

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
