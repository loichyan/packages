%define vtag v0.3.0
%define version 0.3.0
%define date 2026-01-30T08:51:16
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
Requires:    nvidia-container-toolkit
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
install -Dm640 %{SOURCE1} -t %{buildroot}%{_sysconfdir}/pki/akmods-keys/private/
install -Dm640 %{SOURCE2} -t %{buildroot}%{_sysconfdir}/pki/akmods-keys/certs/

%files
%attr(0644,root,root) %{_sysconfdir}/rpm/macros.kmodtool
%attr(0644,root,root) %{_sysconfdir}/pki/akmods-keys/certs
%attr(0644,root,root) %{_sysconfdir}/pki/akmods-keys/private

%changelog
%autochangelog
