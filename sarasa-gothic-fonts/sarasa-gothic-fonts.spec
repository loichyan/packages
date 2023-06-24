%global vtag v0.41.2
%global fontname sarasa-gothic

Name:          %{fontname}-fonts
Version:       %(sed 's/^v\(.\+\)$/\1/' <<< %{vtag})
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

%build

%install
install -Dm644 *.ttc -t %{buildroot}%{_fontdir}
install -Dm644 %{SOURCE1} -t %{buildroot}%{_defaultlicensedir}/%{name}
install -Dm644 %{SOURCE2} -t %{buildroot}%{_defaultdocdir}/%{name}
install -Dm644 %{SOURCE2} %{buildroot}%{_datadir}/metainfo/%{name}.metainfo.xml

%files
%doc README.md
%license LICENSE
%{_fontdir}/*
%{_datadir}/metainfo/%{name}.metainfo.xml

%changelog
%autochangelog
