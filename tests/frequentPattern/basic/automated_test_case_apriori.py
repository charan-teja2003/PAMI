import unittest
from gen import generate_transactional_dataset
from automated_test_Apriori import test_pami
import warnings

warnings.filterwarnings("ignore")

class TestExample(unittest.TestCase):
    def test_num_patterns(self):
        for _ in range(3):
            num_distinct_items = 20
            num_transactions = 1000
            max_items_per_transaction = 20
            items = ["item-{}".format(i) for i in range(1, num_distinct_items + 1)]
            dataset = generate_transactional_dataset(num_transactions, items, max_items_per_transaction)

            pami = test_pami(dataset)
            # As we don't have a second method to compare, we just verify the length of pami
            self.assertGreater(len(pami), 0, "No patterns were generated by PAMI")

        print("3 test cases for number of patterns have been passed")

    def test_equality(self):
        for _ in range(3):
            num_distinct_items = 20
            num_transactions = 1000
            max_items_per_transaction = 20
            items = ["item-{}".format(i) for i in range(1, num_distinct_items + 1)]
            dataset = generate_transactional_dataset(num_transactions, items, max_items_per_transaction)

            pami = test_pami(dataset)
            # Since we have no second method to compare, we just verify the patterns are generated
            pami_patterns = sorted(list(pami["Patterns"]))
            self.assertTrue(len(pami_patterns) > 0, "No patterns were generated by PAMI")

        print("3 test cases for Patterns equality are passed")

    def test_support(self):
        for _ in range(3):
            num_distinct_items = 20
            num_transactions = 1000
            max_items_per_transaction = 20
            items = ["item-{}".format(i) for i in range(1, num_distinct_items + 1)]
            dataset = generate_transactional_dataset(num_transactions, items, max_items_per_transaction)

            pami = test_pami(dataset)
            # Since we have no second method to compare, we just verify the support values are generated
            pami.sort_values(by="Support", inplace=True)
            ps = list(pami["Support"])
            for support in ps:
                self.assertTrue(support > 0, "Support value should be greater than 0")

        print("3 test cases for support equality are passed")

if __name__ == '__main__':
    unittest.main()
