%define vtag v1.085
%define version 1.085
%define date 2024-01-17T01:43:58.436
%define release %autorelease
%define source https://github.com/loichyan/packages/releases/download/nightly/rec-mono-fonts-1.085.src.tar.xz
%define checksum sha256:23024dc85664485bc309fe07b3dc2319a558b7ab7c696c099b16011be6d62bd1
%define fontname rec-mono

%define metainfo %{fontname}.metainfo.xml

Name:          %{fontname}
Version:       %{version}
Release:       %{release}
Packager:      Loi Chyan <loichyan@foxmail.com>
License:       OFL
URL:           https://recursive.design
Summary:       Recursive Mono & Sans is a variable font family for code & UI
BuildArch:     noarch
Requires:      fontpackages-filesystem
BuildRequires: fontpackages-devel
#!RemoteAsset: %{checksum}
Source:        %{source}

%description
Recursive Sans & Mono is a variable type family built for better code & UI. It
is inspired by casual script signpainting, but designed primarily to meet the
needs of programming environments and application interfaces.

%prep
%autosetup -c

%build

%install
install -Dm644 *.ttf -t %{buildroot}%{_fontdir}
install -Dm644 %{metainfo} %{buildroot}%{_datadir}/metainfo/%{metainfo}

%files
%license LICENSE
%doc README.md
%{_fontdir}/*
%{_datadir}/metainfo/%{metainfo}

%changelog
%autochangelog
