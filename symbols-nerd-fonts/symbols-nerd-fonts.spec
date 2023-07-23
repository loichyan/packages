%define vtag v3.0.2
%define version 3.0.2
%define fontname symbols-nerd-fonts
%define fontconf 10-%{fontname}.conf
%define metainfo %{fontname}.metainfo.xml

Name:          %{fontname}
Version:       %{version}
Release:       %autorelease -b 3
Packager:      Loi Chyan <loichyan@foxmail.com>
License:       MIT AND OFL
URL:           https://www.nerdfonts.com
Summary:       Just the Nerd Font Icons. I.e Symbol font only.
BuildArch:     noarch
Requires:      fontpackages-filesystem
BuildRequires: fontpackages-devel
Source:        %{name}-%{vtag}-source.tar.gz

%description
Nerd Fonts is a project that patches developer targeted fonts with a high number
of glyphs (icons). Specifically to add a high number of extra glyphs from popular
'iconic fonts' such as Font Awesome, Devicons, Octicons, and others.

%prep
%autosetup -c

%build

%install
rm -f fonts/*"Windows Compatible.ttf"
install -Dm644 fonts/*.ttf -t %{buildroot}%{_fontdir}
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
