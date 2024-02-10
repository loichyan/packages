%define vtag v39.0.0
%define version 39.0.0
%define date 2023-11-08T02:24:17.569
%define release %autorelease

Name:      mygnome
Version:   %{version}
Release:   %{release}
Packager:  Loi Chyan <loichyan@foxmail.com>
License:   MIT
URL:       https://github.com/loichyan/packages
Summary:   My Gnome setup packages.
BuildArch: noarch
# Gnome desktop
# Adapt from https://pagure.io/fedora-comps/blob/main/f/comps-f39.xml.in
# type=mandatory
Requires : dconf
Requires : gdm
Requires : gnome-boxes
Requires : gnome-connections
Requires : gnome-control-center
Requires : gnome-initial-setup
Requires : gnome-session-wayland-session
Requires : gnome-session-xsession
Requires : gnome-settings-daemon
Requires : gnome-shell
Requires : gnome-software
Requires : gnome-terminal
Requires : gnome-text-editor
Requires : nautilus
Requires : polkit
Requires : yelp
# type=default
Requires : adobe-source-code-pro-fonts
Requires : at-spi2-atk
Requires : at-spi2-core
Requires : avahi
Requires : baobab
#Requires : cheese
Requires : snapshot
Requires : evince
Requires : evince-djvu
#Requires : evince-nautilus
Requires : fprintd-pam
Requires : glib-networking
Requires : gnome-backgrounds
Requires : gnome-bluetooth
Requires : gnome-browser-connector
Requires : gnome-calculator
Requires : gnome-calendar
Requires : gnome-characters
Requires : gnome-classic-session
Requires : gnome-clocks
Requires : gnome-color-manager
Requires : gnome-contacts
Requires : gnome-disk-utility
Requires : gnome-font-viewer
Requires : gnome-logs
Requires : gnome-maps
Requires : gnome-remote-desktop
Requires : gnome-system-monitor
Requires : gnome-terminal-nautilus
Requires : gnome-user-docs
Requires : gnome-user-share
Requires : gnome-weather
Requires : gvfs-afc
Requires : gvfs-afp
Requires : gvfs-archive
Requires : gvfs-fuse
Requires : gvfs-goa
Requires : gvfs-gphoto2
Requires : gvfs-mtp
Requires : gvfs-smb
Requires : librsvg2
Requires : libsane-hpaio
Requires : loupe
Requires : mesa-dri-drivers
Requires : mesa-libEGL
Requires : ModemManager
Requires : NetworkManager-adsl
Requires : NetworkManager-openconnect-gnome
Requires : NetworkManager-openvpn-gnome
Requires : NetworkManager-ppp
Requires : NetworkManager-pptp-gnome
Requires : NetworkManager-ssh-gnome
Requires : NetworkManager-vpnc-gnome
Requires : NetworkManager-wwan
Requires : orca
#Requires : PackageKit-command-not-found
#Requires : PackageKit-gtk3-module
Requires : rygel
Requires : sane-backends-drivers-scanners
Requires : simple-scan
Requires : sushi
Requires : systemd-oomd-defaults
Requires : totem
Requires : tracker
Requires : tracker-miners
Requires : xdg-desktop-portal
Requires : xdg-desktop-portal-gnome
Requires : xdg-desktop-portal-gtk
Requires : xdg-user-dirs-gtk
# Extensions
Requires : gnome-extensions-app
Requires : gnome-shell-extension-appindicator
Requires : gnome-shell-extension-user-theme
# Misc
Requires : gnome-tweaks
Requires : ibus
Requires : ibus-typing-booster
Requires : ibus-rime
Requires : librime
Requires : librime-plugin-lua
Requires : yaru-theme

%description
My Gnome setup packages.

%prep

%build

%install

%files

%changelog
%autochangelog
