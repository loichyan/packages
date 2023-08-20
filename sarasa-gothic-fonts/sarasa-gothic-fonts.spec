%define vtag v0.41.7
%define version 0.41.7
%define date 2023-08-19T14:06:05
%define release %autorelease
%define source https://github.com/loichyan/packages/releases/download/nightly/sarasa-gothic-fonts-0.41.7-source.tar.xz
%define checksum sha256:80c13ccb74b26f10f2f2e9245b7f3ac47e6e4ee834cc51d5ef73d89e12afe908
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
