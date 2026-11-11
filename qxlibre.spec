# Qt minor this plugin is built for. QXLibre uses private Qt headers and the
# QPA ABI, so it has to be rebuilt for every qt6-qtbase update. qt_next is
# the first Qt version this build must not be installed with.
%global qt_version 6.12.0
%global qt_next 6.12.1

Name:		qxlibre
Version:	%{qt_version}
Release:	1
Summary:	Qt platform plugin for X11
License:	(LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only) AND BSD-3-Clause
Group:		System/Libraries
URL:		https://github.com/X11Libre/QXLibre
Source0:	%{url}/archive/refs/tags/%{version}.tar.gz#/%{name}-%{version}.tar.gz
# Input-device lifetime fixes from main after the 6.12.0 tag:
# do not delete devices the application registered itself, and do not
# free an XI2 master's slave devices twice.
Patch0:		qxlibre-6.12.0-input-device-lifetime.patch

BuildRequires:	cmake
BuildRequires:	ninja
BuildRequires:	qt6-cmake
BuildRequires:	cmake(Qt6CorePrivate)
BuildRequires:	cmake(Qt6GuiPrivate)
BuildRequires:	pkgconfig(egl)
BuildRequires:	pkgconfig(glx)
BuildRequires:	pkgconfig(glib-2.0)
BuildRequires:	pkgconfig(ice)
BuildRequires:	pkgconfig(opengl)
BuildRequires:	pkgconfig(sm)
BuildRequires:	pkgconfig(vulkan)
BuildRequires:	pkgconfig(x11)
BuildRequires:	pkgconfig(x11-xcb)
BuildRequires:	pkgconfig(xcb)
BuildRequires:	pkgconfig(xcb-cursor)
BuildRequires:	pkgconfig(xcb-glx)
BuildRequires:	pkgconfig(xcb-icccm)
BuildRequires:	pkgconfig(xcb-image)
BuildRequires:	pkgconfig(xcb-keysyms)
BuildRequires:	pkgconfig(xcb-present)
BuildRequires:	pkgconfig(xcb-randr)
BuildRequires:	pkgconfig(xcb-render)
BuildRequires:	pkgconfig(xcb-renderutil)
BuildRequires:	pkgconfig(xcb-shape)
BuildRequires:	pkgconfig(xcb-shm)
BuildRequires:	pkgconfig(xcb-sync)
BuildRequires:	pkgconfig(xcb-util)
BuildRequires:	pkgconfig(xcb-xfixes)
BuildRequires:	pkgconfig(xcb-xinput)
BuildRequires:	pkgconfig(xcb-xkb)
BuildRequires:	pkgconfig(xkbcommon)
BuildRequires:	pkgconfig(xkbcommon-x11)
# Smoke test: the plugin has to open a window on Xvfb and report xcb.
BuildRequires:	qt6-qttools
BuildRequires:	x11-server-xvfb

Requires:	%{mklibname Qt6Core} >= %{qt_version}
Requires:	%{mklibname Qt6Core} < %{qt_next}
Requires:	%{mklibname Qt6Gui} >= %{qt_version}
Requires:	%{mklibname Qt6Gui} < %{qt_next}

%description
QXLibre is a Qt platform plugin for X11, forked from the xcb plugin in
Qt 6.12 and developed for the XLibre X server. It also runs on any other
X server, and it can serve Qt builds that have no X11 support of their own.

The plugin installs beside Qt's own xcb plugin. For an X11 session, select
it with QT_QPA_PLATFORM='xlibre;xcb' (xcb is the fallback when this plugin
is missing or was built for a different Qt). Leave that variable unset in
a Wayland session so Qt applications keep using Wayland.

On stock Qt the plugin loads as xlibre and reports the platform name xcb,
which is what existing applications check for.

%package devel
Summary:	Development files for %{name}
Group:		Development/KDE and Qt
Requires:	%{name} = %{EVRD}
Requires:	qt6-cmake >= %{qt_version}
Requires:	qt6-cmake < %{qt_next}
Requires:	qmake-qt6 >= %{qt_version}
Requires:	qmake-qt6 < %{qt_next}
Requires:	%{mklibname -d Qt6Core} >= %{qt_version}
Requires:	%{mklibname -d Qt6Core} < %{qt_next}
Requires:	%{mklibname -d Qt6Gui} >= %{qt_version}
Requires:	%{mklibname -d Qt6Gui} < %{qt_next}
# The module is already private. Qt's config still names a private
# counterpart, and the cmake dependency generator emits that require
# even though the find_package call never runs. Same as qt6-qtbase.
Provides:	cmake(Qt6XLibreQpaPrivatePrivate) = %{EVRD}

%description devel
Headers, CMake config and qmake files for the QXLibre Qt platform plugin.
The module is private to the plugin.

%prep
%autosetup -n QXLibre-%{version} -p1

%build
%set_build_flags
# Distro LDFLAGS pass --no-undefined. Qt plugins are modules loaded by
# the application, so keep that flag on the shared library only.
module_ldflags=$(printf '%%s\n' "$LDFLAGS" | sed -e 's#-Wl,--no-undefined##g')
%{_qtdir}/bin/qt-cmake -S . -B build -G Ninja \
	-DCMAKE_BUILD_TYPE:STRING=RelWithDebInfo \
	-DCMAKE_INSTALL_PREFIX:PATH=%{_qtdir} \
	-DCMAKE_INSTALL_DO_STRIP:BOOL=OFF \
	-DQT_BUILD_TESTS:BOOL=OFF \
	-DQT_GENERATE_SBOM:BOOL=OFF \
	-DCMAKE_C_FLAGS:STRING="$CFLAGS" \
	-DCMAKE_C_FLAGS_RELEASE:STRING="$CFLAGS -DNDEBUG" \
	-DCMAKE_C_FLAGS_RELWITHDEBINFO:STRING="$CFLAGS" \
	-DCMAKE_CXX_FLAGS:STRING="$CXXFLAGS" \
	-DCMAKE_CXX_FLAGS_RELEASE:STRING="$CXXFLAGS -DNDEBUG" \
	-DCMAKE_CXX_FLAGS_RELWITHDEBINFO:STRING="$CXXFLAGS" \
	-DCMAKE_EXE_LINKER_FLAGS:STRING="$LDFLAGS" \
	-DCMAKE_SHARED_LINKER_FLAGS:STRING="$LDFLAGS" \
	-DCMAKE_MODULE_LINKER_FLAGS:STRING="$module_ldflags"
%{__cmake} --build build

%install
DESTDIR=%{buildroot} %{__cmake} --install build

%check
xvfb-run -a env -u WAYLAND_DISPLAY \
	QT_QPA_PLATFORM=xlibre \
	QT_PLUGIN_PATH="%{buildroot}%{_qtdir}/plugins" \
	qtdiag6 > qxlibre-qtdiag.txt
grep -q ' on "xcb" ' qxlibre-qtdiag.txt

%files
%license LICENSES/BSD-3-Clause.txt
%license LICENSES/GPL-2.0-only.txt
%license LICENSES/GPL-3.0-only.txt
%license LICENSES/LGPL-3.0-only.txt
%license LICENSES/LicenseRef-Qt-Commercial.txt
%doc README.md RELEASE-NOTES.md
%{_qtdir}/lib/libQt6XLibreQpa.so.*
%{_qtdir}/plugins/platforms/libqxlibre.so
%dir %{_qtdir}/plugins/xlibreglintegrations
%{_qtdir}/plugins/xlibreglintegrations/libqxlibre-egl-integration.so
%{_qtdir}/plugins/xlibreglintegrations/libqxlibre-glx-integration.so

%files devel
%{_qtdir}/lib/libQt6XLibreQpa.so
%{_qtdir}/lib/libQt6XLibreQpa.prl
%{_qtdir}/lib/cmake/Qt6XLibreQpaPrivate/
%{_qtdir}/lib/cmake/Qt6Gui/Qt6QXLibre*
%{_qtdir}/lib/cmake/Qt6BuildInternals/StandaloneTests/QXLibreTestsConfig.cmake
%{_qtdir}/mkspecs/modules/qt_lib_xlibre_qpa_lib_private.pri
%{_qtdir}/metatypes/qt6xlibreqpaprivate_metatypes.json
%{_qtdir}/modules/XLibreQpaPrivate.json
