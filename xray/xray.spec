%define vtag v1.8.8
%define version 1.8.8
%define date 2024-02-25T14:31:59
%define release %autorelease
%define source https://github.com/loichyan/packages/releases/download/nightly/xray-1.8.8.src.tar.xz
%define checksum sha256:3bb1957421a095d5a8e69b997491416ae80af2aa92fa511c32191a3486794a5d

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
