%define vtag v39.1.0
%define version 39.1.0
%define date 2024-03-13T23:15:19.980
%define release %autorelease

Name:      mysilverblue
Version:   %{version}
Release:   %{release}
Packager:  Loi Chyan <loichyan@foxmail.com>
License:   MIT
URL:       https://github.com/loichyan/packages
Summary:   My Silverblue setup packages.
BuildArch: noarch
Requires:  fira-code-fonts
Requires:  code
Requires:  fish
Requires:  google-noto-serif-cjk-vf-fonts
Requires:  mozilla-openh264
Requires:  nerd-font-symbols
Requires:  nix-mount
Requires:  podman-compose
Requires:  podman-docker
Requires:  rec-mono-fonts
Requires:  snapper
Requires:  wezterm
Requires:  wl-clipboard
#Requires:  mygnome
#Requires:  v2raya
#Requires:  xray

%description
My Silverblue setup packages.

%prep

%build

%install

%files

%changelog
%autochangelog
