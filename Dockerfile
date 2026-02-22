FROM gentoo/portage:20260222 AS portage
LABEL authors="mplic"

FROM gentoo/stage3:nomultilib-20260216

COPY --from=portage /var/db/repos/gentoo /var/db/repos/gentoo

COPY assets/make.conf /etc/portage/make.conf

RUN emerge --sync
RUN emerge -qv1 sys-apps/portage
RUN emerge -qv app-eselect/eselect-repository \
    dev-util/pkgdev \
    app-editors/vim
RUN eselect repository create emc
RUN mkdir -p /var/db/repos/emc/app-portage/pyerge
COPY assets/pyerge-0.7.2.ebuild /var/db/repos/emc/app-portage/pyerge
COPY assets/metadata.xml /var/db/repos/emc/app-portage/pyerge
RUN chown -R portage:portage /var/db/repos/emc
RUN cp /usr/share/portage/config/repos.conf /etc/portage/repos.conf/gentoo.conf
WORKDIR /var/db/repos/emc/app-portage/pyerge
RUN sed -i 's/\r$//' pyerge-0.7.2.ebuild
RUN pkgdev manifest
RUN pkgcheck scan
