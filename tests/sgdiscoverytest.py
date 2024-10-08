import sys
import unittest
from unittest import TestCase

import numpy as np
import pandas as pd

sys.path.append("../")
import random

import fairsd as dsd


def list_of_descriptors(num_des=3):
    # create list of Descriptor
    los = []
    # nominal descriptors
    for i in range(0, num_des):
        attribute_name = "a" + str(i)
        los.append(dsd.Descriptor(attribute_name=attribute_name, attribute_value=True))
    # numeric descriptors
    for i in range(0, num_des):
        attribute_name = "b" + str(i)
        los.append(
            dsd.Descriptor(attribute_name=attribute_name, up_bound=3, low_bound=1, is_numeric=True)
        )
    return los


def istantiate_dataset():
    data = {
        "a0": [True, True, False, True, False, False],
        "b0": [2, 2, 3, 4, 5, 6],
        "y_true": [0, 0, 0, 1, 1, 1],
        "y_pred": [0, 0, 1, 0, 1, 1],
    }
    return pd.DataFrame(data)


class TestDescriptorMethods(TestCase):
    def test_is_present_in(self):
        los = list_of_descriptors()

        self.assertTrue(dsd.Descriptor("a2", attribute_value=True).is_present_in(los), "error1")
        self.assertFalse(dsd.Descriptor("a1", attribute_value=False).is_present_in(los), "error2")
        self.assertFalse(dsd.Descriptor("b1", attribute_value=False).is_present_in(los), "error3")
        self.assertTrue(
            dsd.Descriptor("b1", up_bound=3, low_bound=1, is_numeric=True).is_present_in(los),
            "error4",
        )
        self.assertFalse(
            dsd.Descriptor("b1", up_bound=3, low_bound=0, is_numeric=True).is_present_in(los),
            "error5",
        )
        self.assertFalse(
            dsd.Descriptor("a1", up_bound=3, low_bound=1, is_numeric=True).is_present_in(los),
            "error6",
        )
        self.assertFalse(dsd.Descriptor("c1", attribute_value=False).is_present_in(los), "error7")
        self.assertFalse(
            dsd.Descriptor("d1", up_bound=3, low_bound=1, is_numeric=True).is_present_in(los),
            "error8",
        )


class TestDescriptionMethods(TestCase):
    def setUp(self):
        self.los = list_of_descriptors(3)
        self.des = dsd.Description(self.los)
        self.des.support = 5
        self.des.set_quality(0.1)

    def test__lt__(self):
        # test with equal quality and different support
        los1 = list_of_descriptors(1)
        des1 = dsd.Description(los1)
        des1.support = 5
        des1.set_quality(0.1)
        self.assertFalse(des1.__lt__(self.des))
        des1.support = 4
        des1.set_quality(0.1)
        self.assertTrue(des1.__lt__(self.des))
        des1.support = 6
        des1.set_quality(0.1)
        self.assertFalse(des1.__lt__(self.des))

        # test with different qualityes
        des1.set_quality(0.2)
        self.assertFalse(des1.__lt__(self.des))
        des1.set_quality(0.01)
        self.assertTrue(des1.__lt__(self.des))
        des1.set_quality(0.1)
        self.assertFalse(des1.__lt__(self.des))

    def test_to_boolean_array(self):
        los = list_of_descriptors(1)
        des = dsd.Description(los)
        self.assertTrue(
            np.array_equal(
                des.to_boolean_array(istantiate_dataset()),
                np.array([True, True, False, False, False, False]),
            )
        )

        des = dsd.Description()
        self.assertTrue(
            np.array_equal(
                des.to_boolean_array(istantiate_dataset()),
                np.array([True, True, True, True, True, True]),
            )
        )

    def test_get_attributes(self):
        self.assertEqual(self.des.get_attributes(), ["a0", "a1", "a2", "b0", "b1", "b2"])

    def test_is_present_in(self):
        list_t = []
        for i in range(3):
            list_t.append(dsd.Description(list_of_descriptors(i + 1)))

        self.assertTrue(dsd.Description(list_of_descriptors(2)).is_present_in(list_t))
        self.assertFalse(dsd.Description(list_of_descriptors(4)).is_present_in(list_t))


class TestDiscretizerMethods(TestCase):
    """
    This test assumes that the classes Discretizer, Description and Descriptor works correctly.
    These three classes are tested above.
    """

    def test_discretize_mdlp(self):
        discretizer = dsd.Discretizer(discretization_type="mdlp", target="y_true")

        dataset = istantiate_dataset()
        description = dsd.Description()
        res = discretizer.discretize(dataset, description, "b0")

        d0 = dsd.Descriptor("b0", up_bound=3, low_bound=None, to_discretize=False, is_numeric=True)
        d1 = dsd.Descriptor("b0", up_bound=None, low_bound=3, to_discretize=False, is_numeric=True)
        correct_result = [d0, d1]
        self.assertEqual(len(res), 2)
        self.assertTrue(correct_result[0].is_present_in(res))
        self.assertTrue(correct_result[1].is_present_in(res))

    def test_discretize_equalfreq(self):
        discretizer = dsd.Discretizer(discretization_type="equalfreq", num_bins=2)

        dataset = istantiate_dataset()
        description = dsd.Description()
        res = discretizer.discretize(dataset, description, "b0")

        d0 = dsd.Descriptor("b0", up_bound=3, low_bound=None, to_discretize=False, is_numeric=True)
        d1 = dsd.Descriptor("b0", up_bound=None, low_bound=3, to_discretize=False, is_numeric=True)
        correct_result = [d0, d1]
        self.assertEqual(len(res), 2)
        self.assertTrue(correct_result[0].is_present_in(res))
        self.assertTrue(correct_result[1].is_present_in(res))

    def test_discretize_equalwidth(self):
        discretizer = dsd.Discretizer(discretization_type="equalwidth", num_bins=2)

        dataset = istantiate_dataset()
        description = dsd.Description()
        res = discretizer.discretize(dataset, description, "b0")

        d0 = dsd.Descriptor("b0", up_bound=4, low_bound=None, to_discretize=False, is_numeric=True)
        d1 = dsd.Descriptor("b0", up_bound=None, low_bound=4, to_discretize=False, is_numeric=True)
        correct_result = [d0, d1]
        self.assertEqual(len(res), 2)
        self.assertTrue(correct_result[0].is_present_in(res))
        self.assertTrue(correct_result[1].is_present_in(res))


class TestSearchSpaceMethods(TestCase):
    def test_extract_search_space_AND_init_methods(self):
        dataset = istantiate_dataset()
        ss = dsd.SearchSpace(
            dataset,
            ignore=["y_pred", "y_true"],
            discretizer=dsd.Discretizer(discretization_type="equalfreq", num_bins=2),
        )

        # creation of correct result
        d0 = dsd.Descriptor("a0", attribute_value=True, is_numeric=False)
        d1 = dsd.Descriptor("a0", attribute_value=False, is_numeric=False)
        d2 = dsd.Descriptor("b0", up_bound=3, low_bound=None, to_discretize=False, is_numeric=True)
        d3 = dsd.Descriptor("b0", up_bound=None, low_bound=3, to_discretize=False, is_numeric=True)
        correct_result = [d0, d1, d2, d3]

        discretizer = dsd.Discretizer(discretization_type="mdlp", target="y_true")
        result = ss.extract_search_space(dataset, discretizer)

        # batch of tests 1
        self.assertEqual(len(result), 4)
        self.assertTrue(correct_result[0].is_present_in(result))
        self.assertTrue(correct_result[1].is_present_in(result))
        self.assertTrue(correct_result[2].is_present_in(result))
        self.assertTrue(correct_result[3].is_present_in(result))

        # batch of tests 2: with not null description
        descr = dsd.Description(
            [d2]
        )  # b0>3, This description excludes the feature b0 because all b0>3 have positive class
        result = ss.extract_search_space(dataset, discretizer, descr)

        self.assertEqual(len(result), 2)
        self.assertTrue(correct_result[0].is_present_in(result))
        self.assertTrue(correct_result[1].is_present_in(result))

        # batch of tests 3: Numeric attribute treated as nominal a one
        ss = dsd.SearchSpace(dataset, ignore=["y_pred", "y_true"], nominal_features=["b0"])
        result = ss.extract_search_space(dataset, discretizer)

        # creation of correct result
        d0 = dsd.Descriptor("a0", attribute_value=True, is_numeric=False)
        d1 = dsd.Descriptor("a0", attribute_value=False, is_numeric=False)
        d2 = dsd.Descriptor("b0", attribute_value=2, is_numeric=False)
        d3 = dsd.Descriptor("b0", attribute_value=3, is_numeric=False)
        d4 = dsd.Descriptor("b0", attribute_value=4, is_numeric=False)
        d5 = dsd.Descriptor("b0", attribute_value=5, is_numeric=False)
        d6 = dsd.Descriptor("b0", attribute_value=6, is_numeric=False)
        correct_result = [d0, d1, d2, d3, d4, d5, d6]

        self.assertEqual(len(result), 7)
        self.assertTrue(correct_result[0].is_present_in(result))
        self.assertTrue(correct_result[1].is_present_in(result))
        self.assertTrue(correct_result[2].is_present_in(result))
        self.assertTrue(correct_result[3].is_present_in(result))
        self.assertTrue(correct_result[4].is_present_in(result))
        self.assertTrue(correct_result[5].is_present_in(result))
        self.assertTrue(correct_result[6].is_present_in(result))


COSTANT_SEED = 3


class TestQF(dsd.QualityFunction):
    """
    This quality function is created only for testing the sg_discovery algorithms.
    The evaluate function return a pseudo random number each time it is called.
    The seed is always =3, in this way the sequence of returned numbers is always reproducible.
    """

    def __init__(self):
        random.seed(a=COSTANT_SEED)

    def evaluate(self, y_true=None, y_pred=None, sensitive_features=None):
        return random.random()


class TestBeamSeacrchMethods(TestCase):
    """
    A toy dataset is used for testing. A maximum of 8 descriptions can be generated from this dataset,
    in this way the result of the algorithm can be calculated manually.
    The quality function is the TestQF defined above.
    """

    def test_execute(self):
        data = {"a0": [True, True, False, True, False, False], "b0": ["a", "b", "a", "b", "a", "b"]}
        x = pd.DataFrame(data)
        y_true = pd.Series([0, 0, 0, 1, 1, 1])
        task = dsd.SubgroupDiscoveryTask(
            x, y_true, qf=TestQF().evaluate, depth=6, min_quality=0, min_support=0
        )

        result_set = dsd.BeamSearch(beam_width=10).execute(task)
        result_set = result_set.descriptions_list
        self.assertEqual(len(result_set), 8)

        # create correct result
        correct_result = []
        random.seed(a=COSTANT_SEED)
        correct_result.append((random.random(), "a0 = 'True' "))
        correct_result.append((random.random(), "a0 = 'False' "))
        correct_result.append((random.random(), "b0 = 'a' "))
        correct_result.append((random.random(), "b0 = 'b' "))
        correct_result.append((random.random(), "a0 = 'True' AND b0 = 'a' "))
        correct_result.append((random.random(), "a0 = 'True' AND b0 = 'b' "))
        correct_result.append((random.random(), "a0 = 'False' AND b0 = 'a' "))
        correct_result.append((random.random(), "a0 = 'False' AND b0 = 'b' "))
        correct_result.sort(reverse=True)

        for i in range(8):
            self.assertEqual(correct_result[i][1], result_set[i].__repr__())

        # test 2 with reduced result set size
        task = dsd.SubgroupDiscoveryTask(
            x, y_true, qf=TestQF().evaluate, result_set_size=3, min_quality=0, min_support=0
        )
        result_set = dsd.BeamSearch(beam_width=10).execute(task)
        result_set = result_set.descriptions_list

        self.assertEqual(len(result_set), 3)
        for i in range(3):
            self.assertEqual(correct_result[i][1], result_set[i].__repr__())


class TestDSSDMethods(TestCase):
    """
    A toy dataset is used for testing. A maximum of 8 descriptions can be generated from this dataset,
    in this way the result of the algorithm can be calculated manually.
    The quality function is the TestQF defined above.
    """

    def test_execute(self):
        data = {"a0": [True, True, False, True, False, False], "b0": ["a", "b", "a", "b", "a", "b"]}
        x = pd.DataFrame(data)
        y_true = pd.Series([0, 0, 0, 1, 1, 1])
        task = dsd.SubgroupDiscoveryTask(
            x, y_true, qf=TestQF().evaluate, depth=1, min_quality=0, min_support=0
        )

        result_set = dsd.DSSD(beam_width=10, a=1).execute(task)

        result_set = result_set.descriptions_list
        self.assertEqual(len(result_set), 4)

        # create correct result
        correct_result = []
        random.seed(a=COSTANT_SEED)
        correct_result.append((random.random(), "a0 = 'True' "))
        correct_result.append((random.random(), "a0 = 'False' "))
        correct_result.append((random.random(), "b0 = 'a' "))
        correct_result.append((random.random(), "b0 = 'b' "))
        correct_result.sort(reverse=True)

        for i in range(4):
            self.assertEqual(correct_result[i][1], result_set[i].__repr__())

        # test 2 with reduced result set size
        task = dsd.SubgroupDiscoveryTask(
            x,
            y_true,
            qf=TestQF().evaluate,
            depth=1,
            result_set_size=3,
            min_quality=0,
            min_support=0,
        )
        result_set = dsd.DSSD(beam_width=10, a=1).execute(task)
        result_set = result_set.descriptions_list

        self.assertEqual(len(result_set), 3)
        for i in range(3):
            self.assertEqual(correct_result[i][1], result_set[i].__repr__())


if __name__ == "__main__":
    unittest.main()
