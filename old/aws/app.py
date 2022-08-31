#!/usr/bin/env python3
from typing import Optional

from aws_cdk import core

import website


class WebsiteService(core.Construct):
    def __init__(
        self,
        scope: core.Construct,
        id: str,
        *,
        domain_name: Optional[str] = None,
        prod: bool = False,
        site_env: Optional[core.Environment] = None,
        cert_env: Optional[core.Environment] = None,
    ):
        super().__init__(scope, id)

        stack_prefix = f"rileychase-net-{id}"

        self.dns = None
        self.cert = None
        if domain_name:
            self.dns = website.DnsStack(
                self, f"{stack_prefix}-dns", domain_name=domain_name, env=cert_env
            )
            self.cert = website.CertificateStack(
                self,
                f"{stack_prefix}-cert",
                env=cert_env,
                hosted_zone=self.dns.hosted_zone,
                domain_name=domain_name,
                alternate_names=[f"*.{domain_name}"],
            )

        self.site = website.WebsiteStack(app, f"{stack_prefix}-website", env=site_env)


env_dev = core.Environment(account="184932712216", region="ap-southeast-2")
env_dev_cert = core.Environment(account="184932712216", region="us-east-1")


app = core.App()
dev_site = WebsiteService(
    app, "dev", domain_name="rileychase.dev", site_env=env_dev, cert_env=env_dev_cert
)

app.synth()
