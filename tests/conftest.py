import pytest
import numpy as np
from tarsiflow import with_model_context, Model
from tarsiflow.datatypes import (
    Float,
    Integer,
    Array
)


@pytest.fixture
def sample_operations():

    @with_model_context
    def compute_x(
        a: float
    ) -> float:
        return a * 2
    
    @with_model_context
    def compute_y(
        b: int
    ) -> float:
        return b * 2
    
    @with_model_context
    def compute_z(
        c: np.ndarray
    ) -> np.ndarray:
        return c * 2
    
    @with_model_context
    def compute_w(
        z: np.ndarray
    ) -> np.ndarray:
        return z * 2
    
    return {
        "compute_x": compute_x,
        "compute_y": compute_y,
        "compute_z": compute_z,
        "compute_w": compute_w
    }


@pytest.fixture
def sample_model(sample_operations):

    schema = [

        # Inputs
        Float("a", default_value=1.00),
        Integer("b", default_value=2),
        Array("c", default_value=np.array([1, 2, 3])),

        # Outputs
        Float(
            "x", 
            sample_operations["compute_x"]
        ),
        Float(
            "y",
            sample_operations["compute_y"],
            from_task=True
        ),
        Array(
            "z",
            sample_operations["compute_z"]
        ),
        Array(
            "w",
            sample_operations["compute_w"]
        )
        
    ]

    model = Model()

    for field in schema:
        model.register(field)

    model.initialise()

    return model
