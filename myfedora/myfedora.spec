%define vtag v43.0.0
%define version 43.0.0
%define date 2026-01-30T08:41:57

%define release %autorelease

Name:      myfedora
Version:   %{version}
Release:   %{release}
Packager:  Loi Chyan <loichyan@outlook.com>
License:   MIT
URL:       https://github.com/loichyan/packages
Summary:   My Fedora setup packages.
BuildArch: noarch
Requires:  alacritty
Requires:  default-fonts-cjk
Requires:  fish
Requires:  foot
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
