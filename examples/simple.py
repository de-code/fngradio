import fngradio as fngr

@fngr.interface()
def add_int_numbers(a: int, b: int) -> int:
    """
    Add two int numbers
    """
    return a + b


if __name__ == '__main__':
    add_int_numbers.launch(share=False, mcp_server=True)
