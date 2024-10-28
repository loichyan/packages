%define vtag v40.2.0
%define version 40.4.0
%define date 2024-10-28T02:49:07

%define release %autorelease

Name:      myfedora
Version:   %{version}
Release:   %{release}
Packager:  Loi Chyan <loichyan@foxmail.com>
License:   MIT
URL:       https://github.com/loichyan/packages
Summary:   My Fedora setup packages.
BuildArch: noarch
Requires:  alacritty
Requires:  code
Requires:  fira-code-fonts
Requires:  fish
Requires:  google-noto-serif-cjk-vf-fonts
Requires:  kitty
Requires:  nerd-font-symbols
Requires:  nix-mount
Requires:  podman-compose
Requires:  podman-docker
Requires:  rec-mono-fonts
Requires:  snapper
Requires:  wezterm
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
