import math
import pytest
import numpy as np
from tarsiflow.datatypes import (
    Float,
    Integer,
    Array,
    List
)


def test_basic_instantiation():

    basic = Float(
        name="null_field"
    )

    assert math.isnan(basic.value)


def test_non_basic_instantiation():

    non_basic = Float(
        name="non_basic",
        default_value=5.0
    )

    assert non_basic.value == 5.0


def test_basic_coercion():

    basic_coercion = Integer(
        name="non_basic",
        default_value=100.0
    )

    assert basic_coercion.value == 100
    assert isinstance(basic_coercion.value, int)


def test_empty_array_instantiation():

    basic_array = Array(
        name="basic_array"
    )

    np.testing.assert_array_equal(
        basic_array.value, 
        np.array([np.nan])
    )


def test_basic_array_instantiation():

    basic_array = Array(
        name="basic_array",
        default_value=np.array([1, 2, 3])
    )

    np.testing.assert_array_equal(
        basic_array.value, 
        np.array([1, 2, 3])
    )


def test_basic_list_instantiation():

    basic_list = List(
        name="basic_list",
        default_value=[
            {"name": "X", "value": 1},
            {"name": "Y", "value": 2}
        ]
    )

    assert basic_list.length == 2
    assert basic_list[0]["name"] == "X"
    assert basic_list[0]["value"] == 1



if __name__ == "__main__":
    pytest.main()
