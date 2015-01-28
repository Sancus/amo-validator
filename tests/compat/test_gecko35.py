from helper import CompatTestCase
from validator.compat import FX35_DEFINITION


class TestFX35Compat(CompatTestCase):
    """Test that compatibility tests for Gecko 35 are properly executed."""

    VERSION = FX35_DEFINITION

    def nsIBoxObject_changed(self, interface):
        self.run_script_for_compat("""
            var obj = Components.interfaces.{interface};
        """.format(interface=interface))
        self.assert_silent()
        self.assert_compat_error()

    def test_nsIBoxObject_changed(self):
        self.nsIBoxObject_changed('nsIBoxObject')

    def test_nsIBrowserBoxObject_changed(self):
        self.nsIBoxObject_changed('nsIBrowserBoxObject')

    def test_nsIContainerBoxObject_changed(self):
        self.nsIBoxObject_changed('nsIContainerBoxObject')

    def test_nsIEditorBoxObject_changed(self):
        self.nsIBoxObject_changed('nsIEditorBoxObject')

    def test_nsIIFrameBoxObject_changed(self):
        self.nsIBoxObject_changed('nsIIFrameBoxObject')

    def test_nsIListBoxObject_changed(self):
        self.nsIBoxObject_changed('nsIListBoxObject')

    def test_nsIMenuBoxObject_changed(self):
        self.nsIBoxObject_changed('nsIMenuBoxObject')

    def test_nsIPopupBoxObject_changed(self):
        self.nsIBoxObject_changed('nsIPopupBoxObject')

    def test_nsIScrollBoxObject_changed(self):
        self.nsIBoxObject_changed('nsIScrollBoxObject')

    def test_nsITreeBoxObject_changed(self):
        self.nsIBoxObject_changed('nsITreeBoxObject')

    def test_nsIFoo_BoxObject_no_error(self):
        self.run_script_for_compat("""
            var nsIFoo = myBoxObject;
        """)
        self.assert_silent()
        self.assert_compat_silent()
