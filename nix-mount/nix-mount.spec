%define vtag v0.2.0
%define version 0.2.0
%define date 2025-05-14T07:54:46
%define release %autorelease

Name:          nix-mount
Version:       %{version}
Release:       %{release}
Packager:      Loi Chyan <loichyan@foxmail.com>
License:       MIT
URL:           https://github.com/nix-community/nix-installers
Summary:       Create /nix mount point for OStree
BuildArch:     noarch
BuildRequires: systemd-rpm-macros
Source0:       nix.mount
Source1:       nix-setup.service

%description
Create /nix mount point for OStree

%prep
%setup -qcT

%build

%install
install -Dm644 %{SOURCE0} %{SOURCE1} -t %{buildroot}%{_unitdir}

%files
%{_unitdir}/nix.mount
%{_unitdir}/nix-setup.service

%changelog
%autochangelog
