# Project general coding standards


## Code indentation
- Always use 4 spaces for indentation
- Avoid using tabs for indentation
- Ensure consistent indentation across all files
- Use a linter to enforce indentation rules

## Code formatting
- Use a linter to enforce code formatting rules
- Always add spaces around operators, including `=`, `+`, `-`, `*`, `/`, and `%`.
- Always add spaces after commas in lists, dictionaries, and function arguments
- Use `black` for Python code formatting
- Always wrap lines in code.
- Do not break lines longer than 79 characters.
- Do not break long strings into multiple lines.

## Naming conventions
- Use snake_case for variables, dictionaries, pandas data frames, numpy, arrays, functions, and methods
- Use PascalCase for component names, interfaces, and type aliases
- Prefix private class members with an underscore (e.g., `_privateMember`)
- use ALL_CAPS for constants (e.g., `MAX_LENGTH`)

## Error handling
- Use `try-catch` blocks for async operations and handle errors gracefully
- Implement proper error boundaries in React components to catch rendering errors
- Always log errors with contextual information.

## Docstrings
- Use google-style docstrings for all public functions and classes
- Include parameter types, return types, and a description of the function's purpose
- Always include Args, Returns, Raises, and Examples sections in docstrings
- Try to keep docstrings concise and informative

## Python code style
- Use snake_case for Python variables, dictionaries, pandas data frames, numpy, arrays, functions, and methods
- Use snake_case for Python functions, methods, and variables.
- Use PascalCase for component names, interfaces, and type aliases
- Use PascalCase for modules, classes, packages, and exceptions
- Use ALL_CAPS for constants (e.g., `MAX_LENGTH`)
- Always use docstrings for all public functions and classes and follow the google-style docstring format as described above.
- Use `is` for comparison to `None` (e.g., `if variable is None:`)
- Use `==` for comparison to other values (e.g., `if variable == value:`)
- Use `with` statements for file handling to ensure proper resource management
- Use `enumerate()` for iterating over lists with index
- Use `zip()` for iterating over multiple lists in parallel
- Use list comprehensions for creating lists from existing lists
- Use `set()` for creating sets from existing lists
- Use `dict()` for creating dictionaries from existing lists.
- Do not break lines longer than 79 characters.
- Do not break long strings into multiple lines.
- Do not break long comma separated lists into multiple lines.
- Do not break long comma separated dictionary lists into multiple lines.
- Always wrap lines in code.
- Always use 4 spaces for indentation.
- Always add spaces around operators, including `=`, `+`, `-`, `*`, `/`, and `%`.
- Always add spaces after commas in lists, dictionaries, and function arguments.

## Julia code style
- Use snake_case for Julia variables, functions, and methods
- Use PascalCase for modules, types, and constants
- Use ALL_CAPS for constants (e.g., `MAX_LENGTH`)
- Always use docstrings for all public functions and types and follow the google-style docstring format as described above.
- Use `is` for comparison to `nothing` (e.g., `if variable === nothing:`)
- Use `==` for comparison to other values (e.g., `if variable == value:`)
- Use `do` blocks for passing functions as arguments
- Use list comprehensions for creating arrays from existing arrays
- Use `Set()` for creating sets from existing arrays
- Use `Dict()` for creating dictionaries from existing arrays.
- Do not break lines longer than 92 characters.
- Do not break long strings into multiple lines.
- Do not break long comma separated lists into multiple lines.
- Do not break long comma separated dictionary lists into multiple lines.
- Always wrap lines in code.
- Always use 4 spaces for indentation.
- Always add spaces around operators, including `=`, `+`, `-`, `*, `/`, and `%`.
- Always add spaces after commas in lists, dictionaries, and function arguments.

