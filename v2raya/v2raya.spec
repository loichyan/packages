%define vtag v2.2.2
%define version 2.2.2
%define date 2023-08-31T15:36:08
%define release %autorelease
%define source https://github.com/loichyan/packages/releases/download/nightly/v2raya-2.2.2.src.tar.xz
%define checksum sha256:30bfa5aa4a87c3fe699b1d7c6f4b13d0c1ce6e29173e74a6fc22dd5dd8590d0a

Name:          v2raya
Version:       %{version}
Release:       %{release}
Packager:      Loi Chyan <loichyan@foxmail.com>
License:       AGPL-3.0
Url:           https://github.com/v2rayA/v2rayA
Summary:       A Linux web GUI client of Project V which supports V2Ray, Xray, SS, SSR, Trojan and Pingtunnel
BuildRequires: golang >= 1.23
BuildRequires: systemd-rpm-macros
#!RemoteAsset: %{checksum}
Source:        %{source}

%description
A Linux web GUI client of Project V which supports V2Ray, Xray, SS, SSR, Trojan and Pingtunnel

%prep
%autosetup -c
%define BUILD_DIR %{_builddir}/%{name}-%{version}

%build
# build: core
cd %{BUILD_DIR}/service
go build -ldflags '-X github.com/v2rayA/v2rayA/conf.Version='%{version}' -s -w' -trimpath -o v2raya

%install
cd %{BUILD_DIR}
install -Dm755 service/v2raya -t %{buildroot}%{_bindir}
install -dm750 %{buildroot}/etc/v2raya/
install -Dm644 install/universal/v2raya.default -t %{buildroot}%{_sysconfdir}/default/v2raya
install -Dm644 install/universal/v2raya.desktop -t %{buildroot}%{_datadir}/applications/
install -Dm644 install/universal/v2raya.service -t %{buildroot}%{_unitdir}
install -Dm644 install/universal/v2raya-lite.service -t %{buildroot}%{_userunitdir}
install -Dm644 gui/public/img/icons/android-chrome-512x512.png %{buildroot}%{_datadir}/icons/hicolor/512x512/apps/v2raya.png

%files
%config(noreplace) %{_sysconfdir}/default/v2raya
%license LICENSE
%doc README.md
%{_sysconfdir}/v2raya/
%{_bindir}/v2raya
%{_unitdir}/v2raya.service
%{_userunitdir}/v2raya-lite.service
%{_datadir}/applications/v2raya.desktop
%{_datadir}/icons/hicolor/512x512/apps/v2raya.png

%changelog
%autochangelog
