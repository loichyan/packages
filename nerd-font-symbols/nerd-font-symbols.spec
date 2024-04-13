%define vtag v3.2.1
%define version 3.2.1
%define date 2024-04-12T14:41:15
%define release %autorelease
%define source https://github.com/loichyan/packages/releases/download/nightly/nerd-font-symbols-3.2.1.src.tar.xz
%define checksum sha256:e6cf27e65b3878d4a92ca6ea5d57982371bba92684b1e85aea7f6cdb4f6333fe
%define fontname nerd-font-symbols

%define fontname nerd-font-symbols
%define metainfo %{fontname}.metainfo.xml
%define fontconf 10-%{fontname}.conf

Name:          %{fontname}
Version:       %{version}
Release:       %{release}
Packager:      Loi Chyan <loichyan@foxmail.com>
License:       MIT AND OFL
URL:           https://www.nerdfonts.com/
Summary:       Just the Nerd Font Icons. I.e Symbol font only.
BuildArch:     noarch
Requires:      fontpackages-filesystem
BuildRequires: fontpackages-devel
#!RemoteAsset: %{checksum}
Source:        %{source}

%description
Nerd Fonts is a project that patches developer targeted fonts with a high number
of glyphs (icons). Specifically to add a high number of extra glyphs from popular
'iconic fonts' such as Font Awesome, Devicons, Octicons, and others.

%prep
%autosetup -c

%build

%install
install -Dm644 *.ttf -t %{buildroot}%{_fontdir}
install -Dm644 %{fontconf} %{buildroot}%{_fontconfig_templatedir}/%{fontconf}
install -dm755 %{buildroot}%{_fontconfig_confdir}
ln -s %{_fontconfig_templatedir}/%{fontconf} %{buildroot}%{_fontconfig_confdir}/%{fontconf}
install -Dm644 %{metainfo} %{buildroot}%{_datadir}/metainfo/%{metainfo}

%files
%license LICENSE
%doc README.md
%{_fontdir}/*
%{_fontconfig_templatedir}/%{fontconf}
%{_fontconfig_confdir}/%{fontconf}
%{_datadir}/metainfo/%{metainfo}

%changelog
%autochangelog
