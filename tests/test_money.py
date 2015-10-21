# -*- coding: utf-8
from __future__ import unicode_literals

from decimal import Decimal, getcontext
import math

from django.test import TestCase

from shop.money.money_maker import AbstractMoney, MoneyMaker, _make_money


class AbstractMoneyTest(TestCase):

    def test_is_abstract(self):
        self.assertRaises(TypeError, lambda: AbstractMoney(1))


class MoneyMakerTest(TestCase):

    def test_create_money_type_without_arguments(self):
        Money = MoneyMaker()
        money = Money()
        self.assertTrue(money.is_nan())

    def test_create_money_type_with_unknown_currency(self):
        self.assertRaises(ValueError, lambda: MoneyMaker(currency_code="ABC"))

    def test_create_money_type_without_decimal_places(self):
        Money = MoneyMaker(currency_code='JPY')
        self.assertEqual(Money._cents, 0)

    def test_create_instance_with_value_as_none(self):
        Money = MoneyMaker()
        money = Money(value=None)
        self.assertTrue(money.is_nan())

    def test_create_instance_with_invalid_value(self):
        Money = MoneyMaker()
        self.assertRaises(ValueError, lambda: Money(value="invalid"))

    def test_wrong_currency_raises_assertion_error(self):
        # If we try to call a money class with a value that has a
        # different currency than the class, and the value is an
        # instance of the money class, there should be an
        # AssertionError.
        Money = MoneyMaker(currency_code="EUR")
        value = Money()
        value._currency_code = "USD"
        self.assertRaises(AssertionError, lambda: Money(value))

    def test_create_instance_from_decimal(self):
        Money = MoneyMaker()
        value = Decimal("1.2")
        inst = Money(value)
        self.assertEquals(inst, value)

    def test_unicode_with_value(self):
        Money = MoneyMaker()
        value = Money(1)
        self.assertEqual(unicode(value), "€ 1.00")

    def test_unicode_with_nan(self):
        Money = MoneyMaker()
        value = Money()
        self.assertEqual(unicode(value), "€ –")

    def test_unicode_with_too_much_precision(self):
        Money = MoneyMaker()
        value = Money(1)
        prec = getcontext().prec
        value._cents = Decimal("0." + ("0" * prec))
        self.assertRaises(ValueError, lambda: unicode(value))

    def test_str(self):
        Money = MoneyMaker()
        value = Money()
        self.assertEqual(str(value), "€ –".encode("utf-8"))

    def test_reduce(self):
        Money = MoneyMaker()
        value = Money()
        func, args = value.__reduce__()
        self.assertTrue(func is _make_money)
        self.assertEqual(args, ("EUR", "NaN"))

        Money = func(*args)
        self.assertTrue(Money.is_nan())

    def test_format(self):
        Money = MoneyMaker()
        self.assertEqual(format(Money()), "€ –")
        self.assertEqual(format(Money(1)), "€ 1.00")

    def test_format_with_context(self):
        # This uses Decimal.__format__
        Money = MoneyMaker()
        self.assertEqual(Money(1).__format__("", getcontext()), "€ 1")

    def test_add(self):
        Money = MoneyMaker()
        self.assertEqual(Money(1) + (Money(2)), Money(3))
        self.assertEqual(Money(1) + (Money(0)), Money(1))
        self.assertEqual(Money(1) + (Money(-1)), Money(0))
        self.assertEqual(Money(1).__radd__(Money(2)), Money(3))

        self.assertEqual(Money(1) + (0), Money(1))
        self.assertEqual(Money(1) + (0.0), Money(1))
        self.assertRaises(ValueError, lambda: Money(1) + (1))
        self.assertRaises(ValueError, lambda: Money(1) + (1.0))

        self.assertEqual(Money(1) + Money('NaN'), Money(1))

    def test_sub(self):
        Money = MoneyMaker()
        self.assertEqual(Money(1) - (Money(2)), Money(-1))
        self.assertRaises(ValueError, lambda: Money(1).__rsub__(Money(2)))

    def test_neg(self):
        Money = MoneyMaker()
        self.assertEqual(- Money(1), -1)
        self.assertEqual(- Money(-1), 1)
        self.assertEqual(- Money(0), 0)

    def test_mul(self):
        Money = MoneyMaker()
        self.assertEqual(Money(1) * 1, Money(1))
        self.assertEqual(Money(1) * 0, Money(0))
        self.assertEqual(Money(1) * -1, Money(-1))
        self.assertEqual(Money(1) * 1, Money(1))
        self.assertEqual(Money(1) * 0, Money(0))
        self.assertEqual(Money(1).__rmul__(-1), Money(-1))
        self.assertEqual(Money(1).__rmul__(1.0), Money(1))
        self.assertEqual(unicode(Money(1) * None), "€ –")
        self.assertRaises(ValueError, lambda: Money(1) * (Money(1)))

    def test_div(self):
        Money = MoneyMaker()
        self.assertEqual(Money(1) / 2, Money(0.5))
        self.assertEqual(Money(1) / 2.0, Money(0.5))
        self.assertRaises(ValueError, lambda: Money(1) / Money(2))
        self.assertRaises(ValueError, lambda: Money(1).__rdiv__(2))

    def test_truediv(self):
        Money = MoneyMaker()
        self.assertEqual(Money(1).__truediv__(2), Money(0.5))
        self.assertEqual(Money(1).__truediv__(2.0), Money(0.5))
        self.assertRaises(ValueError, lambda: Money(1).__truediv__(Money(2)))
        self.assertRaises(ValueError, lambda: Money(1).__rtruediv__(2))

    def test_pow(self):
        Money = MoneyMaker()
        self.assertRaises(ValueError, lambda: Money(1) ** Money(2))

    def test_float(self):
        Money = MoneyMaker()

        money = Money(Decimal('sNaN'))
        self.assertRaises(ValueError, lambda: float(money))

        money = Money(Decimal('NaN'))
        self.assertTrue(math.isnan(float(money)))

        money = Money(Decimal('-NaN'))
        self.assertTrue(math.isnan(float(money)))

        money = Money(Decimal('1.0'))
        self.assertEqual(float(money), 1.0)

    def test_get_currency(self):
        Money = MoneyMaker()
        self.assertEqual(Money.get_currency(), 'EUR')

    def test_as_decimal(self):
        Money = MoneyMaker()
        money = Money('1.23')
        quantized_decimal = Decimal('1.23').quantize(Decimal('.01'))
        self.assertEqual(money.as_decimal(), quantized_decimal)

    def test_as_integer(self):
        Money = MoneyMaker()
        money = Money('1.23')
        self.assertEqual(money.as_integer(), 123)
