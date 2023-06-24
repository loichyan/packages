Name:          nix-mount
Version:       0.1.1
Release:       %autorelease
Packager:      Loi Chyan <loichyan@foxmail.com>
License:       MIT OR Apache-2.0
URL:           https://www.nerdfonts.com
Summary:       Mount /nix.
BuildArch:     noarch
BuildRequires: systemd-rpm-macros
Source1:       nix-mount.service
Source2:       nix.mount

%description
Mount /nix for single user nix installation.

%files
%{_unitdir}/nix-mount.service
%{_unitdir}/nix.mount

%prep

%build

%install
install -dm755 %{buildroot}%{_unitdir}
install -m644 %{SOURCE1} %{buildroot}%{_unitdir}
install -m644 %{SOURCE2} %{buildroot}%{_unitdir}

%changelog
%autochangelog
