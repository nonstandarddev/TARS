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

    

