from abc import ABC, abstractmethod
from typing import List, Any

class Expr(ABC):
    @abstractmethod
    def accept(self, visitor):
        pass

class Stmt(ABC):
    @abstractmethod
    def accept(self, visitor):
        pass

# --- Expressions ---

class Literal(Expr):
    def __init__(self, value: Any):
        self.value = value

    def accept(self, visitor):
        return visitor.visit_literal_expr(self)

class Binary(Expr):
    def __init__(self, left: Expr, operator: str, right: Expr):
        self.left = left
        self.operator = operator
        self.right = right

    def accept(self, visitor):
        return visitor.visit_binary_expr(self)

class Unary(Expr):
    def __init__(self, operator: str, right: Expr):
        self.operator = operator
        self.right = right

    def accept(self, visitor):
        return visitor.visit_unary_expr(self)

class Grouping(Expr):
    def __init__(self, expression: Expr):
        self.expression = expression

    def accept(self, visitor):
        return visitor.visit_grouping_expr(self)

class Variable(Expr):
    def __init__(self, name: str):
        self.name = name

    def accept(self, visitor):
        return visitor.visit_variable_expr(self)

class Call(Expr):
    def __init__(self, callee: Expr, arguments: List[Expr]):
        self.callee = callee
        self.arguments = arguments

    def accept(self, visitor):
        return visitor.visit_call_expr(self)

# --- Statements ---

class ExpressionStmt(Stmt):
    def __init__(self, expression: Expr):
        self.expression = expression

    def accept(self, visitor):
        return visitor.visit_expression_stmt(self)

class PrintStmt(Stmt):
    def __init__(self, expression: Expr):
        self.expression = expression

    def accept(self, visitor):
        return visitor.visit_print_stmt(self)

class VarDecl(Stmt):
    def __init__(self, name: str, initializer: Expr, is_mut: bool):
        self.name = name
        self.initializer = initializer
        self.is_mut = is_mut

    def accept(self, visitor):
        return visitor.visit_var_decl_stmt(self)

class Block(Stmt):
    def __init__(self, statements: List[Stmt]):
        self.statements = statements

    def accept(self, visitor):
        return visitor.visit_block_stmt(self)

class FunctionDecl(Stmt):
    def __init__(self, name: str, params: List[str], body: Block):
        self.name = name
        self.params = params
        self.body = body

    def accept(self, visitor):
        return visitor.visit_function_decl_stmt(self)

class Assign(Expr):
    def __init__(self, name: str, value: Expr):
        self.name = name
        self.value = value

    def accept(self, visitor):
        return visitor.visit_assign_expr(self)
