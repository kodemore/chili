from chili import encode, serializable


def test_can_encode_parent_child() -> None:
    # given
    @serializable
    class Parent:
        foo: int

        def __init__(self, foo):
            self.foo = foo

        def some_logic(self):
            pass

    @serializable
    class Child(Parent):
        bar: float

        def __init__(self, foo, bar):
            super().__init__(foo)
            self.bar = bar

        def more_logic(self):
            pass

    parent_obj = Parent(5)
    child_obj = Child(7, 0.2)

    # when
    encoded_parent = encode(parent_obj)
    encoded_child = encode(child_obj)

    # then
    assert encoded_child == {"bar": 0.2, "foo": 7}

    assert encoded_parent == {"foo": 5}
