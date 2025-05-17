import sys
import re

PRINT_PREFX = "모그모그"
PRINT_POSTFIX = "다쿠뽀~"
ASCII_PRINT_POSTFIX = "다쿠뽀!"

BRANCH_REGEX = r"메멘토(\s*(\S+))모그리(\s*(\S+))"

class KuppoLangParser:
    def __init__(self):
        self.variables = {}
        self.start = False
        self.end = False

    def delete_comment(self, line: str):
        line = re.sub(r"#.*", "", line)
        return line.strip()

    def tokenize(self, line: str):
        if line.startswith("시작이다쿠뽀"):
            return ("START",)
        if line.startswith("끝이다쿠뽀"):
            return ("END",)
        if line.startswith(PRINT_PREFX):
            if line.endswith(PRINT_POSTFIX):
                return ("PRINT", line)
            if line.endswith(ASCII_PRINT_POSTFIX):
                return ("ASCII_PRINT", line)
            
            raise ValueError(f"Invalid print command: {line}")
        if line.startswith("폼폼"):
            return ("JUMP", line[2:])
        
        # 쿠뿌{exp}?{statement}
        if re.match(BRANCH_REGEX, line):
            return ("BRANCH", line)
        if re.match(r"(쿠뽀+)!(\s*(\S+))", line):
            return ("ASSIGN", line)


        # if re.search(r"쿠뽀+([.\?~]쿠뽀+)+", line):
        #     return ("EXPR", line)
        # if re.match(r"쿠뽀+", line) or re.match(r"(폼)|(포(오*)옴)", line):
        #     return ("USE", line)

        return ("EXPR", line)

    def parse(self, tokens):
        if tokens[0] == "START":
            self.start = True
            print("시작이다 쿠뽀~!")
            return 
        elif tokens[0] == "END":
            self.end = True

            if self.start:
                print("끝이다 쿠뽀...")
            return
        
        if not self.start:
            return
        if self.end:
            return

        if tokens[0] == "ASSIGN":
            return self.parse_assign(tokens[1])
        elif tokens[0] == "PRINT":
            return self.parse_print(tokens[1])
        elif tokens[0] == "ASCII_PRINT":
            return self.parse_ascii_print(tokens[1])
        elif tokens[0] in ("EXPR", "USE"):
            return self.parse_expr(tokens[1])
        elif tokens[0] == "JUMP":
            return ("JUMP", self.parse_expr(tokens[1]))
        elif tokens[0] == "BRANCH":
            match = re.match(BRANCH_REGEX, tokens[1])
            branch_exp = match.group(2)
            execute_stmt = match.group(4)

            val_branch = self.evaluate_expression(branch_exp)

            if val_branch == 0:
                return
            else:
                # print(f"쿠뿌~! {val_branch}이므로 {execute_stmt}을 실행한다 쿠뽀~!")
                return self.parse_start(execute_stmt)
        
        raise ValueError(f"Unknown token: {tokens[0]}")
    
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
        print_expression = command[len(PRINT_PREFX):-len(PRINT_POSTFIX)].strip()
        is_enter = (print_expression == "")
        if is_enter:
            print()
            return
        
        value = self.parse_start(print_expression)
        print(f"{value}", end="")

    def parse_ascii_print(self, command):
        ascii_expression = command[len(PRINT_PREFX):-len(ASCII_PRINT_POSTFIX)].strip()
        if ascii_expression == "":
            # space bar
            print(" ", end="")
            return

        value = self.parse_start(ascii_expression)
        print(f"{chr(value)}", end="")

    def parse_expr(self, command):
        result = self.evaluate_expression(command)
        return result

    def evaluate_expression(self, expression):
        # 폼, 포오옴 => 정수
        # 쿠뽀, 쿠뽀뽀 => 변수
        # 쿠뽀~쿠뽀 => 덧셈
        # 쿠뽀?쿠뽀 => 뺄셈

        if re.match(r"(\S+)\s*([.~\?])\s*(\S+)", expression):
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
        terms = re.split(r"([.\?~])", expression)
        terms = [term.strip() for term in terms if term.strip()]
        result = self.evaluate_expression(terms[0])

        for i in range(1, len(terms) - 1, 2):
            operator = terms[i]
            operand = self.evaluate_expression(terms[i + 1])

            if operator == ".":
                result += operand
            elif operator == "?":
                result -= operand
            elif operator == "~":
                result *= operand

        return result

    def get_variable(self, token: str):
        if token.startswith("쿠뽀"):
            index = len(token) - 1
            return self.variables.get(index)
        
        raise ValueError(f"Invalid variable token: {token}")

    def execute(self, code: str):
        lines = code.strip().splitlines()
        lines = [self.delete_comment(line) for line in lines]
        idx = 0
        
        while idx < len(lines):
            line = lines[idx].strip()
            if line == "":
                idx += 1
                continue

            token = self.tokenize(line)
            if token[0] == "END":
                self.parse(token)
                break

            result = self.parse(token)
            if isinstance(result, tuple) and result[0] == "JUMP":
                idx = result[1]
                continue
            idx += 1

def run(code):
    interpreter = KuppoLangParser()
    interpreter.execute(code)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python kuppolang.py <filename>")
        sys.exit(1)
    filename = sys.argv[1]
    with open(filename, "r") as f:
        code = f.read()
    interpreter = KuppoLangParser()
    interpreter.execute(code)