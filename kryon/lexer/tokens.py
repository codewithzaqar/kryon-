from enum import Enum, auto

class TokenType(Enum):
    # Single-character tokens
    LEFT_PAREN = auto()
    RIGHT_PAREN = auto()
    LEFT_BRACE = auto()
    RIGHT_BRACE = auto()
    LEFT_BRACKET = auto()
    RIGHT_BRACKET = auto()
    COMMA = auto()
    DOT = auto()
    MINUS = auto()
    PLUS = auto()
    SEMICOLON = auto()
    COLON = auto()
    STAR = auto()
    SLASH = auto()
    BANG = auto()
    ARROW = auto()
    AMPERSAND = auto() 
    PIPE = auto() 

    # One or two character tokens
    BANG_EQUAL = auto()
    EQUAL = auto()
    EQUAL_EQUAL = auto()
    GREATER = auto()
    GREATER_EQUAL = auto()
    LESS = auto()
    LESS_EQUAL = auto()
    AMPERSAND_AMPERSAND = auto()
    PIPE_PIPE = auto()

    # Literals
    IDENTIFIER = auto()
    STRING = auto()
    NUMBER = auto()

    # Keywords
    FN = auto()
    LET = auto()
    MUT = auto()
    IF = auto()
    ELSE = auto()
    WHILE = auto()
    FOR = auto()
    RETURN = auto()
    TRUE = auto()
    FALSE = auto()
    ASYNC = auto()
    AWAIT = auto()
    SPAWN = auto()
    STRUCT = auto()
    IMPL = auto()
    AND = auto()
    OR = auto()
    PRINT = auto()

    # Special
    EOF = auto()
    UNKNOWN = auto()

class Token:
    def __init__(self, type: TokenType, lexeme: str, literal: object, line: int):
        self.type = type
        self.lexeme = lexeme
        self.literal = literal
        self.line = line

    def __repr__(self):
        return f"Token({self.type}, '{self.lexeme}', {self.literal}, Line {self.line})"
