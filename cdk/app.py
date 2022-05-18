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

        sdk = lambda_.LayerVersion(
            self, 'OptimizelySDK',
            compatible_runtimes=[lambda_.Runtime.PYTHON_3_8],
            code=lambda_.Code.from_asset('src/optimizely-sdk'),
        )

        overview_function = lambda_.Function(
            self, 'OverviewFunction',
            runtime=lambda_.Runtime.PYTHON_3_8,
            code=lambda_.Code.from_asset('src/overview'),
            handler='index.handler',
        )

        decide_function = lambda_.Function(
            self, 'DecideFunction',
            runtime=lambda_.Runtime.PYTHON_3_8,
            code=lambda_.Code.from_asset('src/decide'),
            handler='index.handler',
            layers=[sdk],
            environment={
                'OPTIMIZELY_SDK_KEY': os.getenv('OPTIMIZELY_SDK_KEY'),
            }
        )

        viewer_request_function = cloudfront.Function(
            self, 'ViewerRequestFunction',
            code=cloudfront.FunctionCode.from_file(file_path='src/viewer-request/index.js'),
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

        api.root.add_resource('decide').add_method(
            http_method='GET',
            integration=apigateway.LambdaIntegration(
                decide_function,
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
        cache_key_policy = cloudfront.CachePolicy(
            self, 'CacheKeyPolicy',
            min_ttl=Duration.seconds(0),
            default_ttl=Duration.minutes(5),
            max_ttl=Duration.minutes(5),
            cookie_behavior=cloudfront.CacheCookieBehavior.allow_list(
                'Optimizely-Variation-Key',
            ),
        )

        # Forward all custom headers to origin
        origin_request_policy = cloudfront.OriginRequestPolicy(
            self, 'OriginRequestPolicy',
            cookie_behavior=cloudfront.OriginRequestCookieBehavior.allow_list(
                'Optimizely-Variation-Key',
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
                function_associations=[
                    cloudfront.FunctionAssociation(
                        event_type=cloudfront.LambdaEdgeEventType.VIEWER_REQUEST,
                        function=viewer_request_function,
                    )
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
        region=os.getenv('CDK_DEFAULT_REGION'),
    ),
)
app.synth()
