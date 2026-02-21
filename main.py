import numpy as np
from tarsiflow import (
    Field,
    Model,
    with_model_context
)


@with_model_context
def compute_aal(
    avg_severity,
    avg_n_claims
) -> float:
    return avg_severity * avg_n_claims


@with_model_context
def compute_trial_losses(
    avg_severity,
    avg_n_claims,
    n_trials
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
    

if __name__ == "__main__":

    schema = [
        Field("avg_severity", 500_000),
        Field("avg_n_claims", 5),
        Field("aal", compute=compute_aal)
    ]

    model = Model()

    for field in schema:
        model.register(field)

    model.initialise()

    delta = model.refresh(input_name="avg_severity", input_value=400_000)

    print(delta)

