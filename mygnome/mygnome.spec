%define vtag v47.1.0
%define version 47.1.0
%define date 2024-11-25T10:47:03
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
# NOTE: Gnome Boxes is not available on Fedora's flatpak repository
Requires : gnome-boxes

%description
My Gnome setup packages.

%prep

%build

%install

%files

%changelog
%autochangelog
