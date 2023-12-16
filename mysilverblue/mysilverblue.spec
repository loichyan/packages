%define vtag v0.3.0
%define version 0.3.0
%define date 2023-12-16T05:44:58.268
%define release %autorelease

Name:      mysilverblue
Version:   %{version}
Release:   %{release}
Packager:  Loi Chyan <loichyan@foxmail.com>
License:   MIT
URL:       https://github.com/loichyan/packages
Summary:   My Silverblue setup packages.
BuildArch: noarch
Requires:  cascadia-code-fonts
Requires:  fira-code-fonts
Requires:  code
Requires:  fish
Requires:  geary
Requires:  google-chrome-stable
Requires:  google-noto-serif-cjk-vf-fonts
Requires:  mozilla-openh264
Requires:  nerd-font-symbols
Requires:  nix-mount
Requires:  podman-compose
Requires:  podman-docker
Requires:  wezterm
Requires:  wl-clipboard
# Requires:  mygnome
# Requires:  v2raya
# Requires:  xray

%description
My Silverblue setup packages.

%prep

%build

%install

%files

%changelog
%autochangelog
