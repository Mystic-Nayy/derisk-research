from decimal import Decimal
from pydantic import BaseModel, ValidationInfo, field_validator

from shared.helpers import add_leading_zeros


class DataAccumulatorsSyncEvent(BaseModel):
    """
    Model to parse and validate data for AccumulatorsSync event.

    This model validates and converts the lending and debt accumulators from hexadecimal
    strings to `Decimal` format, scaled by `1e27`.

    Attributes:
        token (str): The token address as a hexadecimal string.
        lending_accumulator (Decimal): The lending accumulator value, converted from hex to Decimal.
        debt_accumulator (Decimal): The debt accumulator value, converted from hex to Decimal.
    """

    token: str
    lending_accumulator: Decimal
    debt_accumulator: Decimal

    @field_validator("lending_accumulator", "debt_accumulator", mode="before")
    def hex_to_decimal(cls, v: str) -> Decimal:
        """
        Converts a hexadecimal string to a Decimal value, scaled by 1e27.

        Args:
            v (str): The hexadecimal string to be converted.

        Returns:
            Decimal: The converted decimal value scaled by 1e27.
        """
        return Decimal(int(v, 16)) / Decimal("1e27")


class LiquidationEventData(BaseModel):
    """
    Class for converting liquidation event to an object model.

    Attributes:
        liquidator: The address of the liquidator.
        user: The address of the user.
        debt_token: The address of the debt token.
        debt_raw_amount: A numeric string of the debt_raw_amount converted to decimal.
        debt_face_amount: A numeric string of the debt_face_amount converted to decimal.
        collateral_token: The address of collateral token.
        collateral_amount: A numeric string of the collateral_amount converted to decimal.
    """

    liquidator: str
    user: str
    debt_token: str
    debt_raw_amount: str
    debt_face_amount: str
    collateral_token: str
    collateral_amount: str

    @field_validator("liquidator", "user", "debt_token", "collateral_token")
    def validate_valid_addresses(cls, value: str, info: ValidationInfo) -> str:
        """
        Check if the value is an address and format it to having leading zeros.

        Raises:
            ValueError

        Returns:
            str
        """
        if not value.startswith("0x"):
            raise ValueError("Invalid address provided for %s" % info.field_name)
        return add_leading_zeros(value)

    @field_validator("debt_raw_amount", "debt_face_amount", "collateral_amount")
    def validate_valid_numbers(cls, value: str, info: ValidationInfo) -> Decimal:
        """
        Convert the hexadecimal string value to a decimal.

        Raises:
            ValueError: If value is not a valid hexadecimal.

        Returns:
            Decimal: Converted decimal value.
        """
        try:
            return Decimal(int(value, base=16))
        except ValueError:
            raise ValueError("%s field is not a valid hexadecimal number" % info.field_name)

class WithdrawalEventData(BaseModel):
    """
    Class for representing withdrawal event data.

    Attributes:
        user (str): The address of the user making the withdrawal.
        amount (Decimal): The amount withdrawn.
        token (str): The address of the token being withdrawn.
    """

    user: str
    amount: Decimal
    token: str

    @field_validator("user", "token")
    def validate_addresses(cls, value: str) -> str:
        """
        Validates that the provided address starts with '0x' and formats it with leading zeros.

        Args:
            value (str): The address string to validate.

        Returns:
            str: The validated and formatted address.

        Raises:
            ValueError: If the provided address does not start with '0x'.
        """
        if not value.startswith("0x"):
            raise ValueError(f"Invalid address provided: {value}")
        return add_leading_zeros(value)

    @field_validator("amount", mode="before")
    def validate_amount(cls, value: str) -> Decimal:
        """
        Validates that the provided amount is numeric and converts it to a Decimal.

        Args:
            value (str): The amount string to validate.

        Returns:
            Decimal: The validated and converted amount as a Decimal.

        Raises:
            ValueError: If the provided amount is not numeric.
        """
        if not value.isdigit():
            raise ValueError("Amount field is not numeric")
        return Decimal(value)
