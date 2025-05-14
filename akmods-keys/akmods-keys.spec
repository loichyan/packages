%define vtag v0.2.0
%define version 0.2.0
%define date 2024-11-29T13:08:00
%define release %autorelease

Name:          akmods-keys
Version:       %{version}
Release:       %{release}
Packager:      Loi Chyan <loichyan@foxmail.com>
License:       MIT
URL:           https://github.com/CheariX/silverblue-akmods-keys
Summary:       Keys for akmods
BuildArch:     noarch
Requires:      akmod-nvidia
Requires:      xorg-x11-drv-nvidia
Requires:      xorg-x11-drv-nvidia-cuda
Supplements:   akmods
Source0:       macros.kmodtool
Source1:       private_key.priv
Source2:       public_key.der

%description
Akmods ostree keys for signing modules.

%prep
%setup -qcT

%build

%install
install -Dm640 %{SOURCE0} -t %{buildroot}%{_sysconfdir}/rpm/
install -Dm640 %{SOURCE1} -t %{buildroot}%{_sysconfdir}/pki/%{name}/private/
install -Dm640 %{SOURCE2} -t %{buildroot}%{_sysconfdir}/pki/%{name}/certs/

%files
%attr(0644,root,root) %{_sysconfdir}/pki/%{name}/certs
%attr(0644,root,root) %{_sysconfdir}/pki/%{name}/private
%attr(0644,root,root) %{_sysconfdir}/rpm/macros.kmodtool

%changelog
%autochangelog
