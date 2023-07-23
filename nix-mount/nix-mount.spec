%define vtag 0.1.1
%define version 0.1.1

Name:          nix-mount
Version:       0.1.1
Release:       %autorelease
Packager:      Loi Chyan <loichyan@foxmail.com>
License:       MIT OR Apache-2.0
URL:           https://github.com/dnkmmr69420/nix-installer-scripts
Summary:       Mount /nix.
BuildArch:     noarch
BuildRequires: systemd-rpm-macros
Source:        %{name}-%{vtag}-source.tar.gz

%description
Mount /nix for single user nix installation.

%prep
%autosetup -c

%build

%install
install -dm755 %{buildroot}%{_unitdir}
install -m644 %{SOURCE1} %{buildroot}%{_unitdir}
install -m644 %{SOURCE2} %{buildroot}%{_unitdir}

%files
%{_unitdir}/nix-mount.service
%{_unitdir}/nix.mount

%changelog
%autochangelog
