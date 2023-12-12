%define vtag v1.8.6
%define version 1.8.6
%define date 2023-11-18T01:11:40
%define release %autorelease
%define source https://github.com/loichyan/packages/releases/download/nightly/xray-1.8.6.src.tar.xz
%define checksum sha256:5ff631e2cae551361749397ba169dad23ce53bcc73391ea88874690122338f05

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
