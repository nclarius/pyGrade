import unittest
from tree import *


class MyTestCase(unittest.TestCase):

    def test_printout(self):
        print("\nprintout")
        print("book.printout_oneline():\n", book.printout_oneline() + "\n")
        print("book.prinout_plain():\n", book.printout_plain() + "\n")
        print("book.prinout_fancy():\n", book.printout_fancy() + "\n")
        print("str(book):\n", str(book), "\n")
        self.assertEqual(abc.printout_oneline(), abc_printout_oneline)
        self.assertEqual(abc.printout_plain(), abc_printout_plain)
        self.assertEqual(abc.printout_fancy(), abc_printout_fancy)

    def test_preorder(self):
        print("\npreorder")
        print("book.preorder():\n", Tree.names(book.preorder()))
        print("abc.preorder():\n", Tree.names(abc.preorder()))
        self.assertEqual(Tree.names(book.preorder()), book_preorder)
        self.assertEqual(Tree.names(abc.preorder()), abc_preorder)

    def test_postorder(self):
        print("\npostorder")
        print("book.postorder():\n", Tree.names(book.postorder()))
        print("abc.postorder():\n", Tree.names(abc.postorder()))
        self.assertEqual(Tree.names(book.postorder()), book_postorder)
        self.assertEqual(Tree.names(abc.postorder()), abc_postorder)


if __name__ == '__main__':
    unittest.main()

# --------------------
# Test tree definitions
# --------------------

# book:
# - Book
# - - Chapter 1
# - - - Section 1.1
# - - - Section 1.2
# - - Chapter 2
# - - - Section 2.1
# - - - - Subsection 2.1.1
# - - - - Subsection 2.1.2
# - - Chapter 3
book = Tree('Book', [
    Tree('Chapter 1', [Tree('Section 1.1'), Tree('Section 1.2')]),
    Tree('Chapter 2', [Tree('Section 2.1', [Tree('Subsection 2.1.1'), Tree('Subsection 2.1.2')])]),
    Tree('Chapter 3')
    ])

book_preorder = ['Book',
                 'Chapter 1', 'Section 1.1', 'Section 1.2',
                 'Chapter 2', 'Section 2.1', 'Subsection 2.1.1', 'Subsection 2.1.2',
                 'Chapter 3']
book_postorder = ['Section 1.1', 'Section 1.2', 'Chapter 1',
                  'Subsection 2.1.1', 'Subsection 2.1.2', 'Section 2.1', 'Chapter 2',
                  'Chapter 3',
                  'Book']

# abc:
# - A
# - - B
# - - - D
# - - C
# - - - E
# - - - F
# - - - G
# - - - - H
abc = Tree('A', [
    Tree('B', [Tree('D')]),
    Tree('C', [Tree('E'), Tree('F'), Tree('G', [Tree('H')])])
           ])

abc_printout_oneline = "[A [B [D]], [C [E], [F], [G [H]]]]"
abc_printout_plain = "A\n" +\
                     "   B\n" +\
                     "      D\n" +\
                     "   C\n" +\
                     "      E\n" +\
                     "      F\n" +\
                     "      G\n" +\
                     "         H\n"
abc_printout_fancy = "|--A\n" +\
                     "   |--B\n" +\
                     "   |  |--D\n" +\
                     "   |  \n" +\
                     "   |--C\n" +\
                     "      |--E\n" +\
                     "      |--F\n" +\
                     "      |--G\n" +\
                     "         |--H\n"

abc_preorder = ['A', 'B', 'D', 'C', 'E', 'F', 'G', 'H']
abc_postorder = ['D', 'B', 'E', 'F', 'H', 'G', 'C', 'A']
