import constants
import fastapi
import features
import pandas as pd
import pydantic

from hamilton import base
from hamilton.experimental import h_async

app = fastapi.FastAPI()

# know the model schema somehow.
model_input_features = constants.model_x_features


def load_invariant_feature_values() -> dict:
    """This function would load the invariant feature values from a database or file.
    :return: a dictionary of invariant feature values.
    """
    return {
        "age_mean": 33.0,
        "age_std_dev": 12.0,
    }


def fake_model(df: pd.DataFrame) -> pd.Series:
    """Function to simulate a model"""
    # do some transformation.
    return df.sum()  # this is nonsensical but provides a single number.


# you would load the model from disk or a registry
model = fake_model
# need to load the invariant features somehow.
invariant_feature_values = load_invariant_feature_values()


# can instantiate an async driver once for the life of the app:
dr = h_async.AsyncDriver({}, features, result_builder=base.SimplePythonDataFrameGraphAdapter())


class PredictRequest(pydantic.BaseModel):
    """Assumption here is that all this data is available for the API."""

    id: int
    reason_for_absence: int
    month_of_absence: int
    day_of_the_week: int
    seasons: int
    transportation_expense: int
    distance_from_residence_to_work: int
    service_time: int
    age: int
    work_load_average_per_day: float
    hit_target: int
    disciplinary_failure: int
    education: int
    son: int
    social_drinker: int
    social_smoker: int
    pet: int
    weight: int
    height: int
    body_mass_index: int


@app.post("/predict")
async def predict_model_version1(request: PredictRequest) -> dict:
    """Illustrates how a prediction could be made that needs to compute some features first.
    In this version we go to the feature store, and then pass in what we get from the feature
    store as overrides to the model.
    """
    # one liner to quickly create some series from the request.
    input_series = pd.DataFrame([request.dict()]).to_dict(orient="series")
    # create the features -- point here is we're reusing the same code as in the training!
    # with the ability to provide static values for things like `age_mean` and `age_std_dev`.
    features = await dr.execute(
        model_input_features, inputs=input_series, overrides=invariant_feature_values
    )
    prediction = model(features)
    return {"prediction": prediction.values[0]}


if __name__ == "__main__":
    # If you run this as a script, then the app will be started on localhost:8000
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

    example_request_input = {
        "id": 11,
        "reason_for_absence": 26,
        "month_of_absence": 7,
        "day_of_the_week": 3,
        "seasons": 2,
        "transportation_expense": 1,
        "distance_from_residence_to_work": 1,
        "service_time": 289,
        "age": 36,
        "work_load_average_per_day": 13,
        "hit_target": 33,
        "disciplinary_failure": 239.554,
        "education": 97,
        "son": 0,
        "social_drinker": 1,
        "social_smoker": 2,
        "pet": 1,
        "weight": 90,
        "height": 172,
        "body_mass_index": 30,
    }