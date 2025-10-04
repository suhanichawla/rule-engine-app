"""Expression parser for rule evaluation.

Supports boolean expressions with AND, OR, parentheses, and comparison operators.

Example expressions:
- age >= 18
- age >= 18 AND credit_score > 700
- (age >= 18 AND credit_score > 700) OR country == 'USA'
- status IN ['active', 'pending'] AND balance > 1000
"""

import logging
import re
from dataclasses import dataclass
from enum import Enum
from typing import Any, List, Union

logger = logging.getLogger(__name__)


class TokenType(Enum):
    """Token types for expression parsing."""
    FIELD = "FIELD"
    OPERATOR = "OPERATOR"
    VALUE = "VALUE"
    AND = "AND"
    OR = "OR"
    LPAREN = "LPAREN"
    RPAREN = "RPAREN"
    EOF = "EOF"


@dataclass
class Token:
    """A single token in the expression."""
    type: TokenType
    value: Any
    position: int


class ExpressionTokenizer:
    """Tokenizer for boolean expressions."""

    OPERATORS = ['==', '!=', '>=', '<=', '>', '<', 'contains', 'not_contains', 'in', 'not_in']

    def __init__(self, expression: str):
        self.expression = expression
        self.position = 0
        self.length = len(expression)

    def tokenize(self) -> List[Token]:
        """Tokenize the expression into a list of tokens."""
        tokens = []

        while self.position < self.length:
            self._skip_whitespace()

            if self.position >= self.length:
                break

            # Check for parentheses
            if self.expression[self.position] == '(':
                tokens.append(Token(TokenType.LPAREN, '(', self.position))
                self.position += 1
                continue

            if self.expression[self.position] == ')':
                tokens.append(Token(TokenType.RPAREN, ')', self.position))
                self.position += 1
                continue

            # Check for AND/OR (case-insensitive)
            word = self._peek_word().upper()
            if word == 'AND':
                tokens.append(Token(TokenType.AND, 'AND', self.position))
                self.position += 3
                continue

            if word == 'OR':
                tokens.append(Token(TokenType.OR, 'OR', self.position))
                self.position += 2
                continue

            # Check for operators
            operator = self._try_read_operator()
            if operator:
                tokens.append(Token(TokenType.OPERATOR, operator, self.position - len(operator)))
                continue

            # Check for string literals
            if self.expression[self.position] in ['"', "'"]:
                value = self._read_string()
                tokens.append(Token(TokenType.VALUE, value, self.position))
                continue

            # Check for array literals
            if self.expression[self.position] == '[':
                array = self._read_array()
                tokens.append(Token(TokenType.VALUE, array, self.position))
                continue

            # Check for numbers or booleans
            if self.expression[self.position].isdigit() or self.expression[self.position] == '-':
                value = self._read_number()
                tokens.append(Token(TokenType.VALUE, value, self.position))
                continue

            # Check for boolean literals (case-insensitive)
            word_lower = self._peek_word().lower()
            if word_lower in ['true', 'false']:
                word = self._peek_word()
                tokens.append(Token(TokenType.VALUE, word_lower == 'true', self.position))
                self.position += len(word)
                continue

            # Check for null (case-insensitive)
            if self._peek_word().lower() == 'null':
                word = self._peek_word()
                tokens.append(Token(TokenType.VALUE, None, self.position))
                self.position += len(word)
                continue

            # Otherwise, it's a field name
            field = self._read_field()
            if not field:
                # Prevent infinite loop if we can't parse anything
                raise ValueError(
                    f"Unexpected character '{self.expression[self.position]}' at position {self.position}. "
                    f"Context: ...{self.expression[max(0, self.position-10):self.position+10]}..."
                )
            tokens.append(Token(TokenType.FIELD, field, self.position - len(field)))

        tokens.append(Token(TokenType.EOF, None, self.position))
        return tokens

    def _skip_whitespace(self):
        """Skip whitespace characters."""
        while self.position < self.length and self.expression[self.position].isspace():
            self.position += 1

    def _peek_word(self) -> str:
        """Peek at the next word without consuming it."""
        start = self.position
        end = start
        while end < self.length and (self.expression[end].isalnum() or self.expression[end] == '_'):
            end += 1
        return self.expression[start:end]

    def _try_read_operator(self) -> str:
        """Try to read an operator."""
        # Check multi-character operators first (order matters)
        for op in ['not_contains', 'not_in', '==', '!=', '>=', '<=', 'contains', 'in']:
            if self.expression[self.position:].startswith(op):
                # For word-based operators (in, contains, not_in, not_contains),
                # make sure they're not part of a field name
                next_pos = self.position + len(op)
                if op in ['in', 'contains', 'not_in', 'not_contains']:
                    if next_pos < self.length and (self.expression[next_pos].isalnum() or self.expression[next_pos] == '_'):
                        # This is part of a field name, not an operator
                        continue
                self.position += len(op)
                return op

        # Check single = and throw error (if we reach here, it's not ==)
        if self.position < self.length and self.expression[self.position] == '=':
            raise ValueError(
                f"Single '=' operator at position {self.position}. "
                f"Use '==' for equality comparison. "
                f"Context: ...{self.expression[max(0, self.position-10):self.position+10]}..."
            )

        # Check single-character operators
        if self.position < self.length and self.expression[self.position] in ['>', '<']:
            op = self.expression[self.position]
            self.position += 1
            return op

        return None

    def _read_string(self) -> str:
        """Read a string literal."""
        quote = self.expression[self.position]
        self.position += 1
        start = self.position

        while self.position < self.length and self.expression[self.position] != quote:
            if self.expression[self.position] == '\\':
                self.position += 2  # Skip escaped character
            else:
                self.position += 1

        value = self.expression[start:self.position]
        self.position += 1  # Skip closing quote
        return value

    def _read_array(self) -> List[Any]:
        """Read an array literal [value1, value2, ...]."""
        self.position += 1  # Skip '['
        values = []

        while self.position < self.length:
            self._skip_whitespace()

            if self.expression[self.position] == ']':
                self.position += 1
                break

            if self.expression[self.position] in ['"', "'"]:
                values.append(self._read_string())
            elif self.expression[self.position].isdigit() or self.expression[self.position] == '-':
                values.append(self._read_number())
            else:
                start = self.position
                while self.position < self.length and self.expression[self.position] not in [',', ']']:
                    self.position += 1
                value = self.expression[start:self.position].strip()
                value_lower = value.lower()
                if value_lower == 'true':
                    values.append(True)
                elif value_lower == 'false':
                    values.append(False)
                elif value_lower == 'null':
                    values.append(None)
                else:
                    values.append(value)

            self._skip_whitespace()

            if self.position < self.length and self.expression[self.position] == ',':
                self.position += 1

        return values

    def _read_number(self) -> Union[int, float]:
        """Read a number (integer or float)."""
        start = self.position

        if self.expression[self.position] == '-':
            self.position += 1

        while self.position < self.length and (self.expression[self.position].isdigit() or self.expression[self.position] == '.'):
            self.position += 1

        value_str = self.expression[start:self.position]

        if '.' in value_str:
            return float(value_str)
        return int(value_str)

    def _read_field(self) -> str:
        """Read a field name."""
        start = self.position

        while self.position < self.length and (self.expression[self.position].isalnum() or self.expression[self.position] == '_'):
            self.position += 1

        return self.expression[start:self.position]


# AST Node types
@dataclass
class ComparisonNode:
    """A comparison operation (e.g., age >= 18 or ip_country == account_country)."""
    field: str
    operator: str
    value: Any
    is_field_comparison: bool = False  # True if value is a field reference


@dataclass
class BinaryOpNode:
    """A binary operation (AND/OR)."""
    operator: str  # "AND" or "OR"
    left: Union['BinaryOpNode', ComparisonNode]
    right: Union['BinaryOpNode', ComparisonNode]


class ExpressionParser:
    """Parser for boolean expressions."""

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.position = 0

    def parse(self) -> Union[ComparisonNode, BinaryOpNode]:
        """Parse the tokens into an AST."""
        return self._parse_or()

    def _current_token(self) -> Token:
        """Get the current token."""
        if self.position < len(self.tokens):
            return self.tokens[self.position]
        return self.tokens[-1]  # EOF

    def _advance(self):
        """Move to the next token."""
        self.position += 1

    def _parse_or(self) -> Union[ComparisonNode, BinaryOpNode]:
        """Parse OR expressions (lowest precedence)."""
        left = self._parse_and()

        while self._current_token().type == TokenType.OR:
            self._advance()
            right = self._parse_and()
            left = BinaryOpNode(operator="OR", left=left, right=right)

        return left

    def _parse_and(self) -> Union[ComparisonNode, BinaryOpNode]:
        """Parse AND expressions."""
        left = self._parse_comparison()

        while self._current_token().type == TokenType.AND:
            self._advance()
            right = self._parse_comparison()
            left = BinaryOpNode(operator="AND", left=left, right=right)

        return left

    def _parse_comparison(self) -> Union[ComparisonNode, BinaryOpNode]:
        """Parse comparison or parenthesized expression."""
        # Check for parentheses
        if self._current_token().type == TokenType.LPAREN:
            self._advance()
            expr = self._parse_or()
            if self._current_token().type != TokenType.RPAREN:
                raise ValueError(f"Expected ')' at position {self._current_token().position}")
            self._advance()
            return expr

        # Parse comparison: field operator value
        if self._current_token().type != TokenType.FIELD:
            raise ValueError(f"Expected field name at position {self._current_token().position}")

        field = self._current_token().value
        self._advance()

        if self._current_token().type != TokenType.OPERATOR:
            raise ValueError(f"Expected operator at position {self._current_token().position}")

        operator = self._current_token().value
        self._advance()

        # Right side can be either a VALUE (literal) or FIELD (field reference)
        current_token = self._current_token()
        if current_token.type == TokenType.VALUE:
            value = current_token.value
            is_field_comparison = False
        elif current_token.type == TokenType.FIELD:
            value = current_token.value  # Store field name
            is_field_comparison = True
        else:
            raise ValueError(f"Expected value or field name at position {current_token.position}")

        self._advance()

        return ComparisonNode(field=field, operator=operator, value=value, is_field_comparison=is_field_comparison)


def parse_expression(expression: str) -> Union[ComparisonNode, BinaryOpNode]:
    """Parse an expression string into an AST.

    Args:
        expression: The expression string to parse

    Returns:
        AST root node

    Raises:
        ValueError: If the expression is invalid
    """
    logger.debug(f"Parsing expression: {expression}")
    tokenizer = ExpressionTokenizer(expression)
    tokens = tokenizer.tokenize()
    logger.debug(f"Tokens: {tokens}")

    parser = ExpressionParser(tokens)
    ast = parser.parse()
    logger.debug(f"AST: {ast}")

    return ast


def extract_fields_from_ast(node: Union[ComparisonNode, BinaryOpNode]) -> List[str]:
    """Extract all field names referenced in an expression AST.

    Args:
        node: The AST node (ComparisonNode or BinaryOpNode)

    Returns:
        List of unique field names
    """
    fields = []

    if isinstance(node, ComparisonNode):
        fields.append(node.field)
        if node.is_field_comparison:
            fields.append(node.value)
    elif isinstance(node, BinaryOpNode):
        fields.extend(extract_fields_from_ast(node.left))
        fields.extend(extract_fields_from_ast(node.right))

    return list(set(fields))

