"""Blueprints are fixed data the planner may split but never change."""
import pytest

from app.services.team_project_blueprints import (
    BlueprintMissing, all_files, backend_family, endpoint_ids, get_blueprint,
)
from app.services.team_project_constants import TECH_STACKS, THEMES

CASES = [(t["key"], s) for t in THEMES for s in ("vanilla", "express")]


@pytest.mark.parametrize("theme,stack", CASES)
def test_every_theme_and_family_has_a_blueprint(theme, stack):
    bp = get_blueprint(theme, stack)
    assert bp["theme"] == theme and bp["backend_family"] == backend_family(stack)


def test_every_stack_maps_to_a_known_family():
    assert {backend_family(s["key"]) for s in TECH_STACKS} <= {"flask", "express"}


@pytest.mark.parametrize("theme,stack", CASES)
def test_endpoint_ids_are_unique_and_well_formed(theme, stack):
    bp = get_blueprint(theme, stack)
    ids = endpoint_ids(bp)
    assert len(ids) == len(set(ids))
    assert {"auth.register", "auth.login"} <= set(ids)
    for e in bp["endpoints"]:
        assert e["method"] in {"GET", "POST", "PUT", "DELETE"} and e["path"].startswith("/api/")
    # same method+path never appears twice
    pairs = [(e["method"], e["path"]) for e in bp["endpoints"]]
    assert len(pairs) == len(set(pairs))


@pytest.mark.parametrize("theme,stack", CASES)
def test_files_are_owned_once_and_the_skeleton_is_complete(theme, stack):
    bp = get_blueprint(theme, stack)
    files = all_files(bp)
    assert len(files) == len(set(files)), "a file listed in two groups"
    skeleton = bp["files"]["skeleton"]
    assert "README.md" in skeleton
    assert any(f.endswith(("requirements.txt", "package.json")) for f in skeleton)
    assert any(f.endswith(("app.py", "server.js")) for f in skeleton)
    assert bp["run"]["backend"] and bp["auth"]["token_key"] == "auth_token"


def test_flask_and_express_share_the_same_endpoints_but_not_files():
    flask, express = get_blueprint("crm", "vanilla"), get_blueprint("crm", "express")
    assert endpoint_ids(flask) == endpoint_ids(express)
    assert flask["files"]["backend"] != express["files"]["backend"]
    assert get_blueprint("crm", "react")["backend_family"] == "flask"


def test_blueprint_names_are_consistent_across_the_contract():
    """The clients/customers drift that broke team 3: the path name and the endpoint id agree."""
    bp = get_blueprint("crm", "express")
    assert all("customers" in e["path"] or e["id"].startswith(("auth", "deals")) for e in bp["endpoints"])


def test_get_blueprint_returns_a_copy_and_unknown_theme_raises():
    a = get_blueprint("booking", "vanilla")
    a["endpoints"].clear()
    assert get_blueprint("booking", "vanilla")["endpoints"], "mutating a returned copy must not leak"
    with pytest.raises(BlueprintMissing):
        get_blueprint("no_such_theme", "vanilla")
