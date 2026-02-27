FROM gentoo/portage:20260227 AS portage
LABEL authors="mplic"

FROM gentoo/stage3:nomultilib-20260223

COPY --from=portage /var/db/repos/gentoo /var/db/repos/gentoo

COPY assets/make.conf /etc/portage/make.conf

RUN emerge --sync
RUN emerge -qv1 sys-apps/portage
RUN emerge -qv app-eselect/eselect-repository \
    dev-util/pkgdev \
    app-editors/vim \
    app-text/dos2unix
RUN eselect repository create emc
RUN mkdir -p /var/db/repos/emc/app-portage/pyerge
COPY assets/*.ebuild /var/db/repos/emc/app-portage/pyerge
COPY assets/metadata.xml /var/db/repos/emc/app-portage/pyerge
RUN chown -R portage:portage /var/db/repos/emc
RUN chmod -x /var/db/repos/emc/app-portage/pyerge/*
RUN cp /usr/share/portage/config/repos.conf /etc/portage/repos.conf/gentoo.conf
WORKDIR /var/db/repos/emc/app-portage/pyerge
RUN dos2unix ./pyerge-*.ebuild
RUN sed -i 's/    /\t/g' ./pyerge-*.ebuild
COPY dist/*.tar.gz /var/cache/distfiles/
RUN pkgdev manifest
RUN pkgcheck scan
