%define vtag v0.41.3
%define version 0.41.3
%define repo be5invis/Sarasa-Gothic
%define fontname sarasa-gothic
%define metainfo %{fontname}.metainfo.xml

Name:          %{fontname}-fonts
Version:       %{version}
Release:       %autorelease
Packager:      Loi Chyan <loichyan@foxmail.com>
License:       OFL-1.1
URL:           https://github.com/%{repo}
Summary:       Sarasa Gothic / 更纱黑体 / 更紗黑體 / 更紗ゴシック / 사라사 고딕
BuildArch:     noarch
Requires:      fontpackages-filesystem
BuildRequires: p7zip
BuildRequires: fontpackages-devel
#!RemoteAsset
Source0:       https://github.com/%{repo}/releases/download/%{vtag}/%{fontname}-ttc-%{version}.7z
#!RemoteAsset
Source1:       https://raw.githubusercontent.com/%{repo}/%{vtag}/LICENSE
#!RemoteAsset
Source2:       https://raw.githubusercontent.com/%{repo}/%{vtag}/README.md
Source3:       %{metainfo}

%description
A CJK programming font based on Iosevka and Source Han Sans.

%prep
%autosetup -c
cp %{SOURCE1} LICENSE
cp %{SOURCE2} README.md

%build

%install
install -Dm644 *.ttc -t %{buildroot}%{_fontdir}
install -Dm644 %{SOURCE3} %{buildroot}%{_datadir}/metainfo/%{metainfo}

%files
%license LICENSE
%doc README.md
%{_fontdir}/*
%{_datadir}/metainfo/%{metainfo}

%changelog
