%define vtag v40.0.0
%define version 40.0.0
%define date 2024-04-27T06:54:31.586

%define release %autorelease

Name:      myfedora
Version:   %{version}
Release:   %{release}
Packager:  Loi Chyan <loichyan@foxmail.com>
License:   MIT
URL:       https://github.com/loichyan/packages
Summary:   My Fedora setup packages.
BuildArch: noarch
Requires:  fira-code-fonts
Requires:  code
Requires:  fish
Requires:  google-noto-serif-cjk-vf-fonts
Requires:  kitty
Requires:  mozilla-openh264
Requires:  nerd-font-symbols
Requires:  nix-mount
Requires:  podman-compose
Requires:  podman-docker
Requires:  rec-mono-fonts
Requires:  snapper
Requires:  wl-clipboard
#Requires:  v2raya
#Requires:  xray

%description
My Fedora setup packages.

%prep

%build

%install

%files

%changelog
%autochangelog
