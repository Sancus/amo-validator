import os
import requests
import sys

download_errors = []

ALLOWED = "allowed"
WARNING = "warning"
ERROR = "error"

ANGULARJS_VERSIONS = {
    ERROR: [
        "1.0.2",
        "1.0.3",
        "1.0.4",
        "1.0.5",
        "1.0.6",
        "1.0.7",
        "1.0.8",
        "1.1.0",
        "1.1.1",
        "1.1.2",
        "1.1.3",
        "1.1.4",
        "1.1.5",
        "1.2.0",
        "1.2.1",
        "1.2.2",
        "1.2.3",
        "1.2.4",
        "1.2.5",
        "1.2.6",
        "1.2.7",
        "1.2.8",
        "1.2.9",
        "1.2.10",
        "1.2.11",
        "1.2.12",
        "1.2.13",
        "1.2.14",
        "1.2.15",
        "1.2.16",
        "1.2.17",
        "1.2.18",
        "1.2.19",
        "1.2.20",
        "1.2.21",
        "1.2.22",
        "1.2.23",
        "1.2.24",
        "1.2.25",
        "1.2.26",
        "1.2.27",
        "1.2.28",
        "1.2.29",
        "1.2.30",
        "1.3.0",
        "1.3.1",
        "1.3.2",
        "1.3.3",
        "1.3.4",
        "1.3.5",
        "1.3.6",
        "1.3.7",
        "1.3.8",
        "1.3.9",
        "1.3.10",
        "1.3.11",
        "1.3.12",
        "1.3.13",
        "1.3.14",
        "1.3.15",
        "1.3.16",
        "1.3.17",
        "1.3.18",
        "1.3.19",
        "1.3.20",
        "1.4.0",
        "1.4.1",
        "1.4.2",
        "1.4.3",
        "1.4.4",
        "1.4.5",
        "1.4.6",
        "1.4.7",
        "1.4.8",
        "1.4.9",
        "1.4.10",
        "1.4.11",
        "1.4.12",
        "1.5.0",
        "1.5.1",
        "1.5.2",
        "1.5.3",
        "1.5.4",
        "1.5.5",
        "1.5.6",
        "1.5.7",
        "1.5.8",
        "1.5.9",
        "1.6.0",
        "1.6.1",
        "1.6.2",
        "1.6.3",
    ],
    ALLOWED: [
        "1.6.4",
    ],
}

BACKBONE_VERSIONS = {
    ALLOWED: [
        "1.0.0",
        "1.1.0",
        "1.1.1",
        "1.1.2",
        "1.2.0",
        "1.2.1",
        "1.2.2",
        "1.2.3",
        "1.3.1",
        "1.3.2",
        "1.3.3",
    ]
}

BOOTSTRAP_VERSIONS = {
    ALLOWED: [
        "3.1.1",
        "3.2.0",
        "3.3.0",
        "3.3.1",
        "3.3.2",
        "3.3.4",
        "3.3.5",
        "3.3.6",
        "3.3.7",
    ]
}

DOJO_VERSIONS = {
    ALLOWED: [
        "1.7.0",
        "1.7.1",
        "1.7.2",
        "1.7.3",
        "1.7.4",
        "1.7.5",
        "1.7.6",
        "1.7.7",
        "1.7.8",
        "1.7.9",
        "1.7.10",
        "1.7.11",
        "1.7.12",
        "1.8.0",
        "1.8.1",
        "1.8.2",
        "1.8.3",
        "1.8.4",
        "1.8.5",
        "1.8.6",
        "1.8.7",
        "1.8.8",
        "1.8.9",
        "1.8.10",
        "1.8.11",
        "1.8.12",
        "1.8.13",
        "1.8.14",
        "1.9.0",
        "1.9.1",
        "1.9.2",
        "1.9.3",
        "1.9.4",
        "1.9.5",
        "1.9.6",
        "1.9.7",
        "1.9.8",
        "1.9.9",
        "1.9.10",
        "1.9.11",
        "1.10.0",
        "1.10.1",
        "1.10.2",
        "1.10.3",
        "1.10.4",
        "1.10.5",
        "1.10.6",
        "1.10.7",
        "1.10.8",
        "1.11.0",
        "1.11.1",
        "1.11.2",
        "1.11.3",
        "1.11.4",
        "1.12.1",
        "1.12.2",
    ]
}

DOMPURIFY_VERSIONS = {
    ALLOWED: [
        "0.8.6",
        "0.8.7",
        "0.8.9",
    ]
}

JQUERY_VERSIONS = {
    ERROR: [
        "1.2",
        "1.2.1",
        "1.2.2",
        "1.2.3",
        "1.2.4",
        "1.2.5",
        "1.2.6",
        "1.3",
        "1.3.1",
        "1.3.2",
        "1.4",
        "1.4.1",
        "1.4.2",
        "1.4.3",
        "1.4.4",
        "1.5",
        "1.5.1",
        "1.5.2",
        "1.6",
        "1.6.1",
        "1.6.2",
        "1.6.3",
        "1.6.4",
        "1.7.0",
        "1.7.1",
        "1.7.2",
        "1.8.0",
        "1.8.1",
        "1.8.2",
        "1.8.3",
        "1.9.0",
        "1.9.1",
        "1.10.0",
        "1.10.1",
        "1.10.2",
        "1.11.0",
        "1.11.1",
        "1.11.2",
        "1.11.3",
        "1.12.0",
        "1.12.1",
        "1.12.2",
        "1.12.3",
        "1.12.4",
    ],
    ALLOWED: [
        "3.0.0",
        "3.1.0",
        "3.1.1",
        "3.2.0",
        "3.2.1",
    ]
}

JQUERYUI_VERSIONS = {
    ALLOWED: [
        "1.10.0",
        "1.10.1",
        "1.10.2",
        "1.10.3",
        "1.10.4",
        "1.11.0",
        "1.11.1",
        "1.11.2",
        "1.11.3",
        "1.11.4",
        "1.12.0",
        "1.12.1",
    ]
}

MOMENTJS_VERSIONS = {
    ALLOWED: [
        "2.11.2",
        "2.12.0",
        "2.13.0",
        "2.14.0",
        "2.14.1",
        "2.14.2",
        "2.15.0",
        "2.15.1",
        "2.15.2",
        "2.16.0",
        "2.17.0",
        "2.17.1",
        "2.18.0",
        "2.18.1",
    ]
}

MOOTOOLS_VERSIONS = {
    ALLOWED: [
        "1.5.1",
        "1.5.2",
        "1.6.0",
    ]
}

PROTOTYPE_VERSIONS = {
    ALLOWED: [
        "1.7.0.0",
        "1.7.1.0",
        "1.7.2.0",
        "1.7.3.0",
    ]
}

REACT_VERSIONS = {
    ALLOWED: [
        "0.14.0",
        "0.14.1",
        "0.14.2",
        "0.14.3",
        "0.14.4",
        "0.14.5",
        "0.14.6",
        "0.14.7",
        "0.14.8",
        "15.0.0",
        "15.0.1",
        "15.0.2",
        "15.1.0",
        "15.2.0",
        "15.2.1",
        "15.3.0",
        "15.3.1",
        "15.3.2",
        "15.4.0",
        "15.4.1",
        "15.4.2",
        "15.5.4",
    ]
}

UNDERSCORE_VERSIONS = {
    ALLOWED: [
        "1.2.0",
        "1.2.1",
        "1.2.2",
        "1.2.3",
        "1.2.4",
        "1.3.0",
        "1.3.1",
        "1.3.2",
        "1.3.3",
        "1.4.0",
        "1.4.1",
        "1.4.2",
        "1.4.3",
        "1.4.4",
        "1.5.0",
        "1.5.1",
        "1.5.2",
        "1.6.0",
        "1.7.0",
        "1.8.0",
        "1.8.1",
        "1.8.2",
        "1.8.3",
    ]
}

WEBEXTENSION_POLYFILL_VERSIONS = {
    ALLOWED: [
        "0.1.1",
    ]
}


def process(url, rule, file):
    dest_folder = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                               sys.argv[1], rule)

    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)

    destination = os.path.join(dest_folder, file)
    if os.path.exists(destination):
        return

    try:
        response = requests.get(url)
        response.raise_for_status()
        with open(destination, "wb") as code:
            code.write(response.content)
            print "Downloaded: {}".format(url)
    except requests.exceptions.HTTPError:
        global download_errors
        download_errors.append((url, response.status_code, response.reason))


def get_pattern(prefix, url_pattern, library, outputFilename=None):
    for rule, versions in library.iteritems():
        for version in versions:
            url = url_pattern % version
            filenameSuffix = outputFilename or url.split("/")[-1]
            process(url, rule, "%s.%s.%s" % (prefix, version, filenameSuffix))


def get_patterns():
    # AngularJS
    get_pattern("angularjs",
                "https://code.angularjs.org/%s/angular.js",
                ANGULARJS_VERSIONS)
    get_pattern("angularjs",
                "https://code.angularjs.org/%s/angular.min.js",
                ANGULARJS_VERSIONS)

    # Backbone
    get_pattern("backbone",
                "https://raw.githubusercontent.com/jashkenas/backbone/%s/backbone.js",
                BACKBONE_VERSIONS)
    get_pattern("backbone",
                "https://raw.githubusercontent.com/jashkenas/backbone/%s/backbone-min.js",
                BACKBONE_VERSIONS)

    # Bootstrap
    get_pattern("bootstrap",
                "https://raw.githubusercontent.com/twbs/bootstrap/v%s/dist/js/bootstrap.js",
                BOOTSTRAP_VERSIONS)
    get_pattern("bootstrap",
                "https://raw.githubusercontent.com/twbs/bootstrap/v%s/dist/js/bootstrap.min.js",
                BOOTSTRAP_VERSIONS)

    # Dojo Toolkit
    get_pattern("dojo",
                "https://download.dojotoolkit.org/release-%s/dojo.js",
                DOJO_VERSIONS)
    get_pattern("dojo",
                "https://download.dojotoolkit.org/release-%s/dojo.js.uncompressed.js",
                DOJO_VERSIONS)

    # DOMPurify
    get_pattern("dompurify",
                "https://raw.githubusercontent.com/cure53/DOMPurify/%s/src/purify.js",
                DOMPURIFY_VERSIONS)
    get_pattern("dompurify",
                "https://raw.githubusercontent.com/cure53/DOMPurify/%s/dist/purify.min.js",
                DOMPURIFY_VERSIONS)

    # jQuery
    get_pattern("jquery",
                "https://code.jquery.com/jquery-%s.js",
                JQUERY_VERSIONS,
                "jquery.js")
    get_pattern("jquery",
                "https://code.jquery.com/jquery-%s.min.js",
                JQUERY_VERSIONS,
                "jquery.min.js")

    # jQueryUI
    get_pattern("jquery-ui",
                "https://code.jquery.com/ui/%s/jquery-ui.js",
                JQUERYUI_VERSIONS)
    get_pattern("jquery-ui",
                "https://code.jquery.com/ui/%s/jquery-ui.min.js",
                JQUERYUI_VERSIONS)

    # moment.js
    get_pattern("moment",
                "https://raw.githubusercontent.com/moment/moment/%s/moment.js",
                MOMENTJS_VERSIONS)
    get_pattern("moment",
                "https://raw.githubusercontent.com/moment/moment/%s/min/moment.min.js",
                MOMENTJS_VERSIONS)

    # MooTools
    get_pattern("mootools",
                "https://raw.githubusercontent.com/mootools/mootools-core/%s/dist/mootools-core.js",
                MOOTOOLS_VERSIONS)
    get_pattern("mootools",
                "https://raw.githubusercontent.com/mootools/mootools-core/%s/dist/mootools-core.min.js",
                MOOTOOLS_VERSIONS)

    # Prototype.js
    get_pattern("prototype",
                "https://ajax.googleapis.com/ajax/libs/prototype/%s/prototype.js",
                PROTOTYPE_VERSIONS)

    # React
    get_pattern("react",
                "https://unpkg.com/react@%s/dist/react.js",
                REACT_VERSIONS)
    get_pattern("react",
                "https://unpkg.com/react@%s/dist/react.min.js",
                REACT_VERSIONS)

    # React DOM
    get_pattern("react-dom",
                "https://unpkg.com/react-dom@%s/dist/react-dom.js",
                REACT_VERSIONS)
    get_pattern("react-dom",
                "https://unpkg.com/react-dom@%s/dist/react-dom.min.js",
                REACT_VERSIONS)

    # Underscore
    get_pattern("underscore",
                "https://raw.github.com/documentcloud/underscore/%s/underscore.js",
                UNDERSCORE_VERSIONS)
    get_pattern("underscore",
                "https://raw.github.com/documentcloud/underscore/%s/underscore-min.js",
                UNDERSCORE_VERSIONS)

    # Webextension polyfill
    get_pattern("webextension-polyfill",
                "https://unpkg.com/webextension-polyfill@%s/dist/browser-polyfill.js",
                WEBEXTENSION_POLYFILL_VERSIONS)
    get_pattern("webextension-polyfill",
                "https://unpkg.com/webextension-polyfill@%s/dist/browser-polyfill.min.js",
                WEBEXTENSION_POLYFILL_VERSIONS)


print "Downloading third-party library files..."
get_patterns()
if download_errors:
    for url, code, reason in download_errors:
        print "Failed: {} is '{}' ({}).".format(url, reason, code)
    print "Some files failed to download, please check the output above...Exiting."
    sys.exit(1)
print "Downloading third-party library files complete."
