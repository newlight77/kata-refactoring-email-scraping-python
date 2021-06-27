class TestClass:

    @classmethod
    def setup_class(cls):
        print('\nsetup_class()')

    @classmethod
    def teardown_class(cls):
        print('teardown_class()')

    def setup_method(self, method):
        print('\nsetup_method()')

    def teardown_method(self, method):
        print('\nteardown_method()')

    def test_3(self):
        print('- test_3()')

    def test_4(self):
        print('- test_4()')
