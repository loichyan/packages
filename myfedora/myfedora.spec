%define vtag v42.0.0
%define version 42.0.0
%define date 2025-05-12T08:39:07

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
