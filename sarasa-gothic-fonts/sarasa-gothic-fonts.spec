%define vtag v0.41.3
%define version 0.41.3
%define fontname sarasa-gothic

Name:          %{fontname}-fonts
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
Source0:       %{url}/releases/download/%{vtag}/%{fontname}-ttc-%{version}.7z
Source1:       https://raw.githubusercontent.com/be5invis/Sarasa-Gothic/%{vtag}/LICENSE
Source2:       https://raw.githubusercontent.com/be5invis/Sarasa-Gothic/%{vtag}/README.md
Source3:       %{name}.metainfo.xml

%description
A CJK programming font based on Iosevka and Source Han Sans.

%prep
%autosetup -c
cp %{SOURCE1} .
cp %{SOURCE2} .

%build

%install
install -Dm644 *.ttc -t %{buildroot}%{_fontdir}
install -Dm644 %{SOURCE3} %{buildroot}%{_datadir}/metainfo/%{name}.metainfo.xml

%files
%license LICENSE
%doc README.md
%{_fontdir}/*
%{_datadir}/metainfo/%{name}.metainfo.xml

%changelog
