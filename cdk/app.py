#!/usr/bin/env python3
import os
from constructs import Construct
from aws_cdk import (
    App,
    Environment,
    Stack,
    Duration,
    aws_certificatemanager as acm,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
    aws_lambda as lambda_,
    aws_route53 as route53,
    aws_route53_targets as targets,
    aws_s3 as s3,
    aws_s3_deployment as s3_deployment,
    aws_synthetics_alpha as synthetics,
)

class OptimizelyFullStackStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Determine domain name and sub domain from the context variables
        domain_name = self.node.try_get_context('domainName')
        subdomain = 'fs.{}'.format(domain_name)

        # Assumption: Hosted Zone is created outside of this project
        # Fetch the Route53 Hosted Zone
        zone = route53.HostedZone.from_lookup(
            self, 'Zone',
            domain_name=domain_name,
        )

        # Public SSL certificate for subdomain
        certificate = acm.DnsValidatedCertificate(
            self, 'Certificate',
            domain_name=subdomain,
            hosted_zone=zone,
            region='us-east-1',
        )

        # Content Delivery Network
        distribution = cloudfront.Distribution(
            self, 'CDN',
            default_root_object='index.html',
            domain_names=[subdomain],
            certificate=certificate,
            default_behavior=cloudfront.BehaviorOptions(
                origin=origins.HttpOrigin('www.optimizely.com'),
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                cache_policy=cloudfront.CachePolicy.CACHING_DISABLED,
            )
        )

        # Both IPv4 and IPv6 addresses
        target = route53.RecordTarget.from_alias(
            alias_target=targets.CloudFrontTarget(distribution)
        )
        route53.AaaaRecord(
            self, 'DnsRecordIpv6',
            record_name=subdomain,
            target=target,
            zone=zone,
        )
        route53.ARecord(
            self, 'DnsRecordIpv4',
            record_name=subdomain,
            target=target,
            zone=zone,
        )


app = App()
OptimizelyFullStackStack(app, 'OptimizelyFullStack',
    env=Environment(
        account=os.getenv('CDK_DEFAULT_ACCOUNT'),
        region=os.getenv('CDK_DEFAULT_REGION')
    ),
)
app.synth()
