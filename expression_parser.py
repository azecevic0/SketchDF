import re
import sys

import numpy as np
from enum import Enum, auto

class Token(Enum):
    NUMBER      = r'\d+(\.\d*)?'
    ABS         = r'abs'
    SINH        = r'sinh'
    COSH        = r'cosh'
    TANH        = r'tanh'
    ARCSINH     = r'arcsinh'
    ARCCOSH     = r'arccosh'
    ARCTANH     = r'arct(an|g)h'
    SIN         = r'sin'
    COS         = r'cos'
    TAN         = r't(an|g)'
    ARCSIN      = r'arcsin'
    ARCCOS      = r'arccos'
    ARCTAN      = r'arct(an|g)'
    LOG         = r'l(og|n)'
    EXP         = r'exp'
    POWER       = r'\^|\*\*'
    PLUS        = r'\+'
    MINUS       = r'-'
    MULTIPLY    = r'\*'
    DIVIDE      = r'/'
    E           = r'e'
    PI          = r'pi'
    VARIABLE    = r'[a-z]'
    LPAREN      = r'\('
    RPAREN      = r'\)'
    BLANK       = r'\s+'
    WILDCARD    = r'.'


class Operation(Enum):
    ADD         = np.add
    SUBTRACT    = np.subtract
    MULTIPLY    = np.multiply
    DIVIDE      = np.divide
    NEGATIVE    = np.negative
    POWER       = np.power
    ABS         = np.abs
    LOG         = np.log
    EXP         = np.exp
    SIN         = np.sin
    COS         = np.cos
    TAN         = np.tan
    ARCSIN      = np.arcsin
    ARCCOS      = np.arccos
    ARCTAN      = np.arctan
    SINH        = np.sinh
    COSH        = np.cosh
    TANH        = np.tanh
    ARCSINH     = np.arcsinh
    ARCCOSH     = np.arccosh
    ARCTANH     = np.arctanh
    E           = np.e
    PI          = np.pi
    CONST       = auto()
    VARIABLE    = auto()


class Lexer:
    def __init__(self, expression):
        regex = re.compile(
            '|'.join(f'(?P<{token.name}>{token.value})' for token in Token),
            re.I
        )

        self.iterator = re.finditer(regex, expression)

    def __call__(self):
        for match in self.iterator:
            token_type = Token[match.lastgroup]
            token_value = match.group()
            if token_type == Token.WILDCARD:
                raise SyntaxError(f'Lexical error: Unexpected token {token_value}')
            if token_type != Token.BLANK:
                return token_type, token_value

        return None


class Parser:
    def __init__(self, expression, *, variable_name='x'):
        self.lexer = Lexer(expression)
        self.variable_name = variable_name.lower()
        self.current_token = None
        self.__consume()

    def parse(self):
        ast = self.__expr()
        if self.current_token:
            raise SyntaxError(f'Expected terminator, got {self.current_token[0].name}')
        return ast

    def __consume(self):
        self.current_token = self.lexer()

    def __expect(self, token, msg):
        if self.current_token[0] != token:
            raise SyntaxError(f'Expected {msg}, got {self.current_token[0].name}')
        self.__consume()

    def __expr(self):
        node = self.__term()

        while self.current_token and self.current_token[0] in (Token.PLUS, Token.MINUS):
            token_type = self.current_token[0]
            self.__consume()
            if token_type == Token.PLUS:
                node = Operation.ADD, node, self.__term()
            elif token_type == Token.MINUS:
                node = Operation.SUBTRACT, node, self.__term()

        return node

    def __term(self):
        node = self.__negative()

        while self.current_token and self.current_token[0] in (Token.MULTIPLY, Token.DIVIDE):
            token_type = self.current_token[0]
            self.__consume()
            if token_type == Token.MULTIPLY:
                node = Operation.MULTIPLY, node, self.__negative()
            elif token_type == Token.DIVIDE:
                node = Operation.DIVIDE, node, self.__negative()

        return node
    
    def __negative(self):
        if self.current_token and self.current_token[0] == Token.MINUS:
            self.__consume()
            return Operation.NEGATIVE, self.__power()
        return self.__power()
    
    def __power(self):
        node = self.__factor()

        while self.current_token and self.current_token[0] == Token.POWER:
            self.__consume()
            node = Operation.POWER, node, self.__power()
        
        return node

    def __factor(self):
        token = self.current_token

        match token:
            case [Token.NUMBER, value]:
                self.__consume()
                return Operation.CONST, float(value)
            
            case [Token.E | Token.PI as const, _]:
                self.__consume()
                return Operation.CONST, Operation[const.name].value
            
            case [Token.VARIABLE, name]:
                if name.lower() != self.variable_name:
                    raise SyntaxError(f'Unexpected variable {self.variable_name}, got {name.lower()}')
                self.__consume()
                return Operation.VARIABLE, name
            
            case [
                Token.ABS |
                Token.LOG |
                Token.EXP |
                Token.SIN |
                Token.COS |
                Token.TAN |
                Token.ARCSIN |
                Token.ARCCOS |
                Token.ARCTAN |
                Token.SINH |
                Token.COSH |
                Token.TANH |
                Token.ARCSINH |
                Token.ARCCOSH |
                Token.ARCTANH
                as function,
                _
            ]:
                self.__consume()
                self.__expect(Token.LPAREN, f'opening parenthesis after {function.name}')
                expr_node = self.__expr()
                self.__expect(Token.RPAREN, f'closing parenthesis after {function.name} argument')
                return Operation[function.name], expr_node
            
            case [Token.LPAREN, _]:
                self.__consume()
                expr_node = self.__expr()
                self.__expect(Token.RPAREN, f'closing parenthesis after expression')
                return expr_node

            case _:
                raise SyntaxError(f'Unexpected token {token.name}')


def evaluate_AST(node):
    match node:
        case [Operation.CONST, value]:
            return lambda x: np.full_like(x, value)
        
        case [Operation.VARIABLE, _]:
            return lambda x: x
        
        case [
            Operation.ADD |
            Operation.SUBTRACT |
            Operation.MULTIPLY |
            Operation.DIVIDE |
            Operation.POWER
            as operation,
            lhs,
            rhs
        ]:
            opeartor = operation.value
            return lambda x: opeartor(evaluate_AST(lhs)(x), evaluate_AST(rhs)(x))
        
        case [
            Operation.NEGATIVE |
            Operation.ABS |
            Operation.LOG |
            Operation.EXP |
            Operation.SIN |
            Operation.COS |
            Operation.TAN |
            Operation.ARCSIN |
            Operation.ARCCOS |
            Operation.ARCTAN |
            Operation.SINH |
            Operation.COSH |
            Operation.TANH |
            Operation.ARCSINH |
            Operation.ARCCOSH |
            Operation.ARCTANH
            as operation,
            arg
        ]:
            operator = operation.value
            return lambda x: operator(evaluate_AST(arg)(x))
        
        case _:
            raise ValueError(f'Invalid AST node: {node}')


if __name__ == '__main__':
    expr = sys.argv[1]
    parser = Parser(expr)
    ast = parser.parse()
    print(ast)

    val = float(sys.argv[2])
    print(evaluate_AST(ast)(val))