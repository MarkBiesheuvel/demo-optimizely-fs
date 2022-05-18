// Names of the required cookies
var COOKIE_VARIATION_KEY = 'Optimizely-Variation-Key'
var COOKIE_VARIABLES = 'Optimizely-Variables'

function containsCookie(request) {
    // TODO: validate whether the signature of the JWT token is valid (using HMAC module in CloudFront Functions)
    return COOKIE_VARIATION_KEY in request.cookies &&
        COOKIE_VARIABLES in request.cookies
}

function handler(event) {
    // Collect information from CloudFront event
    var request = event.request;

    // No cookie found, so we send the user to /decide to generate one
    if (!containsCookie(request)) {
        // TODO: include the original URI+method, so DecideFunction can redirect back
        request.uri = '/decide'
        request.method = 'GET'
    }

    // Return modified request object
    return request
}
