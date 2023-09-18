%define vtag 1.9.0
%define version 1.9.0
%define lua_plugin_vtag 399b680793e4c0adf3a18422b7e3d452018aea06
%define date 2023-09-18T09:07:48.412
%define release %autorelease -n 2
%define source https://github.com/loichyan/packages/releases/download/nightly/librime-1.9.0.src.tar.xz
%define checksum sha256:a61aa048e84a557c2c3bf1565b3de8e8a51121c9a1b8efbc676ab2f34ac0265f

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
%cmake -DCMAKE_BUILD_TYPE=Release -DBUILD_MERGED_PLUGINS=Off -DENABLE_EXTERNAL_PLUGINS=On
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
