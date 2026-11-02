"""Input and arithmetic contracts for the trusted computation component."""

from __future__ import annotations

import copy
import unittest

from zoomconnect.execution import (
    ExecutionError,
    MAX_ITEMS,
    approved_algorithms,
    evaluate,
    validate_binding,
)


class ExecutionContracts(unittest.TestCase):
    def binding(self, algorithm="total", **changes):
        descriptor = {
            "BASE_PIN": "ROOT", "COMMON_ACTION": "calculate",
            "INNER_LENS": "ARBITRARY_WORLD", "UNIQUE_ACTION": "measurement",
            "algorithm": algorithm,
        }
        descriptor.update(changes)
        return descriptor

    def request(self, data, **changes):
        request = {
            "BASE_PIN": "ROOT", "COMMON_ACTION": "calculate",
            "INNER_LENS": "ARBITRARY_WORLD", "UNIQUE_ACTION": "measurement",
            "data": data,
        }
        request.update(changes)
        return request

    def test_approved_operations_produce_expected_values(self):
        data = [4500, 3800, 5200]
        expected = {"total": 13500, "count": 3, "average": 4500, "min": 3800, "max": 5200}
        self.assertEqual(set(approved_algorithms()), set(expected))
        for algorithm, result in expected.items():
            with self.subTest(algorithm=algorithm):
                self.assertEqual(evaluate(self.request(data), self.binding(algorithm)), result)

    def test_empty_total_and_count_are_defined(self):
        self.assertEqual(evaluate(self.request([]), self.binding("total")), 0)
        self.assertEqual(evaluate(self.request([]), self.binding("count")), 0)

    def test_empty_extrema_and_average_are_rejected(self):
        for algorithm in ("average", "min", "max"):
            with self.subTest(algorithm=algorithm):
                with self.assertRaises(ExecutionError) as failure:
                    evaluate(self.request([]), self.binding(algorithm))
                self.assertEqual(failure.exception.code, "INPUT_EMPTY")

    def test_binding_normalization_copies_and_versions_the_contract(self):
        original = self.binding()
        normalized = validate_binding(original)
        original["algorithm"] = "max"
        self.assertEqual(normalized["algorithm"], "total")
        self.assertEqual(normalized["version"], 1)
        self.assertEqual(normalized["input_type"], "number_list")

    def test_algorithm_names_cannot_evaluate_or_import_code(self):
        for name in ("__import__('os').system('anything')", "builtins.sum", "unregistered"):
            with self.subTest(name=name):
                with self.assertRaises(ExecutionError) as failure:
                    validate_binding(self.binding(name))
                self.assertEqual(failure.exception.code, "UNAPPROVED_ALGORITHM")

    def test_unknown_contract_fields_are_not_silently_accepted(self):
        with self.assertRaises(ExecutionError):
            validate_binding(self.binding(unsafe_source="arbitrary code"))

    def test_invalid_versions_are_rejected(self):
        for version in (0, -1, True, 1.5, "1", 2**31):
            with self.subTest(version=version):
                with self.assertRaises(ExecutionError):
                    validate_binding(self.binding(version=version))

    def test_unsupported_input_contract_is_rejected(self):
        with self.assertRaises(ExecutionError):
            validate_binding(self.binding(input_type="arbitrary_object"))

    def test_missing_cycle_selection_is_rejected(self):
        request = self.request([1, 2])
        del request["COMMON_ACTION"]
        with self.assertRaises(ExecutionError) as failure:
            evaluate(request, self.binding())
        self.assertEqual(failure.exception.code, "REQUEST_FIELDS")

    def test_request_cannot_override_implementation_or_add_hidden_parameters(self):
        with self.assertRaises(ExecutionError):
            evaluate(self.request([1], algorithm="max"), self.binding())

    def test_each_cycle_selection_field_must_match_the_contract(self):
        for field in ("BASE_PIN", "COMMON_ACTION", "INNER_LENS", "UNIQUE_ACTION"):
            with self.subTest(field=field):
                request = self.request([1, 2])
                request[field] = "DIFFERENT"
                with self.assertRaises(ExecutionError) as failure:
                    evaluate(request, self.binding())
                self.assertEqual(failure.exception.code, "CONTRACT_MISMATCH")

    def test_non_list_input_is_not_coerced(self):
        for data in (123, "123", {"a": 1}, (1, 2), None):
            with self.subTest(data=data):
                with self.assertRaises(ExecutionError):
                    evaluate(self.request(data), self.binding())

    def test_boolean_values_are_not_treated_as_numbers(self):
        for value in (True, False):
            with self.subTest(value=value):
                with self.assertRaises(ExecutionError) as failure:
                    evaluate(self.request([1, value]), self.binding())
                self.assertEqual(failure.exception.code, "BAD_NUMBER")

    def test_nested_or_text_values_are_rejected(self):
        for value in ([2], "2", {"value": 2}, None):
            with self.subTest(value=value):
                with self.assertRaises(ExecutionError):
                    evaluate(self.request([1, value]), self.binding())

    def test_nan_infinity_and_excessive_integers_are_rejected(self):
        for value in (float("nan"), float("inf"), -float("inf"), 10**1000):
            with self.subTest(type=type(value).__name__):
                with self.assertRaises(ExecutionError):
                    evaluate(self.request([value]), self.binding())

    def test_item_limit_is_enforced_before_computation(self):
        with self.assertRaises(ExecutionError) as failure:
            evaluate(self.request([0] * (MAX_ITEMS + 1)), self.binding("count"))
        self.assertEqual(failure.exception.code, "INPUT_LIMIT")
        self.assertEqual(evaluate(self.request([0] * MAX_ITEMS), self.binding("count")), MAX_ITEMS)

    def test_average_does_not_overflow_a_finite_result(self):
        self.assertEqual(evaluate(self.request([1e308, 1e308]), self.binding("average")), 1e308)

    def test_average_preserves_small_contributions_during_cancellation(self):
        self.assertEqual(evaluate(self.request([1e16, 1, -1e16]), self.binding("average")), 1 / 3)

    def test_non_finite_total_is_rejected(self):
        with self.assertRaises(ExecutionError):
            evaluate(self.request([1e308, 1e308]), self.binding("total"))

    def test_computation_does_not_mutate_the_request_or_external_contract(self):
        request, binding = self.request([1, 2.5, -3]), self.binding()
        original_request, original_binding = copy.deepcopy(request), copy.deepcopy(binding)
        self.assertEqual(evaluate(request, binding), 0.5)
        self.assertEqual(request, original_request)
        self.assertEqual(binding, original_binding)


if __name__ == "__main__":
    unittest.main()
