%define vtag v1.0.5
%define version 1.0.5
%define date 2024-01-27T13:20:33
%define release %autorelease
%define source https://github.com/loichyan/packages/releases/download/nightly/sarasa-gothic-fonts-1.0.5.src.tar.xz
%define checksum sha256:312d482f53a5005742834bb515b038265497a90dae9dceb5b82795732cc70c84
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
