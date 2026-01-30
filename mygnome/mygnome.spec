%define vtag v49.0.0
%define version 49.0.0
%define date 2026-01-30T09:14:52
%define release %autorelease

Name:      mygnome
Version:   %{version}
Release:   %{release}
Packager:  Loi Chyan <loichyan@outlook.com>
License:   MIT
URL:       https://github.com/loichyan/packages
Summary:   My Gnome setup packages.
BuildArch: noarch
Requires:  gnome-tweaks
Requires:  ibus
Requires:  ibus-rime
Requires:  ibus-typing-booster
Requires:  librime
Requires:  librime-lua

%description
My Gnome setup packages.

%prep

%build

%install

%files

%changelog
%autochangelog
