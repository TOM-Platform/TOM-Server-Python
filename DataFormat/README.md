# DataTypes.json

- This file contains the data types used in the data format.
- Conventions for `key`:
    - Format: AB, where A is the service (0-999), B is the identifier (0-99)
    - Use 0-99 (i.e., B only) for common data types, which does not have a specific service
    - Use A00-A99 for specific services

# ProtoFiles

- This directory contains the proto files for the data format.
- The proto files are used to generate the data format classes in the respective languages.
    - Use the `protoc` compiler to generate the classes. See [DeveloperGuide.md](../DeveloperGuide.md) for details.
- The generated classes are used to serialize and deserialize the data format.
- Use subdirectories to organize the proto files based on the service.