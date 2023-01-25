import autoflake

from .NodeSelector import input_modules

src = """
import pandas

df1 = "something"
df2 = "something as well"
print(df2)
"""


def delete_unused_variables(code: str) -> str:
    def pre_process(src: str) -> str:
        return "def some_function():\n" + src.replace("\n", "\n\t")

    def post_process(src: str) -> str:
        return src[1:].replace("\n\t", "\n")

    code = pre_process(code)
    module_names = ",".join([module.module_name for module in input_modules])
    new_code = autoflake.fix_code(
        code, additional_imports=module_names, remove_unused_variables=True, remove_rhs_for_unused_variables=True
    )
    return post_process(new_code)


def main():
    print(delete_unused_variables(src))


if __name__ == "__main__":
    main()
