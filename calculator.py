#hyperskill smart calculator project
import re
import enum


class Status(enum.Enum):

    exit = 0
    help = 1
    unknown_command = 2
    is_empty = 3
    has_equal = 4
    invalid_expression = 5
    invalid_identifier = 6
    unknown_variable = 7
    invalid_assignment = 8
    ok = 9
    division_by_zero = 10


class Calculator:

    help_message = (Status.help, "This program can add and subtract numbers")
    help_command = "/help"
    exit_command = "/exit"
    unknown_command = (Status.unknown_command, "Unknown command")
    unknown_variable = (Status.unknown_variable, "Unknown variable")
    invalid_expression = (Status.invalid_expression, "Invalid expression")
    invalid_identifier = (Status.invalid_identifier, "Invalid identifier")
    invalid_assignment = (Status.invalid_assignment, "Invalid assignment")
    division_by_zero = (Status.division_by_zero, "Division by zero")
    exit_bye = (Status.exit, "Bye")
    plus = "+"
    minus = "-"

    def __init__(self):
        self.numbers = []
        self.expression = ""
        self.string = ""
        self.left_part = ""
        self.right_part = ""
        self.variables = {}

    def clear(self):
        self.numbers = []

    @staticmethod
    def substract(num1, num2):
        return num1 - num2

    @staticmethod
    def add(num1, num2):
        return num1 + num2

    @staticmethod
    def multiply(num1, num2):
        return num1 * num2

    def divide(self, numerator, denominator):
        if denominator == 0:
            return self.division_by_zero
        else:
            return Status.ok, numerator // denominator

    def is_command(self):
        if self.string.startswith("/"):
            return True
        return False

    def is_help(self):
        if self.string == self.help_command:
            return True
        return False

    def is_exit(self):
        if self.is_command() and self.string == self.exit_command:
            return True
        return False

    def is_empty(self):
        if self.string == "":
            return True
        return False

    def is_valid_command(self):
        if self.is_help() or self.is_exit():
            return True
        return False

    def is_assignment_expression(self):
        if "=" in self.string:
            return True
        return False

    def split_expression(self, expression):
        expression = expression + " "
        number_str = ""
        variable = ""
        split_expression = []
        i = 0
        while i < len(expression):
            if expression[i].isdigit():
                while expression[i].isdigit():
                    number_str += expression[i]
                    i += 1
                split_expression.append(number_str)
                number_str = ""
            elif expression[i].isalpha():
                while expression[i].isalpha():
                    variable += expression[i]
                    i += 1
                number = self.variables[variable]
                split_expression.append(str(number))
                variable = ""
            elif expression[i] == " ":
                i += 1
            elif expression[i] == ")" or "(":
                split_expression.append(expression[i])
                i += 1
            else:
                split_expression.append(expression[i])
                i += 1
        return Status.ok, split_expression

    def split(self):
        split_by_equal = self.string.split("=")
        self.left_part = split_by_equal[0].strip()
        self.right_part = split_by_equal[1].strip()

    @staticmethod
    def is_sign(item):
        re_expression = "((-|\+)*|(\*|/){1,1})"
        pattern_string = re.compile(re_expression)
        if pattern_string.match(item):
            return True
        return False

    def get_value_from_dict(self, item):
        if item in self.variables:
            number = self.variables[item]
            return Status.ok, number
        return self.unknown_variable

    def validate_assignment(self):
        self.split()
        if self.left_part.isalpha():
            if self.right_part.isalpha():
                return self.get_value_from_dict(self.right_part)
            if self.right_part.isdigit():
                return Status.ok, self.right_part
            return self.invalid_assignment
        return self.invalid_identifier

    def execute_assignment_expression(self):
        status, value = self.validate_assignment()
        if self.string.count("=") == 1:
            if status == Status.ok:
                self.variables[self.left_part] = value
                return Status.ok, None
            return status, value
        return self.invalid_assignment

    def execute_command(self):
        if self.is_help():
            return self.help_message
        if self.is_exit():
            return self.exit_bye
        return self.unknown_command

    def validate_number_parentheses(self):
        parentheses = []
        number_parentheses = 0
        for char in self.string:
            if char == "(":
                parentheses.append(char)
                number_parentheses += 1
            elif char == ")":
                try:
                    parentheses.pop()
                except IndexError:
                    return self.invalid_expression
        if not parentheses:
            return Status.ok, number_parentheses
        return self.invalid_expression

    def check_expression_is_variable(self, expression):
        if expression.isalpha():
            if expression in self.variables:
                return Status.ok, str(self.variables[expression])
            return self.unknown_variable
        return Status.ok, None

    def validate_parentheses_expression(self, expression):
        status, value = self.check_expression_is_variable(expression)
        if value is None:
            try:
                return Status.ok, int(expression)
            except ValueError:
                variables = "|".join(self.variables.keys()) + "|"
                if variables == "|":
                    variables = ""
                operand_expression = "(" + variables + "\d+)"
                re_expression = "(\+|-)?" + operand_expression + \
                    "\s*(((\+|-)+|(\*|/){1,1})\s*" + operand_expression + ")+"
                pattern_string = re.compile(re_expression)
                if pattern_string.match(expression):
                    status, value = Status.ok, expression
                else:
                    status, value = self.invalid_expression
        return status, value

    def do_some_fucking_magic(self):
        parentheses = ""
        i = 0
        index_start = 0
        if "(" and ")" not in self.string:
            index_end = len(self.string)
        else:
            while self.string[i] != ")":
                char = self.string[i]
                if parentheses == "":
                    if char == "(":
                        index_start = i + 1
                else:
                    if char == "(":
                        index_start = i + 1
                        parentheses = ""
                i += 1
            index_end = i
        expression_indexes = [index_start, index_end]
        return Status.ok, expression_indexes

    def check_parentheses_expression(self):
        status, value = self.do_some_fucking_magic()
        start_index = value[0]
        end_index = value[1]
        expression = self.string[start_index: end_index]
        status, value = self.validate_parentheses_expression(expression)
        if status == Status.ok:
            value = [start_index, end_index]
        return status, value

    def replace_parentheses_by_number(self):
        status, value = self.check_parentheses_expression()
        start_index = value[0]
        end_index = value[1]
        if status is Status.ok:
            status, value = self.split_expression(self.string[start_index:end_index])
            if status is Status.ok:
                status, value = self.execute_calculation_expression_parentheses(value)
                if start_index != 0:
                    self.string = self.string[:start_index - 1] + str(value) + self.string[end_index + 1:]
                    return status, None
        return status, value

    def execute_calculation_expression(self):
        status, value = self.validate_number_parentheses()
        if status == Status.ok:
            while len(self.string) > 0:
                status, value = self.replace_parentheses_by_number()
                if value is not None:
                    break
        return status, value

    def get_variable_value(self, item):
        first = 0
        second = 1
        if item.isalpha():
            if item in self.variables:
                return self.get_value_from_dict(item)
            return self.unknown_variable
        if item[first] == self.plus and item[second:].isalpha():
            variable = item[second:]
            if variable in self.variables:
                return Status.ok, str(self.get_value_from_dict(variable))
            return self.unknown_variable
        if item[first] == self.minus and item[second:].isalpha():
            variable = item[second:]
            if variable in self.variables:
                return Status.ok, str((-1) * self.get_value_from_dict(variable))
            return self.unknown_variable
        return Status.ok, item

    def convert_digit_to_int(self, item):
        try:
            number = int(item)
            return Status.ok, number
        except ValueError:
            if self.is_sign(item):
                return Status.ok, None
            return self.invalid_assignment

    def add_numbers_to_list(self, split_expression):
        numbers = []
        status, value = Status.ok, numbers
        for item in split_expression:
            status, value = self.get_variable_value(item)
            if status == Status.ok:
                status, value = self.convert_digit_to_int(value)
                if status is Status.ok and value is not None:
                    numbers.append(value)
        if status == Status.ok:
            value = numbers
        return status, value

    def execute_calculation_expression_parentheses(self, split_expression):
        status, numbers = self.add_numbers_to_list(split_expression)
        multiply = "*"
        division = "/"
        signs = [x for x in split_expression if split_expression.index(x) % 2 == 1]
        while len(signs) > 0:
            if multiply in signs:
                index = signs.index(multiply)
                numbers[index] = self.multiply(numbers[index], numbers[index + 1])
                numbers.pop(index + 1)
                signs.pop(index)
            elif division in signs:
                index = signs.index(division)
                status, value = self.divide(numbers[index], numbers[index + 1])
                numbers[index] = value
                numbers.pop(index + 1)
                signs.pop(index)
            else:
                for item in signs:
                    index = signs.index(item)
                    if self.minus in item:
                        if signs[index].count(self.minus) % 2 == 1:
                            numbers[index] = self.substract(numbers[index], numbers[index + 1])
                    else:
                        numbers[index] = self.add(numbers[index], numbers[index + 1])
                    numbers.pop(index + 1)
                    signs.pop(index)
        number = numbers.pop()
        return Status.ok, number

    def read_input_data(self, input_str):
        self.clear()
        self.string = input_str.strip()
        if self.is_empty():
            return Status.is_empty, None
        if self.is_command():
            return self.execute_command()
        if self.is_assignment_expression():
            return self.execute_assignment_expression()
        return self.execute_calculation_expression()


def main():
    calculator = Calculator()
    while not calculator.is_exit():
        expression = input()
        result = calculator.read_input_data(expression)
        if result[0] == Status.exit:
            print(result[1])
            break
        else:
            if result[1] is not None:
                print(result[1])
            continue


main()

