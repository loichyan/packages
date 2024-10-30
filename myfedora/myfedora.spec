%define vtag v40.2.0
%define version 41.0.0
%define date 2024-10-30T14:36:27

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
Requires:  fish
Requires:  kitty
Requires:  langpacks-zh_CN
Requires:  nerd-font-symbols
Requires:  nix-mount
Requires:  podman-compose
Requires:  podman-docker
Requires:  snapper
Requires:  wezterm
Requires:  wl-clipboard

%description
My Fedora setup packages.

%prep

%build

%install

%files

%changelog
%autochangelog
