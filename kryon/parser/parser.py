from ..lexer.tokens import TokenType, Token
from ..ast import nodes as ast
from typing import List

class ParseError(Exception):
    pass

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.current = 0
        self.errors = []

    def parse(self) -> List[ast.Stmt]:
        statements = []
        while not self.is_at_end():
            try:
                stmt = self.declaration()
                if stmt:
                    statements.append(stmt)
            except ParseError:
                self.synchronize()
        return statements

    def declaration(self) -> ast.Stmt:
        if self.match(TokenType.FN):
            return self.function_declaration()
        if self.match(TokenType.LET, TokenType.MUT):
            return self.var_declaration()
        return self.statement()

    def function_declaration(self) -> ast.FunctionDecl:
        name = self.consume(TokenType.IDENTIFIER, "Expect function name.")
        
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after function name.")
        parameters = []
        if not self.check(TokenType.RIGHT_PAREN):
            while True:
                param_name = self.consume(TokenType.IDENTIFIER, "Expect parameter name.")
                # Skip type annotation for now (simplified)
                if self.check(TokenType.COLON):
                    self.advance()
                    self.consume(TokenType.IDENTIFIER, "Expect type name.")
                
                parameters.append(param_name.lexeme)
                if not self.match(TokenType.COMMA):
                    break
        
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after parameters.")
        
        # Skip return type arrow if present
        if self.match(TokenType.ARROW):
            self.consume(TokenType.IDENTIFIER, "Expect return type.")

        self.consume(TokenType.LEFT_BRACE, "Expect '{' before function body.")
        body = self.block()
        
        return ast.FunctionDecl(name.lexeme, parameters, body)

    def var_declaration(self) -> ast.VarDecl:
        is_mut = self.previous().type == TokenType.MUT
        name = self.consume(TokenType.IDENTIFIER, "Expect variable name.")
        
        initializer = None
        if self.match(TokenType.EQUAL):
            initializer = self.expression()
        
        self.consume(TokenType.SEMICOLON, "Expect ';' after variable declaration.")
        return ast.VarDecl(name.lexeme, initializer, is_mut)

    def statement(self) -> ast.Stmt:
        
        if self.match(TokenType.LEFT_BRACE):
            return self.block()
        
        return self.expression_statement()

    def block(self) -> ast.Block:
        statements = []
        while not self.check(TokenType.RIGHT_BRACE) and not self.is_at_end():
            statements.append(self.declaration())
        
        self.consume(TokenType.RIGHT_BRACE, "Expect '}' after block.")
        return ast.Block(statements)

    def expression_statement(self) -> ast.ExpressionStmt:
        expr = self.expression()
        # Ensure we consume the semicolon
        self.consume(TokenType.SEMICOLON, "Expect ';' after expression.")
        return ast.ExpressionStmt(expr)

    def expression(self) -> ast.Expr:
        return self.assignment()

    def assignment(self) -> ast.Expr:
        expr = self.or_logic()
        
        if self.match(TokenType.EQUAL):
            equals = self.previous()
            value = self.assignment()
            
            if isinstance(expr, ast.Variable):
                return ast.Assign(expr.name, value) # Need Assign node in AST
            # Error handling for invalid lvalue would go here
            
        return expr

    def or_logic(self) -> ast.Expr:
        expr = self.and_logic()
        while self.match(TokenType.OR):
            operator = self.previous()
            right = self.and_logic()
            expr = ast.Binary(expr, operator.lexeme, right)
        return expr

    def and_logic(self) -> ast.Expr:
        expr = self.equality()
        while self.match(TokenType.AND):
            operator = self.previous()
            right = self.equality()
            expr = ast.Binary(expr, operator.lexeme, right)
        return expr

    def equality(self) -> ast.Expr:
        expr = self.comparison()
        while self.match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            operator = self.previous()
            right = self.comparison()
            expr = ast.Binary(expr, operator.lexeme, right)
        return expr

    def comparison(self) -> ast.Expr:
        expr = self.term()
        while self.match(TokenType.GREATER, TokenType.GREATER_EQUAL, TokenType.LESS, TokenType.LESS_EQUAL):
            operator = self.previous()
            right = self.term()
            expr = ast.Binary(expr, operator.lexeme, right)
        return expr

    def term(self) -> ast.Expr:
        expr = self.factor()
        while self.match(TokenType.MINUS, TokenType.PLUS):
            operator = self.previous()
            right = self.factor()
            expr = ast.Binary(expr, operator.lexeme, right)
        return expr

    def factor(self) -> ast.Expr:
        expr = self.unary()
        while self.match(TokenType.SLASH, TokenType.STAR):
            operator = self.previous()
            right = self.unary()
            expr = ast.Binary(expr, operator.lexeme, right)
        return expr

    def unary(self) -> ast.Expr:
        if self.match(TokenType.BANG, TokenType.MINUS):
            operator = self.previous()
            right = self.unary()
            return ast.Unary(operator.lexeme, right)
        return self.call()

    def call(self) -> ast.Expr:
        expr = self.primary()
        
        while True:
            if self.match(TokenType.LEFT_PAREN):
                expr = self.finish_call(expr)
            else:
                break
        return expr

    def finish_call(self, callee: ast.Expr) -> ast.Call:
        arguments = []
        if not self.check(TokenType.RIGHT_PAREN):
            while True:
                arguments.append(self.expression())
                if not self.match(TokenType.COMMA):
                    break
        
        paren = self.consume(TokenType.RIGHT_PAREN, "Expect ')' after arguments.")
        return ast.Call(callee, arguments)

    def primary(self) -> ast.Expr:
        if self.match(TokenType.FALSE): return ast.Literal(False)
        if self.match(TokenType.TRUE): return ast.Literal(True)
        if self.match(TokenType.NUMBER, TokenType.STRING):
            return ast.Literal(self.previous().literal)
        
        if self.match(TokenType.IDENTIFIER):
            return ast.Variable(self.previous().lexeme)
        
        if self.match(TokenType.LEFT_PAREN):
            expr = self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Expect ')' after expression.")
            return ast.Grouping(expr)
        
        raise self.error(self.peek(), "Expect expression.")

    # --- Helper Methods ---

    def match(self, *types: TokenType) -> bool:
        for type in types:
            if self.check(type):
                self.advance()
                return True
        return False

    def consume(self, type: TokenType, message: str) -> Token:
        if self.check(type):
            return self.advance()
        raise self.error(self.peek(), message)

    def check(self, type: TokenType) -> bool:
        if self.is_at_end():
            return False
        return self.peek().type == type

    def advance(self) -> Token:
        if not self.is_at_end():
            self.current += 1
        return self.previous()

    def is_at_end(self) -> bool:
        return self.peek().type == TokenType.EOF

    def peek(self) -> Token:
        return self.tokens[self.current]

    def previous(self) -> Token:
        return self.tokens[self.current - 1]

    def error(self, token: Token, message: str) -> ParseError:
        msg = f"[line {token.line}] Error at '{token.lexeme}': {message}"
        self.errors.append(msg)
        return ParseError(msg)

    def synchronize(self):
        self.advance()
        while not self.is_at_end():
            if self.previous().type == TokenType.SEMICOLON:
                return
            if self.peek().type in [
                TokenType.FN, TokenType.LET, TokenType.MUT, 
                TokenType.FOR, TokenType.IF, TokenType.WHILE, 
                TokenType.PRINT, TokenType.RETURN
            ]:
                return
            self.advance()
