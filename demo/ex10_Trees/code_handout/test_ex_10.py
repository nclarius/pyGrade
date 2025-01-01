# -*- coding: UTF-8 -*-
"""
Universität Tübingen - Seminar für Sprachwissenschaft
VL 'Programming and Data Analysis' SS 2019
© Johannes Dellert, Maxim Korniyenko, Natalie Clarius, Gerhard Jäger

Assignment 09: Trees and X-bar theory
Tests
"""
import unittest

from ex_10 import *


class TestTask1(unittest.TestCase):

    ############
    # Setup
    ############

    def setUp(self):
        self.book = Tree('Book', [
            Tree('Chapter 1', [Tree('Section 1.1'), Tree('Section 1.2')]),
            Tree('Chapter 2', [Tree('Section 2.1', [Tree('Subsection 2.1.1'), Tree('Subsection 2.1.2')])]),
            Tree('Chapter 3')
        ])

        self.book_preorder = ['Book',
                     'Chapter 1', 'Section 1.1', 'Section 1.2',
                     'Chapter 2', 'Section 2.1', 'Subsection 2.1.1', 'Subsection 2.1.2',
                     'Chapter 3']
        self.book_postorder = ['Section 1.1', 'Section 1.2', 'Chapter 1',
                      'Subsection 2.1.1', 'Subsection 2.1.2', 'Section 2.1', 'Chapter 2',
                      'Chapter 3',
                      'Book']

    ############
    # Traversals
    ############

    # Preorder

    def test_preorder_1(self):
        self.assertEqual(Tree.names(self.book.preorder())[:4], self.book_preorder[:4])

    def test_preorder_2(self):
        self.assertEqual(Tree.names(self.book.preorder()), self.book_preorder)

    # Postorder

    def test_postorder_1(self):
        self.assertEqual(Tree.names(self.book.postorder())[:4], self.book_postorder[:4])

    def test_postorder_2(self):
        self.assertEqual(Tree.names(self.book.postorder()), self.book_postorder)


class TestTask2(unittest.TestCase):

    def setUp(self):
        ############
        # well-formed trees
        ############

        self.the = \
            Tree('D2', [
                Tree('D1', [
                    Tree('D0', [
                        Tree('the')
                    ])
                ])
            ])

        self.cat_terminal = \
            Tree('cat')

        self.cat_N = \
            Tree('N0', [
                self.cat_terminal
            ])

        self.cat_Nbar = \
            Tree('N1', [
                self.cat_N
            ])

        self.cat_NP = \
            Tree('N2', [
                self.cat_Nbar
            ])

        self.the_cat = \
            Tree('N2', [
                self.the, self.cat_Nbar
            ])

        self.mat_terminal = \
            Tree('mat')

        self.mat_N = \
            Tree('N0', [
                self.mat_terminal
            ])

        self.mat_Nbar = \
            Tree('N1', [
                self.mat_N
            ])

        self.mat_NP = \
            Tree('N2', [
                self.mat_Nbar
            ])

        self.the_mat = \
            Tree('N2', [
                self.the, self.mat_Nbar
            ])

        # adjunct
        self.small_cat = \
            Tree('N1', [
                Tree('A2', [
                    Tree('A1', [
                        Tree('A0', [
                            Tree('small')
                        ])
                    ])
                ]),
                self.cat_Nbar
            ])

        # iteration of adjuncts
        self.small_black_cat = \
            Tree('N1', [
                Tree('A2', [
                    Tree('A1', [
                        Tree('A0', [
                            Tree('small')
                        ])
                    ])
                ]),
                Tree('N1', [
                    Tree('A2', [
                        Tree('A1', [
                            Tree('A0', [
                                Tree('black')
                            ])
                        ])
                    ]),
                    self.cat_Nbar
                ])
            ])

        # complement
        self.on_the_mat_Pbar = \
            Tree('P1', [
                Tree('P0', [
                    Tree('on')
                ]),
                Tree('N2', [
                    self.the,
                    Tree('N1', [
                        Tree('N0', [
                            Tree('mat')
                        ])
                    ])
                ])
            ])

        # complement
        self.on_the_mat = \
            Tree('P2', [
                self.on_the_mat_Pbar
            ])

        # adjunct
        self.cat_on_the_mat = \
            Tree('N1', [
                self.cat_Nbar,
                self.on_the_mat
            ])

        # adjunct
        self.the_cat_on_the_mat = \
            Tree('N2', [
                self.the,
                self.cat_on_the_mat
            ])

        # len(category) > 1
        self.quickly = \
            Tree('Adv2', [
                Tree('Adv1', [
                    Tree('Adv0', [
                        Tree('quickly')
                    ])
                ])
            ])

        ###############
        # ill-formed trees
        ###############

        # categories of phrase and bar don't match
        self.cat_ill_Dbar_category_mismatch = \
            Tree('P1', [
                Tree('P0', [
                    Tree('on')
                ])
            ])
        self.cat_ill_Dbar_category_mismatch.parent = \
            Tree('D2', [
                Tree('P1', [
                    Tree('P0', [
                        Tree('on')
                    ])
                ])
            ])
        self.cat_ill_Dbar_category_mismatch_recursion = \
            Tree('N2', [
                Tree('D2', [
                    Tree('P1', [
                        Tree('P0', [
                            Tree('on')
                        ])
                    ])
                ]),
                Tree('N1', [
                    Tree('N0', [
                        Tree('cat')
                    ])
                ])
            ])

        # categories of head and bar don't match
        self.cat_ill_Dhead_category_mismatch = \
            Tree('P0', [
                Tree('on')
            ])
        self.cat_ill_Dhead_category_mismatch.parent = \
            Tree('D1', [
                Tree('P0', [
                    Tree('on')
                ])
            ])
        self.cat_ill_Dhead_category_mismatch_recursion = \
            Tree('N2', [
                Tree('D2', [
                    Tree('D1', [
                        Tree('P0', [
                            Tree('on')
                        ])
                    ])
                ]),
                Tree('N1', [
                    Tree('N0', [
                        Tree('cat')
                    ])
                ])
            ])

        # no N' level
        self.cat_ill_no_N1 = \
            Tree('N2', [
                self.the,
                self.cat_N
            ])

        # one N' level too many
        self.cat_ill_two_N1 = \
            Tree('N2', [
                Tree('N1', [
                    self.cat_Nbar
                ])
            ])

        # two heads
        self.mat_ill_two_heads = \
            Tree('N1', [
                self.mat_N,
                self.mat_N
            ])
        self.mat_ill_two_heads_recursion = \
            Tree('P2', [
                Tree('P1', [
                    Tree('P0', [
                        Tree('on')
                    ]),
                    self.mat_ill_two_heads
                ])
            ])

        # no head
        self.mat_ill_no_head = \
            Tree('N1', [
                Tree('cat')
            ])
        self.mat_ill_no_head_recursion = \
            Tree('P2', [
                Tree('P1', [
                    Tree('P0', [
                        Tree('on')
                    ]),
                    self.mat_ill_no_head
                ])
            ])

        # nonsense at X2: phrase structure
        self.cat_ill_nonense_phrase = \
            Tree('N2', [
                Tree('not a cat')
            ])

        # nonsense at X2: no specifier structure
        self.cat_ill_nonense_no_specifier = \
            Tree('N2', [
                Tree('N1', [
                    Tree('not a cat')
                ])
            ])

        # nonsense: at N2: specifier structure
        self.cat_ill_nonense_specifier = \
            Tree('N2', [
                Tree('D2', [
                    Tree('not a cat')
                ]),
                Tree('N1', [
                    Tree('not a cat')
                ])
            ])

        # nonsense at X1: no adjunct or complement structure
        self.cat_ill_nonense_no_adjunct_or_complement = \
            Tree('N1', [
                Tree('N0', [
                    Tree('N0', [
                        Tree('not a cat')
                    ])
                ])
            ])

        # nonsense at X1: complement structure
        self.cat_ill_nonense_complement = \
            Tree('N1', [
                Tree('N0', [
                    Tree('not a cat')
                ]),
                Tree('N2', [
                    Tree('not a cat')
                ])
            ])

        # nonense at X1: adjunct structure 1
        self.cat_ill_nonense_adjunct1 = \
            Tree('N1', [
                Tree('P2', [
                    Tree('not a cat')
                ]),
                Tree('N1', [
                    Tree('not a cat')
                ])
            ])

        # nonsense at X1: adjunct structure 2
        self.cat_ill_nonense_adjunct2 = \
            Tree('N1', [
                Tree('N1', [
                    Tree('not a cat')
                ]),
                Tree('P2', [
                    Tree('not a cat')
                ])
            ])

        # nonense at X0: head structure
        self.cat_ill_nonense_head = \
            Tree('N0', [
                Tree('not a cat', [
                    Tree('not a cat')
                ])
            ])

    ############
    # Projection levels
    ############

    # Xbar

    def test_01_is_xbar_1(self):
        self.assertTrue(self.the_cat_on_the_mat.is_xbar())
        self.assertTrue(self.cat_on_the_mat.is_xbar())
        self.assertTrue(self.cat_N.is_xbar())
        self.assertTrue(self.cat_terminal.is_xbar())

    def test_01_is_xbar_2(self):
        self.assertFalse(self.cat_ill_no_N1.is_xbar())
        self.assertFalse(self.cat_ill_Dbar_category_mismatch_recursion.is_xbar())
        self.assertFalse(self.mat_ill_no_head.is_xbar())

    # Phrase    # already implemented

    def test_02_is_phrase_projection_1(self):
        self.assertTrue(self.cat_NP.is_phrase_projection())
        self.assertFalse(self.cat_N.is_phrase_projection())

    def test_02_is_phrase_projection_2(self):
        self.assertTrue(self.the_cat_on_the_mat.is_phrase_projection())

    def test_02_is_phrase_projection_3(self):
        self.assertFalse(self.cat_N.is_phrase_projection())

    def test_02_is_phrase_projection_4(self):
        self.assertFalse(self.cat_ill_no_N1.is_phrase_projection())

    # Bar

    def test_03_is_bar_projection_1(self):
        self.assertTrue(self.cat_Nbar.is_bar_projection())
        self.assertFalse(self.cat_NP.is_bar_projection())

    def test_03_is_bar_projection_3(self):
        self.assertFalse(self.cat_ill_Dbar_category_mismatch.is_bar_projection())

    def test_03_is_bar_projection_4(self):
        self.assertFalse(self.mat_ill_two_heads.is_bar_projection())
        self.assertFalse(self.mat_ill_no_head.is_bar_projection())

    # Head

    def test_04_is_head_projection_1(self):
        self.assertTrue(self.cat_N.is_head_projection())
        self.assertFalse(self.cat_NP.is_head_projection())

    def test_04_is_head_projection_2(self):
        self.assertFalse(self.cat_ill_Dhead_category_mismatch.is_head_projection())

    ############
    # Structural constraints
    ############

    # No specifier

    def test_05_is_no_specifier_structure_1(self):
        self.assertTrue(self.cat_NP.is_no_specifier_structure())
        self.assertTrue(self.on_the_mat.is_no_specifier_structure())

    def test_05_is_no_specifier_structure_2(self):
        self.assertFalse(self.cat_ill_nonense_no_specifier.is_no_specifier_structure())

    # Specifier

    def test_06_is_specifier_structure_1(self):
        self.assertTrue(self.the_cat.is_specifier_structure())
        self.assertTrue(self.the_cat_on_the_mat.is_specifier_structure())

    def test_06_is_specifier_structure_2(self):
        self.assertFalse(self.cat_ill_nonense_specifier.is_specifier_structure())

    # No adjunct or complement

    def test_07_is_no_adjunct_or_complement_structure_1(self):
        self.assertTrue(self.cat_Nbar.is_no_adjunct_or_complement_structure())
        self.assertTrue(self.cat_Nbar.is_no_adjunct_or_complement_structure())

    def test_07_is_no_adjunct_or_complement_structure_2(self):
        self.assertFalse(self.cat_ill_nonense_no_adjunct_or_complement.is_no_adjunct_or_complement_structure())

    # Complement    # already implemented

    def test_08_is_complement_structure_1(self):
        self.assertTrue(self.on_the_mat_Pbar.is_complement_structure())
        self.assertTrue(self.on_the_mat_Pbar.is_complement_structure())

    # Adjunct

    def test_09_is_adjunct_structure_1(self):
        self.assertTrue(self.cat_on_the_mat.is_adjunct_structure())

    def test_09_is_adjunct_structure_2(self):
        self.assertFalse(self.cat_ill_nonense_adjunct1.is_adjunct_structure())
        self.assertFalse(self.cat_ill_nonense_adjunct2.is_adjunct_structure())

    # Head

    def test_10_is_head_structure_1(self):
        self.assertTrue(self.cat_N.is_head_structure())
        self.assertTrue(self.cat_N.is_head_structure())

    def test_10_is_head_structure_2(self):
        self.assertFalse(self.cat_ill_nonense_head.is_head_structure())


if __name__ == '__main__':
    unittest.main()
