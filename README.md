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

@with_model_context
def costly_operation():
    import time
    time.sleep(10)

# Declaration of schema
schema = [
    Field("price", 100),
    Field("quantity", 5),
    Field("revenue", compute=compute_revenue),
    Field("tax", compute=compute_tax),
    Field("costly_operation", compute=costly_operation)
]

# Model setup
model = Model()
for field in schema:
    model.register(field)

# Initialise dependencies and values (one-time operation) - this will initially compute all
# outputs including the 'costly' delay of 10 seconds
model.initialise()
```

With this setup, the model 'knows' that `revenue` is dependent on `price` and `quantity`,

```python
model.dependents

# defaultdict(<class 'list'>, {'price': ['revenue', 'tax'], 'quantity': ['revenue'], 'rate': ['tax']})
```

So, if I change `quantity` *only* `revenue` needs to be recalculated (and we can ignore `tax`),

```python
delta = model.refresh("quantity", 10)
```

More crucially the `costly_operation` (which is programmed to take 10 seconds) is completely ignored
as the input field that we modified (`quantity`) has nothing to do with its value.

Note that `delta` is a dictionary object that logs the key-value pairs for downstream outputs of the model
that are dependent on `quantity`. In this case it might look something like this,

```
{
    "revenue": 1000
}
```

You can imagine this package being incorporated into the backend of a web application where state is 
maintained on the backend and corresponding updates are transmitted back and forth via *event* payloads.

## Applications

This package could be combined with [WebSockets](https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API) 
to create stateful, efficient reactive web applications.

In particular, stochastic financial models (such as those found within the actuarial domain) could
benefit from this design pattern.
