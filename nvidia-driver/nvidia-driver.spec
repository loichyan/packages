%define vtag v0.2.0
%define version 0.2.0
%define date 2024-11-29T13:08:00
%define release %autorelease

Name:        nvidia-driver
Version:     %{version}
Release:     %{release}
Packager:    Loi Chyan <loichyan@outlook.com>
License:     MIT
URL:         https://github.com/loichyan/packages
Summary:     Nvidia driver with secure boot support
BuildArch:   noarch
Requires:    akmod-nvidia
Requires:    xorg-x11-drv-nvidia
Requires:    xorg-x11-drv-nvidia-cuda
Supplements: akmods
Source0:     macros.kmodtool
Source1:     private_key.priv
Source2:     public_key.der

%description
Nvidia driver with secure boot support for silverblue.

%prep
%setup -qcT

%build

%install
# See <https://github.com/CheariX/silverblue-akmods-keys>
install -Dm640 %{SOURCE0} -t %{buildroot}%{_sysconfdir}/rpm/
install -Dm640 %{SOURCE1} -t %{buildroot}%{_sysconfdir}/pki/%{name}/private/
install -Dm640 %{SOURCE2} -t %{buildroot}%{_sysconfdir}/pki/%{name}/certs/

%files
%attr(0644,root,root) %{_sysconfdir}/pki/%{name}/certs
%attr(0644,root,root) %{_sysconfdir}/pki/%{name}/private
%attr(0644,root,root) %{_sysconfdir}/rpm/macros.kmodtool

%changelog
%autochangelog
