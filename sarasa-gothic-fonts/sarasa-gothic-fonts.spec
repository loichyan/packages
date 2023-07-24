%define vtag v0.41.3
%define version 0.41.3
%define fontname sarasa-gothic-fonts
%define metainfo %{fontname}.metainfo.xml

Name:          %{fontname}
Version:       %{version}
Release:       %autorelease
Packager:      Loi Chyan <loichyan@foxmail.com>
License:       OFL-1.1
URL:           https://github.com/be5invis/Sarasa-Gothic
Summary:       Sarasa Gothic / 更纱黑体 / 更紗黑體 / 更紗ゴシック / 사라사 고딕
BuildArch:     noarch
Requires:      fontpackages-filesystem
BuildRequires: p7zip
BuildRequires: fontpackages-devel
Source0:       sarasa-gothic-ttc-%{version}.7z
Source1:       LICENSE
Source2:       README.md
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
%autochangelog
