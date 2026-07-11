from ..ast import nodes as ast
from .environment import Environment, RuntimeError
from ..lexer.tokens import Token
import time

class KryonRuntimeError(RuntimeError):
    pass

class ReturnSignal(Exception):
    """Used to unwind the stack when a return statement is encountered."""
    def __init__(self, value):
        self.value = value

class Interpreter:
    def __init__(self):
        self.globals = Environment()
        self.environment = self.globals
        self._setup_builtins()

    def _setup_builtins(self):
        self.globals.define("print", lambda *args: print(*args))
        self.globals.define("clock", lambda: time.time())
        self.globals.define("input", lambda prompt="": input(prompt))

    def interpret(self, statements: list[ast.Stmt]):
        try:
            for statement in statements:
                self.execute(statement)
        except KryonRuntimeError as e:
            print(f"Runtime Error: {e.message}")
        except ReturnSignal as e:
            print(f"Unexpected return outside function")

    def execute(self, stmt: ast.Stmt):
        stmt.accept(self)

    def evaluate(self, expr: ast.Expr) -> Any:
        return expr.accept(self)

    # --- Statement Visitors ---

    def visit_expression_stmt(self, stmt: ast.ExpressionStmt):
        self.evaluate(stmt.expression)

    def visit_var_decl_stmt(self, stmt: ast.VarDecl):
        value = None
        if stmt.initializer is not None:
            value = self.evaluate(stmt.initializer)
        self.environment.define(stmt.name, value)

    def visit_block_stmt(self, stmt: ast.Block):
        # Create a new scope
        previous_env = self.environment
        self.environment = Environment(self.environment)
        
        try:
            for statement in stmt.statements:
                self.execute(statement)
        finally:
            # Restore previous scope
            self.environment = previous_env

    def visit_if_stmt(self, stmt: ast.If):
        if self.is_truthy(self.evaluate(stmt.condition)):
            self.execute(stmt.then_branch)
        elif stmt.else_branch is not None:
            self.execute(stmt.else_branch)

    def visit_while_stmt(self, stmt: ast.While):
        while self.is_truthy(self.evaluate(stmt.condition)):
            self.execute(stmt.body)

    def visit_function_decl_stmt(self, stmt: ast.FunctionDecl):
        # Define function in current environment
        self.environment.define(stmt.name, stmt)

    def visit_return_stmt(self, stmt: ast.Return):
        value = None
        if stmt.value is not None:
            value = self.evaluate(stmt.value)
        raise ReturnSignal(value)

    # --- Expression Visitors ---

    def visit_literal_expr(self, expr: ast.Literal):
        return expr.value

    def visit_grouping_expr(self, expr: ast.Grouping):
        return self.evaluate(expr.expression)

    def visit_unary_expr(self, expr: ast.Unary):
        right = self.evaluate(expr.right)
        if expr.operator == "-":
            return -right
        if expr.operator == "!":
            return not self.is_truthy(right)
        return None

    def visit_binary_expr(self, expr: ast.Binary):
        left = self.evaluate(expr.left)
        right = self.evaluate(expr.right)

        if expr.operator == "+":
            if isinstance(left, str) or isinstance(right, str):
                return str(left) + str(right)
            return left + right
        if expr.operator == "-": return left - right
        if expr.operator == "*": return left * right
        if expr.operator == "/": 
            if right == 0: raise KryonRuntimeError(None, "Division by zero")
            return left / right
        
        if expr.operator == ">": return left > right
        if expr.operator == ">=": return left >= right
        if expr.operator == "<": return left < right
        if expr.operator == "<=": return left <= right
        if expr.operator == "==": return left == right
        if expr.operator == "!=": return left != right
        
        if expr.operator == "and": # Logical AND
            if not self.is_truthy(left): return left
            return right
        if expr.operator == "or": # Logical OR
            if self.is_truthy(left): return left
            return right

        return None

    def visit_variable_expr(self, expr: ast.Variable):
        return self.environment.get(expr.name)

    def visit_assign_expr(self, expr: ast.Assign):
        value = self.evaluate(expr.value)
        self.environment.assign(expr.name, value)
        return value

    def visit_call_expr(self, expr: ast.Call):
        callee = self.evaluate(expr.callee)
        arguments = [self.evaluate(arg) for arg in expr.arguments]

        if callable(callee):
            if len(arguments) != callee.__code__.co_argcount:
                 # Simple check, doesn't handle *args
                 pass 
            return callee(*arguments)
        
        if isinstance(callee, ast.FunctionDecl):
            return self.execute_function(callee, arguments)
            
        raise KryonRuntimeError(None, "Can only call functions and classes.")

    def execute_function(self, func: ast.FunctionDecl, arguments: list):
        # Create new environment for function scope
        previous_env = self.environment
        self.environment = Environment(self.environment)
        
        # Bind parameters
        for param, arg in zip(func.params, arguments):
            self.environment.define(param, arg)
        
        try:
            for stmt in func.body.statements:
                self.execute(stmt)
        except ReturnSignal as e:
            value = e.value
            self.environment = previous_env
            return value
        
        self.environment = previous_env
        return None

    def is_truthy(self, obj):
        if obj is None: return False
        if isinstance(obj, bool): return obj
        return True
