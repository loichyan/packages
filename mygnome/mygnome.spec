%define vtag v0.1.0
%define version 0.1.0
%define date 2023-08-24T10:49:00.000
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
# Adapt from https://pagure.io/fedora-comps/blob/main/f/comps-f38.xml.in
# Mandatory
Requires : dconf
Requires : gdm
#Requires : gnome-boxes
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
# Default
Requires : adobe-source-code-pro-fonts
Requires : at-spi2-atk
Requires : at-spi2-core
Requires : avahi
Requires : baobab
Requires : cheese
Requires : eog
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
Requires : gnome-photos
Requires : gnome-remote-desktop
Requires : gnome-system-monitor
Requires : gnome-terminal-nautilus
Requires : gnome-themes-extra
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
Requires : libproxy-duktape
Requires : librsvg2
Requires : libsane-hpaio
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
Requires : gnome-shell-extension-appindicator
Requires : gnome-shell-extension-pop-shell
Requires : gnome-shell-extension-pop-shell-shortcut-overrides
Requires : gnome-shell-extension-user-theme
# Misc
Requires : gnome-tweaks
Requires : ibus
Requires : ibus-typing-booster
Requires : ibus-rime
Requires : librime
Requires : librime-plugin-lua
Requires : pop-launcher
Requires : yaru-theme

%description
My Gnome setup packages.

%prep

%build

%install

%files

%changelog
%autochangelog
