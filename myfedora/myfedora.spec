%define vtag v41.2.0
%define version 41.2.0
%define date 2024-11-21T22:01:06

%define release %autorelease

Name:      myfedora
Version:   %{version}
Release:   %{release}
Packager:  Loi Chyan <loichyan@foxmail.com>
License:   MIT
URL:       https://github.com/loichyan/packages
Summary:   My Fedora setup packages.
BuildArch: noarch
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
