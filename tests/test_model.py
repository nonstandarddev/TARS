import pytest
import numpy as np


def test_model_dependencies(sample_model):

    dependents = sample_model.dependents

    assert dependents["a"] == ["x"]
    assert dependents["b"] == ["y"]
    assert dependents["c"] == ["z"]
    assert dependents["z"] == ["w"]


def test_model_refresh(sample_model):

    delta = sample_model.refresh(
        "c",
        np.array([4, 5, 6])
    )

    assert "z" in delta
    assert "w" in delta
    np.testing.assert_array_equal(delta["z"], np.array([8, 10, 12]))
    np.testing.assert_array_equal(delta["w"], np.array([16, 20, 24]))


if __name__ == "__main__":
    pytest.main()