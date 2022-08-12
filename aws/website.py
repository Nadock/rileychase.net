import pathlib
from typing import List, Optional

from aws_cdk import (
    core,
    aws_s3 as s3,
    aws_s3_deployment as s3_deployment,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as cf_origins,
    aws_route53 as route_53,
    aws_route53_targets as route_53_targets,
    aws_certificatemanager as acm,
)


class WebsiteStack(core.Stack):
    def __init__(
        self,
        scope: core.Construct,
        construct_id: str,
        domain_names: Optional[List[str]] = None,
        certificate: Optional[acm.Certificate] = None,
        hosted_zone: Optional[route_53.HostedZone] = None,
        **kwargs
    ):
        super().__init__(scope, construct_id, **kwargs)

        self.s3_bucket = s3.Bucket(
            self,
            "site_s3_bucket",
            access_control=s3.BucketAccessControl.PRIVATE,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            encryption=s3.BucketEncryption.S3_MANAGED,
        )

        self.s3_deployment = s3_deployment.BucketDeployment(
            self,
            "site_s3_deployment",
            destination_bucket=self.s3_bucket,
            destination_key_prefix="website/main",
            sources=[
                s3_deployment.Source.asset(
                    str(pathlib.Path(__file__).parent.parent / "public")
                )
            ],
        )

        self.cf_distribution = cloudfront.Distribution(
            self,
            "site_cf_distribution",
            default_behavior=cloudfront.BehaviorOptions(
                origin=cf_origins.S3Origin(self.s3_bucket)
            ),
            domain_names=domain_names,
            certificate=certificate,
        )

        if hosted_zone:
            self.dns_alias = route_53.AaaaRecord(
                self,
                "dns_alias",
                zone=hosted_zone,
                target=route_53.RecordTarget.from_alias(
                    route_53_targets.CloudFrontTarget(self.cf_distribution)
                ),
            )


class DnsStack(core.Stack):
    def __init__(
        self, scope: core.Construct, construct_id: str, *, domain_name: str, **kwargs
    ):
        super().__init__(scope, construct_id, **kwargs)

        self.hosted_zone = route_53.PublicHostedZone(
            self, "hosted_zone", zone_name=domain_name
        )


class CertificateStack(core.Stack):
    def __init__(
        self,
        scope: core.Construct,
        construct_id: str,
        *,
        hosted_zone: route_53.HostedZone,
        domain_name: str,
        alternate_names: Optional[List[str]] = None,
        **kwargs
    ):
        super().__init__(scope, construct_id, **kwargs)

        self.cert = acm.Certificate(
            self,
            "cert",
            domain_name=domain_name,
            subject_alternative_names=alternate_names,
            validation=acm.CertificateValidation.from_dns(hosted_zone),
        )
