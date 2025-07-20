%define vtag v42.1.0
%define version 42.1.0
%define date 2025-07-20T06:29:18

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
Requires:  foot
Requires:  kitty
Requires:  langpacks-zh_CN
Requires:  nerd-font-symbols
Requires:  podman
Requires:  podman-docker
Requires:  snapper
Requires:  wl-clipboard

%description
My Fedora setup packages.

%prep

%build

%install

%files

%changelog
%autochangelog
