DEFAULTS = {
    "label": "Hi World",
    "update_interval": 1000,
    "callbacks": {
        "on_left": "do_nothing",
        "on_middle": "do_nothing",
        "on_right": "do_nothing",
    },
}

VALIDATION_SCHEMA = {
    "label": {"type": "string", "default": DEFAULTS["label"]},
    "update_interval": {
        "type": "integer",
        "default": DEFAULTS["update_interval"],
        "min": 0,
        "max": 60000,
    },
    "callbacks": {
        "type": "dict",
        "schema": {
            "on_left": {
                "type": "string",
                "default": DEFAULTS["callbacks"]["on_left"],
            },
            "on_middle": {
                "type": "string",
                "default": DEFAULTS["callbacks"]["on_middle"],
            },
            "on_right": {
                "type": "string",
                "default": DEFAULTS["callbacks"]["on_right"],
            },
        },
        "default": DEFAULTS["callbacks"],
    },
}
