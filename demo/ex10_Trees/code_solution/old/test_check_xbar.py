import unittest
from check_xbar import *
# from check_xbar_traversive import *
from tree import *


class TestCheckXbar(unittest.TestCase):

    def test_is_terminal(self):
        self.assertTrue(is_terminal(cat_terminal))
        self.assertFalse(is_terminal(cat_N))

    def test_same_cat(self):
        self.assertTrue(same_cat(cat_terminal, cat_N))
        self.assertTrue(same_cat(cat_N, cat_NP))
        self.assertTrue(same_cat(cat_NP, cat_NP.parent))

    def test_category(self):
        self.assertEqual(category(cat_Nbar), "N")
        self.assertEqual(category(cat_terminal), "N")
        self.assertEqual(category(on_the_mat), "P")
        self.assertEqual(category(quickly), "Adv")

    def test_level(self):
        self.assertEqual(level(cat_terminal), 0)
        self.assertEqual(level(cat_N), 0)
        self.assertEqual(level(cat_Nbar), 1)
        self.assertEqual(level(cat_NP), 2)
        self.assertEqual(level(on_the_mat), 2)
        self.assertEqual(level(quickly), 2)

    def test_is_xbar(self):
        self.assertFalse(is_xbar(cat_terminal))
        self.assertTrue(is_xbar(cat_N))
        self.assertTrue(is_xbar(cat_Nbar))
        self.assertTrue(is_xbar(cat_NP))
        self.assertTrue(is_xbar(on_the_mat))
        self.assertFalse(is_xbar(cat_wrong_no_N1))
        self.assertFalse(is_xbar(cat_wrong_two_N1))
        self.assertFalse(is_xbar(cat_wrong_category_mismatch))
        self.assertFalse(is_xbar(cat_wrong_two_heads))

    def test_is_phrase(self):
        self.assertTrue(is_phrase(cat_NP))
        self.assertFalse(is_phrase(cat_Nbar))
        self.assertFalse(is_phrase(cat_N))
        self.assertTrue(is_phrase(the_small_cat))
        self.assertTrue(is_phrase(the_small_black_cat))
        self.assertTrue(is_phrase(the_cat_on_the_mat))
        self.assertTrue(is_phrase(on_the_mat))

    def test_is_bar(self):
        self.assertFalse(is_bar(cat_N))
        self.assertTrue(is_bar(cat_Nbar))
        self.assertFalse(is_bar(cat_NP))

    def test_is_head(self):
        self.assertFalse(is_head(cat_terminal))
        self.assertTrue(is_head(cat_N))
        self.assertFalse(is_head(cat_Nbar))


if __name__ == '__main__':
    unittest.main()

# --------------------
# Test tree definitions
# --------------------

cat_terminal = Tree('cat')
cat_N = Tree('N0', [cat_terminal])
cat_Nbar = Tree('N1', [cat_N])
cat_NP = Tree('N2', [cat_Nbar])
the = Tree('D2', [Tree('D1', [Tree('D0', [Tree('the')])])])

the_cat = Tree('N2', [the, cat_Nbar])

the_small_cat = Tree('N2',
                     [the,
                      Tree('N1',
                           [Tree('A2', [Tree('A1', [Tree('A0', [Tree('small')])])]),
                            cat_Nbar
                            ])
                      ])  # adjunct

the_small_black_cat = Tree('N2',
                           [the,
                            Tree('N1',
                                 [Tree('A2', [Tree('A1', [Tree('A0', [Tree('small')])])]),
                                  Tree('N1',
                                       [Tree('A2', [Tree('A1', [Tree('A0', [Tree('black')])])]),
                                        cat_Nbar
                                        ])
                                  ])
                            ])  # iteration of adjuncts

on_the_mat = Tree('P2', [Tree('P1',
                              [Tree('P0', [Tree('on')]),
                               Tree('N2',
                                    [Tree('D2', [Tree('D1', [Tree('D0', [Tree('the')])])]),
                                     Tree('N1', [Tree('N0', [Tree('mat')])])])
                               ])
                         ])  # complement

the_cat_on_the_mat = Tree('N2',
                          [the,
                           Tree('N1', [cat_Nbar, on_the_mat])
                           ])

quickly = Tree('Adv2', [Tree('Adv1', [Tree('Adv0', [Tree('quickly')])])])  # len(category) > 1

cat_wrong_no_N1 = Tree('N2', [the, cat_N])  # no N' level
cat_wrong_two_N1 = Tree('N2', [Tree('N1', [cat_Nbar])])  # one N' level too many
cat_wrong_category_mismatch = Tree('P2', [the, Tree('N1', [cat_N])])  # categories of phrase and bar don't match
cat_wrong_two_heads = Tree('N1', [cat_N, cat_N])  # two heads
