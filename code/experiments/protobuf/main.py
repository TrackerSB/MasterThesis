
if __name__ == "__main__":
    from example_pb2 import Person
    person = Person()
    person.id = 1234
    person.name = "John Doe"
    print("Person:")
    print(person)
    print("Serialized:")
    serialized = person.SerializeToString()
    print(serialized)
    print()
    print("Deserialized:")
    deserialized_person = Person()
    deserialized_person.ParseFromString(serialized)
    print(deserialized_person)
