from .tokens import TokenType, Token

class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.tokens = []
        self.start = 0
        self.current = 0
        self.line = 1
        
        # Keyword map
        self.keywords = {
            "fn": TokenType.FN,
            "let": TokenType.LET,
            "mut": TokenType.MUT,
            "if": TokenType.IF,
            "else": TokenType.ELSE,
            "while": TokenType.WHILE,
            "for": TokenType.FOR,
            "return": TokenType.RETURN,
            "true": TokenType.TRUE,
            "false": TokenType.FALSE,
            "async": TokenType.ASYNC,
            "await": TokenType.AWAIT,
            "spawn": TokenType.SPAWN,
            "struct": TokenType.STRUCT,
            "impl": TokenType.IMPL,
            "and": TokenType.AND,
            "or": TokenType.OR,
            # "print": TokenType.PRINT,
        }

    def scan_tokens(self) -> list[Token]:
        while not self.is_at_end():
            self.start = self.current
            self.scan_token()
        
        self.tokens.append(Token(TokenType.EOF, "", None, self.line))
        return self.tokens

    def is_at_end(self) -> bool:
        return self.current >= len(self.source)

    def scan_token(self):
        c = self.advance()
        
        if c == '(':
            self.add_token(TokenType.LEFT_PAREN)
        elif c == ')':
            self.add_token(TokenType.RIGHT_PAREN)
        elif c == '{':
            self.add_token(TokenType.LEFT_BRACE)
        elif c == '}':
            self.add_token(TokenType.RIGHT_BRACE)
        elif c == '[':
            self.add_token(TokenType.LEFT_BRACKET)
        elif c == ']':
            self.add_token(TokenType.RIGHT_BRACKET)
        elif c == ',':
            self.add_token(TokenType.COMMA)
        elif c == '.':
            self.add_token(TokenType.DOT)
        elif c == '-':
            if self.match('>'):
                self.add_token(TokenType.ARROW)
            else:
                self.add_token(TokenType.MINUS)
        elif c == '+':
            self.add_token(TokenType.PLUS)
        elif c == ';':
            self.add_token(TokenType.SEMICOLON)
        elif c == ':':
            self.add_token(TokenType.COLON)
        elif c == '*':
            self.add_token(TokenType.STAR)
        elif c == '/':
            if self.peek() == '/':
                # Single line comment
                while self.peek() != '\n' and not self.is_at_end():
                    self.advance()
            elif self.peek() == '*':
                # Multi-line comment (simplified)
                self.advance() # consume *
                while not self.is_at_end() and not (self.peek() == '*' and self.peek_next() == '/'):
                    if self.peek() == '\n':
                        self.line += 1
                    self.advance()
                if not self.is_at_end():
                    self.advance() # consume *
                    self.advance() # consume /
            else:
                self.add_token(TokenType.SLASH)
        elif c == ' ':
            pass # Ignore whitespace
        elif c == '\r' or c == '\t':
            pass # Ignore whitespace
        elif c == '\n':
            self.line += 1
        elif c == '=':
            if self.match('='):
                self.add_token(TokenType.EQUAL_EQUAL)
            else:
                self.add_token(TokenType.EQUAL)
        elif c == '!':
            if self.match('='):
                self.add_token(TokenType.BANG_EQUAL)
            else:
                self.add_token(TokenType.BANG) 
        elif c == '<':
            if self.match('='):
                self.add_token(TokenType.LESS_EQUAL)
            else:
                self.add_token(TokenType.LESS)
        elif c == '>':
            if self.match('='):
                self.add_token(TokenType.GREATER_EQUAL)
            else:
                self.add_token(TokenType.GREATER)
        elif c == '&':
            if self.match('&'):
                self.add_token(TokenType.AND)
            else:
                self.add_token(TokenType.AMPERSAND)
        elif c == '|':
            if self.match('|'):
                self.add_token(TokenType.OR)
            else:
                self.add_token(TokenType.PIPE)
        elif c == '"':
            self.string()
        elif c.isdigit():
            self.number()
        elif c.isalpha() or c == '_':
            self.identifier()
        else:
            # Error handling would go here
            pass

    def advance(self) -> str:
        char = self.source[self.current]
        self.current += 1
        return char

    def match(self, expected: str) -> bool:
        if self.is_at_end():
            return False
        if self.source[self.current] != expected:
            return False
        
        self.current += 1
        return True

    def peek(self) -> str:
        if self.is_at_end():
            return '\0'
        return self.source[self.current]

    def peek_next(self) -> str:
        if self.current + 1 >= len(self.source):
            return '\0'
        return self.source[self.current + 1]

    def string(self):
        while self.peek() != '"' and not self.is_at_end():
            if self.peek() == '\n':
                self.line += 1
            self.advance()
        
        if self.is_at_end():
            # Unterminated string error
            return
        
        # Closing "
        self.advance()
        
        value = self.source[self.start + 1 : self.current - 1]
        self.add_token(TokenType.STRING, value)

    def number(self):
        while self.peek().isdigit():
            self.advance()
        
        # Look for fractional part
        if self.peek() == '.' and self.peek_next().isdigit():
            self.advance() # consume .
            while self.peek().isdigit():
                self.advance()
        
        text = self.source[self.start:self.current]
        self.add_token(TokenType.NUMBER, float(text))

    def identifier(self):
        while self.peek().isalnum() or self.peek() == '_':
            self.advance()
        
        text = self.source[self.start:self.current]
        token_type = self.keywords.get(text, TokenType.IDENTIFIER)
        self.add_token(token_type)

    def add_token(self, type: TokenType, literal: object = None):
        text = self.source[self.start:self.current]
        self.tokens.append(Token(type, text, literal, self.line))
