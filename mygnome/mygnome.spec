%define vtag v48.0.0
%define version 48.0.0
%define date 2025-05-12T08:40:31
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
Requires : librime-lua

%description
My Gnome setup packages.

%prep

%build

%install

%files

%changelog
%autochangelog
