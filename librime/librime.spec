%define vtag 1.13.1
%define version 1.13.1
%define lua_plugin_vtag e3912a4b3ac2c202d89face3fef3d41eb1d7fcd6
%define date 2025-02-16T10:41:02
%define release %autorelease
%define source https://github.com/loichyan/packages/releases/download/nightly/librime-1.13.1.src.tar.xz
%define checksum sha256:ae15af09415725211772d76ace083e131ab9d82107de66c5c9bc7dc00bb24441

# Adapt from https://src.fedoraproject.org/rpms/librime/blob/rawhide/f/librime.spec
Name:          librime
Version:       %{version}
Release:       %{release}
License:       GPL-3.0-only
URL:           https://rime.im/
Summary:       Rime Input Method Engine Library
BuildRequires: gcc-c++
BuildRequires: cmake
BuildRequires: boost-devel
BuildRequires: glog-devel
BuildRequires: leveldb-devel
BuildRequires: marisa-devel
BuildRequires: opencc-devel
BuildRequires: yaml-cpp-devel
BuildRequires: gtest-devel
BuildRequires: luajit-devel
#!RemoteAsset: %{checksum}
Source:        %{source}

%description
Rime Input Method Engine Library

Support for shape-based and phonetic-based input methods,
including those for Chinese dialects.

A selected dictionary in Traditional Chinese,
powered by opencc for Simplified Chinese output.

%package     devel
Summary:     Development files for %{name}
Requires:    %{name} = %{version}-%{release}

%description devel
The %{name}-devel package contains libraries and header files for
developing applications that use %{name}.

%package     tools
Summary:     Tools for %{name}
Requires:    %{name} = %{version}-%{release}

%description tools
The %{name}-tools package contains tools for %{name}.

%package     plugin-lua
License:     BSD-3-clause
URL:           https://rime.im/
Summary:     Extending RIME with Lua scripts
Requires:    %{name} = %{version}-%{release}

%description plugin-lua
Extending RIME with Lua scripts

Supports extending RIME processors, segmentors, translators and filters
Provides high-level programming model for translators and filters

Loaded dynamically as a librime plugin

%prep
%autosetup -c

%build
%cmake -DCMAKE_BUILD_TYPE=Release -DBUILD_MERGED_PLUGINS=OFF -DENABLE_EXTERNAL_PLUGINS=ON
%cmake_build

%install
%cmake_install
%ldconfig_scriptlets

%files
%doc README.md
%license LICENSE
%{_libdir}/*.so.*

%files devel
%doc README.md
%license LICENSE
%{_includedir}/*
%{_libdir}/*.so
%{_libdir}/pkgconfig/rime.pc
%dir %{_datadir}/cmake/rime
%{_datadir}/cmake/rime/RimeConfig.cmake

%files tools
%license LICENSE
%{_bindir}/rime_deployer
%{_bindir}/rime_dict_manager
%{_bindir}/rime_patch
%{_bindir}/rime_table_decompiler

%files plugin-lua
%doc plugins/librime-lua/README.md
%license plugins/librime-lua/LICENSE
%{_libdir}/rime-plugins/librime-lua.so

%changelog
%autochangelog
