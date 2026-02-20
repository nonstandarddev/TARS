# TARS (`tarsiflow`) :robot:

## Background

`tarsiflow` is a declarative framework designed to create *efficient* computational models with inbuilt, dynamic
*dependency resolution* at its core.

## Usage

With `tarsiflow` you can create a computational graph that respects dependencies (much like
spreadsheet software e.g. Microsoft Excel),

For example, consider the following model,

```python
from tarsiflow import (
    with_model_context,
    Model,
    Field
)

# Ordinary Python functions
@with_model_context
def compute_revenue(
    price: float,
    quantity: float
) -> float:
    return (price * quantity)

@with_model_context
def compute_tax(
    rate: float,
    price: float
) -> float:
    return (rate * price)

# Declaration of schema
schema = [
    Field("price", 100),
    Field("quantity", 5),
    Field("revenue", compute=compute_revenue),
    Field("tax", compute=compute_tax)
]

# Model setup
model = Model()
for field in schema:
    model.register(field)

# Initialise dependencies and values (one-time operation)
model.initialise()
```

With this setup, the model 'knows' that `revenue` is dependent on `price` and `quantity`.

So, if I change `quantity` *only* `revenue` needs to be recalculated (and we can ignore `tax`),

```python
model.set("quantity", 10)
model.refresh("quantity")
```

## Applications

This package could be combined with [WebSockets](https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API) 
to create stateful, efficient reactive web applications.

In particular, stochastic financial models (such as those found within the actuarial domain) could
benefit from this design pattern.
