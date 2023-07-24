# {{ METADATA BEGIN
%define name nix-mount
%define vtag v0.1.1
%define version 0.1.1
# METADATA END }}

Name:          %{name}
Version:       %{version}
Release:       %autorelease
Packager:      Loi Chyan <loichyan@foxmail.com>
License:       MIT OR Apache-2.0
URL:           https://github.com/dnkmmr69420/nix-installer-scripts
Summary:       Mount /nix.
BuildArch:     noarch
BuildRequires: systemd-rpm-macros
Source1:       nix.mount
Source2:       %{name}.service

%description
Mount /nix for single user nix installation.

%prep

%build

%install
install -Dm644 %{SOURCE1} %{SOURCE2} -t %{buildroot}%{_unitdir}

%files
%{_unitdir}/%{name}.service
%{_unitdir}/nix.mount

%changelog
%autochangelog
