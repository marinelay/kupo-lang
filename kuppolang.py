import re

PRINT_PREFIX = "노동만세"
ASCII_PRINT_PREFIX = "노동멋져"
class KuppoLangParser:
    def __init__(self):
        self.variables = {}

    def delete_comment(self, line: str):
        # 주석을 제거하는 정규 표현식
        line = re.sub(r"#.*", "", line)
        return line.strip()

    def tokenize(self, line: str):
        if line.startswith("모그리다쿠뽀"):
            return ("START",)
        if line.startswith("메멘토모그리"):
            return ("END",)
        if line.startswith(PRINT_PREFIX):
            return ("PRINT", line)
        if line.startswith(ASCII_PRINT_PREFIX):
            return ("ASCII_PRINT", line)
        if re.match(r"(쿠뽀+)!(\s*(\S+))", line):
            return ("ASSIGN", line)
        if re.search(r"쿠뽀+([~\?]쿠뽀+)+", line):
            return ("EXPR", line)
        if re.match(r"쿠뽀+", line) or re.match(r"(폼)|(포(오*)옴)", line):
            return ("USE", line)

        return ("UNKNOWN", line)

    def parse(self, tokens):
        if tokens[0] == "ASSIGN":
            return self.parse_assign(tokens[1])
        elif tokens[0] == "PRINT":
            return self.parse_print(tokens[1])
        elif tokens[0] == "ASCII_PRINT":
            return self.parse_ascii_print(tokens[1])
        elif tokens[0] == "START":
            print("시작이다 쿠뽀~!")
            return 
        elif tokens[0] == "END":
            print("끝이다 쿠뽀...")
            return
        elif tokens[0] in ("EXPR", "USE"):
            return self.parse_expr(tokens[1])
        return "UNKNOWN COMMAND"
    
    def parse_start(self, line):
        return self.parse(self.tokenize(line))

    def parse_assign(self, command):
        match = re.match(r"(쿠뽀+)!(\s*(\S+))", command)
        if match:
            var = len(match.group(1)) - 1
            value = self.evaluate_expression(match.group(2))
            self.variables[var] = value
            # print(f"{match.group(1)}에 {value}를 넣었다 쿠뽀~!")
        else:
            print("Invalid assignment command")


    def parse_use(self, command):
        match = re.findall(r"쿠뽀+", command)
        if match:
            value = self.variables[len(match.group(1)) - 1]
            return value

    def parse_print(self, command):
        print_expression = command[len(PRINT_PREFIX):].strip()
        is_enter = print_expression.startswith("!!")
        if is_enter:
            print_expression = print_expression[2:]
        else:
            print_expression = print_expression[1:]
        
        value = self.parse_start(print_expression)
        print(f"{value}", end="" if not is_enter else "\n")

    def parse_ascii_print(self, command):
        ascii_expression = command[len(ASCII_PRINT_PREFIX):].strip()
        is_enter = ascii_expression.startswith("!!")
        if is_enter:
            ascii_expression = ascii_expression[2:]
        else:
            ascii_expression = ascii_expression[1:]

        if ascii_expression == "뽐":
            # space bar
            print(" ", end="" if not is_enter else "\n")
            return

        value = self.parse_start(ascii_expression)
        print(f"{chr(value+64)}", end="" if not is_enter else "\n")

    def parse_expr(self, command):
        result = self.evaluate_expression(command)
        return result

    def evaluate_expression(self, expression):
        # 폼, 포오옴 => 정수
        # 쿠뽀, 쿠뽀뽀 => 변수
        # 쿠뽀~쿠뽀 => 덧셈
        # 쿠뽀?쿠뽀 => 뺄셈

        if re.match(r"(\S+)\s*([~\?])\s*(\S+)", expression):
            return self.evaluate_expression_with_operators(expression)
        elif re.match(r"쿠뽀+", expression):
            # Get variable value
            return self.get_variable(expression)
        elif re.match(r"(폼)|(포(오*)옴)", expression):
            # 폼, 포오옴 => 정수
            match = re.match(r"(폼)|(포(오*)옴)", expression)
            if match.group(1):
                return 1
            elif match.group(2):
                return len(match.group(2))
        else:
            raise ValueError(f"Invalid expression: {expression}")



    
    def evaluate_expression_with_operators(self, expression):
        terms = re.split(r"([~\?])", expression)
        terms = [term.strip() for term in terms if term.strip()]
        result = self.evaluate_expression(terms[0])

        for i in range(1, len(terms) - 1, 2):
            operator = terms[i]
            # print(terms[i + 1])
            operand = self.evaluate_expression(terms[i + 1])

            if operator == "~":
                result += operand
            elif operator == "?":
                result -= operand
            # elif operator == "*":
            #     result *= operand
            # elif operator == "/" and operand != 0:
            #     result //= operand

        return result

    def get_variable(self, token: str):
        if token.startswith("쿠뽀"):
            index = len(token) - 1
            return self.variables.get(index)
        
        raise ValueError(f"Invalid variable token: {token}")

    def execute(self, code: str):
        for line in code.strip().splitlines():
            line = self.delete_comment(line)
            tokens = self.tokenize(line.strip())
            result = self.parse(tokens)
            # if result:
            #     print(result)

# 테스트
interpreter = KuppoLangParser()
code = """
모그리다쿠뽀
쿠뽀!폼~포오옴        # 첫 번째 변수에 4
쿠뽀뽀!포오옴       # 두 번째 변수에 3
쿠뽀뽀뽀!포오오옴    # 세 번째 변수에 4
노동만세!!쿠뽀뽀~쿠뽀뽀?쿠뽀뽀    # 3 + 3 - 3 = 3
쿠뽀뽀뽀뽀!포오옴      # 네 번째 변수에 3
쿠뽀뽀뽀뽀뽀뽀!포오오오옴 # 여섯 번째 변수에 5
노동만세!!쿠뽀뽀뽀뽀뽀뽀~쿠뽀뽀  # 5 + 3 = 8 출력
노동멋져!포오오오오오오옴 # H
노동멋져!포오오오옴 # E
노동멋져!포오오오오오오오오오오옴 # L
노동멋져!포오오오오오오오오오오옴 # L
노동멋져!포오오오오오오오오오오오오오옴 # O
노동멋져!뽐 # space bar
노동멋져!포오오오오오오오오오옴 # K
노동멋져!포오오오오오오오오오오오오오오오오오오오옴 # U
노동멋져!포오오오오오오오오오오오오오오옴 # P
노동멋져!!포오오오오오오오오오오오오오옴 # O

메멘토모그리
"""
interpreter.execute(code)