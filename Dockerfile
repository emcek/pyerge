FROM gentoo/portage:20260312 AS portage
LABEL authors="mplic"

FROM gentoo/stage3:nomultilib-20260309

COPY --from=portage /var/db/repos/gentoo /var/db/repos/gentoo

COPY assets/make.conf /etc/portage/make.conf

#RUN emerge --sync
VOLUME /var/cache/distfiles
COPY distfiles/* /var/cache/distfiles/
RUN emerge -qv1 sys-apps/portage
RUN emerge -qv app-eselect/eselect-repository \
    dev-util/pkgdev \
    app-editors/vim \
    app-text/dos2unix \
    app-portage/eix \
    app-portage/genlop \
    app-portage/smart-live-rebuild \
    app-admin/sudo \
    dev-python/uv
RUN sudo eselect editor set vim && eselect repository create emc
RUN mkdir -p /var/db/repos/emc/app-portage/pyerge
COPY assets/*.ebuild /var/db/repos/emc/app-portage/pyerge/
COPY assets/metadata.xml /var/db/repos/emc/app-portage/pyerge/
RUN chown -R portage:portage /var/db/repos/emc && chmod -x /var/db/repos/emc/app-portage/pyerge/*
RUN cp /usr/share/portage/config/repos.conf /etc/portage/repos.conf/gentoo.conf
WORKDIR /var/db/repos/emc/app-portage/pyerge
RUN dos2unix ./pyerge-*.ebuild && sed -i 's/ \{4\}/\t/g' ./pyerge-*.ebuild
RUN echo '' >> pyerge-0.7.2.ebuild && echo '' >> pyerge-0.8.0.ebuild
RUN pkgdev manifest && pkgcheck scan
RUN groupadd --gid 10001 emcgroup \
 && useradd  --uid 10000 \
             --gid emcgroup \
             --create-home \
             --shell /bin/bash \
             --home-dir /home/emc \
             emc
RUN echo 'emc ALL=(ALL) NOPASSWD: ALL' >> /etc/sudoers
USER emc:emcgroup
ENV HOME=/home/emc
RUN mkdir -p /home/emc/pyerge
WORKDIR /home/emc/pyerge/
COPY --chown=emc:emcgroup . .
RUN uv sync -p 3.14 --no-group dev --extra test --frozen --no-install-project
