"""Tomorrowkit orientation and provisional patent matter workspace.

Services run from /home/user/workspace (the repo root). Conventions:

- Persistent state (anything written and read across runs) lives under
  ``DATA_DIR`` (defined below), never a hardcoded ``data/.apps/tomorrowkit/``
  at the call site. ``DATA_DIR`` defaults to ``data/.apps/tomorrowkit/`` but
  honors the ``TOMORROWKIT_DATA_DIR`` env var, so an editing agent can point a
  throwaway instance at a *copy* of the data instead of the live store (see
  the update-app skill).
- Static assets shipped alongside this file (templates, CSS, JS, fonts) live
  under ``assets/`` and are addressed via ``Path(__file__).parent``.
- Listen port: bind ``PORT`` (defined below), which defaults to this app's
  assigned port but honors the ``TOMORROWKIT_PORT`` env var.

This is a synchronous Flask app served by the threaded Werkzeug server. The
system_interface proxy at ``/service/tomorrowkit/`` fronts it; all URLs in the
templates and scripts are relative so the app works both behind the proxy and
when addressed directly on its own port.
"""

import io
import os
from datetime import datetime, timezone
from pathlib import Path

from flask import (
    Flask,
    Response,
    abort,
    render_template,
    request,
    send_file,
    send_from_directory,
)
from pydantic import ValidationError
from werkzeug.serving import run_simple

from tomorrowkit.data_types import (
    MatterDocument,
    MatterId,
    MatterIntake,
    OrientationProfile,
)
from tomorrowkit.errors import MatterNotFoundError, StaleMatterError
from tomorrowkit.export import build_export_zip_bytes
from tomorrowkit.factories import (
    create_matter_from_intake,
    create_matter_from_orientation,
)
from tomorrowkit.storage import FileMatterStore, MatterStoreInterface

# Persistent state for this app lives under DATA_DIR. It defaults to
# ``data/.apps/tomorrowkit/`` but is overridable via the ``TOMORROWKIT_DATA_DIR``
# env var so a throwaway instance can run against a *copy* of the data while
# editing -- see the update-app skill.
DATA_DIR = Path(os.environ.get("TOMORROWKIT_DATA_DIR", "data/.apps/tomorrowkit"))

# Listen port. Defaults to this app's assigned port but is overridable via the
# ``TOMORROWKIT_PORT`` env var so an editing agent can boot a throwaway
# instance on a spare port next to the live one (see the update-app skill).
PORT = int(os.environ.get("TOMORROWKIT_PORT", "8090"))

_ASSETS_DIR = Path(__file__).parent / "assets"


def _parse_matter_id_or_404(raw_matter_id: str) -> MatterId:
    try:
        return MatterId(raw_matter_id)
    except ValueError:
        abort(404, description="No such matter")


def _load_matter_or_404(
    store: MatterStoreInterface, raw_matter_id: str
) -> MatterDocument:
    matter_id = _parse_matter_id_or_404(raw_matter_id)
    try:
        return store.load_matter(matter_id)
    except MatterNotFoundError:
        abort(404, description="No such matter")


def build_app(store: MatterStoreInterface) -> Flask:
    app = Flask(
        "tomorrowkit",
        static_folder=None,
        template_folder=str(_ASSETS_DIR / "templates"),
    )

    @app.route("/")
    def home() -> str:
        matters = store.list_matters()
        return render_template("home.html", matters=matters)

    @app.route("/matter/<raw_matter_id>")
    def matter_page(raw_matter_id: str) -> str:
        matter = _load_matter_or_404(store, raw_matter_id)
        return render_template("matter.html", matter=matter)

    @app.route("/matter/<raw_matter_id>/export.zip")
    def matter_export(raw_matter_id: str) -> Response:
        matter = _load_matter_or_404(store, raw_matter_id)
        zip_bytes = build_export_zip_bytes(matter)
        filename_stem = "".join(
            c if c.isalnum() or c in "-_" else "-" for c in matter.title.lower()
        )[:60]
        return send_file(
            io.BytesIO(zip_bytes),
            mimetype="application/zip",
            as_attachment=True,
            download_name=f"{filename_stem or 'matter'}-export.zip",
        )

    @app.route("/matter/<raw_matter_id>/raw")
    def matter_raw(raw_matter_id: str) -> Response:
        # The raw record, pretty-printed, exactly as it sits on disk after validation.
        matter = _load_matter_or_404(store, raw_matter_id)
        return Response(matter.model_dump_json(indent=2), mimetype="application/json")

    @app.route("/api/matters", methods=["POST"])
    def create_matter() -> Response:
        payload = request.get_json(silent=True)
        if payload is None:
            abort(400, description="Expected a JSON body")
        try:
            intake = MatterIntake.model_validate(payload)
        except ValidationError as e:
            abort(400, description=f"Invalid intake: {e.error_count()} problem(s)")
        matter = create_matter_from_intake(intake)
        store.save_matter(matter)
        return Response(
            matter.model_dump_json(), mimetype="application/json", status=201
        )

    @app.route("/api/orientation", methods=["POST"])
    def create_oriented_matter() -> Response:
        payload = request.get_json(silent=True)
        if payload is None:
            abort(400, description="Expected a JSON body")
        try:
            orientation = OrientationProfile.model_validate(payload)
        except ValidationError as e:
            abort(
                400,
                description=f"Invalid orientation: {e.error_count()} problem(s)",
            )
        if (
            orientation.idea_state is None
            or orientation.disclosure_state is None
            or not orientation.objectives
            or orientation.materials_state is None
            or orientation.collaboration_style is None
        ):
            abort(400, description="Expected all five orientation answers")
        matter = create_matter_from_orientation(orientation)
        store.save_matter(matter)
        return Response(
            matter.model_dump_json(), mimetype="application/json", status=201
        )

    @app.route("/api/matters/<raw_matter_id>", methods=["GET"])
    def get_matter(raw_matter_id: str) -> Response:
        matter = _load_matter_or_404(store, raw_matter_id)
        return Response(matter.model_dump_json(), mimetype="application/json")

    @app.route("/api/matters/<raw_matter_id>", methods=["PUT"])
    def update_matter(raw_matter_id: str) -> Response:
        existing = _load_matter_or_404(store, raw_matter_id)
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            abort(400, description="Expected a JSON object body")
        raw_expected_updated_at = payload.get("updated_at")
        if not isinstance(raw_expected_updated_at, str):
            abort(400, description="Expected the matter's updated_at revision")
        try:
            expected_updated_at = datetime.fromisoformat(
                raw_expected_updated_at.replace("Z", "+00:00")
            )
        except ValueError:
            abort(400, description="Invalid updated_at revision")
        # The identity and creation time are owned by the server, and every
        # save stamps a fresh updated_at.
        payload["matter_id"] = str(existing.matter_id)
        payload["created_at"] = existing.created_at.isoformat()
        payload["updated_at"] = datetime.now(timezone.utc).isoformat()
        try:
            updated = MatterDocument.model_validate(payload)
        except ValidationError as e:
            abort(
                400,
                description=f"Invalid matter document: {e.error_count()} problem(s)",
            )
        try:
            store.save_matter_if_current(updated, expected_updated_at)
        except StaleMatterError:
            abort(409, description="Matter changed in another session; reload it")
        except MatterNotFoundError:
            abort(404, description="No such matter")
        return Response(updated.model_dump_json(), mimetype="application/json")

    @app.route("/api/matters/<raw_matter_id>", methods=["DELETE"])
    def delete_matter(raw_matter_id: str) -> Response:
        matter_id = _parse_matter_id_or_404(raw_matter_id)
        try:
            store.delete_matter(matter_id)
        except MatterNotFoundError:
            abort(404, description="No such matter")
        return Response('{"deleted": true}', mimetype="application/json")

    @app.route("/static/<path:filename>")
    def static_asset(filename: str) -> Response:
        return send_from_directory(_ASSETS_DIR / "static", filename)

    @app.route("/favicon.ico")
    def favicon() -> Response:
        return send_from_directory(_ASSETS_DIR / "static", "favicon.svg")

    @app.route("/health")
    def health() -> Response:
        return Response('{"status": "ok"}', mimetype="application/json")

    return app


def main() -> None:
    store = FileMatterStore(matters_directory=DATA_DIR / "matters")
    app = build_app(store)
    run_simple(
        "127.0.0.1", PORT, app, threaded=True, use_reloader=False, use_debugger=False
    )


if __name__ == "__main__":
    main()
