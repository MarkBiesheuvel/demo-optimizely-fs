#!/usr/bin/env python3
import os
from constructs import Construct
from aws_cdk import (
    App,
    Environment,
    Stack,
    Duration,
    RemovalPolicy,
    aws_apigateway as apigateway,
    aws_certificatemanager as acm,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
    aws_dynamodb as dynamodb,
    aws_lambda as lambda_,
    aws_route53 as route53,
    aws_route53_targets as targets,
    aws_synthetics_alpha as synthetics,
)


class OptimizelyFullStackStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        stack = Stack.of(self)

        # Determine domain name and sub domain from the context variables
        domain_name = self.node.try_get_context('domainName')
        subdomain = 'fs.{}'.format(domain_name)

        overview_function = lambda_.Function(
            self, 'OverviewFunction',
            runtime=lambda_.Runtime.PYTHON_3_8,
            code=lambda_.Code.from_asset('src/overview'),
            handler='index.handler',
        )

        viewer_request_function = lambda_.Function(
            self, 'ViewerRequestFunction',
            runtime=lambda_.Runtime.PYTHON_3_8,
            code=lambda_.Code.from_asset('src/viewer-request'),
            handler='index.handler',
            current_version_options=lambda_.VersionOptions(
                retry_attempts=0,
            )
        )

        api = apigateway.RestApi(
            self, 'Api',
            endpoint_types=[apigateway.EndpointType.REGIONAL],
        )

        api.root.add_method(
            http_method='GET',
            integration=apigateway.LambdaIntegration(
                overview_function,
                proxy=True,
            ),
        )

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

        # Use a single custom header to cache different variations under different keys
        cache_key_policy = cloudfront.CachePolicy(self, 'CacheKeyPolicy',
            min_ttl=Duration.seconds(0),
            default_ttl=Duration.minutes(5),
            max_ttl=Duration.minutes(5),
            header_behavior=cloudfront.CacheHeaderBehavior.allow_list(
                'Optimizely-Variartion-Key',
            ),
        )

        # Forward all custom headers to origin
        origin_request_policy = cloudfront.OriginRequestPolicy(self, 'OriginRequestPolicy',
            header_behavior=cloudfront.OriginRequestHeaderBehavior.allow_list(
                'Optimizely-Variartion-Key',
                'Optimizely-Variables',
                'Optimizely-User-Id',
            ),
        )

        # Content Delivery Network
        distribution = cloudfront.Distribution(
            self, 'CDN',
            domain_names=[subdomain],
            certificate=certificate,
            default_behavior=cloudfront.BehaviorOptions(
                origin=origins.HttpOrigin(
                    domain_name='{}.execute-api.{}.{}'.format(
                        api.rest_api_id,
                        stack.region,
                        stack.url_suffix,
                    ),
                    origin_path='/{}'.format(
                        api.deployment_stage.stage_name
                    )
                ),
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                cache_policy=cache_key_policy,
                origin_request_policy=origin_request_policy,
                edge_lambdas=[
                    cloudfront.EdgeLambda(
                        event_type=cloudfront.LambdaEdgeEventType.VIEWER_REQUEST,
                        function_version=viewer_request_function.current_version,
                    ),
                ],
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
        region='us-east-1', # Needs to be N. Virginia since using Lambda@Edge
    ),
)
app.synth()
