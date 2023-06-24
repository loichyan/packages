%global vtag v3.0.2
%global fontname symbols-nerd-fonts
%global fontconf 10-symbols-nerd-fonts.conf

Name:          %{fontname}
Version:       %(sed 's/^v\(.\+\)$/\1/' <<< %{vtag})
Release:       %autorelease -b 2
Packager:      Loi Chyan <loichyan@foxmail.com>
License:       MIT AND OFL
URL:           https://www.nerdfonts.com
Summary:       Just the Nerd Font Icons. I.e Symbol font only.
BuildArch:     noarch
Requires:      fontpackages-filesystem
BuildRequires: fontpackages-devel
Source0:       https://github.com/ryanoasis/nerd-fonts/releases/download/%{vtag}/NerdFontsSymbolsOnly.zip
Source1:       https://raw.githubusercontent.com/ryanoasis/nerd-fonts/%{vtag}/10-nerd-font-symbols.conf
Source2:       https://raw.githubusercontent.com/ryanoasis/nerd-fonts/%{vtag}/LICENSE
Source3:       https://raw.githubusercontent.com/ryanoasis/nerd-fonts/%{vtag}/readme.md
Source4:       %{name}.metainfo.xml

%description
Nerd Fonts is a project that patches developer targeted fonts with a high number
of glyphs (icons). Specifically to add a high number of extra glyphs from popular
'iconic fonts' such as Font Awesome, Devicons, Octicons, and others.

%files
%license LICENSE
%doc readme.md
%{_fontdir}/*
%{_fontconfig_templatedir}/%{fontconf}
%{_fontconfig_confdir}/%{fontconf}
%{_datadir}/metainfo/%{name}.metainfo.xml

%prep
cp %{SOURCE2} .
cp %{SOURCE3} .
%autosetup -c

%build

%install
rm -f *Windows\ Compatible.ttf
install -Dm644 *.ttf -t %{buildroot}%{_fontdir}
install -Dm644 %{SOURCE1} %{buildroot}%{_fontconfig_templatedir}/%{fontconf}
install -dm755 %{buildroot}%{_fontconfig_confdir}
ln -s %{_fontconfig_templatedir}/%{fontconf} %{buildroot}%{_fontconfig_confdir}/%{fontconf}
install -Dm644 %{SOURCE4} %{buildroot}%{_datadir}/metainfo/%{name}.metainfo.xml

%changelog
%autochangelog
