from specklepy.api import operations
from specklepy.api.client import SpeckleClient
from specklepy.api.credentials import get_default_account
from specklepy.objects import Base
from specklepy.transports.server import ServerTransport

HOST = "staging.speckle.dev"
STREAM_ID = "fca8b6b6be"
COMMIT_ID = "0b25f9a50c"


# density (kg/m^3) and embodied carbon (kg CO^2/kg) estimates
# from https://www.greenspec.co.uk/building-design/embodied-energy/
class Concrete(Base):
    density: str = 2400
    embodied_carbon = 0.159


class Glass(Base):
    density: str = 2500
    embodied_carbon = 0.85


class Steel(Base):
    density: str = 7800
    embodied_carbon = 1.37


MATERIALS_MAPPING = {
    "@floorSlab": "Concrete",
    "@banister": "Glass",
    "@facade": "Glass",
    "@columns": "Steel",
}


def add_materials_data(level: Base) -> Base:
    names = level.get_member_names()
    for name in names:
        if name not in MATERIALS_MAPPING.keys():
            break
        material = Base.get_registered_type(MATERIALS_MAPPING[name])()
        prop = level[name]
        if isinstance(prop, Base):
            prop["@material"] = material
        elif isinstance(prop, list):
            for item in prop:
                item["@material"] = material
    return level


def send_with_materials(
    stream_id: str = STREAM_ID, commit_id: str = COMMIT_ID, branch_name: str = "🐍 demo"
) -> str:
    # create and authenticate a client
    client = SpeckleClient(host=HOST)
    # this assumes you already have a local account. If you don't already have one, you'll need
    # to download the Speckle Manager and add an account for your server
    # See the docs for more info: https://speckle.guide/user/manager.html
    account = get_default_account()
    client.authenticate(token=account.token)

    # get the specified commit data
    commit = client.commit.get(stream_id, commit_id)

    # create an authenticated server transport from the client and receive the commit obj
    transport = ServerTransport(client, stream_id)
    levels = operations.receive(commit.referencedObject, transport)["data"]

    # process the data
    levels = [add_materials_data(level) for level in levels]

    # create a branch if necessary
    branches = client.branch.list(stream_id=stream_id)
    has_res_branch = any(b.name == branch_name for b in branches)
    if not has_res_branch:
        client.branch.create(
            stream_id, name=branch_name, description="new stuff from py"
        )

    # send the data to the server
    base = Base(data=levels)
    obj_id = operations.send(base, [transport])

    return client.commit.create(
        stream_id,
        obj_id,
        branch_name,
        message="add detached materials",
    )


if __name__ == "__main__":
    send_with_materials()
