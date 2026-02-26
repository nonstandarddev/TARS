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

You can imagine this package being incorporated into a web service where state is 
maintained on the backend and corresponding updates are transmitted back and forth via *event* payloads.

## CPU-bound Tasks

This framework also permits the creation and execution of heavy-duty CPU-bound tasks.

For example, note here the usage of `model.refresh_task()`,

```python
import numpy as np
import asyncio
from tarsiflow import (
    Field,
    Model,
    with_model_context
)


@with_model_context
def compute_aal(
    avg_severity: float,
    avg_n_claims: float
) -> float:
    return avg_severity * avg_n_claims


@with_model_context
def compute_trial_losses(
    avg_severity: float,
    avg_n_claims: float,
    n_trials: int
) -> np.ndarray:
    trial_frequencies = np.random.poisson(
        lam=avg_n_claims,
        size=n_trials
    )
    trial_losses = np.array([
        np.random.exponential(scale=avg_severity, size=k).sum()
        for k in trial_frequencies
    ])
    return trial_losses


@with_model_context
def compute_net_losses(
    trial_losses: np.ndarray,
    agg_excess: float,
    agg_limit: float
) -> np.ndarray:
    return np.fmin(np.fmax(trial_losses - agg_excess, 0), agg_limit)
    

async def main():

    schema = [

        # Inputs
        Field("avg_severity", default_value=500_000),
        Field("avg_n_claims", default_value=5),
        Field("n_trials", default_value=10_000_000),
        Field("agg_excess", default_value=1_000_000),
        Field("agg_limit", default_value=3_000_000),

        # Outputs
        Field(
            "aal", 
            compute_aal
        ),
        Field(
            "trial_losses", 
            compute_trial_losses, 
            from_task=True,
            type="array"
        ),
        Field(
            "net_losses", 
            compute_net_losses,
            type="array"
        )

    ]

    model = Model()

    for field in schema:
        model.register(field)

    model.initialise()

    delta = model.refresh(
        input_name="avg_severity", 
        input_value=400_000
    )
    print(delta)

    delta = await model.refresh_task(
        output_name="trial_losses"
    )
    print(delta)

if __name__ == "__main__":
    asyncio.run(main())
```

## Applications

This package could be combined with [WebSockets](https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API) 
to create stateful, efficient reactive web applications.

In particular, stochastic financial models (such as those found within the actuarial domain) could
benefit from this design pattern.
