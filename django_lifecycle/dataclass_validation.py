import logging

logger = logging.getLogger(__name__)


class Validations:
    # Snippet grabbed from:
    # https://gist.github.com/rochacbruno/978405e4839142e409f8402eece505e8

    def __post_init__(self):
        """
        Run validation methods if declared.
        The validation method can be a simple check
        that raises ValueError or a transformation to
        the field value.
        The validation is performed by calling a function named:
            `validate_<field_name>(self, value, field) -> field.type`

        Finally, calls (if defined) `validate(self)` for validations that depend on other fields
        """
        for name, field in self.__dataclass_fields__.items():
            validator_name = f"validate_{name}"
            method = getattr(self, validator_name, None)
            if callable(method):
                logger.debug(f"Calling validator: {validator_name}")
                new_value = method(getattr(self, name), field=field)
                setattr(self, name, new_value)

        validate = getattr(self, "validate", None)
        if callable(validate):
            logger.debug(f"Calling validator: validate")
            validate()
