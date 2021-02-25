from devtools import debug
from typing import Any, List
import pandas as pd
import plotly.express as px
from speckle.api import operations
from speckle.api.client import SpeckleClient
from speckle.api.credentials import get_default_account, get_local_accounts
from speckle.objects.base import Base
from speckle.transports.server import ServerTransport


HOST = "staging.speckle.dev"
STREAM_ID = "fca8b6b6be"
COMMIT_ID = "d2887b7519"  # commit containing objects with materials already added

# I wanted specific colours hehe
PLOTLY_COLOURS = px.colors.qualitative.Plotly
COLOUR_MAPPING = {
    "floorSlab": PLOTLY_COLOURS[0],
    "banister": PLOTLY_COLOURS[4],
    "facade": PLOTLY_COLOURS[2],
    "columns": PLOTLY_COLOURS[3],
}


def get_authenticated_client() -> SpeckleClient:
    """
    This assumes you already have a local account. If you don't already have one, you'll need
    to download the Speckle Manager and add an account for your server (which can be localhost).
    See the docs for more info: https://speckle.guide/user/manager.html
    """
    client = SpeckleClient(host=HOST)
    account = get_default_account()
    client.authenticate(token=account.token)

    return client


def get_authenticated_local_client() -> SpeckleClient:
    local_client = SpeckleClient(host="localhost:3000", use_ssl=False)
    local_account = next(
        a for a in get_local_accounts() if "localhost" in a.serverInfo.url
    )
    local_client.authenticate(token=local_account.token)

    return local_client


def receive_data(
    client: SpeckleClient, stream_id: str = STREAM_ID, commit_id: str = COMMIT_ID
) -> Any:
    transport = ServerTransport(client, stream_id)

    commit = client.commit.get(stream_id, commit_id)
    data = operations.receive(commit.referencedObject, transport)

    return data["data"]


def construct_points_df(levels: List[Base]) -> pd.DataFrame:
    df_vertices = pd.DataFrame(columns=("x", "y", "z", "element"))

    vertices = []
    for level in levels:
        columns = level["@columns"]
        for column in columns:
            points = column.Vertices
            for p in points:
                vertices.append({"x": p.x, "y": p.y, "z": p.z, "element": "columns"})

        floorslab = level["@floorSlab"]
        points = floorslab.Vertices
        for p in points:
            vertices.append({"x": p.x, "y": p.y, "z": p.z, "element": "floorSlab"})

    return df_vertices.append(vertices)


def construct_carbon_df(level: Base) -> pd.DataFrame:
    data = {"element": [], "volume": [], "mass": [], "embodied carbon": []}
    names = level.get_dynamic_member_names()
    for name in names:
        prop = level[name]
        if isinstance(prop, Base):
            if not hasattr(prop, "volume"):
                break
            data["volume"].append(prop.volume)
            data["mass"].append(data["volume"][-1] * prop["@material"].density)
            data["embodied carbon"].append(
                data["mass"][-1] * prop["@material"].embodied_carbon
            )
        elif isinstance(prop, list):
            if not hasattr(prop[0], "volume"):
                break
            data["volume"].append(sum(p.volume for p in prop))
            data["mass"].append(data["volume"][-1] * prop[0]["@material"].density)
            data["embodied carbon"].append(
                data["mass"][-1] * prop[0]["@material"].embodied_carbon
            )
        data["element"].append(name[1:])
    return pd.DataFrame(data)


def get_figures() -> dict:
    client = get_authenticated_client()
    figures = {}
    levels = receive_data(client)
    level = levels[0]
    df_vertices = construct_points_df(levels)
    df_carbon = construct_carbon_df(level)

    figures["vertices"] = px.scatter_3d(
        df_vertices,
        x="x",
        y="y",
        z="z",
        color="element",
        color_discrete_map=COLOUR_MAPPING,
        opacity=0.7,
        title="Element Vertices (m)",
    )

    figures["volumes"] = px.pie(
        df_carbon,
        values="volume",
        names="element",
        color="element",
        color_discrete_map=COLOUR_MAPPING,
        title="Volumes of Elements Per Floor (m3)",
    )

    figures["carbon bar"] = px.bar(
        df_carbon,
        x="element",
        y="embodied carbon",
        color="element",
        color_discrete_map=COLOUR_MAPPING,
        title="Embodied Carbon Per Floor (kgC02)",
    )

    figures["carbon pie"] = px.pie(
        df_carbon,
        values="embodied carbon",
        names="element",
        color="element",
        color_discrete_map=COLOUR_MAPPING,
        title="Embodied Carbon Per Floor (kgC02)",
    )

    return figures


def send_results(
    base: Base,
    client: SpeckleClient = None,
    stream_id: str = STREAM_ID,
    branch_name: str = "🐍 results",
) -> str:
    if not client:
        client = get_authenticated_client()
    transport = ServerTransport(client, stream_id)

    branches = client.branch.list(stream_id=stream_id)
    has_res_branch = any(b.name == branch_name for b in branches)
    if not has_res_branch:
        client.branch.create(
            stream_id, name=branch_name, description="new stuff from py"
        )

    obj_id = operations.send(base, [transport])

    return client.commit.create(
        stream_id, obj_id, branch_name, message="floor 0 of twisty building"
    )


if __name__ == "__main__":
    client = get_authenticated_client()
    levels = receive_data(client)

    df_carbon = construct_carbon_df(levels[0])
    df_vertices = construct_points_df(levels)

    debug(levels[0]["@floorSlab"])
    debug(df_carbon.head())
