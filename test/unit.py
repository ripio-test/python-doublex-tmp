# -*- coding:utf-8; tab-width:4; mode:python -*-

from unittest import TestCase
import itertools

from hamcrest import is_not, all_of, contains_string, has_length
from hamcrest.library.text.stringcontainsinorder import *
from hamcrest.library.object.hasproperty import *
from hamcrest.library.number.ordering_comparison import *

from doublex import *
from doublex.doubles import StubProto, SpyProto

class StubTests(TestCase):
    def setUp(self):
        self.stub = Stub()

    def test_record_invocation(self):
        with self.stub:
            self.stub.foo().returns(2)

        assert_that(self.stub.foo(), is_(2))

    def test_using_alias_in_context(self):
        with self.stub as stub:
            stub.foo().returns(2)

        assert_that(self.stub.foo(), is_(2))

    def test_creating_double_with_context(self):
        with Stub() as stub:
            stub.foo().returns(2)

        assert_that(stub.foo(), is_(2))

    def test_record_invocation_with_args(self):
        with self.stub:
            self.stub.foo(1, param='hi').returns(2)

        assert_that(self.stub.foo(1, param='hi'), is_(2))

    def test_record_invocation_with_wrong_args_returns_None(self):
        with self.stub:
            self.stub.foo(1, param='hi').returns(2)

        assert_that(self.stub.foo(1, param='wrong'), is_(None))

    def test_not_stubbed_method_returns_None(self):
        with self.stub:
            self.stub.foo().returns(True)

        assert_that(self.stub.bar(), is_(None))

    def test_raises(self):
        with self.stub:
            self.stub.foo().raises(KeyError)

        try:
            self.stub.foo()
            self.fail("It should raise KeyError")
        except KeyError:
            pass


class VerifiedStubTests(TestCase):
    def setUp(self):
        self.stub = Stub(Collaborator)

    def test_stubbing_a_existing_method(self):
        with self.stub:
            self.stub.hello().returns("bye")

        assert_that(self.stub.hello(), is_("bye"))

    def test_from_instance(self):
        stub = Stub(Collaborator())
        with stub:
            stub.hello().returns("bye")

        assert_that(stub.hello(), is_("bye"))

    def test_stubbing_a_unexisting_method_raises_error(self):
        try:
            with self.stub:
                self.stub.wrong().returns("bye")

        except AttributeError, e:
            expected = "'Collaborator' object has no attribute 'wrong'"
            assert_that(str(e), contains_string(expected))

    def test_stubbing_with_wrong_args_raises_error(self):
        try:
            with self.stub:
                self.stub.hello(1).returns("bye")

        except TypeError, e:
            expected = "hello() takes exactly 1 argument (2 given)"
            assert_that(str(e), contains_string(expected))

    # bitbucket issue #6
    def test_keyworked_or_positional(self):
        with self.stub:
            self.stub.kwarg_method(1).returns(1000)
            self.stub.kwarg_method(key_param=2).returns(2000)

        assert_that(self.stub.kwarg_method(1), is_(1000))
        assert_that(self.stub.kwarg_method(key_param=2), is_(2000))


class SpyTests(TestCase):
    def setUp(self):
        self.spy = Spy()

    def test_simple_invocation(self):
        self.spy.foo()

    def test_called(self):
        self.spy.foo()

        assert_that(self.spy.foo, called())

    def test_not_called(self):
        self.spy.foo()

        assert_that(self.spy.bar, is_not(called()))

    def test_called_2_times(self):
        self.spy.foo()
        self.spy.foo()

        assert_that(self.spy.foo, called().times(2))
        assert_that(self.spy.foo, is_not(called().times(1)))
        assert_that(self.spy.foo, is_not(called().times(3)))

    def test_called_without_args(self):
        self.spy.foo()

        assert_that(self.spy.foo, called_with())

    def test_called_with_None(self):
        self.spy.foo(None)

        assert_that(self.spy.foo, called_with(None))
        assert_that(self.spy.foo, is_not(called_with()))

    def test_not_called_without_args(self):
        self.spy.foo(1)

        assert_that(self.spy.foo, is_not(called_with()))

    def test_called_with_specified_args(self):
        self.spy.foo(1)

        assert_that(self.spy.foo, called_with(1))

    def test_not_called_with_specified_args(self):
        self.spy.foo()
        self.spy.foo(2)

        assert_that(self.spy.foo, is_not(called_with(1)))

    def test_mixed_args(self):
        self.spy.send_mail('hi')
        self.spy.send_mail('foo@bar.net')

        assert_that(self.spy.send_mail, called())
        assert_that(self.spy.send_mail, called().times(2))
        assert_that(self.spy.send_mail, called_with('foo@bar.net'))

    def test_called_with_several_types_and_kargs(self):
        self.spy.foo(3.0, [1, 2], 'hi', color='red', width=10)

        assert_that(self.spy.foo, called_with(
                3.0, [1, 2], 'hi', color='red', width=10))
        assert_that(self.spy.foo, called_with(
                3.0, [1, 2], 'hi', width=10, color='red'))
        assert_that(self.spy.foo, is_not(called_with(
                [1, 2], 'hi', width=10, color='red')))
        assert_that(self.spy.foo, is_not(called_with(
                [1, 2], 3.0, 'hi', width=10, color='red')))

    def test_called_with_args_and_times(self):
        self.spy.foo(1)
        self.spy.foo(1)
        self.spy.foo(2)

        assert_that(self.spy.foo, called_with(1).times(2))
        assert_that(self.spy.foo, called_with(2))
        assert_that(self.spy.foo, called().times(3))


class VerifiedSpyTests(TestCase):
    def setUp(self):
        self.spy = Spy(Collaborator())

    def test_from_instance(self):
        spy = Spy(Collaborator())
        spy.hello()

        assert_that(spy.hello, called())

    def test_call_unexisting_method(self):
        try:
            self.spy.wrong()
            self.fail('AttributeError should be raised')
        except AttributeError as e:
            expected = "'Collaborator' object has no attribute 'wrong'"
            assert_that(str(e), contains_string(expected))

    def test_check_unexisting_method(self):
        try:
            assert_that(self.spy.wrong, called())
            self.fail('AttributeError should be raised')
        except AttributeError as e:
            expected = "'Collaborator' object has no attribute 'wrong'"
            assert_that(str(e), contains_string(expected))

    def test_create_from_oldstyle_class(self):
        self.spy = Spy(Collaborator)

    def test_create_from_newstyle_class(self):
        self.spy = Spy(ObjCollaborator)


class ProxySpyTest(TestCase):
    def test_must_give_argument(self):
        self.failUnlessRaises(TypeError, ProxySpy)

    def test_given_argument_can_not_be_oldstyle_class(self):
        self.failUnlessRaises(TypeError,
                              ProxySpy, Collaborator)

    def test_given_argument_can_not_be_newstyle_class(self):
        self.failUnlessRaises(TypeError,
                              ProxySpy, ObjCollaborator)


class MockTests(TestCase):
    def setUp(self):
        self.mock = Mock()

    def test_order_matters__ok(self):
        with self.mock:
            self.mock.foo()
            self.mock.bar()

        self.mock.foo()
        self.mock.bar()

        assert_that(self.mock, verify())

    def test_order_matters__fail(self):
        with self.mock:
            self.mock.foo()
            self.mock.bar()

        self.mock.bar()
        self.mock.foo()

        self.failUnlessRaises(
            AssertionError,
            assert_that, self.mock, verify())

    def test_method_name_order_does_not_matter_with_any_order(self):
        with self.mock:
            self.mock.foo()
            self.mock.bar()

        self.mock.bar()
        self.mock.foo()

        assert_that(self.mock, any_order_verify())

    def test_args_order_does_not_matter_with_any_order(self):
        with self.mock:
            self.mock.foo(2)
            self.mock.foo(1)

        self.mock.foo(1)
        self.mock.foo(2)

        assert_that(self.mock, any_order_verify())

    def test_kwargs_order_does_not_matter_with_any_order(self):
        with self.mock:
            self.mock.foo(1, key='a')
            self.mock.foo(1, key='b')

        self.mock.foo(1, key='b')
        self.mock.foo(1, key='a')

        assert_that(self.mock, any_order_verify())


class VerifiesMockTests(TestCase):
    def test_from_instance(self):
        mock = Mock(Collaborator())
        with mock:
            mock.hello()

        mock.hello()

        assert_that(mock, verify())


class DisplayResultsTests(TestCase):
    def setUp(self):
        with Spy() as self.empty_spy:
            self.empty_spy.foo(ANY_ARG).returns(True)

        with Spy(Collaborator) as self.spy:
            self.spy.method_one(ANY_ARG).returns(2)

    def test_empty_spy_stub_method(self):
        assert_that(self.empty_spy.foo.show_history(),
                    "method 'Spy.foo' never invoked")

    def test_spy_stub_method(self):
        assert_that(self.spy.method_one.show_history(),
                    "method 'Collaborator.method_one' never invoked")

    def test_empty_spy_stub_method_invoked(self):
        self.empty_spy.foo()
        expected = [
            "method 'Spy.foo' was invoked",
            "foo()"]
        assert_that(self.empty_spy.foo.show_history(),
                    string_contains_in_order(*expected))

    def test_spy_stub_method_invoked(self):
        self.spy.method_one(1)
        expected = [
            "method 'Collaborator.method_one' was invoked",
            'method_one(1)']
        assert_that(self.spy.method_one.show_history(),
                    string_contains_in_order(*expected))

    def test_empty_spy_non_stubbed_method_invoked(self):
        self.empty_spy.bar(1, 3.0, "text", key1="text", key2=[1, 2])
        expected = [
            "method 'Spy.bar' was invoked",
            "bar(1, 3.0, 'text', key1='text', key2=[1, 2])"]
        assert_that(self.empty_spy.bar.show_history(),
                    string_contains_in_order(*expected))

    def test_spy_several_invoked_same_method(self):
        self.spy.mixed_method(5, True)
        self.spy.mixed_method(8, False)

        expected = "method 'Collaborator.mixed_method' was invoked"
        assert_that(self.spy.mixed_method.show_history(),
                    contains_string(expected))


class FrameworApiTest(TestCase):
    def test_called_requires_spy(self):
        stub = Stub()
        try:
            assert_that(stub.method, called())
            self.fail('exception should be raised')
        except WrongApiUsage as e:
            assert_that(str(e), contains_string('takes a spy method (got'))


class ApiMismatchTest(TestCase):
    def setUp(self):
        self.spy = Spy(Collaborator)

    def test_default_params(self):
        self.spy.mixed_method(1)

    def test_give_karg(self):
        self.spy.mixed_method(1, key_param=True)

    def test_give_karg_without_key(self):
        self.spy.mixed_method(1, True)

    def test_fail_missing_method(self):
        try:
            self.spy.missing()
            self.fail("TypeError should be raised")

        except AttributeError, e:
            expected = "'Collaborator' object has no attribute 'missing'"
            assert_that(str(e), contains_string(expected))

    def test_fail_wrong_args(self):
        try:
            self.spy.hello("wrong")
            self.fail("TypeError should be raised")

        except TypeError, e:
            expected = "Collaborator.hello() takes exactly 1 argument (2 given)"
            assert_that(str(e), contains_string(expected))

    def test_fail_wrong_kargs(self):
        try:
            self.spy.kwarg_method(wrong_key=1)
            self.fail("TypeError should be raised")

        except TypeError, e:
            expected = "Collaborator.kwarg_method() got an unexpected keyword argument 'wrong_key'"
            assert_that(str(e), contains_string(expected))


class ANY_ARG_StubTests(TestCase):
    def setUp(self):
        self.stub = Stub()

    def test_any_args(self):
        with self.stub:
            self.stub.foo(ANY_ARG).returns(True)

        assert_that(self.stub.foo(), is_(True))
        assert_that(self.stub.foo(1), is_(True))
        assert_that(self.stub.foo(key1='a'), is_(True))
        assert_that(self.stub.foo(1, 2, 3, key1='a', key2='b'), is_(True))

    def test_fixed_args_and_any_args(self):
        with self.stub:
            self.stub.foo(1, ANY_ARG).returns(True)

        assert_that(self.stub.foo(1, 2, 3), is_(True))
        assert_that(self.stub.foo(1, key1='a'), is_(True))


class ANY_ARG_SpyTests(TestCase):
    def setUp(self):
        self.spy = Spy()

    def test_no_args(self):
        self.spy.foo()
        assert_that(self.spy.foo, called_with(ANY_ARG))

    def test_one_arg(self):
        self.spy.foo(1)
        assert_that(self.spy.foo, called_with(ANY_ARG))

    def test_one_karg(self):
        self.spy.foo(key='val')
        assert_that(self.spy.foo, called_with(ANY_ARG))

    def test_three_args(self):
        self.spy.foo(1, 2, 3)
        assert_that(self.spy.foo, called_with(1, ANY_ARG))
        assert_that(self.spy.foo, never(called_with(2, ANY_ARG)))

    def test_args_and_kargs(self):
        self.spy.foo(1, 2, 3, key1='a', key2='b')
        assert_that(self.spy.foo, called_with(1, ANY_ARG))
        assert_that(self.spy.foo, never(called_with(2, ANY_ARG)))

    def test__called__and__called_with__any_args_is_the_same(self):
        self.spy.foo()
        self.spy.foo(3)
        self.spy.foo('hi')
        self.spy.foo(None)

        assert_that(self.spy.foo, called().times(4))
        assert_that(self.spy.foo, called_with(ANY_ARG).times(4))


class MatcherTests(TestCase):
    def setUp(self):
        self.spy = Spy()

    def test_check_has_length(self):
        self.spy.foo("abcd")

        assert_that(self.spy.foo, called_with(has_length(4)))
        assert_that(self.spy.foo, called_with(has_length(greater_than(3))))
        assert_that(self.spy.foo, called_with(has_length(less_than(5))))
        assert_that(self.spy.foo,
                    is_not(called_with(has_length(greater_than(5)))))

    def test_stub_has_length(self):
        with self.spy:
            self.spy.foo(has_length(less_than(4))).returns('<4')
            self.spy.foo(has_length(4)).returns('four')
            self.spy.foo(
                has_length(
                    all_of(greater_than(4),
                           less_than(8)))).returns('4<x<8')
            self.spy.foo(has_length(greater_than(8))).returns('>8')

        assert_that(self.spy.foo((1, 2)), is_('<4'))
        assert_that(self.spy.foo('abcd'), is_('four'))
        assert_that(self.spy.foo('abcde'), is_('4<x<8'))
        assert_that(self.spy.foo([0] * 9), is_('>8'))

    def test_stub_contains_string(self):
        with Stub() as stub:
            stub.method(contains_string("some")).returns(1000)

        assert_that(stub.method("awesome"), is_(1000))

    # doc
    def test_times_arg_may_be_matcher(self):
        self.spy.foo()
        self.spy.foo(1)
        self.spy.foo(1)
        self.spy.foo(2)

        assert_that(self.spy.never, is_not(called()))                    # = 0 times
        assert_that(self.spy.foo, called())                              # > 0
        assert_that(self.spy.foo, called().times(greater_than(0)))       # > 0 (same)
        assert_that(self.spy.foo, called().times(4))                     # = 4
        assert_that(self.spy.foo, called().times(greater_than(2)))       # > 2
        assert_that(self.spy.foo, called().times(less_than(6)))          # < 6

        assert_that(self.spy.foo, is_not(called_with(5)))                 # = 0 times
        assert_that(self.spy.foo, called_with().times(1))                 # = 1
        assert_that(self.spy.foo, called_with(anything()))                # > 0
        assert_that(self.spy.foo, called_with(anything()).times(4))       # = 4
        assert_that(self.spy.foo, called_with(1).times(2))                # = 2
        assert_that(self.spy.foo, called_with(1).times(greater_than(1)))  # > 1
        assert_that(self.spy.foo, called_with(1).times(less_than(5)))     # < 5

    # doc
    def test_called_args(self):
        self.spy.m1()
        self.spy.m2(None)
        self.spy.m3(2)
        self.spy.m4("hi", 3.0)
        self.spy.m5([1, 2])
        self.spy.m6(name="john doe")

        assert_that(self.spy.m1, called())
        assert_that(self.spy.m2, called())

        assert_that(self.spy.m1, called_with())
        assert_that(self.spy.m2, called_with(None))
        assert_that(self.spy.m3, called_with(2))
        assert_that(self.spy.m4, called_with("hi", 3.0))
        assert_that(self.spy.m5, called_with([1, 2]))
        assert_that(self.spy.m6, called_with(name="john doe"))

        assert_that(self.spy.m3, called_with(less_than(3)))
        assert_that(self.spy.m3, called_with(greater_than(1)))
        assert_that(self.spy.m6, called_with(name=contains_string("doe")))


class StubObserverTests(TestCase):
    def setUp(self):
        self.stub = Stub()

    def test_observer_called(self):
        observer = Observer()
        self.stub.foo.attach(observer.update)
        self.stub.foo(2)

        assert_that(observer.state, is_(2))

    def test_observer_called_tested_using_a_doublex_spy(self):
        observer = Spy()
        self.stub.foo.attach(observer.update)
        self.stub.foo(2)

        assert_that(observer.update, called_with(2))


class StubDelegateTests(TestCase):
    def setUp(self):
        self.stub = Stub()

    def assert_012(self, method):
        for x in range(3):
            assert_that(method(), is_(x))

    def test_delegate_to_other_method(self):
        with self.stub:
            self.stub.foo().delegates(Collaborator().hello)

        assert_that(self.stub.foo(), is_("hello"))

    def test_delegate_to_list(self):
        with self.stub:
            self.stub.foo().delegates(range(3))

        self.assert_012(self.stub.foo)

    def test_delegate_to_generator(self):
        with self.stub:
            self.stub.foo().delegates(x for x in range(3))

        self.assert_012(self.stub.foo)

    def test_delegate_to_count(self):
        with self.stub:
            self.stub.foo().delegates(itertools.count())

        self.assert_012(self.stub.foo)

    def test_delegate_to_lambda(self):
        with self.stub:
            self.stub.foo().delegates(lambda: 2)

        assert_that(self.stub.foo(), is_(2))

    def test_delegate_to_another_stub(self):
        stub2 = Stub()
        with stub2:
            stub2.bar().returns("hi!")

        with self.stub:
            self.stub.foo().delegates(stub2.bar)

        assert_that(self.stub.foo(), is_("hi!"))

    def test_not_delegable_object(self):
        try:
            with self.stub:
                self.stub.foo().delegates(None)
            fail("Exception should be raised")

        except WrongApiUsage, e:
            expected = "delegates() must be called with callable or iterable instance (got 'None' instead)"
            assert_that(str(e), contains_string(expected))


class MimicTests(TestCase):
    class A(object):
        def method_a(self, n):
            return n + 1

    class B(A):
        def method_b(self):
            return "hi"

    def test_normal_spy_does_not_inherit_collaborator_superclasses(self):
        spy = Spy(self.B)
        assert_that(not isinstance(spy, self.B))

    def test_mimic_spy_DOES_inherit_collaborator_superclasses(self):
        spy = Mimic(Spy, self.B)
        for cls in [self.B, self.A, SpyProto, StubProto, object]:
            assert_that(isinstance(spy, cls), cls)

    def test_mimic_stub_works(self):
        stub = Mimic(Stub, self.B)
        with stub:
            stub.method_a(2).returns(3)

        assert_that(stub.method_a(2), is_(3))

    def test_mimic_stub_from_instance(self):
        stub = Mimic(Stub, self.B())
        with stub:
            stub.method_a(2).returns(3)

        assert_that(stub.method_a(2), is_(3))

    def test_mimic_spy_works(self):
        spy = Mimic(Spy, self.B)
        with spy:
            spy.method_a(5).returns(True)

        assert_that(spy.method_a(5), is_(True))

        assert_that(spy.method_a, called())
        assert_that(spy.method_a, called_with(5))

    def test_mimic_proxy_spy_works(self):
        spy = Mimic(ProxySpy, self.B())
        assert_that(spy.method_a(5), is_(6))

        assert_that(spy.method_a, called())
        assert_that(spy.method_a, called_with(5))

    def test_mimic_mock_works(self):
        mock = Mimic(Mock, self.B)
        with mock:
            mock.method_a(2)

        mock.method_a(2)

        assert_that(mock, verify())


class DoublePropertiesTests(TestCase):
    def test_stub_notset_property_is_None(self):
        stub = Stub(ObjCollaborator)
        assert_that(stub.prop, is_(None))

    def test_stub_property(self):
        stub = Stub(ObjCollaborator)
        with stub:
            stub.prop = 2

        assert_that(stub.prop, is_(2))

    def test_spy_get_property(self):
        spy = Spy(ObjCollaborator)
        discard = spy.prop
        assert_that(spy, property_got('prop'))

    def test_spy_not_get_property(self):
        spy = Spy(ObjCollaborator)
        assert_that(spy, is_not(property_got('prop')))

    def test_spy_get_property_fail(self):
        spy = Spy(ObjCollaborator)
        self.failUnlessRaises(
            AssertionError,
            assert_that, spy, property_got('prop'))

    def test_spy_set_property(self):
        spy = Spy(ObjCollaborator)
        spy.prop = 2
        assert_that(spy, property_set('prop'))

    def test_spy_not_set_property(self):
        spy = Spy(ObjCollaborator)
        assert_that(spy, is_not(property_set('prop')))

    def test_spy_set_property_fail(self):
        spy = Spy(ObjCollaborator)
        self.failUnlessRaises(
            AssertionError,
            assert_that, spy, property_set('prop'))

    def test_properties_are_not_shared(self):
        stub1 = Stub(ObjCollaborator)
        stub2 = Stub()

        stub1.prop = 1000
        assert_that(stub2.prop, is_not(1000))




class Observer(object):
    def __init__(self):
        self.state = None

    def update(self, *args, **kargs):
        self.state = args[0]


class ObjCollaborator(object):
    def __init__(self):
        self._propvalue = 1

    def no_args(self):
        return 1

    def prop_getter(self):
        return self._propvalue

    def prop_setter(self, value):
        self._propvalue = value

    prop = property(prop_getter, prop_setter)


#----------------------------#
#- pyDoubles migrated tests -#
#----------------------------#

class SomeException(Exception):
    pass


class Collaborator:
    """
    The original object we double in tests
    """
    test_field = "OK"

    def hello(self):
        return "hello"

    def something(self):
        return "ok"

    def one_arg_method(self, arg1):
        return arg1

    def two_args_method(self, arg1, arg2):
        return arg1 + arg2

    def kwarg_method(self, key_param=False):
        return key_param

    def mixed_method(self, arg1, key_param=False):
        return key_param + arg1

    def void_method(self):
        pass

    def method_one(self, arg1):
        return 1

    alias_method = one_arg_method


class pyDoubles__ProxySpyTests(TestCase):
    def setUp(self):
        self.spy = ProxySpy(Collaborator())

    #SAME as pyDoublesSpyTests.test_override_original_method_and_is_called
    def test_assert_was_called(self):
        self.spy.hello()

        assert_that(self.spy.hello, called())

    def test_assert_was_called_on_any_method(self):
        self.spy.something()

        assert_that(self.spy.something, called())

    def test_assert_needs_always_a_method_from_a_double(self):
        self.failUnlessRaises(
            WrongApiUsage,
            assert_that, self.spy, called())

    def test_assert_needs_always_a_method_from_a_double_not_the_original(self):
        self.failUnlessRaises(
            WrongApiUsage,
            assert_that, Collaborator().hello, called())

    def test_one_method_called_other_wasnt(self):
        self.spy.something()

        self.failUnlessRaises(
            AssertionError,
            assert_that, self.spy.hello, called())

    def test_two_methods_called_assert_on_the_first(self):
        self.spy.hello()
        self.spy.something()

        assert_that(self.spy.hello, called())

#    # This is testing internal API! Not applicable
#    def test_get_method_name(self):
#        name = _Introspector_().method_name(self.spy.hello)
#
#        self.assertEquals("hello", name)

    def test_call_original_method(self):
        self.assertEquals("ok", self.spy.something())

#    # This is testing internal API! Not applicable
#    def test_get_instance_from_method(self):
#        spy_found = _Introspector_().double_instance_from_method(self.spy.hello)
#
#        self.assertEquals(self.spy, spy_found)

    def test_assert_was_called_when_wasnt(self):
        self.failUnlessRaises(
            AssertionError,
            assert_that, self.spy.hello, called())

    def test_was_called_with_same_parameters(self):
        self.spy.one_arg_method(1)

        assert_that(self.spy.one_arg_method, called_with(1))

    # this is exactly the same that previous! :-S
    def test_was_called_with_same_parameters_in_variables(self):
        arg1 = 1
        self.spy.one_arg_method(arg1)

        assert_that(self.spy.one_arg_method, called_with(1))

    def test_was_called_with_same_parameters_when_not(self):
        self.spy.one_arg_method(1)
        args_checker = called_with(2)

        assert_that(not args_checker.matches(self.spy.one_arg_method))

    def test_was_called_with_same_params_but_no_params_accepted(self):
        self.spy.hello()
        args_checker = called_with("something")

        assert_that(not args_checker.matches(self.spy.hello))

    def test_was_called_with_several_parameters(self):
        self.spy.two_args_method(1, 2)
        args_checker = called_with(1, 2)

        assert_that(args_checker.matches(self.spy.two_args_method))

    #SAME as test_was_called_with_same_parameters_when_not
    def test_was_called_with_parameters_not_matching(self):
        self.spy.one_arg_method(1)
        args_checker = called_with("2")

        assert_that(not args_checker.matches(self.spy.one_arg_method))

    def test_was_called_with_keyed_args_not_matching(self):
        self.spy.kwarg_method(key_param="foo")
        args_checker = called_with(key_param="bar")

        assert_that(not args_checker.matches(self.spy.kwarg_method))

    def test_was_called_with_keyed_args_matching(self):
        self.spy.kwarg_method(key_param="foo")
        assert_that(self.spy.kwarg_method, called_with(key_param="foo"))

    def test_recorded_call_params_are_displayed(self):
        self.spy.kwarg_method(key_param="foo")
        try:
            assert_that(self.spy.kwarg_method, called_with("bar"))
        except AssertionError, e:
            assert_that(str(e), contains_string("foo"))

    def test_stub_out_method(self):
        with self.spy:
            self.spy.one_arg_method(ANY_ARG).returns(3)

        self.assertEquals(3, self.spy.one_arg_method(5))

    def test_stub_method_was_called(self):
        with self.spy:
            self.spy.one_arg_method(ANY_ARG).returns(3)

        self.spy.one_arg_method(5)
        assert_that(self.spy.one_arg_method, called_with(5))

    def test_stub_out_method_returning_a_list(self):
        with self.spy:
            self.spy.one_arg_method(ANY_ARG).returns([1, 2, 3])

        assert_that(self.spy.one_arg_method(5), is_([1, 2, 3]))

    def test_stub_method_returning_list_was_called(self):
        with self.spy:
            self.spy.one_arg_method(ANY_ARG).returns([1, 2, 3])

        self.spy.one_arg_method(5)

        assert_that(self.spy.one_arg_method, called_with(5))

    def test_stub_out_method_with_args(self):
        with self.spy:
            self.spy.one_arg_method(2).returns(3)

        assert_that(self.spy.one_arg_method(2), is_(3))

    def test_stub_method_with_args_was_called(self):
        with self.spy:
            self.spy.one_arg_method(2).returns(3)

        self.spy.one_arg_method(2)

        assert_that(self.spy.one_arg_method, called_with(2))

    def test_stub_out_method_with_args_calls_actual(self):
        with self.spy:
            self.spy.one_arg_method(2).returns(3)

        assert_that(self.spy.one_arg_method(4), is_(4))
        assert_that(self.spy.one_arg_method, called_with(4))

    def test_stub_out_method_with_several_inputs(self):
        with self.spy:
            self.spy.one_arg_method(2).returns(3)
            self.spy.one_arg_method(3).returns(4)

        assert_that(self.spy.one_arg_method(2), is_(3))
        assert_that(self.spy.one_arg_method(3), is_(4))

    def test_recorded_calls_work_on_several_stubs(self):
        with self.spy:
            self.spy.one_arg_method(2).returns(3)
            self.spy.one_arg_method(3).returns(4)

        self.spy.one_arg_method(2)
        self.spy.one_arg_method(3)
        assert_that(self.spy.one_arg_method, called_with(2))
        assert_that(self.spy.one_arg_method, called_with(3))

    def test_matching_stub_definition_is_used(self):
        with self.spy:
            self.spy.one_arg_method(ANY_ARG).returns(1000)
            self.spy.one_arg_method(2).returns(3)

        assert_that(self.spy.one_arg_method(2), is_(3))
        assert_that(self.spy.one_arg_method(8), is_(1000))

    def test_stub_with_kwargs(self):
        with self.spy:
            self.spy.kwarg_method(key_param=2).returns(3)

        assert_that(self.spy.kwarg_method(key_param=2), is_(3))
        assert_that(self.spy.kwarg_method(key_param=6), is_(6))

    def test_stub_raising_exception(self):
        with self.spy:
            self.spy.hello().raises(SomeException)

        try:
            self.spy.hello()
            self.fail("not raised")
        except SomeException:
            pass

    def test_stub_returning_what_receives(self):
        with self.spy:
            self.spy.method_one(ANY_ARG).returns_input()

        assert_that(self.spy.method_one(20), is_(20))

    # Different that pyDoubles. exception raised at setup
    def test_stub_returning_what_receives_when_no_params(self):
        try:
            with self.spy:
                self.spy.hello().returns_input()

            self.fail("TypeError should be raised")
        except TypeError, e:
            assert_that(str(e),
                        contains_string("Collaborator.hello() has no input args"))

    def test_be_able_to_return_objects(self):
        with self.spy:
            self.spy.one_arg_method(ANY_ARG).returns(Collaborator())

        collaborator = self.spy.one_arg_method(1)

        assert_that(collaborator.one_arg_method(1), is_(1))

    def test_any_arg_matcher(self):
        with self.spy:
            self.spy.two_args_method(1, ANY_ARG).returns(1000)

        assert_that(self.spy.two_args_method(1, 2), is_(1000))
        assert_that(self.spy.two_args_method(1, 5), is_(1000))
        assert_that(self.spy.two_args_method(3, 5), is_not(1000))

    # Not supported by pyDoubles
    def test_any_arg_matcher_with_kwargs(self):
        with self.spy:
            self.spy.kwarg_method(key_param=anything()).returns(1000)

        self.assertEquals(1000, self.spy.kwarg_method(key_param=2))

    def test_any_arg_matcher_was_called(self):
        with self.spy:
            self.spy.two_args_method(1, 2).returns(1000)

        self.spy.two_args_method(1, 2)

        assert_that(self.spy.two_args_method, called_with(1, ANY_ARG))

    def test_stub_works_with_alias_method(self):
        with self.spy:
            self.spy.one_arg_method(1).returns(1000)

        self.spy.alias_method(1)
        assert_that(self.spy.one_arg_method, called_with(1))

    def test_was_never_called(self):
        assert_that(self.spy.one_arg_method, is_not(called()))

    def test_was_never_called_is_false(self):
        self.spy.one_arg_method(1)
        try:
            assert_that(self.spy.one_arg_method, is_not(called()))
            self.fail("it was called indeed!")
        except AssertionError:
            pass

    def test_expect_several_times(self):
        self.spy.one_arg_method(1)

        try:
            assert_that(self.spy.one_arg_method, called().times(2))
            self.fail("Should have been called 2 times")
        except AssertionError:
            pass

    def test_fail_incorrect_times_msg_is_human_readable(self):
        self.spy.one_arg_method(1)

        try:
            assert_that(self.spy.one_arg_method, called().times(5))
            self.fail("Should have been called 5 times")
        except AssertionError, e:
            assert_that(str(e), contains_string("5"))
            assert_that(str(e), contains_string("one_arg_method"))

    def test_expect_several_times_matches_exactly(self):
        self.spy.one_arg_method(1)
        self.spy.one_arg_method(1)
        assert_that(self.spy.one_arg_method, called().times(2))

    def test_expect_several_times_with_args_definition(self):
        self.spy.one_arg_method(1)
        self.spy.one_arg_method(1)
        assert_that(self.spy.one_arg_method, called_with(1).times(2))

    def test_expect_several_times_with_incorrect_args(self):
        self.spy.one_arg_method(1)
        self.spy.one_arg_method(1)

        try:
            assert_that(self.spy.one_arg_method, called_with(2).times(2))
            self.fail("Must have 1 as an argument")
        except AssertionError:
            pass

    def test_args_match_but_not_number_of_times(self):
        self.spy.one_arg_method(1)
        self.spy.one_arg_method(2)
        try:
            assert_that(self.spy.one_arg_method,
                        called_with(1).times(2))
            self.fail("Wrong assertion")
        except AssertionError:
            pass


class pyDoubles__SpyTests(TestCase):
    def setUp(self):
        self.spy = Spy(Collaborator())

    def test_override_original_method(self):
        self.assertTrue(self.spy.hello() is None)

    def test_override_original_method_and_is_called(self):
        self.spy.hello()
        assert_that(self.spy.hello, called())

    def test_spy_without_args_is_empty_spy(self):
        self.spy = Spy()
        self.assertTrue(self.spy.hello() is None)

    def test_spy_can_work_from_empty_and_is_called(self):
        self.spy.hello()
        assert_that(self.spy.hello, called())

    def test_spy_based_on_object_must_check_api_match(self):
        try:
            self.spy.hello("unexpected argument")
            self.fail('Expection should raise: Actual object does not accept parameters')
        except TypeError:
            pass

    def test_check_api_match_with_kwargs(self):
        self.assertTrue(self.spy.mixed_method(1, key_param=2) is None)

    def test_check_api_match_with_kwargs_not_used(self):
        self.assertTrue(self.spy.mixed_method(1) is None)

    def test_check_api_match_with_kwargs_not_matching(self):
        try:
            self.spy.mixed_method(1, 2, 3)
            self.fail('TypeError not detected!')
        except TypeError:
            pass

    def test_match_call_with_unicode_and_non_ascii_chars(self):
        non_ascii  = u'España'
        self.spy.one_arg_method(non_ascii)

        assert_that(self.spy.one_arg_method, called_with(non_ascii))

    def test_stub_methods_can_be_handled_separately(self):
        with self.spy:
            self.spy.one_arg_method(1).returns(1000)
            self.spy.two_args_method(5, 5).returns(2000)

        handle1 = self.spy.one_arg_method
        handle2 = self.spy.two_args_method

        self.assertEquals(1000, handle1(1))
        self.assertEquals(2000, handle2(5, 5))
        assert_that(handle1, called_with(1))
        assert_that(handle2, called_with(5, 5))

    #SAME as VerifiedSpyTests.test_check_unexisting_method
    def test_assert_was_called_with_method_not_in_the_api(self):
        try:
            assert_that(self.spy.unexisting_method, called())
            self.fail("AttributeError should be raised")
        except AttributeError:
            pass

    def test_do_not_call_callable_object_if_wasnt_generated_by_the_framework(self):
        class CallableObj():
            just_testing = True

            def __call__(self, *args, **kwargs):
                raise Exception('should not happen')

        obj = CallableObj()
        with self.spy:
            self.spy.one_arg_method(ANY_ARG).returns(obj)

        self.assertEquals(obj, self.spy.one_arg_method(1),
                          "Wrong returned object")


class pyDoubles__MockTests(TestCase):
    def setUp(self):
        self.mock = Mock(Collaborator)

    def test_fail_on_unexpected_call(self):
        try:
            self.mock.hello()
            self.fail('AssertionError should be raised')
        except AssertionError:
            pass

    def test_fail_on_unexpected_call_msg_is_human_readable(self):
        try:
            self.mock.hello()
        except AssertionError, e:
            assert_that(str(e), contains_string("No one"))

    def test_define_expectation_and_call_method(self):
        with self.mock:
            self.mock.hello()

        self.assertTrue(self.mock.hello() is None)

    def test_define_several_expectatiosn(self):
        with self.mock:
            self.mock.hello()
            self.mock.one_arg_method(ANY_ARG)

        self.assertTrue(self.mock.hello() is None)
        self.assertTrue(self.mock.one_arg_method(1) is None)

    def test_define_expectation_args(self):
        with self.mock:
            self.mock.one_arg_method(1)

        self.assertTrue(self.mock.one_arg_method(1) is None)

    def test_define_expectation_args_and_fail(self):
        with self.mock:
            self.mock.one_arg_method(1)

        try:
            self.mock.one_arg_method(2)
            self.fail('Unexpected call')
        except AssertionError:
            pass

    def test_several_expectations_with_args(self):
        with self.mock:
            self.mock.one_arg_method(1)
            self.mock.two_args_method(2, 3)

        self.assertTrue(self.mock.one_arg_method(1) is None)
        self.assertTrue(self.mock.two_args_method(2, 3) is None)

    def test_expect_call_returning_value(self):
        with self.mock:
            self.mock.one_arg_method(1).returns(1000)

        self.assertEquals(1000, self.mock.one_arg_method(1))

    def test_assert_expectations_are_satisfied(self):
        with self.mock:
            self.mock.hello()

        assert_that(self.mock, is_not(verify()))

    def test_assert_satisfied_when_it_really_is(self):
        with self.mock:
            self.mock.hello()

        self.mock.hello()
        assert_that(self.mock, verify())

    def test_number_of_calls_matter(self):
        with self.mock:
            self.mock.hello()

        self.mock.hello()
        self.mock.hello()

        assert_that(self.mock, is_not(verify()))

    # Not applicable to doublex
#    def test_using_when_or_expect_call_without_double(self):
#        self.failUnlessRaises(WrongApiUsage,
#                        expect_call, Collaborator())

    def test_expectations_on_synonyms(self):
        with self.mock:
            self.mock.one_arg_method(ANY_ARG)

        self.mock.alias_method(1)

        assert_that(self.mock, verify())

    def test_several_expectations_with_different_args(self):
        with self.mock:
            self.mock.one_arg_method(1)
            self.mock.one_arg_method(2)

        self.mock.one_arg_method(1)
        self.mock.one_arg_method(1)

        assert_that(self.mock, is_not(verify()))

    def test_expect_several_times(self):
        with self.mock:
            self.mock.one_arg_method(1).times(2)

        self.mock.one_arg_method(1)

        assert_that(self.mock, is_not(verify()))

    def test_expect_several_times_matches_exactly(self):
        with self.mock:
            self.mock.one_arg_method(1).times(2)

        self.mock.one_arg_method(1)
        self.mock.one_arg_method(1)

        assert_that(self.mock, verify())

    def test_expect_several_times_without_args_definition(self):
        with self.mock:
            self.mock.one_arg_method(ANY_ARG).times(2)

        self.mock.one_arg_method(1)
        self.mock.one_arg_method(1)

        assert_that(self.mock, verify())

    def test_defend_agains_less_than_2_times(self):
        try:
            with self.mock:
                self.mock.one_arg_method(ANY_ARG).times(0)

            self.fail('times cant be less than 1')
        except WrongApiUsage:
            pass

    def test_times_and_return_value(self):
        with self.mock:
            self.mock.one_arg_method(ANY_ARG).returns(1000).times(2)

        self.assertEquals(1000, self.mock.one_arg_method(1))
        self.assertEquals(1000, self.mock.one_arg_method(1))

        assert_that(self.mock, verify())

    def test_times_and_return_value_and_input_args(self):
        with self.mock:
            self.mock.one_arg_method(10).returns(1000).times(2)

        self.assertEquals(1000, self.mock.one_arg_method(10))
        self.assertEquals(1000, self.mock.one_arg_method(10))

        assert_that(self.mock, verify())


class pyDoubles__MockFromEmptyObjectTests(TestCase):
    def setUp(self):
        self.mock = Mock()

    def test_mock_can_work_from_empty_object(self):
        with self.mock as mock:
            mock.hello()

        self.mock.hello()

        assert_that(self.mock, verify())

    # Not applicable to doublex
    def test_mock_without_args_is_empty_mock(self):
        pass

    def test_several_expectations_in_empty_mock(self):
        with self.mock:
            self.mock.hello()
            self.mock.one_arg_method(1)

        self.mock.hello()
        self.mock.one_arg_method(1)

        assert_that(self.mock, verify())

    def test_several_expectations_with_args_in_empty_mock(self):
        with self.mock:
            self.mock.one_arg_method(1)
            self.mock.one_arg_method(2)

        self.assertTrue(self.mock.one_arg_method(1) is None)
        self.assertTrue(self.mock.one_arg_method(2) is None)

        assert_that(self.mock, verify())


class pyDoubles__StubMethodsTests(TestCase):
    def setUp(self):
        self.collaborator = Collaborator()

    def test_method_returning_value(self):
        self.collaborator.hello = method_returning("bye")

        self.assertEquals("bye", self.collaborator.hello())

    def test_method_args_returning_value(self):
        self.collaborator.one_arg_method = method_returning("bye")

        self.assertEquals("bye", self.collaborator.one_arg_method(1))

    def test_method_raising_exception(self):
        self.collaborator.hello = method_raising(SomeException)
        try:
            self.collaborator.hello()
            self.fail("exception not raised")
        except SomeException:
            pass


class pyDoubles__MatchersTests(TestCase):
    def setUp(self):
        self.spy = Spy(Collaborator)

    def test_str_cotaining_with_exact_match(self):
        with self.spy:
            self.spy.one_arg_method(contains_string("abc")).returns(1000)

        self.assertEquals(1000, self.spy.one_arg_method("abc"))

    def test_str_containing_with_substr(self):
        with self.spy:
            self.spy.one_arg_method(contains_string("abc")).returns(1000)

        self.assertEquals(1000, self.spy.one_arg_method("XabcX"))

    def test_str_containing_with_substr_unicode(self):
        with self.spy:
            self.spy.one_arg_method(contains_string("abc")).returns(1000)

        self.assertEquals(1000, self.spy.one_arg_method(u"XabcñX"))

    def test_str_containing_but_matcher_not_used(self):
        with self.spy:
            self.spy.one_arg_method("abc").returns(1000)

        self.assertNotEquals(1000, self.spy.one_arg_method("XabcX"))

    def test_was_called_and_substr_matcher(self):
        self.spy.one_arg_method("XabcX")

        assert_that(self.spy.one_arg_method,
                    called_with(contains_string("abc")))

    def test_str_not_containing(self):
        with self.spy:
            self.spy.one_arg_method(is_not(contains_string("abc"))).returns(1000)

        self.assertNotEquals(1000, self.spy.one_arg_method("abc"))

    def test_str_not_containing_stubs_anything_else(self):
        with self.spy:
            self.spy.one_arg_method(is_not(contains_string("abc"))).returns(1000)

        self.assertEquals(1000, self.spy.one_arg_method("xxx"))

    def test_str_not_containing_was_called(self):
        self.spy.one_arg_method("abc")
        assert_that(self.spy.one_arg_method,
                    called_with(is_not(contains_string("xxx"))))

    def test_several_matchers(self):
        with self.spy:
            self.spy.two_args_method(
                contains_string("abc"),
                contains_string("xxx")).returns(1000)

        self.assertNotEquals(1000,
                             self.spy.two_args_method("abc", "yyy"))

    def test_str_length_matcher(self):
        with self.spy:
            self.spy.one_arg_method(has_length(5)).returns(1000)

        self.assertEquals(1000,
                          self.spy.one_arg_method("abcde"))

    def test_matchers_when_passed_arg_is_none(self):
        with self.spy:
            self.spy.one_arg_method(has_length(5)).returns(1000)

        self.assertTrue(self.spy.one_arg_method(None) is None)

    def test_compare_objects_is_not_possible_without_eq_operator(self):
        class SomeObject():
            field1 = field2 = None

        obj = SomeObject()
        obj2 = SomeObject()
        self.spy.one_arg_method(obj)

        try:
            assert_that(self.spy.one_arg_method, called_with(obj2))
            self.fail("they should not match")
        except AssertionError:
            pass

    def test_if_doesnt_match_message_is_human_redable(self):
        self.spy.one_arg_method("XabcX")

        try:
            assert_that(self.spy.one_arg_method,
                        called_with(contains_string("xxx")))

        except AssertionError, e:
            assert_that(str(e), contains_string("xxx"))
            assert_that(
                str(e), contains_string("string containing"))

    def test_obj_with_field_matcher(self):
        obj = Collaborator()
        obj.id = 20
        self.spy.one_arg_method(obj)

        assert_that(self.spy.one_arg_method,
                    called_with(has_property('id', 20)))

    def test_obj_with_several_fields_matcher(self):
        obj = Collaborator()
        obj.id = 21
        self.spy.one_arg_method(obj)
        try:
            assert_that(
                self.spy.one_arg_method,
                called_with(all_of(
                    has_property('id', 20),
                    has_property('test_field', 'OK'))))
            self.fail('Wrong assertion, id field is different')
        except AssertionError:
            pass

#    Not applicable to doublex, cause doublex uses hamcrest matchers
#    def test_obj_with_field_defends_agains_wrong_usage(self):
#        self.spy.one_arg_method(Collaborator())
#        try:
#            assert_that_method(
#                self.spy.one_arg_method).was_called().with_args(
#                obj_with_fields('id = 20'))
#            self.fail('Wrong assertion, argument should be a dictionary')
#        except WrongApiUsage:
#            pass

# NOT APPLICABLE. doubles uses hamcrest matchers
#class pyDoubles__CustomMatchersTest(unittest.TestCase):
#
#    def setUp(self):
#        self.spy = spy(Collaborator())
#
#    def test_use_custom_matcher(self):
#        class CustomMatcher(PyDoublesMatcher):
#            matcher_name = "test matcher"
#
#            def __init__(self, arg):
#                self.defined_arg = arg
#
#            def matches(self, item):
#                return True
#
#        when(self.spy.one_arg_method).with_args(
#            CustomMatcher('zzz')).then_return(1000)
#        self.assertEquals(1000, self.spy.one_arg_method('xx'))
#
#    def test_custom_matcher_do_not_follow_convention(self):
#        class CustomMatcher(PyDoublesMatcher):
#            def matches(self, item):
#                return False
#
#        self.spy.one_arg_method(1)
#        try:
#            assert_that_was_called(self.spy.one_arg_method).with_args(
#                                   CustomMatcher())
#            self.fail('args dont match!')
#        except ArgsDontMatch:
#            pass
