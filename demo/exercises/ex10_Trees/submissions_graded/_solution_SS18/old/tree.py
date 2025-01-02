"""
Definition of tree objects (with arbitrarily many children).
"""

# This class is a modification/extension of https://stackoverflow.com/a/28015122.


class Tree(object):
    """Generic tree node."""

    def __init__(self, name='root', children=None):
        self.name = name
        self.children = []
        self.parent = None
        if children is not None:
            for child in children:
                self.add_child(child)
                child.parent = self  # NEW

    def add_child(self, node):
        assert isinstance(node, Tree)
        self.children.append(node)

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.printout_oneline()
        # return self.printout_plain()
        # return self.printout_fancy()
        # return [self.name] + (child.__str__() for child in self.children)

    # --------------
    # Helper methods
    # --------------

    def preorder(self):
        """Pre-order traversal:
        First yield the node itself, then recurse through its children.

        :return: A list of tree nodes in pre-order."""
        res = []
        res.append(self)
        for child in self.children:
            res += child.preorder()
        return res
        # return [self] + (child.preorder() for child in self.children)

    def postorder(self):
        """Post-order traversal:
        First recurse through the node's children, then yield the node itself.

        :return: A list of tree noes in post-order."""
        res = []
        for child in self.children:
            res += child.postorder()
        res.append(self)
        return res
        # return (child.postorder() for child in self.children) + [self]

    def inorder(self):
        """Post-order traversal:
        First recurse through into the lft child, then visit the node itself, then recurse into the other children in
        order.

        :return: A list of tree noes in in-order."""
        res = []
        if len(self.children) > 0:
            res += self.children[0].inorder()
        res.append(self)
        for i in range(1, len(self.children)):
            res += self.children[i].inorder()
        return res
        # return (self.children[0].inorder() if len(self.children) > 0) +
        #     [self] + (self.children[i].inorder() for i in range(1,len(self.children)))

    @staticmethod
    def names(nodelist):
        """Given a list of nodes, return a list consisting of the names of the nodes.

        :param nodelist: A list of tree nodes.
        :return: A list of of the names of the tree nodes."""
        return [node.name for node in nodelist]

    def printout_oneline(self):
        """One-line string representation"""
        res = "[" + self.name + " "
        for child in self.children:
            res += child.printout_oneline() + ", "
        res = res.strip(', ')
        res += "]"
        return res
        #         return [self] + [child.preorder() for child in self.children]

    def printout_plain(self, ind_level=0):
        """Simple two-dimensional string representation with increasing indentation and no visual edges."""
        # For each level of nesting, increase the indentation by three whitespaces.
        ret = ind_level * "   " + self.name + "\n"
        for child in self.children:
            ret += child.printout_plain(ind_level + 1)
        return ret

    def printout_fancy(self, indent="", last_sibling=True):
        """Fancy two-dimensional string representation with increasing indentation and edges between siblings."""
        # Start with the root by prefixing its name with "|--".
        # Then loop through the node's children, if it has any:
        # If self has no siblings "to the right" (i.e. nodes on the same horizontal level vertically further down), then
        # for its children simply increase the indentation by three whitespaces and recursively descend into the child.
        # Otherwise, if there are more nodes on the level of self downwards the tree, include in the indentation the
        # vertical line "|" continuing downwards the tree to connect to the next sibling of self.
        # While ranging through the children, pass on to each of them the knowledge whether or not they are themselves
        # the youngest among their siblings, which is the case iff they are the last element in the list.

        # v1
        ret = indent + "|--" + self.name + "\n"
        if self.children:
            if last_sibling:
                for i, child in enumerate(self.children):
                    ret += child.printout_fancy(indent + "   ", i == len(self.children) - 1)
            else:
                for i, child in enumerate(self.children):
                    ret += child.printout_fancy(indent + "|  ", i == len(self.children) - 1)
                ret += indent + "|  " + "\n"
        return ret

        # # v2
        # ret = indent + "|  \n" + indent + "|--" + self.name + "\n"
        # if self.children:
        #     if last_sibling:
        #         for i, child in enumerate(self.children):
        #             ret += child.printout_fancy(indent + "   ", i == len(self.children) - 1)
        #     else:
        #         for i, child in enumerate(self.children):
        #             ret += child.printout_fancy(indent + "|  ", i == len(self.children) - 1)
        # return ret

        # # v3
        # ret = indent + "|--" + self.name + "\n"
        # for i, child in enumerate(self.children):
        #     if last_sibling:
        #         ret += child.printout_fancy(indent + "   ", i == len(self.children)-1)
        #     else:
        #         ret += child.printout_fancy(indent + "|  ", i == len(self.children)-1)
        # return ret

