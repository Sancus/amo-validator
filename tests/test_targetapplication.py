from mock import patch
import validator.testcases.targetapplication as targetapp
from validator.errorbundler import ErrorBundle
from validator.json_parser import ManifestJsonParser
from validator.rdf import RDFParser
from helper import _do_test

INVALID_MANIFEST_JSON = """{"name": "My Awesome Addon", "version": "1.25"}"""

VALID_INSTALL_RDF = """
<?xml version="1.0"?>
<RDF xmlns="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
        xmlns:em="http://www.mozilla.org/2004/em-rdf#">
    <Description about="urn:mozilla:install-manifest">
        <em:targetApplication>
            <Description> <!-- Firefox -->
                <em:id>{ec8030f7-c20a-464f-9b0e-13a3a9e97384}</em:id>
                <em:minVersion>1.5</em:minVersion>
                <em:maxVersion>3.0.*</em:maxVersion>
            </Description>
        </em:targetApplication>
    </Description>
</RDF>
"""


def _do_test_raw(rdf, listed=True, overrides=None):
    err = ErrorBundle(listed=listed)
    err.overrides = overrides
    rdf = RDFParser(err, rdf.strip())
    err.save_resource('has_install_rdf', True)
    err.save_resource('install_rdf', rdf)

    targetapp.test_targetedapplications(err)
    return err


def _do_test_raw_webextension(manifest, listed=True):
    err = ErrorBundle(listed=listed)
    manifest = ManifestJsonParser(err, manifest)
    err.save_resource('has_manifest_json', True)
    err.save_resource('manifest_json', manifest)

    targetapp.test_targetedapplications(err)
    return err


def test_valid_targetapps():
    """
    Tests that the install.rdf contains only valid entries for target
    applications.
    """

    results = _do_test('tests/resources/targetapplication/pass.xpi',
                       targetapp.test_targetedapplications,
                       False,
                       True)
    supports = results.get_resource('supports')
    assert 'firefox' in supports and 'mozilla' in supports
    assert len(supports) == 2

    supported_versions = results.supported_versions
    assert (supported_versions['{ec8030f7-c20a-464f-9b0e-13a3a9e97384}'] ==
            ['3.6', '3.6.4', '3.6.*'])


def test_missing_min_max():
    """
    Test that the minVersion and maxVersion properties of each
    targetApplication are mandatory.
    """

    results = _do_test('tests/resources/targetapplication/missing_min.xpi',
                       targetapp.test_targetedapplications,
                       True,
                       True)
    # _do_test() checks for .failed(), but by default this includes warnings.
    # We want to make sure it's a hard error and not just a warning.
    assert results.errors[0]['id'] == ('testcases_targetapplication',
                                       'test_targetedapplications',
                                       'missing_minversion')

    results = _do_test('tests/resources/targetapplication/missing_max.xpi',
                       targetapp.test_targetedapplications,
                       True,
                       True)
    assert results.errors[0]['id'] == ('testcases_targetapplication',
                                       'test_targetedapplications',
                                       'missing_maxversion')


def test_valid_targetapps_webextension_missing_min_max():
    """
    Test that min/max version are *not* mandatory for web extensions.
    """
    results = _do_test('tests/resources/targetapplication/webextension.xpi',
                       targetapp.test_targetedapplications,
                       False,
                       True)
    supports = results.get_resource('supports')
    assert 'firefox' in supports
    assert len(supports) == 1

    supported_versions = results.supported_versions
    supported_firefox_versions = supported_versions[
        '{ec8030f7-c20a-464f-9b0e-13a3a9e97384}']
    assert '42.0' in supported_firefox_versions  # Automatic min version.
    assert '*' in supported_firefox_versions  # Automatic max version.


def test_bad_min_max():
    """Tests that the lower/upper-bound version number for a
    targetApplication entry is indeed a valid version number"""

    _do_test('tests/resources/targetapplication/bad_min.xpi',
             targetapp.test_targetedapplications,
             True,
             True)

    _do_test('tests/resources/targetapplication/bad_max.xpi',
             targetapp.test_targetedapplications,
             True,
             True)


def test_bad_min_max_webextension():
    """Tests that the lower/upper-bound version number is indeed a valid
    version number."""

    _do_test('tests/resources/targetapplication/webextension_bad_min.xpi',
             targetapp.test_targetedapplications,
             True,
             True)

    _do_test('tests/resources/targetapplication/webextension_bad_max.xpi',
             targetapp.test_targetedapplications,
             True,
             True)


def test_bad_order():
    """Tests that the min and max versions are ordered correctly such
    that the earlier version is the min and vice-versa."""

    _do_test('tests/resources/targetapplication/bad_order.xpi',
             targetapp.test_targetedapplications,
             True,
             True)


def test_dup_targets():
    """Tests that there are no duplicate targetAppication elements."""

    results = _do_test(
        'tests/resources/targetapplication/dup_targapp.xpi',
        targetapp.test_targetedapplications,
        True,
        True)
    assert results.errors[0]['id'] == ('testcases_targetapplication',
                                       'test_targetedapplications',
                                       'duplicate_targetapps')


def test_missing_installrdfs_are_handled():
    """
    Tests that install.rdf files are present and supported_versions is set to
    an empty dict if an install.rdf is not found.
    """

    err = ErrorBundle()

    # This is the default, but I'm specifying it for clarity of purpose.
    err.supported_versions = None

    # Test package to make sure has_install_rdf is set to True.
    assert targetapp.test_targetedapplications(err, None) is None
    # The supported versions list must be empty or other tests will fail.
    assert err.supported_versions == {}


def test_supported_versions_not_overwritten():
    """
    Test that supported_versions is not overwritten in subpackages (JARs) when
    install.rdf files are tested for. This could otherwise happen because the
    targetApplication tests previously gave an empty dict to supported_versions
    in order to ensure a valid state when testing for version support.

    If the supported_versions field in an error bundle is None, it represents
    that the list of targeted applications has not been parsed yet. Setting it
    to an empty dict prevents exceptions later on by stating that no supported
    versions are available. If this didn't happen, it would be assumed that
    compatibility (version-dependent) tests were reached before the install.rdf
    was parsed. That would indicate that the validation process has encountered
    an error elsewhere.
    """

    err = ErrorBundle()
    orig_value = err.supported_versions = {'foo': ['bar']}

    # Test package to make sure has_install_rdf is set to True.
    assert targetapp.test_targetedapplications(err, None) is None
    # The supported versions list must match what was specified
    assert err.supported_versions is orig_value


def test_is_ff4():
    """Tests a passing install.rdf package for whether it's built for
    Firefox 4. This doesn't pass or fail a package, but it is used for
    other tests in other modules in higher tiers."""

    results = _do_test('tests/resources/targetapplication/ff4.xpi',
                       targetapp.test_targetedapplications,
                       False,
                       True)

    assert results.get_resource('ff4')
    assert results.get_resource('supports')
    assert 'firefox' in results.get_resource('supports')


def test_no_supported_mozilla_apps():
    """
    Tests that at least one supported Mozilla app is listed as a target
    application.
    """

    assert not _do_test_raw(VALID_INSTALL_RDF).failed()

    assert not _do_test_raw("""
    <?xml version="1.0"?>
    <RDF xmlns="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
         xmlns:em="http://www.mozilla.org/2004/em-rdf#">
        <Description about="urn:mozilla:install-manifest">
            <em:targetApplication>
                <Description> <!-- Something else -->
                    <em:id>Blah blah blah</em:id>
                    <em:minVersion>1.2.3</em:minVersion>
                    <em:maxVersion>4.5.6</em:maxVersion>
                </Description>
            </em:targetApplication>
            <em:targetApplication>
                <Description> <!-- Firefox -->
                    <em:id>{ec8030f7-c20a-464f-9b0e-13a3a9e97384}</em:id>
                    <em:minVersion>1.5</em:minVersion>
                    <em:maxVersion>3.0.*</em:maxVersion>
                </Description>
            </em:targetApplication>
        </Description>
    </RDF>
    """).failed()

    failure_case = """
    <?xml version="1.0"?>
    <RDF xmlns="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
         xmlns:em="http://www.mozilla.org/2004/em-rdf#">
        <Description about="urn:mozilla:install-manifest">
            <em:targetApplication>
                <Description> <!-- Something else -->
                    <em:id>Blah blah blah</em:id>
                    <em:minVersion>1.2.3</em:minVersion>
                    <em:maxVersion>4.5.6</em:maxVersion>
                </Description>
            </em:targetApplication>
            <em:targetApplication>
                <Description> <!-- More junk -->
                    <em:id>More junk</em:id>
                    <em:minVersion>9.8.7</em:minVersion>
                    <em:maxVersion>6.5.4</em:maxVersion>
                </Description>
            </em:targetApplication>
        </Description>
    </RDF>
    """

    assert _do_test_raw(failure_case).failed()
    assert not _do_test_raw(failure_case, listed=False).failed()

    assert not _do_test_raw_webextension("""{
        "name": "My Awesome Addon",
        "version": "1.25",

        "applications": {
            "gecko": {
                "id": "my@awesome.addon"
            }
        }
    }""").failed()

    assert _do_test_raw_webextension(INVALID_MANIFEST_JSON).failed()
    assert not _do_test_raw_webextension(
        INVALID_MANIFEST_JSON, listed=False).failed()


MISSING_ANDROID_APPROVED_APPLICATIONS = {
    '1': {
        'name': 'Firefox',
        'guid': '{ec8030f7-c20a-464f-9b0e-13a3a9e97384}',
        'versions': ['0.3', '29.*']
    }
}


@patch.dict('validator.constants.APPROVED_APPLICATIONS',
            values=MISSING_ANDROID_APPROVED_APPLICATIONS,
            clear=True)
def test_unsupported_mozilla_app_in_approved_apps():
    """
    Test that non approved applications are not validated.

    We submit an add-on which has *only* one targetApplication,
    which targetApplication is a valid Mozilla app but it's missing
    from the approved applications.
    """

    failure_case = """
    <?xml version="1.0"?>
    <RDF xmlns="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
         xmlns:em="http://www.mozilla.org/2004/em-rdf#">

        <Description about="urn:mozilla:install-manifest">
            <em:id>testandroidapp@mozillapps.com</em:id>
            <em:type>2</em:type>
            <em:name>Test Android App</em:name>
            <em:version>0.2</em:version>
            <em:bootstrap>true</em:bootstrap>
            <em:description>App for testing that it will be rejected when
            "android" is missing from the approved apps.</em:description>
            <em:creator>Mister Myster</em:creator>

            <!-- Android -->
            <em:targetApplication>
                <Description>
                    <em:id>{aa3c5121-dab2-40e2-81ca-7ea25febc110}</em:id>
                    <em:minVersion>30.0a1</em:minVersion>
                    <em:maxVersion>32.0</em:maxVersion>
                </Description>
            </em:targetApplication>

        </Description>
    </RDF>
    """

    err = _do_test_raw(failure_case)
    assert err.failed()
    assert err.errors[0]['id'] == ('testcases_targetapplication',
                                   'test_targetedapplications',
                                   'no_mozilla_support')


def test_overrides():
    """Test that the validate() function can override the min/max versions"""

    # Make sure a failing test can be forced to pass.
    assert not _do_test_raw("""
    <?xml version="1.0"?>
    <RDF xmlns="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
         xmlns:em="http://www.mozilla.org/2004/em-rdf#">
        <Description about="urn:mozilla:install-manifest">
            <em:targetApplication>
                <Description> <!-- Firefox -->
                    <em:id>{ec8030f7-c20a-464f-9b0e-13a3a9e97384}</em:id>
                    <em:minVersion>ABCDEFG</em:minVersion>
                    <em:maxVersion>-1.2.3.4</em:maxVersion>
                </Description>
            </em:targetApplication>
        </Description>
    </RDF>
    """, overrides={'targetapp_minVersion':
                        {'{ec8030f7-c20a-464f-9b0e-13a3a9e97384}': '1.5'},
                    'targetapp_maxVersion':
                        {'{ec8030f7-c20a-464f-9b0e-13a3a9e97384}': '3.6'}}
            ).failed()

    # Make sure a test can be forced to fail.
    assert _do_test_raw("""
    <?xml version="1.0"?>
    <RDF xmlns="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
         xmlns:em="http://www.mozilla.org/2004/em-rdf#">
        <Description about="urn:mozilla:install-manifest">
            <em:targetApplication>
                <Description> <!-- Firefox -->
                    <em:id>{ec8030f7-c20a-464f-9b0e-13a3a9e97384}</em:id>
                    <em:minVersion>1.5</em:minVersion>
                    <em:maxVersion>3.6</em:maxVersion>
                </Description>
            </em:targetApplication>
        </Description>
    </RDF>
    """, overrides={'targetapp_minVersion':
                        {'{ec8030f7-c20a-464f-9b0e-13a3a9e97384}': 'foo'},
                    'targetapp_maxVersion':
                        {'{ec8030f7-c20a-464f-9b0e-13a3a9e97384}': 'bar'}}
            ).failed()


def test_manifest_ordering():
    err = ErrorBundle(listed=True)
    manifest = ManifestJsonParser(err, INVALID_MANIFEST_JSON)
    err.save_resource('has_manifest_json', True)
    err.save_resource('manifest_json', manifest)
    rdf = RDFParser(err, VALID_INSTALL_RDF.strip())
    err.save_resource('has_install_rdf', True)
    err.save_resource('install_rdf', rdf)

    targetapp.test_targetedapplications(err)

    assert not err.failed()
