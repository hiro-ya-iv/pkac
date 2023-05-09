#!/usr/bin/env python
# coding: utf-8

import unittest
import os.path
import csv

import dataclasses
import typing


@dataclasses.dataclass
class Record:
    values: typing.List[str] = dataclasses.field(default_factory=list)


@dataclasses.dataclass
class CSVData:
    header: Record = None
    body: typing.List[Record] = dataclasses.field(default_factory=list)


def load_csv_data(csv_path):
    if not file_exists(csv_path):
        return None

    record_count = count_records(csv_path)
    if record_count == 0:
        return None

    return read_records(csv_path, record_count)


def save_csv_data(csv_path, csv_data):
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f, delimiter=',', quoting=csv.QUOTE_ALL)
        writer.writerow(csv_data.header.values)
        writer.writerows(list(map(lambda x: x.values, csv_data.body)))


def convert_to_csv_data(record_object_class, record_objects):
    header = Record(list(record_object_class.__annotations__.keys()))
    body = list(map(lambda x: Record(
        list(map(lambda y: str(getattr(x, y)), header.values))
    ), record_objects))
    return CSVData(header, body)


def file_exists(csv_path):
    return os.path.isfile(csv_path)


def count_records(csv_path):
    with open(csv_path, "r") as f:
        reader = csv.reader(f)
        return sum(1 for _ in reader)


def read_records(csv_path, record_count):
    csv_data = CSVData()

    with open(csv_path, "r") as f:
        reader = csv.reader(f)

        csv_data.header = Record(next(reader))
        if record_count == 1:
            return csv_data

        field_count = len(csv_data.header.values)
        for values in reader:
            if len(values) != field_count:
                print("warning: Skip values: {} Invalid values length: {}, header length: {}.".format(
                    values, len(values), field_count))
                continue
            csv_data.body.append(Record(values))

    return csv_data


class TestCSVFileIO(unittest.TestCase):
    def test_save_and_load(self):
        created_csv_data = CSVData(
            header=Record(["header1", "header2", "header3"]),
            body=[
                Record(["body1value1", "body1value2", "body1value3"]),
                Record(["body2value1", "body2value2", "body2value3"]),
            ]
        )
        print(created_csv_data)

        csv_file_path = "/tmp/csv_file_io_test_save_and_load.csv"
        print(csv_file_path)

        save_csv_data(csv_file_path, created_csv_data)
        loaded_csv_data = load_csv_data(csv_file_path)
        print(loaded_csv_data)

        self.assertEqual(loaded_csv_data, created_csv_data)

    def test_conversion(self):
        created_csv_data = CSVData(
            header=Record(["attr1", "attr2"]),
            body=[
                Record(["0", "1"]),
                Record(["1", "2"]),
            ]
        )
        print("created_csv_data: {}".format(created_csv_data))

        @dataclasses.dataclass
        class TestClass:
            attr1: int
            attr2: int

        @dataclasses.dataclass
        class TestData:
            records: typing.List[TestClass] = dataclasses.field(
                default_factory=list)

            def as_csv_data(self):
                return convert_to_csv_data(TestClass, self.records)

        test_data = TestData(
            records=[
                TestClass(0, 1),
                TestClass(1, 2),
            ]
        )
        csv_data = convert_to_csv_data(TestClass, test_data.records)

        self.assertEqual(csv_data, created_csv_data)
        as_csv_data = test_data.as_csv_data()
        self.assertEqual(as_csv_data, created_csv_data)


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
