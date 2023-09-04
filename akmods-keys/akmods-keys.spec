%define vtag v0.1.0
%define version 0.1.0
%define date 2023-06-25T15:40:38.000
%define release %autorelease
%define source akmods-keys-0.1.0.src.tar.xz
%define checksum *

Name:          akmods-keys
Version:       %{version}
Release:       %{release}
Packager:      Loi Chyan <loichyan@foxmail.com>
License:       MIT
URL:           https://github.com/CheariX/silverblue-akmods-keys
Summary:       Keys for akmods
BuildArch:     noarch
Supplements:   akmods
#!RemoteAsset: %{checksum}
Source:        %{source}

%description
Akmods ostree keys for signing modules.

%prep
%autosetup -c

%build

%install
install -Dm640 macros.kmodtool -t %{buildroot}%{_sysconfdir}/rpm/
install -Dm640 private_key.priv -t %{buildroot}%{_sysconfdir}/pki/%{name}/private/
install -Dm640 public_key.der -t %{buildroot}%{_sysconfdir}/pki/%{name}/certs/

%files
%attr(0644,root,root) %{_sysconfdir}/pki/%{name}/certs
%attr(0644,root,root) %{_sysconfdir}/pki/%{name}/private
%attr(0644,root,root) %{_sysconfdir}/rpm/macros.kmodtool

%changelog
%autochangelog
