# {{ METADATA BEGIN
%define name akmods-keys
%define vtag v0.1.0
%define version 0.1.0
# METADATA END }}

Name:        %{name}
Version:     %{version}
Release:     %autorelease
Packager:    Loi Chyan <loichyan@foxmail.com>
License:     MIT
URL:         https://github.com/CheariX/silverblue-akmods-keys
Summary:     Keys for akmods
BuildArch:   noarch
Supplements: akmods
Source1:     macros.kmodtool
Source2:     private_key.priv
Source3:     public_key.der

%description
Akmods ostree keys for signing modules.

%prep

%build

%install
install -Dm640 %{SOURCE1} -t %{buildroot}%{_sysconfdir}/rpm/
install -Dm640 %{SOURCE2} -t %{buildroot}%{_sysconfdir}/pki/%{name}/private/
install -Dm640 %{SOURCE3} -t %{buildroot}%{_sysconfdir}/pki/%{name}/certs/

%files
%attr(0644,root,root) %{_sysconfdir}/pki/%{name}/certs
%attr(0644,root,root) %{_sysconfdir}/pki/%{name}/private
%attr(0644,root,root) %{_sysconfdir}/rpm/macros.kmodtool

%changelog
%autochangelog
