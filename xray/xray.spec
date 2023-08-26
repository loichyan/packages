%define vtag v1.8.3
%define version 1.8.3
%define date 2023-06-19T00:35:46.000
%define release %autorelease
%define source https://github.com/loichyan/packages/releases/download/nightly/xray-1.8.3-source.tar.xz
%define checksum sha256:29af2d51900828d004b50a48cf371af69fc36944030eb6f28a25de155d45ef00

Name:          xray
Version:       %{version}
Release:       %{release}
Packager:      Loi Chyan <loichyan@foxmail.com>
License:       MPL-2.0
Url:           https://xtls.github.io/
Summary:       Xray, Penetrates Everything.
BuildRequires: golang >= 1.19
BuildRequires: systemd-rpm-macros
#!RemoteAsset: %{checksum}
Source:        %{source}

%description
Xray, Penetrates Everything.
Also the best v2ray-core, with XTLS support.
Fully compatible configuration.


%prep
%autosetup -c

%build
go build -ldflags "-s -w -buildid=" -trimpath -o xray ./main

%install
install -Dm755 xray -t %{buildroot}%{_bindir}

%files
%license LICENSE
%doc README.md
%{_bindir}/xray

%changelog
%autochangelog
