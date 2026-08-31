from copy import deepcopy
from datetime import datetime


class CommandApprovalManager:

    VALID_STATUSES = {
        "pending_approval",
        "approved",
        "modified",
        "rejected",
    }

    FINAL_STATUSES = {
        "approved",
        "modified",
        "rejected",
    }

    def __init__(self):

        self.state = {
            "status": "pending_approval",
            "decision_version": 1,
            "approved_version": None,
            "commander": None,
            "timestamp": None,
            "notes": None,
            "modifications": None,
            "history": [],
        }

    # ======================================================
    # HELPERS
    # ======================================================

    def _timestamp(self):

        return (
            datetime.utcnow()
            .isoformat()
            + "Z"
        )

    def _record_history(
        self,
        action,
        commander=None,
        notes=None,
        modifications=None,
    ):

        event = {
            "action":
                action,

            "decision_version":
                self.state[
                    "decision_version"
                ],

            "commander":
                commander,

            "timestamp":
                self._timestamp(),

            "notes":
                notes,

            "modifications":
                deepcopy(
                    modifications
                ),
        }

        self.state[
            "history"
        ].insert(
            0,
            event,
        )

        self.state[
            "history"
        ] = (
            self.state[
                "history"
            ][:20]
        )

        return event

    def _validate_commander(
        self,
        commander,
    ):

        if not isinstance(
            commander,
            str,
        ):

            raise ValueError(
                "commander must be a string."
            )

        commander = (
            commander.strip()
        )

        if not commander:

            raise ValueError(
                "commander is required."
            )

        return commander

    def _validate_decision_version(
        self,
        decision_version,
    ):

        if decision_version is None:

            return

        try:

            decision_version = int(
                decision_version
            )

        except (
            TypeError,
            ValueError,
        ):

            raise ValueError(
                "decision_version must be an integer."
            )

        current_version = (
            self.state[
                "decision_version"
            ]
        )

        if (
            decision_version
            != current_version
        ):

            raise ValueError(
                (
                    "Stale decision version. "
                    f"Current decision version is "
                    f"{current_version}, but request "
                    f"references version "
                    f"{decision_version}."
                )
            )

    def _require_pending_state(self):

        current_status = (
            self.state[
                "status"
            ]
        )

        if (
            current_status
            != "pending_approval"
        ):

            raise ValueError(
                (
                    "Decision is not awaiting "
                    "authorization. Current status "
                    f"is '{current_status}'."
                )
            )

    def _validate_modifications(
        self,
        modifications,
    ):

        if not isinstance(
            modifications,
            dict,
        ):

            raise ValueError(
                "modifications must be a JSON object."
            )

        if not modifications:

            raise ValueError(
                (
                    "At least one modification "
                    "is required."
                )
            )

        return deepcopy(
            modifications
        )

    # ======================================================
    # TRANSITION CAPABILITIES
    # ======================================================

    def can_approve(self):

        return (
            self.state[
                "status"
            ]
            == "pending_approval"
        )

    def can_modify(self):

        return (
            self.state[
                "status"
            ]
            == "pending_approval"
        )

    def can_reject(self):

        return (
            self.state[
                "status"
            ]
            == "pending_approval"
        )

    # ======================================================
    # GET CURRENT STATE
    # ======================================================

    def get_state(self):

        state = deepcopy(
            self.state
        )

        state[
            "can_approve"
        ] = self.can_approve()

        state[
            "can_modify"
        ] = self.can_modify()

        state[
            "can_reject"
        ] = self.can_reject()

        state[
            "authorization_required"
        ] = (
            self.state[
                "status"
            ]
            == "pending_approval"
        )

        state[
            "authorized"
        ] = (
            self.state[
                "status"
            ]
            in {
                "approved",
                "modified",
            }
            and
            self.state[
                "approved_version"
            ]
            ==
            self.state[
                "decision_version"
            ]
        )

        return state

    # ======================================================
    # APPROVE
    # ======================================================

    def approve(
        self,
        commander,
        notes=None,
        decision_version=None,
    ):

        self._validate_decision_version(
            decision_version
        )

        self._require_pending_state()

        commander = (
            self._validate_commander(
                commander
            )
        )

        timestamp = (
            self._timestamp()
        )

        self.state[
            "status"
        ] = "approved"

        self.state[
            "approved_version"
        ] = (
            self.state[
                "decision_version"
            ]
        )

        self.state[
            "commander"
        ] = commander

        self.state[
            "timestamp"
        ] = timestamp

        self.state[
            "notes"
        ] = notes

        self.state[
            "modifications"
        ] = None

        event = (
            self._record_history(
                action="approved",
                commander=commander,
                notes=notes,
            )
        )

        return {
            "status":
                "approved",

            "event":
                event,

            "approval_state":
                self.get_state(),
        }

    # ======================================================
    # MODIFY
    # ======================================================

    def modify(
        self,
        commander,
        modifications,
        notes=None,
        decision_version=None,
    ):

        self._validate_decision_version(
            decision_version
        )

        self._require_pending_state()

        commander = (
            self._validate_commander(
                commander
            )
        )

        modifications = (
            self._validate_modifications(
                modifications
            )
        )

        timestamp = (
            self._timestamp()
        )

        self.state[
            "status"
        ] = "modified"

        self.state[
            "approved_version"
        ] = (
            self.state[
                "decision_version"
            ]
        )

        self.state[
            "commander"
        ] = commander

        self.state[
            "timestamp"
        ] = timestamp

        self.state[
            "notes"
        ] = notes

        self.state[
            "modifications"
        ] = deepcopy(
            modifications
        )

        event = (
            self._record_history(
                action="modified",
                commander=commander,
                notes=notes,
                modifications=(
                    modifications
                ),
            )
        )

        return {
            "status":
                "modified",

            "event":
                event,

            "approval_state":
                self.get_state(),
        }

    # ======================================================
    # REJECT
    # ======================================================

    def reject(
        self,
        commander,
        notes=None,
        decision_version=None,
    ):

        self._validate_decision_version(
            decision_version
        )

        self._require_pending_state()

        commander = (
            self._validate_commander(
                commander
            )
        )

        timestamp = (
            self._timestamp()
        )

        self.state[
            "status"
        ] = "rejected"

        self.state[
            "approved_version"
        ] = None

        self.state[
            "commander"
        ] = commander

        self.state[
            "timestamp"
        ] = timestamp

        self.state[
            "notes"
        ] = notes

        self.state[
            "modifications"
        ] = None

        event = (
            self._record_history(
                action="rejected",
                commander=commander,
                notes=notes,
            )
        )

        return {
            "status":
                "rejected",

            "event":
                event,

            "approval_state":
                self.get_state(),
        }

    # ======================================================
    # NEW ARES DECISION
    # ======================================================

    def register_new_decision(
        self,
        reason=None,
    ):

        self.state[
            "decision_version"
        ] += 1

        self.state[
            "status"
        ] = "pending_approval"

        self.state[
            "approved_version"
        ] = None

        self.state[
            "commander"
        ] = None

        self.state[
            "timestamp"
        ] = self._timestamp()

        self.state[
            "notes"
        ] = reason

        self.state[
            "modifications"
        ] = None

        event = (
            self._record_history(
                action=(
                    "new_decision_pending_approval"
                ),
                notes=reason,
            )
        )

        return {
            "status":
                "pending_approval",

            "event":
                event,

            "approval_state":
                self.get_state(),
        }

    # ======================================================
    # RESET
    # ======================================================

    def reset(self):

        self.state = {
            "status":
                "pending_approval",

            "decision_version":
                1,

            "approved_version":
                None,

            "commander":
                None,

            "timestamp":
                self._timestamp(),

            "notes":
                None,

            "modifications":
                None,

            "history":
                [],
        }

        return (
            self.get_state()
        )