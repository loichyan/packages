%define vtag v40.0.0
%define version 47.0.0
%define date 2024-10-30T14:36:37
%define release %autorelease

Name:      mygnome
Version:   %{version}
Release:   %{release}
Packager:  Loi Chyan <loichyan@foxmail.com>
License:   MIT
URL:       https://github.com/loichyan/packages
Summary:   My Gnome setup packages.
BuildArch: noarch
Requires : ibus
Requires : ibus-typing-booster
Requires : ibus-rime
Requires : librime
Requires : librime-plugin-lua
#Requires : yaru-theme

%description
My Gnome setup packages.

%prep

%build

%install

%files

%changelog
%autochangelog
