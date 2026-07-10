from ..ast import nodes as ast
from typing import Dict, Any

class RuntimeError(Exception):
    def __init__(self, token, message):
        self.token = token
        self.message = message
        super().__init__(message)

class Interpreter:
    def __init__(self):
        self.globals: Dict[str, Any] = {}
        # Built-in functions
        self.globals["print"] = lambda *args: print(*args)

    def interpret(self, statements: list[ast.Stmt]):
        try:
            for statement in statements:
                self.execute(statement)
        except RuntimeError as e:
            print(f"Runtime Error: {e.message}")

    def execute(self, stmt: ast.Stmt):
        stmt.accept(self)

    def evaluate(self, expr: ast.Expr) -> Any:
        return expr.accept(self)

    # --- Statement Visitors ---

    def visit_expression_stmt(self, stmt: ast.ExpressionStmt):
        self.evaluate(stmt.expression)

    def visit_print_stmt(self, stmt: ast.PrintStmt):
        value = self.evaluate(stmt.expression)
        print(value)

    def visit_var_decl_stmt(self, stmt: ast.VarDecl):
        value = None
        if stmt.initializer is not None:
            value = self.evaluate(stmt.initializer)
        self.globals[stmt.name] = value

    def visit_block_stmt(self, stmt: ast.Block):
        # In a full implementation, this would push a new environment scope
        for statement in stmt.statements:
            self.execute(statement)

    def visit_function_decl_stmt(self, stmt: ast.FunctionDecl):
        # Store function definition in globals
        self.globals[stmt.name] = stmt

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
            return not right
        return None

    def visit_binary_expr(self, expr: ast.Binary):
        left = self.evaluate(expr.left)
        right = self.evaluate(expr.right)

        if expr.operator == "+":
            if isinstance(left, float) or isinstance(right, float):
                return float(left) + float(right)
            if isinstance(left, int) or isinstance(right, int):
                return left + right
            if isinstance(left, str) and isinstance(right, str):
                return left + right
        if expr.operator == "-":
            return left - right
        if expr.operator == "*":
            return left * right
        if expr.operator == "/":
            if right == 0:
                raise RuntimeError(None, "Division by zero")
            return left / right
        
        if expr.operator == ">": return left > right
        if expr.operator == ">=": return left >= right
        if expr.operator == "<": return left < right
        if expr.operator == "<=": return left <= right
        if expr.operator == "==": return left == right
        if expr.operator == "!=": return left != right

        return None

    def visit_variable_expr(self, expr: ast.Variable):
        if expr.name in self.globals:
            return self.globals[expr.name]
        raise RuntimeError(None, f"Undefined variable '{expr.name}'")

    def visit_assign_expr(self, expr: ast.Assign):
        value = self.evaluate(expr.value)
        if expr.name in self.globals:
            self.globals[expr.name] = value
        else:
            raise RuntimeError(None, f"Undefined variable '{expr.name}'")
        return value

    def visit_call_expr(self, expr: ast.Call):
        callee = self.evaluate(expr.callee)
        arguments = [self.evaluate(arg) for arg in expr.arguments]

        if callable(callee):
            return callee(*arguments)
        
        if isinstance(callee, ast.FunctionDecl):
            # Simple function execution without proper scope handling yet
            # Save current args
            old_globals = dict(self.globals)
            for param, arg in zip(callee.params, arguments):
                self.globals[param] = arg
            
            result = None
            # Execute body
            for stmt in callee.body.statements:
                if isinstance(stmt, ast.ExpressionStmt):
                     result = self.evaluate(stmt.expression)
                elif isinstance(stmt, ast.ReturnStmt): # Need ReturnStmt in AST
                     pass 
                else:
                     self.execute(stmt)
            
            # Restore globals (very naive scoping)
            self.globals.clear()
            self.globals.update(old_globals)
            return result
            
        raise RuntimeError(None, "Can only call functions and classes.")
