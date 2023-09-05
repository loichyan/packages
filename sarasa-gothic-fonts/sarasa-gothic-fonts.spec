%define vtag v0.41.9
%define version 0.41.9
%define date 2023-09-04T13:09:59
%define release %autorelease
%define source https://github.com/loichyan/packages/releases/download/nightly/sarasa-gothic-fonts-0.41.9.src.tar.xz
%define checksum sha256:7e3df8959161b0541da8c5b49dcc620e95fb5c939121216b96c835ca9f848e44
%define fontname sarasa-gothic

%define fontname sarasa-gothic
%define metainfo %{fontname}.metainfo.xml

Name:          %{fontname}-fonts
Version:       %{version}
Release:       %{release}
Packager:      Loi Chyan <loichyan@foxmail.com>
License:       OFL-1.1
URL:           https://github.com/be5invis/Sarasa-Gothic
Summary:       Sarasa Gothic / 更纱黑体 / 更紗黑體 / 更紗ゴシック / 사라사 고딕
BuildArch:     noarch
Requires:      fontpackages-filesystem
BuildRequires: p7zip
BuildRequires: fontpackages-devel
#!RemoteAsset: %{checksum}
Source:        %{source}

%description
A CJK programming font based on Iosevka and Source Han Sans.

%prep
%autosetup -c

%build

%install
install -Dm644 *.ttc -t %{buildroot}%{_fontdir}
install -Dm644 %{metainfo} %{buildroot}%{_datadir}/metainfo/%{metainfo}

%files
%license LICENSE
%doc README.md
%{_fontdir}/*
%{_datadir}/metainfo/%{metainfo}

%changelog
%autochangelog
