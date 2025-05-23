%define vtag v3.4.0
%define version 3.4.0
%define date 2025-04-24T16:34:56
%define release %autorelease
%define source https://github.com/loichyan/packages/releases/download/nightly/nerd-font-symbols-3.4.0.src.tar.xz
%define checksum sha256:06fe8460108e6477f9bdb9f10415edcfa20159d2c4cd799e8d57295a3904d46e
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
