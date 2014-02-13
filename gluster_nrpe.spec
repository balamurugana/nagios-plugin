#===============================================================================
# Copyright 2014 Red Hat
# Name: gluster-nrpe-plugin.spec 
#-------------------------------------------------------------------------------
# Purpose: RPM Spec file for installing gluster nrpe plugins
# Version 1.00:13 Feb 2014 Created.
#===============================================================================
%define  __spec_install_post %{nil}
%define  debug_package %{nil}
%define __os_install_post %{_dbpath}/brp-compress

%define name      gluster-nrpe
%define summary   gluster-nrpe plugins for nodes
%define version   1.1
%define release   1
%define license   GPLv2+
%define group     Applications/System
%define source    %{name}-%{version}.tar.gz
%define url       http://www.redhat.com
%define buildroot %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

Name:      %{name}
Summary:   %{summary}
Version:   %{version}
Release:   %{release}
License:   %{license}
Group:     %{group}
Source0:   %{source}
BuildArch: noarch
Requires:  filesystem, bash, grep
Provides:  %{name}
URL:       %{url}
Buildroot: %{buildroot}

%description
Gluster nrpe plugins script for monitoring disk, network, cup and memory
details and configure nrpe to work with nagios server.

%prep
%setup -q

%build

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}
cp -a * /usr/lib64/nagios/plugins/

%clean
rm -rf %{buildroot}

%post
if [ $1 == 1 ]; then
cat >> /etc/nagios/nrpe.cfg <<EOF

### gluster nrpe plugins ###
command[check_disk_and_inode]=/usr/lib64/nagios/plugins/check_disk_and_inode.py -w 20 -c 10
command[check_memory]=/usr/lib64/nagios/plugins/check_memory.py -w 70 -c 85
command[check_swap_usage]=/usr/lib64/nagios/plugins/check_swap_usage.py -w 30 -c 15
command[check_cpu_multicore]=/usr/lib64/nagios/plugins/check_cpu_multicore.py -w 80 -c 90
command[check_interfaces]=/usr/lib64/nagios/plugins/sadf.py net
EOF
fi

%files
%defattr(-, root, root, -)


%changelog
* Thu Feb 13 2014 Timothy Asir Jeyasing
- Initial release
