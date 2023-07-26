%define vtag v0.41.3
%define version 0.41.3
%define release %autorelease
%define source https://github.com/loichyan/packages/releases/download/nightly/sarasa-gothic-fonts-0.41.3.tar.xz
%define checksum ded525b7919533c698b43f3ddb2cd573fd5e09b621b704c3ab114e6984f55558

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
