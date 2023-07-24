# {{ METADATA BEGIN
%define name nerd-font-symbols
%define vtag v3.0.2
%define version 3.0.2
%define repo ryanoasis/nerd-fonts
# METADATA END }}
%define fontname nerd-font-symbols
%define fontconf 10-%{fontname}.conf
%define metainfo %{fontname}.metainfo.xml

Name:          %{name}
Version:       %{version}
Release:       %autorelease
Packager:      Loi Chyan <loichyan@foxmail.com>
License:       MIT AND OFL
URL:           https://github.com/%{repo}
Summary:       Just the Nerd Font Icons. I.e Symbol font only.
BuildArch:     noarch
Requires:      fontpackages-filesystem
BuildRequires: fontpackages-devel
#!RemoteAsset
Source0:       https://github.com/%{repo}/releases/download/%{vtag}/NerdFontsSymbolsOnly.zip
#!RemoteAsset
Source1:       https://raw.githubusercontent.com/%{repo}/%{vtag}/LICENSE
#!RemoteAsset
Source2:       https://raw.githubusercontent.com/%{repo}/%{vtag}/readme.md
#!RemoteAsset
Source3:       https://raw.githubusercontent.com/%{repo}/%{vtag}/%{fontconf}
Source4:       %{metainfo}

%description
Nerd Fonts is a project that patches developer targeted fonts with a high number
of glyphs (icons). Specifically to add a high number of extra glyphs from popular
'iconic fonts' such as Font Awesome, Devicons, Octicons, and others.

%prep
%autosetup -c
cp %{SOURCE1} LICENSE
cp %{SOURCE2} README.md

%build

%install
rm -f *Windows\ Compatible.ttf
install -Dm644 *.ttf -t %{buildroot}%{_fontdir}
install -Dm644 %{SOURCE3} %{buildroot}%{_fontconfig_templatedir}/%{fontconf}
install -dm755 %{buildroot}%{_fontconfig_confdir}
ln -s %{_fontconfig_templatedir}/%{fontconf} %{buildroot}%{_fontconfig_confdir}/%{fontconf}
install -Dm644 %{SOURCE4} %{buildroot}%{_datadir}/metainfo/%{metainfo}

%files
%license LICENSE
%doc README.md
%{_fontdir}/*
%{_fontconfig_templatedir}/%{fontconf}
%{_fontconfig_confdir}/%{fontconf}
%{_datadir}/metainfo/%{metainfo}

%changelog
%autochangelog
